import os
import shutil

import pandas as pd
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import (TextField, ForeignKey, DateTimeField, CharField,
                              BooleanField, PositiveIntegerField, FloatField,
                              DO_NOTHING, PROTECT, Model)
from django.forms import model_to_dict
from django.utils import timezone

from predictions import service_bags
from sml.models import ChoiceEnum

training_fs = FileSystemStorage('trainings/')


class IDateTracked(Model):
    class Meta:
        abstract = True

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Dataset(IDateTracked):
    name = CharField(max_length=256, help_text='The dataset name.')

    def process(self):
        """Concatenate all chunks.

        :return: pandas.DataFrame
        """
        return pd.concat(c.process() for c in self.chunks.all())

    def __str__(self):
        return self.name


class Chunk(IDateTracked):
    dataset = ForeignKey(Dataset, on_delete=PROTECT, related_name='chunks',
                         help_text='The dataset containing this chunk.')
    content = TextField(help_text='The data or a valid path to it.')
    delimiter = CharField(max_length=1, default=',', help_text='The {content} delimiter.')
    service = CharField(max_length=32, blank=False, null=False, choices=service_bags.parsers.to_choices(),
                        help_text='The parsing service used.')
    ignore_features = TextField(default='', blank=True,
                                help_text='Features in content to ignore, separated by the {delimiter}.')
    to_lowercase = BooleanField(default=False, help_text='Lowercase all strings in {content}.')

    def process(self):
        """Parse data referenced by `content` and return it.

        :return: the data parsed.
        """
        params = model_to_dict(self)
        ignore_features, delimiter = params['ignore_features'], params['delimiter']
        params['ignore_features'] = (None if not ignore_features else
        ignore_features.split(self.delimiter) if isinstance(ignore_features, str) else
        ignore_features)
        return service_bags.parsers.build(self.service, **params).process()

    def __str__(self):
        return '#%s ck-%i' % (self.dataset_id, self.id)


class Estimator(IDateTracked):
    input_units = PositiveIntegerField(help_text='The number of units in the input layer.')
    inner_units = PositiveIntegerField(help_text='The number of units in each layer.')
    output_units = PositiveIntegerField(help_text='The number of units in the output layer.')
    inner_layers = PositiveIntegerField(default=2, help_text='The number of inner layers in the estimator.')

    activations = CharField(max_length=32, default='relu', help_text='The activation used in the layers.')
    service = CharField(max_length=32, choices=service_bags.estimators.to_choices(),
                        help_text='The ML service used.')
    target = TextField(null=True, blank=False,
                       help_text='The estimator\'s target. Valid values depend on the type of '
                                 'service used. For classifiers and regressors, feature '
                                 'name(s) are usually expected.')

    def __str__(self):
        return '%s #%i' % (self.service, self.id)


class Task(IDateTracked):
    class Meta:
        abstract = True

    class Status(ChoiceEnum):
        created = 'created'
        running = 'running'
        interrupted = 'interrupted'
        failed = 'failed'
        completed = 'completed'

    dataset = ForeignKey(Dataset, on_delete=DO_NOTHING, help_text='The dataset used on this task.')
    estimator = ForeignKey(Estimator, on_delete=DO_NOTHING, help_text='The estimator used on this task.')
    owner = ForeignKey(User, on_delete=PROTECT, help_text='The user who requested the prediction.')

    status = CharField(max_length=12, choices=Status.choices(), default=Status.created.value,
                       help_text='The current status of this task.')

    output = TextField(blank=True, help_text='The output of this task.')
    errors = TextField(blank=True, help_text='Eventual errors produced by this task.')
    started_at = DateTimeField(null=True, help_text='The starting time of the task.')
    finished_at = DateTimeField(null=True, help_text='The finishing time of the task.')

    @property
    def saved_at(self):
        return os.path.join(training_fs.location, str(self.id))

    def start(self):
        print('executing #%i: %s' % (self.id, self.estimator))

        self.status = Task.Status.running.value
        self.started_at = timezone.now()
        self.save()

        try:
            self.setup()
            self.run()
            self.teardown()
        except KeyboardInterrupt:
            self.status = Task.Status.interrupted.value
        except Exception as e:
            self.rollback()
            self.status = Task.Status.failed.value
            self.errors = str(e)
            raise e
        else:
            self.status = Task.Status.completed.value

        self.finished_at = timezone.now()
        self.save()

    def run(self):
        raise NotImplementedError

    def setup(self):
        pass

    def teardown(self):
        pass

    def rollback(self):
        pass


class Training(Task):
    learning_rate = FloatField(default=0.01)
    dropout_rate = FloatField(default=0.0)
    epochs = PositiveIntegerField(default=100, help_text='The number of epochs in which the model will be trained.')
    batch_size = PositiveIntegerField(default=32, help_text='The batch size used during training.')
    validation_split = FloatField(default=0.3, help_text='The fraction of data used as validation.')

    def run(self):
        print('training...')
        d = self.dataset.process()

        estimator_params = model_to_dict(self.estimator)
        train_params = model_to_dict(self)
        train_params.setdefault('saved_at', self.saved_at)

        service = service_bags.estimators.build(self.estimator.service, **estimator_params)
        self.output = service.train(d, train_params)

    def setup(self):
        os.makedirs(self.saved_at, exist_ok=True)

    def rollback(self):
        if os.path.exists(self.saved_at):
            shutil.rmtree(self.saved_at)

    def __str__(self):
        return '%s-training-%i' % (self.estimator.name, self.id)


class Prediction(Task):
    def run(self):
        print('predicting...')
        d = self.dataset.process()

        estimator_params = model_to_dict(self.estimator)
        train_params = model_to_dict(self)
        train_params.setdefault('saved_at', self.saved_at)

        service = service_bags.estimators.build(self.estimator.service, **estimator_params)
        self.output = service.predict(d, train_params)
