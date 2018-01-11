import numpy as np
import pandas as pd

from .base import GenericDatasetParser


class CsvDatasetParser(GenericDatasetParser):
    def __init__(self, dataset, delimiter=',',
                 ignore_features=(), to_lowercase=False):
        self.dataset = dataset
        self.delimiter = delimiter
        self.ignore_features = ignore_features
        self.to_lowercase = to_lowercase

    def digest(self):
        d = pd.read_csv(self.dataset, delimiter=self.delimiter)
        d.columns = d.columns.str.lower()

        d = d[sorted(set(d.columns) - set(self.ignore_features))]

        if self.to_lowercase:
            # Lower case everything.
            categoricals = d.dtypes == np.object_
            for f, is_categorical in zip(categoricals.index, categoricals):
                if is_categorical:
                    d[f] = d[f].str.lower()

        return d
