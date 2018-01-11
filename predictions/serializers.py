from rest_framework import serializers

from . import models


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dataset
        fields = ('id', 'content', 'delimiter', 'parsing_service')


class EstimatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Estimator
        fields = ('service',)


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())


class TrainingSerializer(TaskSerializer):
    class Meta:
        model = models.Training
        fields = ('dataset', 'status', 'errors',
                  'output', 'user', 'estimator',
                  'learning_rate', 'dropout_rate', 'batch_size',
                  'started_at', 'finished_at',
                  'created_at', 'updated_at')
        read_only_fields = ('status', 'output', 'errors',
                            'started_at', 'finished_at',
                            'created_at', 'updated_at')


class PredictionSerializer(TaskSerializer):
    class Meta:
        model = models.Prediction
        fields = ('dataset', 'status', 'errors',
                  'output', 'user', 'estimator',
                  'started_at', 'finished_at',
                  'created_at', 'updated_at')
        read_only_fields = ('status', 'output', 'errors',
                            'started_at', 'finished_at',
                            'created_at', 'updated_at')
