from . import _parsers, simple_dense_estimator, errors
from .base import Bag
from .stone import estimators as stone_estimators

parsers = Bag({
    'csv': _parsers.CsvDatasetParser,
    # 'json': _parsers.JsonDatasetParser,
    # 'database': _parsers.DatabaseDatasetParser,
})

estimators = Bag({
    'dense-network-classifier': simple_dense_estimator.DenseNetworkClassifier,
    'stone-terminal-heath-classifier': stone_estimators.StoneTerminalClassifier,
})

__all__ = ['parsers', 'estimators']