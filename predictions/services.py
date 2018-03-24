from mlswarm.infrastructure.services import ServiceBuilder
from mlswarm.infrastructure.services.estimators.serializers import (SimpleDenseNetworkClassifier, DummyRegressor)

estimators = ServiceBuilder({
    'dummy-regressor': DummyRegressor,
    'simple-dense-network-classifier': SimpleDenseNetworkClassifier,
})
