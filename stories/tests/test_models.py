from django.test import TestCase

from stories.models import Story


class StorySignalTests(TestCase):
    def test_slug_is_generated_from_title(self):
        story = Story.objects.create(title='Mi Gran Historia', author='Ada')
        self.assertEqual(story.slug, 'mi-gran-historia')

    def test_slug_is_unique_for_duplicate_titles(self):
        first = Story.objects.create(title='Repetida', author='Ada')
        second = Story.objects.create(title='Repetida', author='Grace')
        self.assertEqual(first.slug, 'repetida')
        self.assertEqual(second.slug, 'repetida-2')

    def test_slug_is_not_overwritten_on_update(self):
        story = Story.objects.create(title='Original', author='Ada')
        original_slug = story.slug
        story.title = 'Título cambiado'
        story.save()
        self.assertEqual(story.slug, original_slug)

    def test_get_absolute_url(self):
        story = Story.objects.create(title='Con URL', author='Ada')
        self.assertEqual(story.get_absolute_url(), f'/stories/{story.slug}/')
