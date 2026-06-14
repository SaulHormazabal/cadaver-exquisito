import django_filters

from .models import Story


class StoryFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Título')
    author = django_filters.CharFilter(lookup_expr='icontains', label='Autor')

    class Meta:
        model = Story
        fields = ['title', 'author', 'status']
