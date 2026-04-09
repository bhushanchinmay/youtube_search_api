import os
import time
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
django.setup()

from youtube_api.services import store_video_to_db
from youtube_api.models import Video, VideoThumbnail

def run_benchmark():
    # Mock YouTube API response
    mock_result = {
        'id': {'videoId': 'test_video_id'},
        'snippet': {
            'title': 'Test Video',
            'description': 'Test Description',
            'channelId': 'test_channel_id',
            'publishedAt': '2023-10-27T12:00:00Z',
            'thumbnails': {
                'default': {'url': 'http://example.com/default.jpg'},
                'medium': {'url': 'http://example.com/medium.jpg'},
                'high': {'url': 'http://example.com/high.jpg'},
                'standard': {'url': 'http://example.com/standard.jpg'},
                'maxres': {'url': 'http://example.com/maxres.jpg'},
                'extra1': {'url': 'http://example.com/extra1.jpg'},
                'extra2': {'url': 'http://example.com/extra2.jpg'},
                'extra3': {'url': 'http://example.com/extra3.jpg'},
                'extra4': {'url': 'http://example.com/extra4.jpg'},
                'extra5': {'url': 'http://example.com/extra5.jpg'},
            }
        }
    }

    # Clear existing data
    Video.objects.all().delete()
    VideoThumbnail.objects.all().delete()

    num_iterations = 100

    start_time = time.time()
    for _ in range(num_iterations):
        store_video_to_db(mock_result)
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"Time taken to store {num_iterations} videos: {elapsed_time:.4f} seconds")

    print(f"Videos in DB: {Video.objects.count()}")
    print(f"Thumbnails in DB: {VideoThumbnail.objects.count()}")

if __name__ == '__main__':
    run_benchmark()
