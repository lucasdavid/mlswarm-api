from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from solvian_ml.views import NestedViewSetCreateMixin
from . import models, serializers


class PredictionViewSet(NestedViewSetMixin,
                        viewsets.ModelViewSet):
    queryset = models.Prediction.objects.all()
    serializer_class = serializers.PredictionSerializer


class TrainingViewSet(NestedViewSetMixin,
                      viewsets.ModelViewSet):
    queryset = models.Training.objects.all()
    serializer_class = serializers.TrainingSerializer


class DatasetViewSet(NestedViewSetMixin,
                     viewsets.ModelViewSet):
    queryset = models.Dataset.objects.select_related().defer('chunks__content')
    serializer_class = serializers.DatasetSerializer


class ChunkViewSet(NestedViewSetCreateMixin,
                   viewsets.ModelViewSet):
    queryset = models.Chunk.objects.all()
    serializer_class = serializers.ChunkSerializer


class EstimatorViewSet(NestedViewSetMixin,
                       viewsets.ModelViewSet):
    queryset = models.Estimator.objects.all()
    serializer_class = serializers.EstimatorSerializer
