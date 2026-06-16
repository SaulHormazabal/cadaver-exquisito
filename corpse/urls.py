from django.urls import path

from . import views

app_name = 'corpse'

urlpatterns = [
    path('', views.StoryListView.as_view(), name='list'),
    path('crear/', views.StoryCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.StoryDetailView.as_view(), name='detail'),
    path('<slug:slug>/contribute/', views.FragmentCreateView.as_view(), name='contribute'),
    path('<slug:slug>/close/', views.StoryCloseView.as_view(), name='close'),
]
