from django.contrib.auth import get_user_model
from django.test import TestCase

from corpse.filters import StoryFilter
from corpse.models import Story

User = get_user_model()


class StoryFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        creator = User.objects.create_user(email='creador@example.com')
        Story.objects.create(
            title='El jardín', creator=creator, status=Story.Status.OPEN
        )
        Story.objects.create(
            title='La casa', creator=creator, status=Story.Status.CLOSED
        )
        Story.objects.create(
            title='El bosque', creator=creator, status=Story.Status.OPEN
        )

    def test_filter_by_title_icontains(self):
        f = StoryFilter({'title': 'el'}, queryset=Story.objects.all())
        titles = set(f.qs.values_list('title', flat=True))
        self.assertEqual(titles, {'El jardín', 'El bosque'})

    def test_filter_by_status(self):
        f = StoryFilter(
            {'status': Story.Status.OPEN}, queryset=Story.objects.all()
        )
        self.assertEqual(f.qs.count(), 2)
