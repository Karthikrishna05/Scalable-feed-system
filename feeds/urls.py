from django.urls import path
from . import views

urlpatterns = [
    path('pull/', views.feed_pull_based, name='feed-pull'),
]