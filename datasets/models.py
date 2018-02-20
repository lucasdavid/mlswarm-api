import pandas as pd
from django.db.models import CharField, ForeignKey, TextField, PROTECT

from mlswarm_api.models import IDatable
from . import services


class Dataset(IDatable):
    name = CharField(
        max_length=256,
        help_text='The dataset name.')

    def load(self, skip: int = None, last: int = None):
        """Concatenate loaded chunks of a dataset.

        :return: pandas.DataFrame
        """
        chunks = (self.chunks.all()[skip:last]
                  if any(e is not None for e in (skip, last))
                  else self.chunks.all())

        return pd.concat(c.load() for c in chunks)

    def __str__(self):
        return self.name


class Chunk(IDatable):
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
    properties = TextField(help_text='The properties passed to the parsing service.')

    # def load(self):
    #     """Parse data referenced by `content` and return it.
    #
    #     :return: the data parsed.
    #     """
    #     return services.parsers.build(self.service, **model_to_dict(self)).load()

    def __str__(self):
        return '#%s ck-%i' % (self.dataset_id, self.id)
