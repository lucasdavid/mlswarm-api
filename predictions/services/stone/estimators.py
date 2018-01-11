import os
from collections import Counter
from datetime import datetime
from time import time

import numpy as np
import pandas as pd
import tensorflow as tf
from keras import optimizers
from keras.callbacks import (EarlyStopping, ModelCheckpoint, TensorBoard,
                             TerminateOnNaN, ReduceLROnPlateau)
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn.exceptions import NotFittedError

from ..base import GenericEstimator


def get_class_weights(y):
    labels = np.argmax(y, axis=1)
    counter = Counter(labels)
    majority = max(counter.values())
    return {cls: float(majority / count) for cls, count in counter.items()}


class StoneTerminalClassifier(GenericEstimator):
    def __init__(self, x, y, saved_at=None):
        self.x = x
        self.y = y
        self.weights = saved_at

    def train(self):
        x, y, ids, dates = (d[e] for e in ('x', 'y', 'ids', 'dates'))
        report_dir = params.namespace
        weights = params.get('weights', settings.Model.resuming_weights)

        os.makedirs(report_dir, exist_ok=True)

        with tf.device(settings.Model.device):
            model = models.get(input_shape=x.shape[1:],
                               inner_units=settings.Model.inner_units,
                               output_units=len(settings.Data.classes),
                               dropout_rate=settings.Train.dropout_rate)

            model.compile(optimizer=optimizers.Adam(settings.Train.lr),
                          loss='categorical_crossentropy',
                          metrics=['accuracy'])

            if weights:
                print('loading weights from', weights)
                model.load_weights(weights)

            class_weight = settings.Train.class_weight
            if class_weight == 'balanced':
                class_weight = get_class_weights(y)

            ping = time()
            try:
                model.fit(x, y,
                          batch_size=settings.Model.batch_size,
                          epochs=settings.Train.epochs,
                          validation_split=settings.Train.validation_split,
                          class_weight=class_weight,
                          verbose=2,
                          callbacks=[
                              TerminateOnNaN(),
                              EarlyStopping(
                                  patience=settings.Train.early_stop_patience),
                              ReduceLROnPlateau(
                                  patience=settings.Train.reduce_on_plateau_patience),
                              ModelCheckpoint(
                                  os.path.join(report_dir, 'model.hdf5'),
                                  verbose=1),
                              TensorBoard(os.path.join(report_dir, 'training/'))
                          ])
            except KeyboardInterrupt:
                print('interrupted by user')
            else:
                print('done -- time elapsed: %.4f sec' % (time() - ping))

        # Return train report.
        history = {k: [float(_v) for _v in v] for k, v in
                   model.history.history.items()}
        return history

    def test(self, d, params):
        x, y, ids, dates = (d[e] for e in ('x', 'y', 'ids', 'dates'))
        report_dir = params.namespace
        weights = params.get('weights',
                             os.path.join(report_dir, settings.Model.weights))

        os.makedirs(report_dir, exist_ok=True)

        with tf.device(settings.Model.device):
            model = models.get(input_shape=x.shape[1:],
                               inner_units=settings.Model.inner_units,
                               output_units=len(settings.Data.classes))

            if not os.path.exists(weights):
                raise NotFittedError('A saved model could not be found at %s. '
                                     'Did you train the model?' % weights)

            print('loading weights from', weights)
            model.load_weights(weights)

            p = model.predict(x, batch_size=settings.Model.batch_size)

        label = np.argmax(y, axis=-1)
        predicted = np.argmax(p, axis=-1)

        # Export results to a CSV file
        results = dict(
            zip(('probability_' + c for c in settings.Data.classes), p.T))
        results.update({settings.Data.id_field: ids,
                        'label': label,
                        'predicted': predicted})
        results = pd.DataFrame(results)
        results.set_index(settings.Data.id_field, inplace=True)
        results.to_csv(os.path.join(report_dir, 'test', 'results.csv'))

        print(52 * '-')
        print('accuracy:', metrics.accuracy_score(label, predicted))
        print('classification report:',
              metrics.classification_report(label, predicted), sep='\n')
        cm = metrics.confusion_matrix(label, predicted)
        print('confusion matrix:', cm / cm.sum(axis=1).reshape(-1, 1), sep='\n')
        print(52 * '-')

        if settings.Test.plotting:
            plt.figure(figsize=(12, 10))
            plotting.classification_histogram(p)
            plt.clf()
            plotting.error_histogram(label, p, dates)
            plt.clf()

    def predict(self, d, params):
        x, y, ids, dates = (d[e] for e in ('x', 'y', 'ids', 'dates'))
        report_dir = params.namespace
        weights = params.get('weights',
                             os.path.join(report_dir, settings.Model.weights))

        os.makedirs(os.path.join(report_dir, 'predict'), exist_ok=True)

        with tf.device(settings.Model.device):
            model = models.get(input_shape=x.shape[1:],
                               inner_units=settings.Model.inner_units,
                               output_units=len(settings.Data.classes))

            if not os.path.exists(weights):
                raise NotFittedError('A saved model could not be found at %s. '
                                     'Did you train the model?' % weights)

            print('loading weights from', weights)
            model.load_weights(weights)

            p = model.predict(x, batch_size=settings.Model.batch_size)

        predicted = np.argmax(p, axis=-1)

        results = dict(
            zip(('probability_' + c for c in settings.Data.classes), p.T))
        results.update({settings.Data.id_field: ids, 'predicted': predicted})
        results = pd.DataFrame(results)
        results.set_index(settings.Data.id_field, inplace=True)
        results.to_csv(os.path.join(report_dir, 'predict',
                                    str(datetime.utcnow()) + '.csv'))

        return results.to_dict(orient='records')
