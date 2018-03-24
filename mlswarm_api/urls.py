from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework_extensions.routers import ExtendedDefaultRouter

from datasets import views as d_views
from predictions import views as p_views
from . import settings, views as root_views

router = ExtendedDefaultRouter()
router.register('users', root_views.UserViewSet)

(router
    .register('datasets', d_views.DatasetViewSet, base_name='dataset')
    .register('chunks', d_views.ChunkViewSet,
              parents_query_lookups=['dataset'],
              base_name='dataset-chunks'))

t_router = (router
            .register('estimators', p_views.EstimatorViewSet, base_name='estimator')
            .register('trainings', p_views.TrainingViewSet,
                      parents_query_lookups=['estimator'],
                      base_name='training'))
t_router.register('tests', p_views.TestViewSet,
                  parents_query_lookups=['estimator', 'training'],
                  base_name='test')
t_router.register('predictions', p_views.PredictViewSet,
                  parents_query_lookups=['estimator', 'training'],
                  base_name='predictions')

urlpatterns = [
    url('^', include(router.urls)),
    url('^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^admin/', admin.site.urls),
    url('^docs/', include_docs_urls(title=settings.DOCS.get('title', None),
                                    description=settings.DOCS.get('description', None))),
]
