from django.test import TestCase
from django.urls import reverse

from stories.models import Story


class StoryListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Story.objects.create(
            title='El jardín', author='Ada', status=Story.Status.PUBLISHED
        )
        Story.objects.create(
            title='La casa', author='Grace', status=Story.Status.DRAFT
        )

    def test_list_renders_full_page(self):
        response = self.client.get(reverse('stories:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stories/story_list.html')
        self.assertContains(response, 'El jardín')
        self.assertContains(response, 'La casa')

    def test_list_filtered_by_querystring(self):
        response = self.client.get(reverse('stories:list'), {'author': 'ada'})
        self.assertContains(response, 'El jardín')
        self.assertNotContains(response, 'La casa')

    def test_htmx_request_returns_only_partial(self):
        response = self.client.get(
            reverse('stories:list'), HTTP_HX_REQUEST='true'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stories/partials/_story_table.html')
        self.assertTemplateNotUsed(response, 'stories/story_list.html')
        self.assertNotContains(response, '<nav class="navbar')


class StoryCrudViewTests(TestCase):
    def test_create_view_persists_and_redirects(self):
        response = self.client.post(
            reverse('stories:create'),
            {'title': 'Nueva', 'author': 'Ada', 'status': 'draft', 'body': 'x'},
        )
        story = Story.objects.get(title='Nueva')
        self.assertRedirects(response, story.get_absolute_url())
        self.assertEqual(story.slug, 'nueva')

    def test_update_view_changes_fields(self):
        story = Story.objects.create(title='Vieja', author='Ada')
        response = self.client.post(
            reverse('stories:update', args=[story.slug]),
            {'title': 'Vieja', 'author': 'Grace', 'status': 'published', 'body': ''},
        )
        self.assertRedirects(response, story.get_absolute_url())
        story.refresh_from_db()
        self.assertEqual(story.author, 'Grace')
        self.assertEqual(story.status, 'published')

    def test_delete_view_removes_object(self):
        story = Story.objects.create(title='Borrar', author='Ada')
        response = self.client.post(reverse('stories:delete', args=[story.slug]))
        self.assertRedirects(response, reverse('stories:list'))
        self.assertFalse(Story.objects.filter(pk=story.pk).exists())
