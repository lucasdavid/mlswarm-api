import pandas as pd
from django.contrib.auth.models import User
from django.db.models import (Model, TextField, ForeignKey, DateTimeField, CharField,
                              FilePathField, BooleanField, PositiveIntegerField, FloatField,
                              DO_NOTHING, PROTECT)
from django.forms import model_to_dict
from django.utils import timezone

from ml.utils import ChoiceEnum
from . import services

estimator_choices = services.estimators.registered
estimator_choices = list(zip(estimator_choices, estimator_choices))
parser_choices = services.parsers.registered
parser_choices = list(zip(parser_choices, parser_choices))


class IDateTracked(Model):
    class Meta:
        abstract = True

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Dataset(IDateTracked):
    description = CharField(max_length=256, help_text='The dataset description.')

    @property
    def excerpt(self):
        return (self.description[:32] + '...'
                if len(self.description) > 32
                else self.description)

    def __str__(self):
        return '#%i %s' % (self.id, str(self.excerpt))

    def parse(self):
        return pd.concat(c.parse() for c in self.chunks)


class Chunk(IDateTracked):
    dataset = ForeignKey(Dataset, on_delete=PROTECT, related_name='chunks',
                         help_text='The dataset containing this chunk.')
    content = TextField(help_text='The data or a valid path to it.')
    delimiter = CharField(max_length=1, default=',', help_text='The {content} delimiter.')
    parsing_service = CharField(max_length=32, choices=parser_choices, blank=False, null=False,
                                help_text='the parsing service used.')
    ignore_features = TextField(blank=True, help_text='Features in content to ignore, separated by the {delimiter}.')
    to_lowercase = BooleanField(default=False, help_text='Lowercase all strings in {content}.')

    def parse(self):
        """Parse data referenced by `content` and return it.

        :return: the data parsed.
        """
        parser_cls = services.parsers.get(self.parsing_service)
        parser = parser_cls(**model_to_dict(self))
        return parser.parse()

    def __str__(self):
        return '#%s ck-%i' % (self.dataset_id, self.id)


class Estimator(IDateTracked):
    # layers = PositiveIntegerField(default=2)
    # units = PositiveIntegerField()
    # activations = CharField()
    service = CharField(max_length=32, choices=estimator_choices, help_text='The ML service used.')

    def build(self):
        estimator_cls = services.estimators.get(self.service)
        return estimator_cls(**model_to_dict(self))

    def __str__(self):
        return '#%i %s' % (self.id, self.service)


class Task(IDateTracked):
    class Meta:
        abstract = True

    class StatusType(ChoiceEnum):
        created = 'created'
        running = 'running'
        interrupted = 'interrupted'
        failed = 'failed'
        completed = 'completed'

    dataset = ForeignKey(Dataset, on_delete=DO_NOTHING, help_text='The dataset used on this task.')
    estimator = ForeignKey(Estimator, on_delete=DO_NOTHING, help_text='The estimator used on this task.')
    creator = ForeignKey(User, on_delete=PROTECT, help_text='The user who requested the prediction.')

    status = CharField(max_length=12, choices=StatusType.choices(), default=StatusType.created.value,
                       help_text='The current status of this task.')

    output = TextField(blank=True, help_text='The output of this task.')
    errors = TextField(blank=True, help_text='Eventual errors produced by this task.')
    started_at = DateTimeField(null=True, help_text='The starting time of the task.')
    finished_at = DateTimeField(null=True, help_text='The finishing time of the task.')

    def start(self):
        print('executing #%i: %s' % (self.id, self.estimator))

        self.status = Task.StatusType.running.value
        self.started_at = timezone.now()
        self.save()

        try:
            self.run()
        except KeyboardInterrupt:
            self.status = Task.StatusType.interrupted.value
        except Exception as e:
            self.status = Task.StatusType.failed.value
            self.errors = str(e)
        else:
            self.status = Task.StatusType.completed.value

        self.finished_at = timezone.now()
        self.save()

    def run(self):
        raise NotImplementedError


class Training(Task):
    learning_rate = FloatField(default=0.01)
    dropout_rate = FloatField(default=0.0)
    epochs = PositiveIntegerField(default=10, help_text='The number of epochs in which the model will be trained.')
    batch_size = PositiveIntegerField(default=32, help_text='The batch size used during training.')
    saved_at = FilePathField(null=True, help_text='Path where model should be saved.')

    def __str__(self):
        return '%s-training-%i' % (self.estimator.name, self.id)

    def run(self):
        print('training...')
        data = self.dataset.parse()
        estimator = self.estimator.build()
        self.output = estimator.train(data)


class Prediction(Task):
    def run(self):
        print('predicting...')
        data = self.dataset.parse()
        estimator = self.estimator.build()
        self.output = estimator.predict(data)
