from django.contrib.auth import get_user_model
from django.test import TestCase

from corpse.models import Fragment, Story

User = get_user_model()


class StoryModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create_user(email='creador@example.com')

    def _story(self, **kwargs):
        defaults = {'title': 'Mi historia', 'creator': self.creator}
        defaults.update(kwargs)
        return Story.objects.create(**defaults)

    def test_slug_is_generated_from_title(self):
        story = self._story(title='Mi Gran Historia')
        self.assertEqual(story.slug, 'mi-gran-historia')

    def test_slug_is_unique_for_duplicate_titles(self):
        first = self._story(title='Repetida')
        second = self._story(title='Repetida')
        self.assertEqual(first.slug, 'repetida')
        self.assertEqual(second.slug, 'repetida-2')

    def test_get_absolute_url(self):
        story = self._story()
        self.assertEqual(story.get_absolute_url(), f'/historias/{story.slug}/')

    def test_is_full(self):
        story = self._story(max_fragments=2)
        self.assertFalse(story.is_full())
        Fragment.objects.create(story=story, author=self.creator, text='uno', order=1)
        self.assertFalse(story.is_full())
        Fragment.objects.create(story=story, author=self.creator, text='dos', order=2)
        self.assertTrue(story.is_full())

    def test_visible_snippet_tail_returns_last_n_words(self):
        story = self._story(visibility=Story.Visibility.TAIL, tail_words=3)
        Fragment.objects.create(
            story=story, author=self.creator,
            text='uno dos tres cuatro cinco', order=1,
        )
        self.assertEqual(story.visible_snippet(), 'tres cuatro cinco')

    def test_visible_snippet_tail_shorter_than_n_returns_all(self):
        story = self._story(visibility=Story.Visibility.TAIL, tail_words=10)
        Fragment.objects.create(
            story=story, author=self.creator, text='uno dos', order=1,
        )
        self.assertEqual(story.visible_snippet(), 'uno dos')

    def test_visible_snippet_full_returns_whole_last_fragment(self):
        story = self._story(visibility=Story.Visibility.FULL)
        Fragment.objects.create(
            story=story, author=self.creator, text='primero', order=1,
        )
        Fragment.objects.create(
            story=story, author=self.creator, text='segundo completo', order=2,
        )
        self.assertEqual(story.visible_snippet(), 'segundo completo')

    def test_visible_snippet_empty_without_fragments(self):
        story = self._story()
        self.assertEqual(story.visible_snippet(), '')

    def test_assembled_text_orders_fragments(self):
        story = self._story(max_fragments=3)
        Fragment.objects.create(story=story, author=self.creator, text='A', order=1)
        Fragment.objects.create(story=story, author=self.creator, text='C', order=3)
        Fragment.objects.create(story=story, author=self.creator, text='B', order=2)
        self.assertEqual(story.assembled_text(), 'A\n\nB\n\nC')


class FragmentSignalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.creator = User.objects.create_user(email='creador@example.com')
        cls.other = User.objects.create_user(email='otro@example.com')

    def test_story_auto_closes_when_full(self):
        story = Story.objects.create(
            title='Corta', creator=self.creator, max_fragments=2,
        )
        Fragment.objects.create(story=story, author=self.creator, text='uno', order=1)
        story.refresh_from_db()
        self.assertEqual(story.status, Story.Status.OPEN)
        Fragment.objects.create(story=story, author=self.other, text='dos', order=2)
        story.refresh_from_db()
        self.assertEqual(story.status, Story.Status.CLOSED)
