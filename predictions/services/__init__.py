from . import _parsers, _estimators, errors
from .base import Bag
from .stone import estimators as stone_estimators

parsers = Bag({
    'csv': _parsers.CsvDatasetParser,
    # 'json': _parsers.JsonDatasetParser,
    # 'database': _parsers.DatabaseDatasetParser,
})

estimators = Bag({
    'simple-classifier': _estimators.SimpleClassifier,
    'stone-terminal-heath-classifier': stone_estimators.StoneTerminalClassifier,
})

__all__ = ['parsers', 'estimators', 'errors']
