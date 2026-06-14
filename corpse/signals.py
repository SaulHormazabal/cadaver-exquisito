from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Fragment, Story


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


@receiver(post_save, sender=Fragment)
def close_story_when_full(sender, instance, created, **kwargs):
    """Cierra la historia automáticamente al alcanzar el máximo de fragmentos."""
    if not created:
        return

    story = instance.story
    if story.is_open and story.is_full():
        story.status = Story.Status.CLOSED
        story.save(update_fields=['status'])
