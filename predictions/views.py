from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin, DetailSerializerMixin

from .models import Estimator, Training, Test, Predict
from .serializers import (EstimatorSerializer, EstimatorDetailSerializer,
                          TaskSerializer, TrainingSerializer,
                          TestSerializer, PredictSerializer)


class EstimatorViewSet(DetailSerializerMixin,
                       viewsets.ModelViewSet):
    queryset = (Estimator.objects
                .prefetch_related('trainings'))
    serializer_class = EstimatorSerializer
    serializer_detail_class = EstimatorDetailSerializer


class TaskCreateMixin(NestedViewSetMixin):
    def perform_create(self, serializer: TaskSerializer):
        # Save parents' ids within the model.
        d = self.get_parents_query_dict()
        d = {k + '_id': v for k, v in d.items()}

        serializer.save(**d, owner=self.request.user)
        serializer.instance.start()


class TrainingViewSet(TaskCreateMixin,
                      viewsets.ModelViewSet):
    queryset = (Training.objects
                .prefetch_related('chunks'))
    serializer_class = TrainingSerializer


class TestViewSet(TaskCreateMixin,
                  viewsets.ModelViewSet):
    queryset = Test.objects
    serializer_class = TestSerializer


class PredictViewSet(TaskCreateMixin,
                     viewsets.ModelViewSet):
    queryset = Predict.objects
    serializer_class = PredictSerializer
