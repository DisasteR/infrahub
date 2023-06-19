import pytest

from infrahub.core.branch import Branch
from infrahub.core.initialization import create_branch


async def test_graphql_endpoint(session, client, client_headers, default_branch: Branch, car_person_data):
    query = """
    query {
        person {
            edges {
                node {
                    name {
                        value
                    }
                    cars {
                        edges {
                            node {
                                name {
                                    value
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    # Must execute in a with block to execute the startup/shutdown events
    with client:
        response = client.post(
            "/graphql",
            json={"query": query},
            headers=client_headers,
        )

    assert response.status_code == 200
    assert "errors" not in response.json()
    assert response.json()["data"] is not None
    result = response.json()["data"]

    result_per_name = {result["node"]["name"]["value"]: result for result in result["person"]["edges"]}
    assert sorted(result_per_name.keys()) == ["Jane", "John"]
    assert len(result_per_name["John"]["node"]["cars"]["edges"]) == 2
    assert len(result_per_name["Jane"]["node"]["cars"]["edges"]) == 1


@pytest.mark.xfail(reason="Need to investigate, Currently working alone but failing when it's part of the test suite")
async def test_graphql_endpoint_generics(
    session, default_branch: Branch, client, client_headers, car_person_data_generic
):
    query = """
    query {
        person {
            name {
                value
            }
            cars {
                name {
                    value
                }
            }
        }
    }
    """

    # Must execute in a with block to execute the startup/shutdown events
    with client:
        response = client.post(
            "/graphql",
            json={"query": query},
            headers=client_headers,
        )

    assert response.status_code == 200
    assert "errors" not in response.json()
    assert response.json()["data"] is not None
    result = response.json()["data"]

    result_per_name = {result["name"]["value"]: result for result in result["person"]}

    assert sorted(result_per_name.keys()) == ["Jane", "John"]
    assert len(result_per_name["John"]["cars"]) == 2
    assert len(result_per_name["Jane"]["cars"]) == 1


async def test_graphql_options(session, client, client_headers, default_branch: Branch, car_person_data):
    await create_branch(branch_name="branch2", session=session)

    # Must execute in a with block to execute the startup/shutdown events
    with client:
        response = client.options(
            "/graphql",
            headers=client_headers,
        )

        assert response.status_code == 200
        assert "Allow" in response.headers
        assert response.headers["Allow"] == "GET, POST, OPTIONS"

        response = client.options(
            "/graphql/branch2",
            headers=client_headers,
        )

        assert response.status_code == 200
        assert "Allow" in response.headers
        assert response.headers["Allow"] == "GET, POST, OPTIONS"

        response = client.options(
            "/graphql/notvalid",
            headers=client_headers,
        )

        assert response.status_code == 404


async def test_read_profile(
    session,
    client,
    admin_headers,
    authentication_base,
):
    query = """
    query {
        account_profile {
            name {
                value
            }
        }
    }
    """

    with client:
        response = client.post(
            "/graphql",
            json={"query": query},
            headers=admin_headers,
        )

    assert response.status_code
    assert response.json() == {"data": {"account_profile": {"name": {"value": "test-admin"}}}}
