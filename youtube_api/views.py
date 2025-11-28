from django import forms
from rest_framework import generics, exceptions
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer

from . import models
from . import serializers


class GetVideosPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 10


class GetVideos(generics.ListAPIView):
    """view to get all the videos, and order them by published date.

    """
    renderer_classes = [JSONRenderer]
    serializer_class = serializers.VideoSerializer
    pagination_class = GetVideosPagination

    def get_queryset(self):
        api_keys = models.APIKey.objects.filter(is_limit_over=False)
        if not len(api_keys):
            raise exceptions.ValidationError("APIKey Quota is over, Add a new APIKey")
        return models.Video.objects.all().order_by('-publish_date_time')


class AddAPIKey(generics.CreateAPIView):
    """view for adding a new Youtube Data API Key in the database.

    """
    renderer_classes = [JSONRenderer]
    serializer_class = serializers.APIKeySerializer
