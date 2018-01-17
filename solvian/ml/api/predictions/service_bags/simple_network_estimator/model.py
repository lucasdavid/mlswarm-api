import os

import numpy as np
from keras import Model, Input, callbacks, optimizers
from keras.layers import Dense, Dropout
from keras.utils import to_categorical
from sklearn import metrics
from sklearn.externals import joblib
from sklearn.preprocessing import LabelEncoder

from ..base import IEstimator


class SimpleNetworkClassifier(IEstimator):
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

    def train(self, data, params):
        learning_rate = params.get('learning_rate')
        epochs = params.get('epochs')
        batch_size = params.get('batch_size')
        validation_split = params.get('validation_split', 0.3)
        shuffle = params.get('shuffle', True)
        saved_at = params.get('saved_at')
        reduce_lr_patience = params.get('reduce_lr_patience', max(1, epochs // 10))
        early_stop_patience = params.get('early_stop_patience', max(1, epochs // 3))

        data_columns = [c for c in data.columns if c != self.target]

        x = data[data_columns]
        y = data[self.target]

        ye = LabelEncoder()
        y = ye.fit_transform(y)

        x = x.values
        y = to_categorical(y)

        joblib.dump(ye, os.path.join(saved_at, 'label_encoder.pkl'))

        model = self.build(dropout_rate=params.get('dropout_rate', 0.0))
        model.compile(optimizer=optimizers.Adam(lr=learning_rate),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])
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

    def test(self, data, params):

        batch_size = params.get('batch_size')
        saved_at = params.get('saved_at')

        data_columns = [c for c in data.columns if c != self.target]
        x = data[data_columns]
        y = data[self.target]

        ye = joblib.load(os.path.join(saved_at, 'label_encoder.pkl'))
        z = ye.transform(y)
        x = x.values

        model = self.build()
        model.load_weights(os.path.join(saved_at, 'weights.hdf5'))

        probabilities = model.predict(x, batch_size=batch_size)
        p = np.argmax(probabilities, axis=1)

        return {
            'true_labels': y,
            'probabilities': probabilities,
            'accuracy': metrics.accuracy_score(z, p),
            'confusion_matrix': metrics.confusion_matrix(z, p),
        }

    def predict(self, data, params):
        batch_size = params.get('batch_size')
        saved_at = params.get('saved_at')

        data_columns = [c for c in data.columns if c != self.target]
        x = data[data_columns].values

        model = self.build()
        model.load_weights(os.path.join(saved_at, 'weights.hdf5'))

        return model.predict(x, batch_size=batch_size)
