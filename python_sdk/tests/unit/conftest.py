import json

import pytest
from pytest_httpx import HTTPXMock

from infrahub_client import InfrahubClient
from infrahub_client.queries import QUERY_ALL_BRANCHES, QUERY_SCHEMA


@pytest.fixture
async def client() -> InfrahubClient:
    return await InfrahubClient.init(address="http://mock")


@pytest.fixture
async def mock_branches_list_query(httpx_mock: HTTPXMock) -> HTTPXMock:
    response = {
        "data": {
            "branch": [
                {
                    "id": "eca306cf-662e-4e03-8180-2b788b191d3c",
                    "name": "main",
                    "is_data_only": False,
                    "is_default": True,
                    "origin_branch": "main",
                    "branched_from": "2023-02-17T09:30:17.811719Z",
                },
                {
                    "id": "7d9f817a-b958-4e76-8528-8afd0c689ada",
                    "name": "cr1234",
                    "is_data_only": True,
                    "is_default": False,
                    "origin_branch": "main",
                    "branched_from": "2023-02-17T09:30:17.811719Z",
                },
            ]
        }
    }
    request_content = json.dumps({"query": QUERY_ALL_BRANCHES}).encode()

    httpx_mock.add_response(method="POST", json=response, match_content=request_content)
    return httpx_mock


@pytest.fixture
async def mock_repositories_query(httpx_mock: HTTPXMock) -> HTTPXMock:
    response1 = {
        "data": {
            "repository": [
                {
                    "id": "9486cfce-87db-479d-ad73-07d80ba96a0f",
                    "name": {"value": "infrahub-demo-edge"},
                    "location": {"value": "git@github.com:dgarros/infrahub-demo-edge.git"},
                    "commit": {"value": "aaaaaaaaaaaaaaaaaaaa"},
                }
            ]
        }
    }
    response2 = {
        "data": {
            "repository": [
                {
                    "id": "9486cfce-87db-479d-ad73-07d80ba96a0f",
                    "name": {"value": "infrahub-demo-edge"},
                    "location": {"value": "git@github.com:dgarros/infrahub-demo-edge.git"},
                    "commit": {"value": "bbbbbbbbbbbbbbbbbbbb"},
                }
            ]
        }
    }

    httpx_mock.add_response(method="POST", url="http://mock/graphql/main", json=response1)
    httpx_mock.add_response(method="POST", url="http://mock/graphql/cr1234", json=response2)
    return httpx_mock


@pytest.fixture
async def mock_schema_query_01(httpx_mock: HTTPXMock) -> HTTPXMock:
    response = {
        "data": {
            "node_schema": [
                {
                    "name": {"value": "repository"},
                    "kind": {"value": "Repository"},
                    "inherit_from": {"value": ["DataOwner", "DataSource"]},
                    "description": {"value": None},
                    "default_filter": {"value": "name__value"},
                    "attributes": [
                        {
                            "name": {"value": "name"},
                            "kind": {"value": "String"},
                            "optional": {"value": False},
                            "unique": {"value": True},
                            "default_value": {"value": None},
                        },
                        {
                            "name": {"value": "description"},
                            "kind": {"value": "String"},
                            "optional": {"value": True},
                            "unique": {"value": False},
                            "default_value": {"value": None},
                        },
                        {
                            "name": {"value": "location"},
                            "kind": {"value": "String"},
                            "optional": {"value": False},
                            "unique": {"value": False},
                            "default_value": {"value": None},
                        },
                        {
                            "name": {"value": "type"},
                            "kind": {"value": "String"},
                            "optional": {"value": False},
                            "unique": {"value": False},
                            "default_value": {"value": "LOCAL"},
                        },
                        {
                            "name": {"value": "default_branch"},
                            "kind": {"value": "String"},
                            "optional": {"value": False},
                            "unique": {"value": False},
                            "default_value": {"value": "main"},
                        },
                        {
                            "name": {"value": "commit"},
                            "kind": {"value": "String"},
                            "optional": {"value": True},
                            "unique": {"value": False},
                            "default_value": {"value": None},
                        },
                    ],
                    "relationships": [
                        {
                            "name": {"value": "tags"},
                            "peer": {"value": "Tag"},
                            "identifier": {"value": "repository__tag"},
                            "cardinality": {"value": "many"},
                            "optional": {"value": True},
                        },
                        {
                            "name": {"value": "queries"},
                            "peer": {"value": "GraphQLQuery"},
                            "identifier": {"value": "graphqlquery__repository"},
                            "cardinality": {"value": "many"},
                            "optional": {"value": True},
                        },
                    ],
                },
                {
                    "name": {"value": "tag"},
                    "kind": {"value": "Tag"},
                    "inherit_from": {"value": []},
                    "description": {"value": None},
                    "default_filter": {"value": "name__value"},
                    "attributes": [
                        {
                            "name": {"value": "name"},
                            "kind": {"value": "String"},
                            "optional": {"value": False},
                            "unique": {"value": True},
                            "default_value": {"value": None},
                        },
                        {
                            "name": {"value": "description"},
                            "kind": {"value": "String"},
                            "optional": {"value": True},
                            "unique": {"value": False},
                            "default_value": {"value": None},
                        },
                    ],
                    "relationships": [],
                },
                {
                    "name": {"value": "graphql_query"},
                    "kind": {"value": "GraphQLQuery"},
                    "inherit_from": {"value": []},
                    "description": {"value": None},
                    "default_filter": {"value": "name__value"},
                    "attributes": [
                        {
                            "name": {"value": "name"},
                            "kind": {"value": "String"},
                            "optional": {"value": False},
                            "unique": {"value": True},
                            "default_value": {"value": None},
                        },
                        {
                            "name": {"value": "description"},
                            "kind": {"value": "String"},
                            "optional": {"value": True},
                            "unique": {"value": False},
                            "default_value": {"value": None},
                        },
                        {
                            "name": {"value": "query"},
                            "kind": {"value": "String"},
                            "optional": {"value": False},
                            "unique": {"value": False},
                            "default_value": {"value": None},
                        },
                    ],
                    "relationships": [
                        {
                            "name": {"value": "tags"},
                            "peer": {"value": "Tag"},
                            "identifier": {"value": "graphqlquery__tag"},
                            "cardinality": {"value": "many"},
                            "optional": {"value": True},
                        }
                    ],
                },
            ]
        }
    }
    request_content = json.dumps({"query": QUERY_SCHEMA}).encode()

    httpx_mock.add_response(method="POST", json=response, match_content=request_content)
    return httpx_mock
