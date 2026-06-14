from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from .filters import StoryFilter
from .forms import StoryForm
from .models import Story


class StoryListView(FilterView):
    model = Story
    filterset_class = StoryFilter
    paginate_by = 10
    template_name = 'stories/story_list.html'
    context_object_name = 'stories'

    def get_template_names(self):
        # En peticiones HTMX devolvemos solo el fragmento de la tabla.
        if self.request.htmx:
            return ['stories/partials/_story_table.html']
        return [self.template_name]


class StoryDetailView(DetailView):
    model = Story
    context_object_name = 'story'


class StoryCreateView(CreateView):
    model = Story
    form_class = StoryForm


class StoryUpdateView(UpdateView):
    model = Story
    form_class = StoryForm


class StoryDeleteView(DeleteView):
    model = Story
    success_url = reverse_lazy('stories:list')
