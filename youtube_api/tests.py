from django.test import TestCase, Client
from django.urls import reverse
from . import models

class VideoAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        models.APIKey.objects.create(key="test_key")

    def test_get_videos_endpoint_success(self):
        # Use reverse() with the named URL pattern
        url = reverse('youtube_api:get_videos')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Optional: Add a check for an empty list in the JSON response if no data is expected
        # or specific keys if data is expected. For a basic test, status 200 is sufficient.
        # For example, if it's okay for it to return an empty list initially:
        # self.assertEqual(response.json().get('results', []), [])
