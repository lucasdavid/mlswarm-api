import json
from typing import ClassVar

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.serializers import (Serializer, ModelSerializer, HyperlinkedModelSerializer)

from mlswarm.infrastructure.services import ServiceBuilder


class UserSerializer(HyperlinkedModelSerializer):
    class GroupSerializer(ModelSerializer):
        class Meta:
            model = Group
            fields = ['name']
            read_only_fields = ['name']

    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'url', 'username', 'email', 'is_staff', 'groups']
        read_only_fields = ['id', 'url', 'is_staff', 'groups']


class PropertiesSerializerMixin:
    services: ServiceBuilder = None

    def service_serializer_cls(self, data: dict) -> ClassVar[Serializer]:
        assert self.services is not None, ('%s does not have a valid builder.' % self)
        return self.services.get(data['service'])

    def validate(self, data: dict) -> dict:
        try:
            properties = (json.loads(data['properties'])
                          if isinstance(data['properties'], str)
                          else data['properties'])
        except json.JSONDecodeError as e:
            raise serializers.ValidationError({
                'properties': ['Value must be valid JSON: %s' % str(e)]
            })

        serializer = self.service_serializer_cls(data)(data=properties)
        assert isinstance(serializer, Serializer), (
            'Service %s\'s schema should be a valid Serializer class instance.'
            % serializer)

        # Check if `properties` conform with the service's schema.
        if not serializer.is_valid():
            raise serializers.ValidationError({
                'properties': serializer.errors
            })

        data['raw_properties'] = json.dumps(serializer.validated_data)
        del data['properties']

        return data
