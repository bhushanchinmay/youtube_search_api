from django.urls import path

from . import services
from . import views

app_name = 'youtube_api'

urlpatterns = [
    path('get_videos', views.GetVideos.as_view(), name='get_videos'),
    path('add_key', views.AddAPIKey.as_view(), name='add_key'),
]

# services.THREAD.start() # Moved to AppConfig
