from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from . import models, serializers


class PredictionViewSet(NestedViewSetMixin,
                        viewsets.ModelViewSet):
    queryset = models.Prediction.objects.all()
    serializer_class = serializers.PredictionSerializer


class TrainingViewSet(NestedViewSetMixin,
                      viewsets.ModelViewSet):
    queryset = models.Training.objects.all()
    serializer_class = serializers.TrainingSerializer


class EstimatorViewSet(NestedViewSetMixin,
                       viewsets.ModelViewSet):
    queryset = models.Estimator.objects.all()
    serializer_class = serializers.EstimatorSerializer
