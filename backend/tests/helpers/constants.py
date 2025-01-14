import os

from infrahub_sdk.utils import str_to_bool

INFRAHUB_USE_TEST_CONTAINERS = str_to_bool(os.getenv("INFRAHUB_USE_TEST_CONTAINERS", "true"))
PORT_NATS = 4222
PORT_REDIS = 6379
PORT_CLIENT_RABBITMQ = 5672
PORT_HTTP_RABBITMQ = 15672
PORT_HTTP_NEO4J = 7474
PORT_BOLT_NEO4J = 7687
PORT_MEMGRAPH = 7687
PORT_PREFECT = 4200
NEO4J_COMMUNITY_IMAGE = "neo4j:5.20.0-community"
NEO4J_ENTERPRISE_IMAGE = "neo4j:5.20.0-enterprise"
NEO4J_IMAGE = os.getenv("NEO4J_DOCKER_IMAGE", NEO4J_ENTERPRISE_IMAGE)
