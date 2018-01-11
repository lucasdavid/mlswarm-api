import numpy as np
import pandas as pd

from .base import GenericDatasetParser


class CsvDatasetParser(GenericDatasetParser):
    def __init__(self,
                 content,
                 delimiter=',',
                 ignore_features=(),
                 to_lowercase=False,
                 **kwargs):
        self.content = content
        self.delimiter = delimiter
        self.ignore_features = ignore_features
        self.to_lowercase = to_lowercase

    def parse(self):
        ignore = self.ignore_features

        if isinstance(ignore, str):
            ignore = set(ignore.split(self.delimiter))

        d = pd.read_csv(self.content, delimiter=self.delimiter)
        retained_columns = [c for c in d.columns if c not in ignore]
        d = d[retained_columns]

        if self.to_lowercase:
            # Lower case everything.
            categoricals = d.dtypes == np.object_
            for f, is_categorical in zip(categoricals.index, categoricals):
                if is_categorical:
                    d[f] = d[f].str.lower()
        return d
