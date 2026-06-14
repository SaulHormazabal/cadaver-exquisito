from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Story


@receiver(pre_save, sender=Story)
def set_story_slug(sender, instance, **kwargs):
    """Genera un slug único a partir del título cuando aún no existe."""
    if instance.slug:
        return

    base = slugify(instance.title) or 'historia'
    slug = base
    counter = 2
    while Story.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f'{base}-{counter}'
        counter += 1
    instance.slug = slug
