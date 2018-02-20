from mlswarm.infrastructure.services import ServiceBuilder
from mlswarm.infrastructure.services.parsers.serializers import CSVParserSerializer, JSONParserSerializer

parsers = ServiceBuilder({
    'csv': CSVParserSerializer,
    'json': JSONParserSerializer
})
