from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse


class Story(models.Model):
    """Una pieza colaborativa de cadáver exquisito."""

    class Visibility(models.TextChoices):
        TAIL = 'tail', 'Solo el final del fragmento anterior'
        FULL = 'full', 'El último fragmento completo'

    class Status(models.TextChoices):
        OPEN = 'open', 'Abierta'
        CLOSED = 'closed', 'Cerrada'

    title = models.CharField('título', max_length=200)
    slug = models.SlugField('slug', max_length=220, unique=True, editable=False)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_stories',
        verbose_name='creador',
    )
    prompt = models.TextField('consigna inicial', blank=True)
    visibility = models.CharField(
        'visibilidad',
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.TAIL,
    )
    tail_words = models.PositiveIntegerField(
        'palabras visibles del final',
        default=5,
        validators=[MinValueValidator(1)],
        help_text='Cuántas palabras del final se muestran (solo si la visibilidad es «solo el final»).',
    )
    max_fragments = models.PositiveIntegerField(
        'número máximo de fragmentos',
        default=5,
        validators=[MinValueValidator(2)],
    )
    status = models.CharField(
        'estado',
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField('creada', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'historia'
        verbose_name_plural = 'historias'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('corpse:detail', kwargs={'slug': self.slug})

    @property
    def is_open(self):
        return self.status == self.Status.OPEN

    def fragment_count(self):
        return self.fragments.count()

    def is_full(self):
        return self.fragment_count() >= self.max_fragments

    def last_fragment(self):
        return self.fragments.last()

    def visible_snippet(self, last=None):
        """Trozo permitido del último fragmento, según la visibilidad.

        Es lo único del cuerpo que se muestra mientras la historia sigue abierta.
        Devuelve cadena vacía si todavía no hay fragmentos.
        Acepta `last` precalculado para evitar un query duplicado.
        """
        if last is None:
            last = self.last_fragment()
        if last is None:
            return ''
        if self.visibility == self.Visibility.FULL:
            return last.text
        words = last.text.split()
        if self.tail_words >= len(words):
            return last.text
        return ' '.join(words[-self.tail_words:])

    def assembled_text(self):
        """Texto completo (todos los fragmentos en orden). Solo para historias cerradas."""
        return '\n\n'.join(fragment.text for fragment in self.fragments.all())


class Fragment(models.Model):
    """Una contribución a una historia."""

    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name='fragments',
        verbose_name='historia',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fragments',
        verbose_name='autor',
    )
    text = models.TextField('texto')
    order = models.PositiveIntegerField('orden')
    created_at = models.DateTimeField('creado', auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'fragmento'
        verbose_name_plural = 'fragmentos'
        constraints = [
            models.UniqueConstraint(
                fields=['story', 'order'],
                name='unique_fragment_order_per_story',
            ),
        ]

    def __str__(self):
        return f'{self.story.title} · fragmento {self.order}'
