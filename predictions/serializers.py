from rest_framework import serializers

from mlswarm_api.serializers import ServiceSerializerMixin
from . import models, services


class EstimatorSerializer(ServiceSerializerMixin,
                          serializers.HyperlinkedModelSerializer):
    service_builder = services.estimators

    class Meta:
        model = models.Estimator
        fields = ['id', 'url', 'service', 'properties', 'created_at', 'updated_at']
        read_only_fields = ['id', 'url', 'created_at', 'updated_at']


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())


class TrainingSerializer(TaskSerializer):
    class Meta:
        model = models.Training
        fields = ['id', 'url', 'dataset', 'status', 'errors', 'report', 'owner', 'estimator',
                  'properties', 'started_at', 'finished_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'report', 'errors', 'started_at', 'finished_at', 'created_at', 'updated_at']


class PredictionSerializer(TaskSerializer):
    class Meta:
        model = models.Prediction
        fields = ['id', 'url', 'dataset', 'status', 'errors', 'report', 'owner', 'estimator',
                  'started_at', 'finished_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'report', 'errors', 'started_at', 'finished_at', 'created_at', 'updated_at']
