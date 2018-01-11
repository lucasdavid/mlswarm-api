from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from predictions import views as predictions_views
from . import views as root_views

router = routers.DefaultRouter()
router.register(r'users', root_views.UserViewSet)
router.register(r'datasets', predictions_views.DatasetViewSet)
router.register(r'estimators', predictions_views.EstimatorViewSet)
router.register(r'trainings', predictions_views.TrainingViewSet)
router.register(r'predictions', predictions_views.PredictionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title='Solvian Machine Learning API',
                                     description='Machine Learning as a service.')),
]
