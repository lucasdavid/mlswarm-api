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


class IDynamicProperties(Model):
    raw_properties = TextField(help_text='The json-like properties of this entity, stored as a string.')

    @property
    def properties(self):
        return json.loads(self.raw_properties) if self.raw_properties else None

    class Meta:
        abstract = True


class IServiceTower(IDynamicProperties):
    service = None
    services = None

    @cached_property
    def loaded(self):
        serializer_cls = self.services.get(self.service)
        serializer = serializer_cls(data=self.properties)
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    class Meta:
        abstract = True
