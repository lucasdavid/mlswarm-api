from rest_framework import serializers

from . import models


class ChunkInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chunk
        fields = ['id', 'dataset', 'delimiter', 'service',
                  'ignore_features', 'to_lowercase', 'created_at', 'updated_at']
        read_only_fields = ['id', 'dataset', 'created_at', 'updated_at']


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    chunks = ChunkInfoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Dataset
        fields = ['id', 'url', 'name', 'chunks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'url', 'chunks', 'created_at', 'updated_at']


class ChunkSerializer(serializers.ModelSerializer):
    dataset = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.Chunk
        fields = ['id', 'dataset', 'content', 'delimiter', 'service',
                  'ignore_features', 'to_lowercase', 'created_at', 'updated_at']
        read_only_fields = ['id', 'dataset', 'created_at', 'updated_at']


class EstimatorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Estimator
        fields = ['id', 'url',
                  'input_units', 'inner_units', 'output_units', 'inner_layers',
                  'service', 'activations', 'target']
        read_only_fields = ['id', 'url']


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault())


class TrainingSerializer(TaskSerializer):
    class Meta:
        model = models.Training
        fields = ['id', 'url', 'dataset', 'status', 'errors', 'output', 'owner', 'estimator',
                  'learning_rate', 'dropout_rate', 'epochs', 'batch_size', 'validation_split',
                  'started_at', 'finished_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'output', 'errors', 'started_at', 'finished_at', 'created_at', 'updated_at']


class PredictionSerializer(TaskSerializer):
    class Meta:
        model = models.Prediction
        fields = ['id', 'url', 'dataset', 'status', 'errors', 'output', 'owner', 'estimator',
                  'started_at', 'finished_at', 'created_at', 'updated_at']
        read_only_fields = ['status', 'output', 'errors', 'started_at', 'finished_at', 'created_at', 'updated_at']
