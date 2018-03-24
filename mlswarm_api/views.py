from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from . import serializers


class NestedCreateMixin(NestedViewSetMixin):
    def perform_create(self, serializer):
        q = self.get_parents_query_dict()
        serializer.save(**{k + '_id': v for k, v in q.items()})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
