import os

import numpy as np
from keras import Model, Input, callbacks
from keras.layers import Dense, Dropout
from keras.utils import to_categorical
from sklearn import metrics

from ..base import IEstimator


class DenseNetworkClassifier(IEstimator):
    def __init__(self, name=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def build(self, dropout_rate=0.0):
        x = Input(shape=[self.input_units])

        for l in range(self.inner_layers):
            y = Dense(self.units, activation=self.activations, name='fc%i' % l)(x)
            y = Dropout(dropout_rate, name='d%i' % l)(y)

        y = Dense(self.output_units, activation='softmax', name='predictions')(y)

        return Model(inputs=x, outputs=y, name=self.name)

    def train(self, data, train_params):
        data_columns = [c for c in data.columns if c != self.target]

        x = data[data_columns]
        y = data[self.target]

        y = to_categorical(y)

        # retrieve params.
        epochs = train_params.get('epochs')
        batch_size = train_params.get('batch_size')
        validation_split = train_params.get('validation_split', default=0.3)
        shuffle = train_params.get('shuffle', default=True)
        saved_at = train_params.get('saved_at')
        reduce_lr_patience = train_params.get('reduce_lr_patience', default=max(1, epochs // 10))
        early_stop_patience = train_params.get('early_stop_patience', default=max(1, epochs // 3))

        model = self.build(dropout_rate=train_params.get('dropout_rate', default=0.0))

        try:
            model.fit(x, y,
                      epochs=epochs,
                      batch_size=batch_size,
                      verbose=2,
                      validation_split=validation_split,
                      shuffle=shuffle,
                      callbacks=[callbacks.TerminateOnNaN(),
                                 callbacks.ModelCheckpoint(os.path.join(saved_at, 'weights.hdf5'), save_best_only=True),
                                 callbacks.TensorBoard(saved_at, batch_size=batch_size),
                                 callbacks.ReduceLROnPlateau(patience=reduce_lr_patience),
                                 callbacks.EarlyStopping(patience=early_stop_patience)])
        except KeyboardInterrupt:
            print('training interrupted')
        else:
            print('training completed')

        return model.history.history

    def test(self, data, test_params):
        data_columns = [c for c in data.columns if c != self.target]
        x = data[data_columns]
        y = data[self.target]

        batch_size = test_params.get('batch_size')
        saved_at = test_params.get('saved_at')

        model = self.build()
        model.load_weights(os.path.join(saved_at, 'weights.hdf5'))

        probabilities = model.predict(x, batch_size=batch_size)
        p = np.argmax(probabilities, axis=1)

        return {
            'true_labels': y,
            'probabilities': probabilities,
            'accuracy': metrics.accuracy_score(y, p),
            'confusion_matrix': metrics.confusion_matrix(y, p),
        }

    def predict(self, data, predict_params):
        data_columns = [c for c in data.columns if c != self.target]
        x = data[data_columns]

        batch_size = predict_params.get('batch_size')
        saved_at = predict_params.get('saved_at')

        model = self.build()
        model.load_weights(os.path.join(saved_at, 'weights.hdf5'))

        return model.predict(x, batch_size=batch_size)
