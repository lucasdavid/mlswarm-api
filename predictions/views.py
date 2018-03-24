from rest_framework import viewsets

from mlswarm_api.views import NestedCreateMixin
from .models import Estimator, Training, Test, Predict
from .serializers import (EstimatorSerializer, TrainingSerializer,
                          TestSerializer, PredictSerializer)


class EstimatorViewSet(viewsets.ModelViewSet):
    queryset = (Estimator.objects
                .prefetch_related('trainings'))
    queryset = Estimator.objects.all()
    serializer_class = EstimatorSerializer


class TrainingViewSet(NestedCreateMixin,
                      viewsets.ModelViewSet):
    queryset = Training.objects.all()
    serializer_class = TrainingSerializer


class TestViewSet(NestedCreateMixin,
                  viewsets.ModelViewSet):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class PredictViewSet(NestedCreateMixin,
                     viewsets.ModelViewSet):
    queryset = Predict.objects.all()
    serializer_class = PredictSerializer
