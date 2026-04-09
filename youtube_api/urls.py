from django.urls import path

from . import views

urlpatterns = [
    path('get_videos', views.GetVideos.as_view()),
    path('add_key', views.AddAPIKey.as_view()),
]
