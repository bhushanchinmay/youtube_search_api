import datetime
from django.test import TestCase, Client
from django.urls import reverse
from . import models
from .services import get_desired_video_details

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

    def test_get_desired_video_details(self):
        """Test the utility function get_desired_video_details."""
        # Scenario 1: Response with videoId
        result_with_id = {
            'id': {'videoId': 'test_video_123'},
            'snippet': {
                'title': 'Test Title',
                'description': 'Test Description',
                'channelId': 'test_channel_456',
                'publishedAt': '2023-10-27T12:00:00Z'
            }
        }
        expected_with_id = {
            'title': 'Test Title',
            'description': 'Test Description',
            'video_id': 'test_video_123',
            'channel_id': 'test_channel_456',
            'publish_date_time': datetime.datetime(2023, 10, 27, 12, 0, 0)
        }
        self.assertEqual(get_desired_video_details(result_with_id), expected_with_id)

        # Scenario 2: Response without videoId
        result_without_id = {
            'id': {'channelId': 'test_channel_only'},
            'snippet': {
                'title': 'Channel Title',
                'description': 'Channel Description',
                'channelId': 'test_channel_only',
                'publishedAt': '2023-10-27T15:30:00Z'
            }
        }
        expected_without_id = {
            'title': 'Channel Title',
            'description': 'Channel Description',
            'video_id': '',
            'channel_id': 'test_channel_only',
            'publish_date_time': datetime.datetime(2023, 10, 27, 15, 30, 0)
        }
        self.assertEqual(get_desired_video_details(result_without_id), expected_without_id)
