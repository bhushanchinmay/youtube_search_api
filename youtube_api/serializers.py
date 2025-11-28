"""This module contains serializers for Video and VideoThumbnail models."""

from rest_framework import serializers

from . import models


class VideoSerializer(serializers.ModelSerializer):
    """
    serializer for Video model.
    """
    thumbnails = serializers.SerializerMethodField()

    def get_thumbnails(self, obj):
        """get video thumbnails.

        :param obj: video object
        :return: thumbnails dictionary
        """
        return [
            VideoThumbNailSerializer(thumbnail).data
            for thumbnail in models.VideoThumbnail.objects.filter(video=obj)]

    class Meta:
        model = models.Video
        fields = '__all__'


class VideoThumbNailSerializer(serializers.ModelSerializer):
    """serializer for VideoThumbnail model.

    """
    class Meta:
        model = models.VideoThumbnail
        fields = '__all__'


class APIKeySerializer(serializers.ModelSerializer):
    """serializer for APIKey model.

    """

    class Meta:
        model = models.APIKey
        fields = '__all__'
