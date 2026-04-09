from django.test import TestCase
from .services import get_video_thumbnails

class GetVideoThumbnailsTests(TestCase):
    def test_get_video_thumbnails_valid(self):
        """Test with a valid response containing multiple thumbnails."""
        result = {
            'snippet': {
                'thumbnails': {
                    'default': {'url': 'http://example.com/default.jpg'},
                    'medium': {'url': 'http://example.com/medium.jpg'}
                }
            }
        }
        expected_output = [
            {'screen_size': 'default', 'url': 'http://example.com/default.jpg'},
            {'screen_size': 'medium', 'url': 'http://example.com/medium.jpg'}
        ]
        self.assertEqual(get_video_thumbnails(result), expected_output)

    def test_get_video_thumbnails_missing_snippet(self):
        """Test when 'snippet' key is missing."""
        result = {}
        self.assertEqual(get_video_thumbnails(result), [])

    def test_get_video_thumbnails_missing_thumbnails(self):
        """Test when 'thumbnails' key is missing within 'snippet'."""
        result = {'snippet': {}}
        self.assertEqual(get_video_thumbnails(result), [])

    def test_get_video_thumbnails_empty_thumbnails(self):
        """Test when 'thumbnails' is an empty dictionary."""
        result = {'snippet': {'thumbnails': {}}}
        self.assertEqual(get_video_thumbnails(result), [])

    def test_get_video_thumbnails_missing_url(self):
        """Test when 'url' key is missing within a thumbnail."""
        result = {
            'snippet': {
                'thumbnails': {
                    'default': {}
                }
            }
        }
        expected_output = [{'screen_size': 'default', 'url': None}]
        self.assertEqual(get_video_thumbnails(result), expected_output)
