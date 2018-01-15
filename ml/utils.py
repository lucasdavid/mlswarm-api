from enum import Enum

from rest_framework_extensions import mixins


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)


class NestedViewSetCreateMixin(mixins.NestedViewSetMixin):
    def perform_create(self, serializer):
        kwargs_id = {key + '_id': value for key, value in self.get_parents_query_dict().items()}
        serializer.save(**kwargs_id)
