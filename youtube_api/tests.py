from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from . import models

User = get_user_model()

class VideoAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        models.APIKey.objects.create(key="test_key")

    def test_get_videos_endpoint_success(self):
        # Try to reverse the URL name if it's defined, otherwise use the hardcoded path
        try:
            # Assuming 'get_videos' is the name in youtube_api.urls.py
            # and 'youtube_api' is the app_name or namespace for the app
            url = reverse('youtube_api:get_videos')
        except: # noqa
            # If reverse fails (e.g., name not set or app namespace needed),
            # construct path manually.
            # Based on project structure: path('youtube_api/', include('youtube_api.urls')) in api/urls.py
            # and in youtube_api.urls: path('get_videos', views.GetVideos.as_view(), name='get_videos')
            # So, the full path is /youtube_api/get_videos
            url = '/youtube_api/get_videos' # Ensure no trailing slash

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Optional: Add a check for an empty list in the JSON response if no data is expected
        # or specific keys if data is expected. For a basic test, status 200 is sufficient.
        # For example, if it's okay for it to return an empty list initially:
        # self.assertEqual(response.json().get('results', []), [])

class SecurityTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        # Based on project structure: /youtube_api/add_key
        try:
            self.url = reverse('youtube_api:add_key')
        except: # noqa
            self.url = '/youtube_api/add_key'

    def test_add_api_key_unauthenticated(self):
        """Test that unauthenticated requests to add_key are rejected."""
        response = self.client.post(self.url, {'key': 'new_test_key'})
        # DRF returns 403 Forbidden for IsAuthenticated failure by default
        self.assertEqual(response.status_code, 403)

    def test_add_api_key_authenticated(self):
        """Test that authenticated requests to add_key are accepted."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(self.url, {'key': 'new_test_key'})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.APIKey.objects.filter(key='new_test_key').exists())
