from django.db import models
from django.urls import reverse


class Story(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Borrador'
        PUBLISHED = 'published', 'Publicada'

    title = models.CharField('título', max_length=200)
    author = models.CharField('autor', max_length=150)
    status = models.CharField(
        'estado',
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    body = models.TextField('contenido', blank=True)
    slug = models.SlugField('slug', max_length=220, unique=True, editable=False)
    created_at = models.DateTimeField('creada', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'historia'
        verbose_name_plural = 'historias'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('stories:detail', kwargs={'slug': self.slug})
