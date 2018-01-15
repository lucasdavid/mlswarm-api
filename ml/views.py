from django.contrib.auth.models import User
from rest_framework import viewsets, mixins
from rest_framework_extensions.mixins import NestedViewSetMixin

from . import serializers


class UserViewSet(NestedViewSetMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
