import asyncio
import datetime
import threading
import time

from apiclient.discovery import build
from django.db import connections

from . import models

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
TIME_INTERVAL = 10  # specify time interval for fetching the results


def fetch_result_for_search_query(query, max_results):
    """fetch the latest videos for a search query using youtube_api.

    :param query: search query.
    :param max_results: maximum number of results using the youtube_api.
    :return: dictionary of all the videos.
    """
    api_keys = models.APIKey.objects.filter(is_limit_over=False)

    if not len(api_keys):
        return {}

    DEVELOPER_KEY = api_keys[0]

    try:
        youtube_object = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                               developerKey=DEVELOPER_KEY)
        search_keyword = youtube_object.search().list(q=query, part="id, snippet",
                                                      maxResults=max_results).execute()

        results = search_keyword.get("items", [])
    except:
        api_keys[0].is_limit_over = True
        api_keys[0].save()
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
    return [{
        'screen_size': screen_size,
        'url': result['snippet']['thumbnails'][screen_size]['url'],
    } for screen_size in result['snippet']['thumbnails']]


def store_video_to_db(result):
    """store video and thumbnails to database.

    :param result: youtube_api response.
    """
    video_dict = get_desired_video_details(result)
    video_obj = models.Video(**video_dict)
    video_obj.save()

    thumbnails = get_video_thumbnails(result)
    for thumbnail in thumbnails:
        thumbnail['video'] = video_obj
        thumbnail_obj = models.VideoThumbnail(**thumbnail)
        thumbnail_obj.save()

    # closing all connections
    for conn in connections.all():
        conn.close()


def get_most_recent_video_time():
    """get most recent time for uploaded video.

    :return: datetime object
    """
    recent_date_time = ''
    search_results = fetch_result_for_search_query('today news', 10)

    if search_results == {}:
        return

    for result in search_results:
        video_date_time_obj = get_date_time_object_from_string(
            result['snippet']['publishedAt'])
        store_video_to_db(result)

        if not recent_date_time:
            recent_date_time = video_date_time_obj

        recent_date_time = max(recent_date_time, video_date_time_obj)
    return recent_date_time


async def search_and_store_youtube_videos():
    """asynchronous function for fetching and storing the latest videos for a search query.

    """
    resent_date_time = get_most_recent_video_time()

    while True:
        search_results = fetch_result_for_search_query('today news', 10)

        if search_results == {}:
            return

        for result in search_results:
            video_date_time_obj = get_date_time_object_from_string(
                result['snippet']['publishedAt'])

            if resent_date_time < video_date_time_obj:
                store_video_to_db(result)
                resent_date_time = video_date_time_obj

        await asyncio.sleep(10)


def start_service():
    """start the service for searching and storing youtube videos for every 10 seconds.

    """
    while True:
        api_keys = models.APIKey.objects.filter(is_limit_over=False)
        if len(api_keys):
            asyncio.run(search_and_store_youtube_videos())
        time.sleep(TIME_INTERVAL)


THREAD_STARTED_FLAG = False
THREAD = threading.Thread(target=start_service, daemon=True)
