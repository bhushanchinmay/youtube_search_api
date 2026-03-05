import datetime
from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse
from . import models, services

class ServiceTests(SimpleTestCase):
    def test_get_desired_video_details_missing_video_id(self):
        """Test video_id is empty string when missing in result['id']."""
        result = {
            'id': {'kind': 'youtube#channel'},
            'snippet': {
                'title': 'Test Title',
                'description': 'Test Description',
                'channelId': 'TestChannelID',
                'publishedAt': '2023-10-27T10:00:00Z',
            }
        }
        details = services.get_desired_video_details(result)
        self.assertEqual(details['video_id'], '')
        self.assertEqual(details['title'], 'Test Title')
        self.assertEqual(details['description'], 'Test Description')
        self.assertEqual(details['channel_id'], 'TestChannelID')
        self.assertEqual(details['publish_date_time'], datetime.datetime(2023, 10, 27, 10, 0, 0))

    def test_get_desired_video_details_with_video_id(self):
        """Test video_id is correctly extracted when present in result['id']."""
        result = {
            'id': {'kind': 'youtube#video', 'videoId': '12345'},
            'snippet': {
                'title': 'Test Title',
                'description': 'Test Description',
                'channelId': 'TestChannelID',
                'publishedAt': '2023-10-27T10:00:00Z',
            }
        }
        details = services.get_desired_video_details(result)
        self.assertEqual(details['video_id'], '12345')


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
