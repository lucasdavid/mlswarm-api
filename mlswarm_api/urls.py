from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework_extensions.routers import ExtendedDefaultRouter

from datasets import views as d_views
from predictions import views as p_views
from . import settings, views as root_views

router = ExtendedDefaultRouter()
router.register(r'users', root_views.UserViewSet)
router.register(r'estimators', p_views.EstimatorViewSet)
router.register(r'trainings', p_views.TrainingViewSet)
router.register(r'predictions', p_views.PredictionViewSet)
(router
    .register(r'datasets', d_views.DatasetViewSet,
              base_name='dataset')
    .register(r'chunks', d_views.ChunkViewSet,
              parents_query_lookups=['dataset'],
              base_name='dataset-chunks'))

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', include_docs_urls(title=settings.DOCS.get('title', None),
                                     description=settings.DOCS.get('description', None))),
]
