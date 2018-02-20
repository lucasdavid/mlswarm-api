import json
import os
import shutil

from datasets.models import Dataset
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import (TextField, ForeignKey, DateTimeField, CharField,
                              DO_NOTHING, PROTECT)
from django.utils import timezone

from mlswarm_api.models import (ChoiceEnum, IDatable,
                                IDynamicProperties,
                                IServiceTower)
from . import services

training_fs = FileSystemStorage('trainings/')


class Estimator(IServiceTower,
                IDatable):
    service = CharField(
        max_length=64,
        choices=services.estimators.to_choices(),
        help_text='The ML service used.')

    service_builder = services.estimators

    def __str__(self):
        return '%s #%i' % (self.service, self.id)


class Task(IDynamicProperties,
           IDatable):
    class Meta:
        abstract = True

    class Status(ChoiceEnum):
        created = 'created'
        running = 'running'
        interrupted = 'interrupted'
        failed = 'failed'
        completed = 'completed'

    dataset = ForeignKey(Dataset, on_delete=DO_NOTHING,
                         help_text='The dataset used on this task.')
    estimator = ForeignKey(Estimator, on_delete=DO_NOTHING,
                           help_text='The estimator used on this task.')
    owner = ForeignKey(User, on_delete=PROTECT,
                       help_text='The user who requested the prediction.')

    status = CharField(max_length=12, choices=Status.choices(),
                       default=Status.created.value,
                       help_text='The current status of this task.')

    output = TextField(blank=True, help_text='The output of this task.')
    errors = TextField(blank=True,
                       help_text='Eventual errors produced by this task.')
    started_at = DateTimeField(null=True,
                               help_text='The starting time of the task.')
    finished_at = DateTimeField(null=True,
                                help_text='The finishing time of the task.')

    @property
    def report(self):
        return json.loads(self.output) if self.output else None

    @property
    def report_dir(self):
        return os.path.join(training_fs.location, str(self.id))

    @classmethod
    def signal_start(cls, sender, instance, created, **kwargs):
        if issubclass(sender, Task) and created:
            # Signal tasks to start after being created.
            instance.start()

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
    def run(self):
        d = self.dataset.loaded
        estimator = self.estimator.loaded

        json_output = estimator.train(d,
                                      report_dir=self.report_dir,
                                      **self.properties_)
        self.output = json.dumps(json_output)

    def setup(self):
        os.makedirs(self.report_dir, exist_ok=True)

    def rollback(self):
        if os.path.exists(self.report_dir):
            shutil.rmtree(self.report_dir)

    def __str__(self):
        return '%s-training-%i' % (str(self.estimator), self.id)


class Prediction(Task):
    def run(self):
        d = self.dataset.loaded
        estimator = self.estimator.loaded
        json_output = estimator.predict(d,
                                        report_dir=self.report_dir,
                                        **self.properties_)
        self.output = json.dumps(json_output)
