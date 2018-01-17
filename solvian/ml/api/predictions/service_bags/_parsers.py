import numpy as np
import pandas as pd

from .base import IParser


class CsvDatasetParser(IParser):
    def parse(self):
        return pd.read_csv(self.content, delimiter=self.delimiter)
