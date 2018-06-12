from typing import ClassVar

from drf_queryfields import QueryFieldsMixin
from rest_framework import serializers
from rest_framework.serializers import Serializer

from mlswarm.infrastructure.services.estimators.serializers import ITrain, ITest, IPredict
from mlswarm_api.serializers import PropertiesSerializerMixin
from . import models, services


class TaskSerializer(QueryFieldsMixin,
                     PropertiesSerializerMixin,
                     serializers.ModelSerializer):
    properties = serializers.JSONField(
        help_text='The json-like properties for task.')
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True)
    estimator = serializers.PrimaryKeyRelatedField(
        read_only=True)

    chunks = serializers.PrimaryKeyRelatedField(
        read_only=False,
        many=True,
        queryset=models.Chunk.objects.all())

    class Meta:
        model = models.Task
        fields = ['id', 'chunks', 'status', 'report', 'errors', 'owner', 'estimator',
                  'properties', 'started_at', 'finished_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'owner', 'estimator', 'report', 'errors',
                            'started_at', 'finished_at', 'created_at', 'updated_at']

    def validate_chunks(self, value):
        if not value:
            raise serializers.ValidationError('At least one chunk must be '
                                              'selected in order to perform '
                                              'this task.')
        return value

    def service_serializer_cls(self, data: dict) -> ClassVar[Serializer]:
        q = self.context['view'].get_parents_query_dict()
        e = models.Estimator.objects.get(pk=q['estimator'])

        return e.services.get(e.service)


class TrainingSerializer(TaskSerializer):
    def service_serializer_cls(self, data: dict) -> ClassVar[ITrain]:
        return super().service_serializer_cls(data).Train

    class Meta:
        model = models.Training
        fields = TaskSerializer.Meta.fields
        read_only_fields = TaskSerializer.Meta.read_only_fields


class TestSerializer(TaskSerializer):
    def service_serializer_cls(self, data: dict) -> ClassVar[ITest]:
        return super().service_serializer_cls(data).Test

    class Meta:
        model = models.Test
        fields = TaskSerializer.Meta.fields
        read_only_fields = TaskSerializer.Meta.read_only_fields


class PredictSerializer(TaskSerializer):
    def service_serializer_cls(self, data: dict) -> ClassVar[IPredict]:
        return super().service_serializer_cls(data).Predict

    class Meta:
        model = models.Predict
        fields = TaskSerializer.Meta.fields
        read_only_fields = TaskSerializer.Meta.read_only_fields


class EstimatorSerializer(PropertiesSerializerMixin,
                          serializers.ModelSerializer):
    properties = serializers.JSONField(help_text='The json-like properties '
                                                 'for this estimator\'s service.')
    services = services.estimators

    class Meta:
        model = models.Estimator
        fields = ['id', 'url', 'service', 'properties', 'created_at', 'updated_at']
        read_only_fields = ['id', 'url', 'created_at', 'updated_at']


class EstimatorDetailSerializer(EstimatorSerializer):
    trainings = TrainingSerializer(many=True, read_only=True)

    class Meta(EstimatorSerializer.Meta):
        fields = EstimatorSerializer.Meta.fields + ['trainings']
        read_only_fields = EstimatorSerializer.Meta.read_only_fields + ['trainings']
