from django.test import TestCase, Client
from django.urls import reverse
from . import models

class VideoAPITests(TestCase):

    def setUp(self):
        self.client = Client()
        models.APIKey.objects.create(key="test_key")

    def test_get_videos_endpoint_success(self):
        url = reverse('youtube_api:get_videos')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_api_key_success(self):
        url = reverse('youtube_api:add_key')
        payload = {'key': 'new_test_key'}
        response = self.client.post(url, payload, content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue(models.APIKey.objects.filter(key='new_test_key').exists())

    def test_add_api_key_invalid_payload(self):
        url = reverse('youtube_api:add_key')
        payload = {} # Missing 'key' field
        response = self.client.post(url, payload, content_type='application/json')

        self.assertEqual(response.status_code, 400)
