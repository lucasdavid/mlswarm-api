import pandas as pd
from django.db.models import CharField, ForeignKey, PROTECT
from django.utils.functional import cached_property

from mlswarm_api.models import IDatable, IServiceTower
from . import services


class Dataset(IDatable):
    name = CharField(
        max_length=256,
        help_text='The dataset name.')

    @cached_property
    def processed(self):
        """Concatenate loaded chunks of a dataset.

        :return: pandas.DataFrame
        """
        return pd.concat(c.loaded.processed for c in self.chunks.all())

    def __str__(self):
        return self.name


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
        help_text='The parsing service used.')

    services = services.parsers

    def __str__(self):
        return '#%s ck-%i' % (self.dataset_id, self.id)
