from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DetailView, View
from django_filters.views import FilterView

from .filters import StoryFilter
from .forms import FragmentForm, StoryCreateForm
from .models import Fragment, Story


class StoryListView(FilterView):
    model = Story
    filterset_class = StoryFilter
    paginate_by = 10
    template_name = 'corpse/story_list.html'
    context_object_name = 'stories'

    def get_queryset(self):
        # select_related evita N queries para story.creator; la anotación
        # fragment_count evita N COUNT queries por fila en la plantilla.
        return (
            super().get_queryset()
            .select_related('creator')
            .annotate(fragment_count=Count('fragments'))
            .order_by('-created_at')
        )

    def get_template_names(self):
        if self.request.htmx:
            return ['corpse/partials/_story_table.html']
        return [self.template_name]


class StoryDetailView(DetailView):
    model = Story
    context_object_name = 'story'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.object
        user = self.request.user
        # Mientras está abierta, solo se expone el trozo permitido del último
        # fragmento. El cuerpo oculto nunca se envía al template.
        last = story.last_fragment()
        count = story.fragment_count()
        context['snippet'] = story.visible_snippet(last=last)
        context['fragment_count'] = count
        context['can_contribute'] = (
            story.is_open
            and count < story.max_fragments
            and user.is_authenticated
            and (last is None or last.author_id != user.id)
        )
        context['is_creator'] = (
            user.is_authenticated and story.creator_id == user.id
        )
        return context


class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    form_class = StoryCreateForm
    template_name = 'corpse/story_form.html'

    def form_valid(self, form):
        story = form.save(commit=False)
        story.creator = self.request.user
        with transaction.atomic():
            story.save()
            Fragment.objects.create(
                story=story,
                author=self.request.user,
                text=form.cleaned_data['first_fragment'],
                order=1,
            )
        self.object = story
        return redirect(story.get_absolute_url())


class FragmentCreateView(LoginRequiredMixin, CreateView):
    model = Fragment
    form_class = FragmentForm
    template_name = 'corpse/fragment_form.html'

    def dispatch(self, request, *args, **kwargs):
        # Verificar autenticación antes del lookup para que usuarios anónimos
        # reciban redirect a login en vez de 404 por un slug inexistente.
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.story = get_object_or_404(Story, slug=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def _turn_error(self):
        """Mensaje de bloqueo del turno, o None si se puede contribuir."""
        story = self.story
        if not story.is_open:
            return 'Esta historia ya está cerrada.'
        if story.is_full():
            return 'Esta historia ya alcanzó su máximo de fragmentos.'
        last = story.last_fragment()
        if last is not None and last.author_id == self.request.user.id:
            return (
                'No puedes escribir dos fragmentos seguidos. '
                'Espera a que aporte otra persona.'
            )
        return None

    def get(self, request, *args, **kwargs):
        error = self._turn_error()
        if error:
            messages.error(request, error)
            return redirect(self.story.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        error = self._turn_error()
        if error:
            messages.error(request, error)
            return redirect(self.story.get_absolute_url())
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['story'] = self.story
        context['snippet'] = self.story.visible_snippet()
        context['fragment_count'] = self.story.fragment_count()
        return context

    def form_valid(self, form):
        story = self.story
        fragment = form.save(commit=False)
        fragment.story = story
        fragment.author = self.request.user
        try:
            with transaction.atomic():
                # El orden se calcula al vuelo; la UniqueConstraint(story, order)
                # corta cualquier carrera entre dos contribuciones simultáneas.
                fragment.order = story.fragment_count() + 1
                fragment.save()
        except IntegrityError:
            messages.warning(
                self.request,
                'Alguien se adelantó; aquí tienes el nuevo final del relato.',
            )
            return self.render_to_response(self.get_context_data(form=form))
        return redirect(story.get_absolute_url())


class StoryCloseView(LoginRequiredMixin, View):
    """Cierre anticipado de la historia, solo por su creador."""

    def post(self, request, slug):
        story = get_object_or_404(Story, slug=slug)
        if story.creator_id != request.user.id:
            messages.error(request, 'Solo quien creó la historia puede cerrarla.')
            return redirect(story.get_absolute_url())
        if story.is_open:
            story.status = Story.Status.CLOSED
            story.save(update_fields=['status'])
            messages.success(
                request, 'Historia cerrada: el texto completo ya es visible.'
            )
        return redirect(story.get_absolute_url())
