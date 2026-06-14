from django import forms

from .models import Fragment, Story


class StoryCreateForm(forms.ModelForm):
    """Crear una historia incluye escribir su primer fragmento."""

    first_fragment = forms.CharField(
        label='Primer fragmento',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
    )

    class Meta:
        model = Story
        fields = ['title', 'prompt', 'visibility', 'tail_words', 'max_fragments']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'prompt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'tail_words': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'max_fragments': forms.NumberInput(attrs={'class': 'form-control', 'min': 2}),
        }


class FragmentForm(forms.ModelForm):
    class Meta:
        model = Fragment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
        }
        labels = {'text': 'Tu fragmento'}
