import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import pytest
import yaml
from fastapi.testclient import TestClient

from infrahub import config
from infrahub.core import registry
from infrahub.core.initialization import first_time_initialization, initialization
from infrahub.core.node import Node
from infrahub.core.schema import SchemaRoot
from infrahub.core.utils import count_relationships, delete_all_nodes
from infrahub.git import InfrahubRepository
from infrahub.utils import get_models_dir
from infrahub_client import Config, InfrahubClient, NodeNotFound
from infrahub_client.types import HTTPMethod

# pylint: disable=unused-argument


async def load_infrastructure_schema(session):
    models_dir = get_models_dir()

    schema_txt = Path(os.path.join(models_dir, "infrastructure_base.yml")).read_text()
    infra_schema = yaml.safe_load(schema_txt)

    default_branch_name = config.SETTINGS.main.default_branch
    branch_schema = registry.schema.get_schema_branch(name=default_branch_name)
    tmp_schema = branch_schema.duplicate()
    tmp_schema.load_schema(schema=SchemaRoot(**infra_schema))
    tmp_schema.process()

    await registry.schema.update_schema_branch(
        schema=tmp_schema, session=session, branch=default_branch_name, update_db=True
    )


class InfrahubTestClient(TestClient):
    def _request(
        self, url: str, method: HTTPMethod, headers: Dict[str, Any], timeout: int, payload: Optional[Dict] = None
    ) -> httpx.Response:
        content = None
        if payload:
            content = str(json.dumps(payload)).encode("UTF-8")
        with self as client:
            return client.request(method=method.value, url=url, headers=headers, timeout=timeout, content=content)

    async def async_request(
        self, url: str, method: HTTPMethod, headers: Dict[str, Any], timeout: int, payload: Optional[Dict] = None
    ) -> httpx.Response:
        return self._request(url=url, method=method, headers=headers, timeout=timeout, payload=payload)


