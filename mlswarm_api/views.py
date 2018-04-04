from django.contrib.auth.models import User
from rest_framework import viewsets

from . import serializers


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (User.objects
                .prefetch_related('groups')
                .only('username', 'email', 'is_staff', 'groups__name'))
    serializer_class = serializers.UserSerializer
