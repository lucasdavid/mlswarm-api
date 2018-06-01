from django.db.models import CharField, ForeignKey, PROTECT
from taggit.managers import TaggableManager

from mlswarm_api.models import IDatable, IServiceTower
from . import services


class Dataset(IDatable):
    name = CharField(
        max_length=256,
        help_text='The dataset name.')

    def __str__(self):
        return str(self.name)


class Chunk(IServiceTower, IDatable):
    dataset = ForeignKey(
        Dataset,
        on_delete=PROTECT,
        help_text='The dataset containing this chunk.',
        related_name='chunks')
    service = CharField(
        max_length=32,
        blank=False,
        null=False,
        choices=services.parsers.to_choices(),
        help_text='The service used to parse the content within the properties.')

    services = services.parsers
    tags = TaggableManager()

    def __str__(self):
        return 'ds-%s #%i' % (self.dataset, self.pk)
