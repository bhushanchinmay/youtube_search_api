from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from . import models
from . import services


User = get_user_model()

class VideoAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()
        models.APIKey.objects.create(key="test_key")
        self.user = get_user_model().objects.create_user(username='testuser', password='password')

    def test_get_videos_endpoint_success(self):
        # Use reverse() with the named URL pattern
        url = reverse('youtube_api:get_videos')

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
