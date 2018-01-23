from django.apps import AppConfig
from django.db.models import signals


class PredictionsConfig(AppConfig):
    name = 'predictions'

    parsers = None
    estimators = None

    def ready(self):
        print('PredictionsConfig#ready')

        from . import models

        # Signal tasks to start after being created.
        signals.post_save.connect(models.Task.signal_start, dispatch_uid='s_start_task')
