from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from . import models


class VideoAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        models.APIKey.objects.create(key='test_key')
        self.user = get_user_model().objects.create_user(username='testuser')
        self.url = reverse('youtube_api:add_key')

    def test_get_videos_endpoint_success(self):
        response = self.client.get(reverse('youtube_api:get_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'], [])

    def test_get_videos_without_available_key(self):
        models.APIKey.objects.update(is_limit_over=True)
        response = self.client.get(reverse('youtube_api:get_videos'))
        self.assertEqual(response.status_code, 400)

    def test_add_api_key_unauthenticated(self):
        response = self.client.post(self.url, {'key': 'new_test_key'}, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(models.APIKey.objects.filter(key='new_test_key').exists())

    def test_add_api_key_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'key': 'new_test_key'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.APIKey.objects.filter(key='new_test_key').exists())

    def test_add_api_key_invalid_payload(self):
        self.client.force_authenticate(user=self.user)
        for payload in ({}, {'key': ''}, {'key': '   '}):
            with self.subTest(payload=payload):
                response = self.client.post(self.url, payload, format='json')
                self.assertEqual(response.status_code, 400)
        self.assertEqual(models.APIKey.objects.count(), 1)

    def test_thumbnail_queries_do_not_grow_per_video(self):
        for i in range(10):
            video = models.Video.objects.create(
                title=str(i), description='', channel_id='channel',
                video_id=str(i), publish_date_time='2026-01-01 12:00:00')
            models.VideoThumbnail.objects.create(video=video, screen_size='default', url='https://example.com/image.jpg')
        # API key existence, pagination count, videos, and all thumbnails.
        with self.assertNumQueries(4):
            response = self.client.get(reverse('youtube_api:get_videos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['results']), 10)
        self.assertTrue(all(len(video['thumbnails']) == 1 for video in response.json()['results']))
