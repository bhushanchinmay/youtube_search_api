import datetime
import time
import logging

from apiclient.discovery import build
from googleapiclient.errors import HttpError
from django.db import close_old_connections, transaction

from . import models

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
logger = logging.getLogger(__name__)

TIME_INTERVAL = 10  # specify time interval for fetching the results


def fetch_result_for_search_query(query, max_results):
    """fetch the latest videos for a search query using youtube_api.

    :param query: search query.
    :param max_results: maximum number of results using the youtube_api.
    :return: dictionary of all the videos.
    """
    api_key_obj = models.APIKey.objects.filter(is_limit_over=False).first()

    if api_key_obj is None:
        return {}

    try:
        youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                               developerKey=api_key_obj.key)
        search_keyword = youtube_object.search().list(q=query, part="id, snippet",
                                                      maxResults=max_results).execute()

        results = search_keyword.get("items", [])
    except HttpError as e:
        if e.resp.status in [403, 429]:  # Quota exceeded or too many requests
            api_key_obj.is_limit_over = True
            api_key_obj.save()
        return {}
    except Exception:
        # Log unexpected errors but don't mark key as limit over
        return {}

    return results


def get_date_time_object_from_string(date_time_str):
    """create a datetime object.

    :param date_time_str: date time in string.
    :return: datetime object.
    """
    return datetime.datetime.strptime(
        date_time_str.split('T')[0] + ' ' + date_time_str.split('T')[1].split('Z')[0],
        '%Y-%m-%d %H:%M:%S')


def get_desired_video_details(result):
    """get detail result for a video.

    :param result: youtube_api response.
    :return: video details.
    """
    if 'videoId' in result['id']:
        video_id = result['id']['videoId']
    else:
        video_id = ''
    return {
        'title': result["snippet"]["title"],
        'description': result['snippet']['description'],
        'video_id': video_id,
        'channel_id': result['snippet']['channelId'],
        'publish_date_time': get_date_time_object_from_string(
            result['snippet']['publishedAt']),
    }


def get_video_thumbnails(result):
    """get video thumbnails.

    :param result: youtube_api response.
    :return: list of details required for thumbnails.
    """
    thumbnails = (result.get('snippet') or {}).get('thumbnails') or {}
    return [{
        'screen_size': screen_size,
        'url': thumbnails.get(screen_size, {}).get('url'),
    } for screen_size in thumbnails]


@transaction.atomic
def store_video_to_db(result):
    """store video and thumbnails to database.

    :param result: youtube_api response.
    """
    video_dict = get_desired_video_details(result)
    video_obj = models.Video(**video_dict)
    video_obj.save()

    thumbnails = get_video_thumbnails(result)
    thumbnail_objs = []
    for thumbnail in thumbnails:
        thumbnail['video'] = video_obj
        thumbnail_objs.append(models.VideoThumbnail(**thumbnail))

    models.VideoThumbnail.objects.bulk_create(thumbnail_objs)


def get_most_recent_video_time():
    """get most recent time for uploaded video.

    :return: datetime object or None
    """
    recent_date_time = None
    search_results = fetch_result_for_search_query('today news', 10)

    if not search_results:
        return None

    for result in search_results:
        video_date_time_obj = get_date_time_object_from_string(
            result['snippet']['publishedAt'])
        store_video_to_db(result)

        if recent_date_time is None:
            recent_date_time = video_date_time_obj

        recent_date_time = max(recent_date_time, video_date_time_obj)

    return recent_date_time


def search_and_store_youtube_videos():
    """Fetch and store one batch, using synchronous Django database calls."""
    # Check the stored watermark once so response order cannot drop newer videos.
    latest = models.Video.objects.order_by('-publish_date_time').first()
    latest_time = latest.publish_date_time if latest else datetime.datetime.min
    for result in fetch_result_for_search_query('today news', 10):
        if not result.get('id', {}).get('videoId'):
            continue
        published = get_date_time_object_from_string(result['snippet']['publishedAt'])
        if published >= latest_time and not models.Video.objects.filter(
                video_id=result['id']['videoId']).exists():
            store_video_to_db(result)


def start_service():
    """Poll periodically and release stale connections at batch boundaries."""
    while True:
        close_old_connections()
        try:
            if models.APIKey.objects.filter(is_limit_over=False).exists():
                search_and_store_youtube_videos()
        except Exception:
            logger.exception('YouTube polling failed; retrying on the next interval.')
        finally:
            close_old_connections()
        time.sleep(TIME_INTERVAL)


THREAD_STARTED_FLAG = False
