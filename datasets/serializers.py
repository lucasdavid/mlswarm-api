from rest_framework import serializers

from mlswarm_api.serializers import PropertiesSerializerMixin
from . import models, services


class ChunkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chunk
        fields = ['id', 'service', 'created_at', 'updated_at']
        read_only_fields = ['id', 'service', 'created_at', 'updated_at']


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    chunks = ChunkInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Dataset
        fields = ['id', 'url', 'name', 'chunks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'url', 'chunks', 'created_at', 'updated_at']


class ChunkSerializer(PropertiesSerializerMixin,
                      serializers.ModelSerializer):
    dataset = serializers.PrimaryKeyRelatedField(read_only=True)
    properties = serializers.JSONField(help_text='The properties of this Chunk\'s service.')
    services = services.parsers

    class Meta:
        model = models.Chunk
        fields = ['id', 'dataset', 'service', 'properties', 'created_at', 'updated_at']
        read_only_fields = ['id', 'dataset', 'created_at', 'updated_at']
