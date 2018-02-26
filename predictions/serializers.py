import json

from rest_framework import serializers

from mlswarm_api.serializers import PropertiesSerializerMixin
from . import models, services


class EstimatorSerializer(PropertiesSerializerMixin,
                          serializers.HyperlinkedModelSerializer):
    properties = serializers.JSONField(help_text='The json-like properties for this estimator\'s service.')
    services = services.estimators

    class Meta:
        model = models.Estimator
        fields = ['id', 'url', 'service', 'properties', 'created_at', 'updated_at']
        read_only_fields = ['id', 'url', 'created_at', 'updated_at']


class TaskSerializer(PropertiesSerializerMixin,
                     serializers.HyperlinkedModelSerializer):
    properties = serializers.JSONField(help_text='The json-like properties for task.')
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = models.Task
        fields = ['id', 'url', 'dataset', 'status', 'errors', 'report', 'owner', 'estimator',
                  'properties', 'started_at', 'finished_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'report', 'errors', 'started_at', 'finished_at', 'created_at', 'updated_at']


class TrainingSerializer(TaskSerializer):
    def get_service_serializer(self, service):
        return super().get_service_serializer(service).Training

    class Meta:
        model = models.Training
        fields = TaskSerializer.Meta.fields
        read_only_fields = TaskSerializer.Meta.read_only_fields


class PredictionSerializer(TaskSerializer):
    def get_service_serializer(self, service):
        return super().get_service_serializer(service).Prediction

    class Meta:
        model = models.Prediction
        fields = TaskSerializer.Meta.fields
        read_only_fields = TaskSerializer.Meta.read_only_fields


class TestSerializer(TaskSerializer):
    def get_service_serializer(self, service):
        return super().get_service_serializer(service).Prediction

    class Meta:
        model = models.Prediction
        fields = TaskSerializer.Meta.fields
        read_only_fields = TaskSerializer.Meta.read_only_fields
