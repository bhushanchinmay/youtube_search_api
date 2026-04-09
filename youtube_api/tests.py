from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from googleapiclient.errors import HttpError
from . import models
from . import services


class VideoAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()
        models.APIKey.objects.create(key="test_key")
        self.user = get_user_model().objects.create_user(username='testuser', password='password')

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


class VideoServiceTests(TestCase):

    def setUp(self):
        self.api_key = models.APIKey.objects.create(key="test_key", is_limit_over=False)

    @patch('youtube_api.services.build')
    def test_fetch_result_http_error_403(self, mock_build):
        mock_resp = MagicMock()
        mock_resp.status = 403
        mock_error = HttpError(resp=mock_resp, content=b'Quota exceeded')

        mock_build.return_value.search.return_value.list.return_value.execute.side_effect = mock_error

        result = services.fetch_result_for_search_query('test query', 10)

        self.assertEqual(result, {})

        self.api_key.refresh_from_db()
        self.assertTrue(self.api_key.is_limit_over)

    @patch('youtube_api.services.build')
    def test_fetch_result_http_error_429(self, mock_build):
        mock_resp = MagicMock()
        mock_resp.status = 429
        mock_error = HttpError(resp=mock_resp, content=b'Too many requests')

        mock_build.return_value.search.return_value.list.return_value.execute.side_effect = mock_error

        result = services.fetch_result_for_search_query('test query', 10)

        self.assertEqual(result, {})

        self.api_key.refresh_from_db()
        self.assertTrue(self.api_key.is_limit_over)

    @patch('youtube_api.services.build')
    def test_fetch_result_http_error_500(self, mock_build):
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_error = HttpError(resp=mock_resp, content=b'Internal server error')

        mock_build.return_value.search.return_value.list.return_value.execute.side_effect = mock_error

        result = services.fetch_result_for_search_query('test query', 10)

        self.assertEqual(result, {})

        self.api_key.refresh_from_db()
        self.assertFalse(self.api_key.is_limit_over)
