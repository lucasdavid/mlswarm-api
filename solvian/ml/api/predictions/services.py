from solvian.ml.infrastructure import Bag
from solvian.ml.infrastructure.parsers import CsvDatasetParser

from solvian.ml.services.stone import TerminalHealthClassifier
from solvian.ml.services.simple_network import SimpleNetworkClassifier

# Register parsers and estimators.
parsers = Bag({
    'csv': CsvDatasetParser
})

estimators = Bag({
    'stone-terminal-health-classifier': TerminalHealthClassifier,
    'simple-network-classifier': SimpleNetworkClassifier
})
