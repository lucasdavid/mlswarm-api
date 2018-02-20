from mlswarm.infrastructure.services import ServiceBuilder
from mlswarm.infrastructure.services.estimators.serializers import (
    SimpleDenseNetworkClassifier, SimpleRegressor)

estimators = ServiceBuilder({
    'simple-dense-network-classifier': SimpleDenseNetworkClassifier,
    'simple-regressor': SimpleRegressor,
})
