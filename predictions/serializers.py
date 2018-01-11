from rest_framework import serializers

from . import models


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dataset
        fields = ('id', 'url', 'delimiter', 'parser')


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())


class TrainingSerializer(TaskSerializer):
    class Meta:
        model = models.Training
        fields = ('dataset', 'status', 'errors',
                  'result', 'user', 'estimator',
                  'started_at', 'finished_at',
                  'created_at', 'updated_at')
        read_only_fields = ('status', 'result', 'errors',
                            'started_at', 'finished_at',
                            'created_at', 'updated_at')


class PredictionSerializer(TaskSerializer):
    class Meta:
        model = models.Prediction
        fields = ('dataset', 'status', 'errors',
                  'result', 'user', 'training',
                  'started_at', 'finished_at',
                  'created_at', 'updated_at')
        read_only_fields = ('status', 'result', 'errors',
                            'started_at', 'finished_at',
                            'created_at', 'updated_at')
