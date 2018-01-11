from rest_framework import viewsets, mixins

from . import models, serializers


class PredictionViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = models.Prediction.objects.all()
    serializer_class = serializers.PredictionSerializer

    def perform_create(self, serializer):
        training = serializer.save()
        training.start()


class TrainingViewSet(viewsets.ModelViewSet):
    queryset = models.Training.objects.all()
    serializer_class = serializers.TrainingSerializer

    def perform_create(self, serializer):
        training = serializer.save()
        training.start()


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer


class EstimatorViewSet(viewsets.ModelViewSet):
    queryset = models.Estimator.objects.all()
    serializer_class = serializers.EstimatorSerializer
