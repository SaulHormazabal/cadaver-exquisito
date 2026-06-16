import django_filters
from django import forms

from .models import Story


class StoryFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Título',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    status = django_filters.ChoiceFilter(
        choices=Story.Status.choices,
        label='Estado',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Story
        fields = ['title', 'status']
