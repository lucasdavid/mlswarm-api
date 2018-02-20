import json
from json import JSONDecodeError

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.serializers import (Serializer, ModelSerializer, HyperlinkedModelSerializer)


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
        read_only_fields = ['name']


class UserSerializer(HyperlinkedModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff', 'groups']
        read_only_fields = ['is_staff', 'groups']


class ServiceSerializerMixin:
    properties = serializers.JSONField()
    service_builder = None

    def validate(self, data):
        try:
            properties = (json.loads(data['properties'])
                          if isinstance(data['properties'], str)
                          else data['properties'])
        except JSONDecodeError as e:
            raise serializers.ValidationError({
                'properties': ['Value must be valid JSON: %s' % str(e)]
            })

        assert self.service_builder is not None, ('%s does not have a valid builder' % self)

        serializer = self.service_builder.build(data['service'], data=properties)
        assert isinstance(serializer, Serializer), (
            'Service %s\'s schema should be a valid Serializer class instance.'
            % serializer)

        # Check if `properties` conform with the service's schema.
        if not serializer.is_valid():
            raise serializers.ValidationError({
                'properties': serializer.errors
            })

        data['properties'] = json.dumps(serializer.validated_data)

        return data

    def to_representation(self, instance):
        r = super().to_representation(instance)

        if isinstance(r['properties'], str):
            try:
                r['properties'] = json.loads(r['properties'])
            except JSONDecodeError:
                pass

        return r
