from typing import ClassVar

from rest_framework import serializers
from rest_framework.serializers import Serializer

from mlswarm.infrastructure.services.estimators.serializers import ITrain, ITest, IPredict
from mlswarm_api.serializers import PropertiesSerializerMixin
from . import models, services


class TaskSerializer(PropertiesSerializerMixin,
                     serializers.ModelSerializer):
    properties = serializers.JSONField(help_text='The json-like properties for task.')
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())
    estimator = serializers.PrimaryKeyRelatedField(read_only=True)

    def service_serializer_cls(self, data: dict) -> ClassVar[Serializer]:
        q = self.context['view'].get_parents_query_dict()
        e = models.Estimator.objects.get(pk=q['estimator'])

        return e.services.get(e.service)

    class Meta:
        model = models.Task
        fields = ['id', 'dataset', 'status', 'errors', 'report', 'owner', 'estimator',
                  'properties', 'started_at', 'finished_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'report', 'owner', 'estimator', 'errors',
                            'started_at', 'finished_at', 'created_at', 'updated_at']


class TrainingSerializer(TaskSerializer):
    def service_serializer_cls(self, data: dict) -> ClassVar[ITrain]:
        return super().service_serializer_cls(data).Train

    class Meta:
        model = models.Training
        fields = TaskSerializer.Meta.fields
        read_only_fields = TaskSerializer.Meta.read_only_fields


class TestSerializer(TaskSerializer):
    def service_serializer_cls(self, data: dict) -> ClassVar[ITest]:
        return super().service_serializer_cls(data).Predict

    class Meta:
        model = models.Predict
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

    trainings = TrainingSerializer(many=True, read_only=True)

    class Meta:
        model = models.Estimator
        fields = ['id', 'url', 'service', 'properties', 'created_at', 'updated_at', 'trainings']
        read_only_fields = ['id', 'url', 'created_at', 'updated_at', 'trainings']
