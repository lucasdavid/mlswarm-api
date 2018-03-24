from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from .models import Dataset, Chunk
from .serializers import DatasetSerializer, ChunkSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = (Dataset.objects
                .prefetch_related('chunks')
                .defer('chunks__raw_properties'))
    serializer_class = DatasetSerializer


class ChunkViewSet(NestedViewSetMixin,
                   viewsets.ModelViewSet):
    queryset = Chunk.objects.all()
    serializer_class = ChunkSerializer

    def perform_create(self, serializer):
        q = self.get_parents_query_dict()
        serializer.save(dataset_id=q['dataset'])
