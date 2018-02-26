from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from mlswarm_api.views import NestedViewSetCreateMixin
from . import models, serializers


class DatasetViewSet(NestedViewSetMixin,
                     viewsets.ModelViewSet):
    queryset = models.Dataset.objects.select_related().defer('chunks__raw_properties')
    serializer_class = serializers.DatasetSerializer


class ChunkViewSet(NestedViewSetCreateMixin,
                   viewsets.ModelViewSet):
    queryset = models.Chunk.objects.all()
    serializer_class = serializers.ChunkSerializer
