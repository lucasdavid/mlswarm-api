from django.contrib import admin

from . import models

admin.site.register(models.Training)
admin.site.register(models.Prediction)
admin.site.register(models.Estimator)
admin.site.register(models.Dataset)
admin.site.register(models.Chunk)
