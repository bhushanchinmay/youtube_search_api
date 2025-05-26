from django.apps import AppConfig
import threading
# We will import services later in the ready() method to avoid circular dependencies
# and ensure the app is ready.

class YoutubeApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'youtube_api'

    def ready(self):
        from . import services # Import services here
        # Basic flag to prevent multiple starts, defined in services.py
        if not getattr(services, 'THREAD_STARTED_FLAG', False):
            services.THREAD_STARTED_FLAG = True # Set flag
            # Ensure the thread is a daemon thread so it exits when Django exits.
            thread = threading.Thread(target=services.start_service, daemon=True)
            thread.start()
            print("Background thread for YouTube service started.")
        pass
