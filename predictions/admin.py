from django.contrib import admin

from . import models

admin.site.register(models.Training)
admin.site.register(models.Test)
admin.site.register(models.Predict)
admin.site.register(models.Estimator)
