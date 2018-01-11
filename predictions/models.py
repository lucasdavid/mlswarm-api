from django.contrib.auth.models import User
from django.db.models import (Model, TextField, ForeignKey, URLField,
                              DateTimeField, CharField, FilePathField,
                              DO_NOTHING, PROTECT, BooleanField,
                              PositiveIntegerField,
                              FloatField)
from django.forms import model_to_dict
from django.utils import timezone

from ml.utils import ChoiceEnum
from . import services

estimator_choices = services.estimators.registered
estimator_choices = list(zip(estimator_choices, estimator_choices))
parser_choices = services.parsers.registered
parser_choices = list(zip(parser_choices, parser_choices))


class Dataset(Model):
    content = URLField(help_text='A valid path to the dataset being '
                                 'predicted or its content.')
    delimiter = CharField(max_length=1, default=',')
    parsing_service = CharField(max_length=32, choices=parser_choices,
                                blank=False, null=False,
                                help_text='the parsing service used.')
    ignore_features = TextField(blank=True)
    to_lowercase = BooleanField(default=False)

    def __str__(self):
        return '#%i %s' % (self.id, str(self.content))

    def parse(self):
        """Parse data referenced by `content` and return it.

        :return: the data parsed.
        """
        parser_cls = services.parsers.get(self.parsing_service)
        parser = parser_cls(**model_to_dict(self))
        return parser.parse()


class Estimator(Model):
    service = CharField(max_length=32,
                        choices=estimator_choices,
                        help_text='The ML service used.')

    def build(self):
        estimator_cls = services.estimators.get(self.service)
        return estimator_cls(**model_to_dict(self))


class Task(Model):
    class Meta:
        abstract = True

    class StatusType(ChoiceEnum):
        created = 'created'
        running = 'running'
        interrupted = 'interrupted'
        failed = 'failed'
        completed = 'completed'

    dataset = ForeignKey(Dataset,
                         on_delete=DO_NOTHING,
                         help_text='The dataset used on this task.')
    estimator = ForeignKey(Estimator,
                           on_delete=DO_NOTHING,
                           help_text='The estimator used on this task.')

    output = TextField(blank=True,
                       help_text='The output of this task. '
                                 'Only valid if `finished_at` is set.')
    errors = TextField(null=True,
                       help_text='Eventual errors produced by the execution '
                                 'of this task. Only valid if `finished_at` '
                                 'is set.')
    user = ForeignKey(User,
                      on_delete=PROTECT,
                      help_text='The user who requested the prediction.')

    started_at = DateTimeField(null=True,
                               help_text='Time in which the data prediction '
                                         'started.')
    finished_at = DateTimeField(null=True,
                                help_text='Time in which the data prediction '
                                          'ended.')

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    status = CharField(max_length=12,
                       choices=StatusType.choices(),
                       default=StatusType.created.value,
                       help_text='The current status of this task.')

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
    batch_size = PositiveIntegerField(default=32)
    saved_at = FilePathField(null=True,
                             help_text='Path where model should be saved.')

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
