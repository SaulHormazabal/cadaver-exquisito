from django.urls import path

from . import views

app_name = 'stories'

urlpatterns = [
    path('', views.StoryListView.as_view(), name='list'),
    path('new/', views.StoryCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.StoryDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.StoryUpdateView.as_view(), name='update'),
    path('<slug:slug>/delete/', views.StoryDeleteView.as_view(), name='delete'),
]
