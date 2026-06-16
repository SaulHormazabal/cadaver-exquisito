from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from corpse.models import Fragment, Story

User = get_user_model()


class StoryListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        creator = User.objects.create_user(email='creador@example.com')
        Story.objects.create(title='El jardín', creator=creator)
        Story.objects.create(title='La casa', creator=creator)

    def test_list_renders_full_page(self):
        response = self.client.get(reverse('corpse:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'corpse/story_list.html')
        self.assertContains(response, 'El jardín')

    def test_htmx_request_returns_only_partial(self):
        response = self.client.get(reverse('corpse:list'), HTTP_HX_REQUEST='true')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'corpse/partials/_story_table.html')
        self.assertTemplateNotUsed(response, 'corpse/story_list.html')


class StoryCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='autor@example.com')

    def test_anonymous_create_redirects_to_login(self):
        response = self.client.get(reverse('corpse:create'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('account_login')))

    def test_create_persists_story_with_first_fragment(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('corpse:create'),
            {
                'title': 'Nueva',
                'prompt': 'Érase una vez',
                'visibility': Story.Visibility.TAIL,
                'tail_words': 5,
                'max_fragments': 3,
                'first_fragment': 'Había una casa al final del camino.',
            },
        )
        story = Story.objects.get(title='Nueva')
        self.assertRedirects(response, story.get_absolute_url())
        self.assertEqual(story.creator, self.user)
        self.assertEqual(story.fragment_count(), 1)
        first = story.fragments.first()
        self.assertEqual(first.order, 1)
        self.assertEqual(first.author, self.user)


class ContributeViewTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(email='creador@example.com')
        self.other = User.objects.create_user(email='otro@example.com')
        self.story = Story.objects.create(
            title='Colaborativa', creator=self.creator, max_fragments=3,
            tail_words=2, visibility=Story.Visibility.TAIL,
        )
        Fragment.objects.create(
            story=self.story, author=self.creator,
            text='primer fragmento aquí', order=1,
        )

    def test_anonymous_cannot_contribute(self):
        response = self.client.get(
            reverse('corpse:contribute', args=[self.story.slug])
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('account_login'), response.url)

    def test_happy_path_contribution(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('corpse:contribute', args=[self.story.slug]),
            {'text': 'segundo fragmento'},
        )
        self.assertRedirects(response, self.story.get_absolute_url())
        self.assertEqual(self.story.fragment_count(), 2)
        last = self.story.last_fragment()
        self.assertEqual(last.order, 2)
        self.assertEqual(last.author, self.other)

    def test_cannot_take_two_turns_in_a_row(self):
        # El creador escribió el último fragmento; no puede continuar él mismo.
        self.client.force_login(self.creator)
        response = self.client.post(
            reverse('corpse:contribute', args=[self.story.slug]),
            {'text': 'no permitido'},
        )
        self.assertRedirects(response, self.story.get_absolute_url())
        self.assertEqual(self.story.fragment_count(), 1)

    def test_cannot_contribute_to_closed_story(self):
        self.story.status = Story.Status.CLOSED
        self.story.save(update_fields=['status'])
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('corpse:contribute', args=[self.story.slug]),
            {'text': 'tarde'},
        )
        self.assertRedirects(response, self.story.get_absolute_url())
        self.assertEqual(self.story.fragment_count(), 1)

    def test_cannot_contribute_when_full(self):
        Fragment.objects.create(
            story=self.story, author=self.other, text='dos', order=2,
        )
        Fragment.objects.create(
            story=self.story, author=self.creator, text='tres', order=3,
        )
        # Ahora está llena (3/3) y auto-cerrada por el signal.
        self.client.force_login(self.other)
        response = self.client.post(
            reverse('corpse:contribute', args=[self.story.slug]),
            {'text': 'cuatro'},
        )
        self.assertRedirects(response, self.story.get_absolute_url())
        self.assertEqual(self.story.fragment_count(), 3)


class DetailVisibilityTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(email='creador@example.com')
        self.other = User.objects.create_user(email='otro@example.com')
        self.story = Story.objects.create(
            title='Secreta', creator=self.creator, max_fragments=2,
            tail_words=2, visibility=Story.Visibility.TAIL,
        )
        Fragment.objects.create(
            story=self.story, author=self.creator,
            text='palabra secreta inicial final visible', order=1,
        )

    def test_open_story_hides_full_body(self):
        response = self.client.get(self.story.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # Solo se muestran las últimas 2 palabras; el cuerpo oculto no aparece.
        self.assertContains(response, 'final visible')
        self.assertNotContains(response, 'palabra secreta inicial')

    def test_closed_story_reveals_full_text_and_authors(self):
        Fragment.objects.create(
            story=self.story, author=self.other,
            text='cierre del relato', order=2,
        )
        # El segundo fragmento alcanza el máximo y la cierra (signal).
        self.story.refresh_from_db()
        self.assertEqual(self.story.status, Story.Status.CLOSED)
        response = self.client.get(self.story.get_absolute_url())
        self.assertContains(response, 'palabra secreta inicial')
        self.assertContains(response, 'cierre del relato')
        self.assertContains(response, str(self.other))


class CloseViewTests(TestCase):
    def setUp(self):
        self.creator = User.objects.create_user(email='creador@example.com')
        self.other = User.objects.create_user(email='otro@example.com')
        self.story = Story.objects.create(
            title='Por cerrar', creator=self.creator, max_fragments=5,
        )
        Fragment.objects.create(
            story=self.story, author=self.creator, text='inicio', order=1,
        )

    def test_creator_can_close_early(self):
        self.client.force_login(self.creator)
        response = self.client.post(reverse('corpse:close', args=[self.story.slug]))
        self.assertRedirects(response, self.story.get_absolute_url())
        self.story.refresh_from_db()
        self.assertEqual(self.story.status, Story.Status.CLOSED)

    def test_non_creator_cannot_close(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('corpse:close', args=[self.story.slug]))
        self.assertRedirects(response, self.story.get_absolute_url())
        self.story.refresh_from_db()
        self.assertEqual(self.story.status, Story.Status.OPEN)
