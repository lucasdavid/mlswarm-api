from rest_framework import serializers

from mlswarm_api.serializers import ServiceSerializerMixin
from . import models, services


class ChunkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chunk
        fields = ['id', 'service', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    chunks = ChunkInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Dataset
        fields = ['id', 'url', 'name', 'chunks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'url', 'chunks', 'created_at', 'updated_at']


class ChunkSerializer(ServiceSerializerMixin,
                      serializers.ModelSerializer):
    dataset = serializers.PrimaryKeyRelatedField(read_only=True)
    service_builder = services.parsers

    class Meta:
        model = models.Chunk
        fields = ['id', 'dataset', 'service', 'properties', 'created_at', 'updated_at']
        read_only_fields = ['id', 'dataset', 'created_at', 'updated_at']
