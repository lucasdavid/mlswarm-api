import abc

from rest_framework import viewsets, mixins
from rest_framework_extensions.mixins import NestedViewSetMixin

from sml.views import NestedViewSetCreateMixin
from . import models, serializers


class TaskViewSetMixin(metaclass=abc.ABCMeta):
    """TaskViewSet Mixin.

    Initiates a task after creating it.

    Example:

        >>> class TrainingViewSet(TaskViewSetMixin, ...):
        ...     queryset = models.Training.objects.all()
        ...     serializer_class = serializers.TrainingSerializer

    """

    def perform_create(self, serializer):
        task = serializer.save()
        task.start()


class PredictionViewSet(TaskViewSetMixin,
                        NestedViewSetMixin,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = models.Prediction.objects.all()
    serializer_class = serializers.PredictionSerializer


class TrainingViewSet(TaskViewSetMixin,
                      NestedViewSetMixin,
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
