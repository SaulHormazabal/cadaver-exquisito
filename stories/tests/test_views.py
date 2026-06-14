from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from stories.models import Story

User = get_user_model()


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


class StoryPaginationFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for i in range(15):
            Story.objects.create(
                title=f'Publicada {i}', author='Ada', status=Story.Status.PUBLISHED
            )
        for i in range(3):
            Story.objects.create(
                title=f'Borrador {i}', author='Ada', status=Story.Status.DRAFT
            )

    def test_pagination_preserves_active_filter(self):
        # Página 2 de un filtro: 15 publicadas, paginate_by=10 -> 5 en la pág. 2,
        # y ninguna de las 3 borradores debe colarse.
        response = self.client.get(
            reverse('stories:list'), {'status': Story.Status.PUBLISHED, 'page': 2}
        )
        self.assertEqual(response.status_code, 200)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 5)
        self.assertTrue(
            all(s.status == Story.Status.PUBLISHED for s in object_list)
        )


class StoryWriteRequiresLoginTests(TestCase):
    def test_anonymous_create_redirects_to_login(self):
        response = self.client.get(reverse('stories:create'))
        login_url = reverse('account_login')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(login_url))

    def test_anonymous_update_and_delete_redirect_to_login(self):
        story = Story.objects.create(title='Protegida', author='Ada')
        for name in ('stories:update', 'stories:delete'):
            response = self.client.get(reverse(name, args=[story.slug]))
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('account_login'), response.url)


class StoryCrudViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='autor@example.com')
        self.client.force_login(self.user)

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