class TestInfrahubClient:
    @pytest.fixture(scope="class")
    async def base_dataset(self, session):
        await delete_all_nodes(session=session)
        await first_time_initialization(session=session)
        await load_infrastructure_schema(session=session)
        await initialization(session=session)

    @pytest.fixture(scope="class")
    async def test_client(
        self,
        base_dataset,
    ):
        # pylint: disable=import-outside-toplevel
        from infrahub.server import app

        return InfrahubTestClient(app)

    @pytest.fixture
    async def client(self, test_client, integration_helper):
        admin_token = await integration_helper.create_token()
        config = Config(api_token=admin_token, requester=test_client.async_request)

        return await InfrahubClient.init(config=config)

    @pytest.fixture(scope="class")
    async def query_99(self, session, test_client):
        obj = await Node.init(schema="CoreGraphQLQuery", session=session)
        await obj.new(
            session=session,
            name="query99",
            query="query query99 { CoreRepository { edges { node { id }}}}",
        )
        await obj.save(session=session)
        return obj

    @pytest.fixture
    async def repo(self, test_client, client, session, git_upstream_repo_10, git_repos_dir):
        # Create the repository in the Graph
        obj = await Node.init(schema="CoreRepository", session=session)
        await obj.new(
            session=session,
            name=git_upstream_repo_10["name"],
            description="test repository",
            location="git@github.com:mock/test.git",
        )
        await obj.save(session=session)

        # Initialize the repository on the file system
        repo = await InfrahubRepository.new(
            id=obj.id,
            name=git_upstream_repo_10["name"],
            location=git_upstream_repo_10["path"],
        )

        repo.client = client

        return repo

    async def test_import_all_graphql_query(self, session, client: InfrahubClient, repo: InfrahubRepository):
        commit = repo.get_commit_value(branch_name="main")
        await repo.import_all_graphql_query(branch_name="main", commit=commit)

        queries = await client.all(kind="CoreGraphQLQuery")
        assert len(queries) == 5

        # Validate if the function is idempotent, another import just after the first one shouldn't change anything
        nbr_relationships_before = await count_relationships(session=session)
        await repo.import_all_graphql_query(branch_name="main", commit=commit)
        assert await count_relationships(session=session) == nbr_relationships_before

        # 1. Modify an object to validate if its being properly updated
        # 2. Add an object that doesn't exist in GIt and validate that it's been deleted
        value_before_change = queries[0].query.value
        queries[0].query.value = "query myquery { BuiltinLocation { edges { node { id }}}}"
        await queries[0].save()

        obj = await Node.init(schema="CoreGraphQLQuery", session=session)
        await obj.new(
            session=session,
            name="soontobedeletedquery",
            query="query soontobedeletedquery { BuiltinLocation { edges { node { id }}}}",
            repository=str(repo.id),
        )
        await obj.save(session=session)

        await repo.import_all_graphql_query(branch_name="main", commit=commit)

        modified_query = await client.get(kind="CoreGraphQLQuery", id=queries[0].id)
        assert modified_query.query.value == value_before_change

        with pytest.raises(NodeNotFound):
            await client.get(kind="CoreGraphQLQuery", id=obj.id)

    async def test_import_all_python_files(self, session, client: InfrahubClient, repo: InfrahubRepository, query_99):
        commit = repo.get_commit_value(branch_name="main")
        await repo.import_all_python_files(branch_name="main", commit=commit)

        check_definitions = await client.all(kind="CoreCheckDefinition")
        assert len(check_definitions) >= 1

        transforms = await client.all(kind="CoreTransformPython")
        assert len(transforms) >= 2

        # Validate if the function is idempotent, another import just after the first one shouldn't change anything
        nbr_relationships_before = await count_relationships(session=session)
        await repo.import_all_python_files(branch_name="main", commit=commit)
        assert await count_relationships(session=session) == nbr_relationships_before

        # 1. Modify an object to validate if its being properly updated
        # 2. Add an object that doesn't exist in Git and validate that it's been deleted
        check_timeout_value_before_change = check_definitions[0].timeout.value
        check_query_value_before_change = check_definitions[0].query.id
        check_definitions[0].timeout.value = 44
        check_definitions[0].query = query_99.id
        await check_definitions[0].save()

        transform_timeout_value_before_change = transforms[0].timeout.value
        transforms[0].timeout.value = 44
        await transforms[0].save()

        transform_query_value_before_change = transforms[1].query.id
        transforms[1].query = query_99.id
        await transforms[1].save()

        # Create Object that will be deleted
        obj1 = await Node.init(schema="CoreCheckDefinition", session=session)
        await obj1.new(
            session=session,
            name="soontobedeletedcheck",
            query=str(query_99.id),
            file_path="check.py",
            class_name="MyCheck",
            repository=str(repo.id),
        )
        await obj1.save(session=session)

        obj2 = await Node.init(schema="CoreTransformPython", session=session)
        await obj2.new(
            session=session,
            name="soontobedeletedtransform",
            query=str(query_99.id),
            file_path="mytransform.py",
            url="mytransform",
            class_name="MyTransform",
            repository=str(repo.id),
        )
        await obj2.save(session=session)

        await repo.import_all_python_files(branch_name="main", commit=commit)

        modified_check0 = await client.get(kind="CoreCheckDefinition", id=check_definitions[0].id)
        assert modified_check0.timeout.value == check_timeout_value_before_change
        assert modified_check0.query.id == check_query_value_before_change

        modified_transform0 = await client.get(kind="CoreTransformPython", id=transforms[0].id)
        modified_transform1 = await client.get(kind="CoreTransformPython", id=transforms[1].id)

        assert modified_transform0.timeout.value == transform_timeout_value_before_change
        assert modified_transform1.query.id == transform_query_value_before_change

        # FIXME not implemented yet
        with pytest.raises(NodeNotFound):
            await client.get(kind="CoreCheckDefinition", id=obj1.id)

        with pytest.raises(NodeNotFound):
            await client.get(kind="CoreTransformPython", id=obj2.id)

    async def test_import_all_yaml_files(self, session, client: InfrahubClient, repo: InfrahubRepository, query_99):
        commit = repo.get_commit_value(branch_name="main")
        await repo.import_all_yaml_files(branch_name="main", commit=commit)

        rfiles = await client.all(kind="CoreRFile")
        assert len(rfiles) == 2

        # Validate if the function is idempotent, another import just after the first one shouldn't change anything
        nbr_relationships_before = await count_relationships(session=session)
        await repo.import_all_yaml_files(branch_name="main", commit=commit)
        assert await count_relationships(session=session) == nbr_relationships_before

        # 1. Modify an object to validate if its being properly updated
        # 2. Add an object that doesn't exist in Git and validate that it's been deleted
        rfile_template_path_value_before_change = rfiles[0].template_path.value
        rfile_query_value_before_change = rfiles[0].query.id
        rfiles[0].template_path.value = "my_path"
        rfiles[0].query = query_99.id
        await rfiles[0].save()

        obj = await Node.init(schema="CoreRFile", session=session)
        await obj.new(
            session=session,
            name="soontobedeletedrfile",
            query=str(query_99.id),
            repository=str(repo.id),
            template_path="mytmp.j2",
        )
        await obj.save(session=session)

        await repo.import_all_yaml_files(branch_name="main", commit=commit)

        modified_rfile = await client.get(kind="CoreRFile", id=rfiles[0].id)
        assert modified_rfile.template_path.value == rfile_template_path_value_before_change
        assert modified_rfile.query.id == rfile_query_value_before_change

        # FIXME not implemented yet
        with pytest.raises(NodeNotFound):
            await client.get(kind="CoreRFile", id=obj.id)
