import json
import os
import shutil
from logging import warning

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db.models import (TextField, ForeignKey, DateTimeField, CharField,
                              DO_NOTHING, PROTECT, ManyToManyField)
from django.utils import timezone

from datasets.models import Chunk
from mlswarm_api.models import (ChoiceEnum, IDatable, IDynamicProperties,
                                IServiceTower)
from . import services

training_fs = FileSystemStorage('trainings/')


class Estimator(IServiceTower,
                IDatable):
    services = services.estimators
    service = CharField(max_length=64,
                        choices=services.to_choices(),
                        help_text='The ML service used.')

    def __str__(self):
        return '%s #%i' % (self.service, self.id)


class Task(IDynamicProperties, IDatable):
    class Meta:
        abstract = True

    class Status(ChoiceEnum):
        created = 'created'
        running = 'running'
        interrupted = 'interrupted'
        failed = 'failed'
        completed = 'completed'

    chunks = ManyToManyField(
        Chunk,
        related_name='%(class)ss',
        help_text='The chunks used on this task.')

    estimator = ForeignKey(
        Estimator,
        on_delete=DO_NOTHING,
        related_name='%(class)ss',
        help_text='The estimator used on this task.')

    owner = ForeignKey(User, on_delete=PROTECT, help_text='The user who requested the prediction.')

    status = CharField(max_length=12, choices=Status.choices(),
                       default=Status.created.value,
                       help_text='The current status of this task.')

    output = TextField(blank=True, help_text='The output of this task.')
    errors = TextField(blank=True, help_text='Eventual errors produced by this task.')
    started_at = DateTimeField(null=True, help_text='The starting time of the task.')
    finished_at = DateTimeField(null=True, help_text='The finishing time of the task.')

    @property
    def report(self):
        return json.loads(self.output) if self.output else None

    @property
    def report_dir(self):
        return os.path.join(training_fs.location, str(self.id))

    @property
    def merged_chunks(self):
        d = [c.loaded for c in self.chunks.all()]
        return d[0].concatenate(d)

    def start(self):
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
            warning(e)

            self.rollback()
            self.status = Task.Status.failed.value
            self.errors = str(e)
        else:
            self.status = Task.Status.completed.value
        finally:
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

    def __str__(self):
        return '%s #%i: %s' % (self.__class__.__name__,
                               self.pk,
                               self.estimator)


class Training(Task):
    def run(self):
        estimator = self.estimator.loaded
        report = estimator.train(self.merged_chunks,
                                 report_dir=self.report_dir,
                                 **self.properties)
        estimator.save(self.report_dir)
        estimator.dispose()
        self.output = json.dumps(report)

    def setup(self):
        os.makedirs(self.report_dir, exist_ok=True)

    def rollback(self):
        if os.path.exists(self.report_dir):
            shutil.rmtree(self.report_dir)


class PostTrainingTask(Task):
    class Meta:
        abstract = True

    training = ForeignKey(Training,
                          on_delete=PROTECT,
                          help_text='Estimator\'s training that will be evaluated.')


class Test(PostTrainingTask):
    def run(self):
        estimator = self.estimator.loaded
        report = (estimator
                  .load(self.training.report_dir)
                  .test(self.merged_chunks, report_dir=self.report_dir, **self.properties))
        estimator.dispose()
        self.output = json.dumps(report)


class Predict(PostTrainingTask):
    def run(self):
        estimator = self.estimator.loaded
        report = (estimator
                  .load(self.training.report_dir)
                  .predict(self.merged_chunks, report_dir=self.report_dir, **self.properties))
        estimator.dispose()
        self.output = json.dumps(report)
