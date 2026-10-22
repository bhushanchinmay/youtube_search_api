import os
import sys
import threading

from django.apps import AppConfig
from django.conf import settings


class YoutubeApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'youtube_api'

    def ready(self):
        if not settings.YOUTUBE_BACKGROUND_SERVICE:
            return
        if any(command in sys.argv for command in (
                'test', 'migrate', 'makemigrations', 'check', 'collectstatic',
                'createsuperuser', 'shell')):
            return
        if 'runserver' in sys.argv and '--noreload' not in sys.argv:
            if os.environ.get('RUN_MAIN') != 'true':
                return
        from . import services
        if not services.THREAD_STARTED_FLAG:
            services.THREAD_STARTED_FLAG = True
            threading.Thread(target=services.start_service, daemon=True).start()
