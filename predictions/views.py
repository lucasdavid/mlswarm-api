from rest_framework import viewsets, mixins
from rest_framework_extensions.mixins import NestedViewSetMixin

from . import models, serializers

from ml.utils import NestedViewSetCreateMixin


class PredictionViewSet(NestedViewSetMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = models.Prediction.objects.all()
    serializer_class = serializers.PredictionSerializer

    def perform_create(self, serializer):
        training = serializer.save()
        training.start()


class TrainingViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Training.objects.all()
    serializer_class = serializers.TrainingSerializer

    def perform_create(self, serializer):
        training = serializer.save()
        training.start()


class DatasetViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Dataset.objects.select_related().defer('chunks__content')
    serializer_class = serializers.DatasetSerializer


class ChunkDatasetViewSet(NestedViewSetCreateMixin, viewsets.ModelViewSet):
    queryset = models.Chunk.objects.all()
    serializer_class = serializers.ChunkSerializer


class EstimatorViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Estimator.objects.all()
    serializer_class = serializers.EstimatorSerializer
