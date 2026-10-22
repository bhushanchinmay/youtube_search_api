import datetime
from unittest.mock import patch

from django.test import SimpleTestCase, TestCase

from . import models, services
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


def video_result(video_id='video', published='2026-01-01T12:00:00Z'):
    return {
        'id': {'videoId': video_id},
        'snippet': {
            'title': 'Test Title', 'description': 'Test Description',
            'channelId': 'channel', 'publishedAt': published,
            'thumbnails': {
                'default': {'url': 'https://example.com/default.jpg'},
                'medium': {'url': 'https://example.com/medium.jpg'},
                'high': {'url': 'https://example.com/high.jpg'},
            },
        },
    }


class VideoDetailsTests(SimpleTestCase):
    def test_details_with_video_id(self):
        self.assertEqual(services.get_desired_video_details(video_result()), {
            'title': 'Test Title', 'description': 'Test Description',
            'channel_id': 'channel', 'video_id': 'video',
            'publish_date_time': datetime.datetime(2026, 1, 1, 12),
        })

    def test_details_without_video_id(self):
        for identity in ({}, {'channelId': 'channel'}, {'kind': 'youtube#channel'}):
            with self.subTest(identity=identity):
                result = video_result()
                result['id'] = identity
                details = services.get_desired_video_details(result)
                self.assertEqual(details['video_id'], '')
                self.assertEqual(details['publish_date_time'], datetime.datetime(2026, 1, 1, 12))

    def test_three_thumbnail_sizes(self):
        self.assertEqual(services.get_video_thumbnails(video_result()), [
            {'screen_size': size, 'url': f'https://example.com/{size}.jpg'}
            for size in ('default', 'medium', 'high')
        ])


class VideoStorageTests(TestCase):
    def test_bulk_thumbnail_insert(self):
        # A transaction savepoint, video insert, thumbnail insert, and release.
        with self.assertNumQueries(4):
            services.store_video_to_db(video_result())
        self.assertEqual(models.Video.objects.count(), 1)
        self.assertEqual(models.VideoThumbnail.objects.count(), 3)

    def test_thumbnail_failure_rolls_back_video(self):
        with patch.object(models.VideoThumbnail.objects, 'bulk_create', side_effect=ValueError('invalid thumbnails')):
            with self.assertRaises(ValueError):
                services.store_video_to_db(video_result())
        self.assertEqual(models.Video.objects.count(), 0)

    @patch('youtube_api.services.build')
    def test_no_api_key_does_not_call_youtube(self, build):
        with self.assertNumQueries(1):
            self.assertEqual(services.fetch_result_for_search_query('news', 10), {})
        build.assert_not_called()

    @patch('youtube_api.services.build')
    def test_fetch_uses_one_key_query(self, build):
        models.APIKey.objects.create(key='test')
        build.return_value.search.return_value.list.return_value.execute.return_value = {'items': [video_result()]}
        with self.assertNumQueries(1):
            self.assertEqual(len(services.fetch_result_for_search_query('news', 10)), 1)

    @patch('youtube_api.services.fetch_result_for_search_query')
    def test_batch_handles_unordered_results_and_retries(self, fetch):
        fetch.return_value = [video_result('latest', '2026-01-01T14:00:00Z'), video_result('older'), video_result('same-time', '2026-01-01T14:00:00Z')]
        services.search_and_store_youtube_videos()
        self.assertEqual(models.Video.objects.count(), 3)
        services.search_and_store_youtube_videos()
        self.assertEqual(models.Video.objects.count(), 3)

    @patch('youtube_api.services.fetch_result_for_search_query', return_value=[])
    def test_empty_batch_returns(self, fetch):
        services.search_and_store_youtube_videos()
        self.assertEqual(models.Video.objects.count(), 0)

    @patch('youtube_api.services.fetch_result_for_search_query')
    def test_channel_result_is_not_stored(self, fetch):
        result = video_result()
        result['id'] = {'channelId': 'channel'}
        fetch.return_value = [result]
        services.search_and_store_youtube_videos()
        self.assertEqual(models.Video.objects.count(), 0)


class PollingTests(SimpleTestCase):
    @patch('youtube_api.services.time.sleep', side_effect=InterruptedError)
    @patch('youtube_api.services.close_old_connections')
    @patch('youtube_api.services.search_and_store_youtube_videos')
    @patch('youtube_api.services.models.APIKey.objects.filter')
    def test_poller_checks_key_and_cleans_batch(self, keys, batch, cleanup, sleep):
        keys.return_value.exists.return_value = True
        with self.assertRaises(InterruptedError):
            services.start_service()
        batch.assert_called_once_with()
        self.assertEqual(cleanup.call_count, 2)
        sleep.assert_called_once_with(services.TIME_INTERVAL)

    @patch('youtube_api.services.time.sleep', side_effect=InterruptedError)
    @patch('youtube_api.services.close_old_connections')
    @patch('youtube_api.services.search_and_store_youtube_videos')
    @patch('youtube_api.services.models.APIKey.objects.filter')
    def test_poller_waits_when_no_keys(self, keys, batch, cleanup, sleep):
        keys.return_value.exists.return_value = False
        with self.assertRaises(InterruptedError):
            services.start_service()
        batch.assert_not_called()
        self.assertEqual(cleanup.call_count, 2)
        sleep.assert_called_once_with(services.TIME_INTERVAL)

    @patch('youtube_api.services.logger')
    @patch('youtube_api.services.time.sleep', side_effect=InterruptedError)
    @patch('youtube_api.services.close_old_connections')
    @patch('youtube_api.services.search_and_store_youtube_videos', side_effect=ValueError('failed'))
    @patch('youtube_api.services.models.APIKey.objects.filter')
    def test_poller_retries_after_failure(self, keys, batch, cleanup, sleep, logger):
        keys.return_value.exists.return_value = True
        with self.assertRaises(InterruptedError):
            services.start_service()
        logger.exception.assert_called_once()
        self.assertEqual(cleanup.call_count, 2)
        sleep.assert_called_once_with(services.TIME_INTERVAL)
