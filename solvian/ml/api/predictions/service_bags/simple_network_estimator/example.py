import os

import pandas as pd

from predictions.service_bags._parsers import CsvDatasetParser
from predictions.service_bags.simple_network_estimator.model import SimpleNetworkClassifier

data_path = 'https://raw.githubusercontent.com/uiuc-cse/data-fa14/gh-pages/data/iris.csv'
saved_at = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'logs')

if __name__ == '__main__':
    os.makedirs(saved_at, exist_ok=True)

    d = CsvDatasetParser(data_path).parse()
    c = SimpleNetworkClassifier(input_units=4,
                                inner_units=32,
                                output_units=3,
                                inner_layers=1,
                                activations='relu',
                                target='species')

    train_results = c.train(d, params=dict(
        epochs=100,
        learning_rate=0.01,
        batch_size=32,
        saved_at=saved_at))

    test_results = c.test(d, params=dict(batch_size=32,
                                         saved_at=saved_at))
    (pd
        .DataFrame(train_results)
        .to_csv(os.path.join(saved_at, 'train-report.csv'),
                index_label='epoch'))
    print(test_results)
