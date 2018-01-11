import abc

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

    @property
    def registered(self):
        return list(self.classes.keys())


class GenericDatasetParser(metaclass=abc.ABCMeta):
    def parse(self):
        raise NotImplementedError


class GenericEstimator(metaclass=abc.ABCMeta):
    def train(self):
        raise NotImplementedError

    def test(self):
        raise NotImplementedError

    def predict(self):
        raise NotImplementedError
