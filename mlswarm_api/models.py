import json
from enum import Enum

from django.db.models import Model, DateTimeField, TextField
from django.utils.functional import cached_property


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)


class IDatable(Model):
    class Meta:
        abstract = True

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class IDynamicProperties:
    properties = TextField(help_text='The properties of this estimator.')

    @property
    def properties_(self):
        return json.loads(self.properties)


class IServiceTower(IDynamicProperties):
    service = None
    service_builder = None

    @cached_property
    def loaded(self):
        serializer_cls = self.service_builder.get(self.service)
        serializer = serializer_cls(**self.properties_)
        return serializer.save()
