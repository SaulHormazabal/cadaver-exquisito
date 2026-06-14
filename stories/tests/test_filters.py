from django.test import TestCase

from stories.filters import StoryFilter
from stories.models import Story


class StoryFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Story.objects.create(
            title='El jardín', author='Ada', status=Story.Status.PUBLISHED
        )
        Story.objects.create(
            title='La casa', author='Grace', status=Story.Status.DRAFT
        )
        Story.objects.create(
            title='El bosque', author='Ada', status=Story.Status.DRAFT
        )

    def test_filter_by_title_icontains(self):
        f = StoryFilter({'title': 'el'}, queryset=Story.objects.all())
        titles = set(f.qs.values_list('title', flat=True))
        self.assertEqual(titles, {'El jardín', 'El bosque'})

    def test_filter_by_author_icontains(self):
        f = StoryFilter({'author': 'ada'}, queryset=Story.objects.all())
        self.assertEqual(f.qs.count(), 2)

    def test_filter_by_status(self):
        f = StoryFilter(
            {'status': Story.Status.PUBLISHED}, queryset=Story.objects.all()
        )
        self.assertEqual(f.qs.count(), 1)
        self.assertEqual(f.qs.first().title, 'El jardín')
