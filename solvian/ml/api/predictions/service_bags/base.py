import abc

import numpy as np

from . import errors


class Bag:
    def __init__(self, classes: dict):
        self.classes = classes

    def get(self, _id: str):
        try:
            return self.classes[_id]
        except KeyError:
            raise errors.ClassNotFound('Cannot find class {%s} in this bag. '
                                       'Available options are: %s.'
                                       % (_id, self.registered))

    def build(self, _id: str, *args, **kwargs):
        return self.get(_id)(*args, **kwargs)

    @property
    def registered(self):
        return list(self.classes.keys())

    def to_choices(self):
        choices = self.registered
        return list(zip(choices, choices))


class IParser(metaclass=abc.ABCMeta):
    def __init__(self,
                 content,
                 delimiter=',',
                 to_lowercase=False,
                 ignore_features=(),
                 **kwargs):
        self.content = content
        self.delimiter = delimiter
        self.to_lowercase = to_lowercase
        self.ignore_features = ignore_features
        self._kwargs = kwargs

    def parse(self):
        """Parse the data, reading it for the estimators.
        """
        raise NotImplementedError

    def process(self):
        d = self.parse()

        if self.ignore_features:
            retained = [c for c in d.columns if c not in self.ignore_features]
            d = d[retained]

        if self.to_lowercase:
            # Lower case everything.
            categoricals = d.columns[d.dtypes == np.object_]
            d[categoricals] = d[categoricals].str.lower()

        return d


class IEstimator(metaclass=abc.ABCMeta):
    def __init__(self, input_units, inner_units, output_units, inner_layers,
                 activations, target, **kwargs):
        self.input_units = input_units
        self.output_units = output_units
        self.inner_layers = inner_layers
        self.units = inner_units
        self.activations = activations
        self.target = target
        self._kwargs = kwargs

    def train(self, data, train_params):
        raise NotImplementedError

    def test(self, data, test_params):
        raise NotImplementedError

    def predict(self, data, predict_params):
        raise NotImplementedError
