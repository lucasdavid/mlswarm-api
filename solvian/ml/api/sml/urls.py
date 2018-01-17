from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework_extensions.routers import ExtendedDefaultRouter

from predictions import views as p_views
from . import views as root_views

router = ExtendedDefaultRouter()
router.register(r'users', root_views.UserViewSet)
router.register(r'estimators', p_views.EstimatorViewSet)
router.register(r'trainings', p_views.TrainingViewSet)
router.register(r'predictions', p_views.PredictionViewSet)
(router
    .register(r'datasets', p_views.DatasetViewSet,
              base_name='dataset')
    .register(r'chunks', p_views.ChunkViewSet,
              parents_query_lookups=['dataset'],
              base_name='dataset-chunks'))

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title='Solvian Machine Learning API',
                                     description='Machine Learning as a service.')),
]
