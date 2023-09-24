from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from graphene import Boolean, InputField, InputObjectType, List, Mutation, String

from infrahub.core.constants import RelationshipCardinality
from infrahub.core.manager import NodeManager
from infrahub.core.query.relationship import (
    RelationshipGetPeerQuery,
    RelationshipPeerData,
)
from infrahub.core.relationship import Relationship
from infrahub.exceptions import NodeNotFound, ValidationError
from infrahub_client.utils import compare_lists

from ..types import RelatedNodeInput

if TYPE_CHECKING:
    from graphql import GraphQLResolveInfo

    from infrahub.database import InfrahubDatabase


# pylint: disable=unused-argument,too-many-branches

RELATIONSHIP_PEERS_TO_IGNORE = ["CoreNode"]


class RelationshipNodesInput(InputObjectType):
    id = InputField(String(required=True), description="ID of the node at the source of the relationship")
    name = InputField(String(required=True), description="Name of the relationship to add or remove nodes")
    nodes = InputField(
        List(of_type=RelatedNodeInput), description="List of nodes to add or remove to the relationships"
    )


class RelationshipMixin:
    @classmethod
    async def mutate(
        cls,
        root: dict,
        info: GraphQLResolveInfo,
        data,
    ):
        db: InfrahubDatabase = info.context.get("infrahub_session")
        at = info.context.get("infrahub_at")
        branch = info.context.get("infrahub_branch")

        if not (
            source := await NodeManager.get_one(
                db=db, id=data.get("id"), branch=branch, at=at, include_owner=True, include_source=True
            )
        ):
            raise NodeNotFound(branch, None, data.get("id"))

        # Check if the name of the relationship provided exist for this node and is of cardinality Many
        if data.get("name") not in source._schema.relationship_names:
            raise ValidationError(
                {"name": f"'{data.get('name')}' is not a valid relationship for '{source.get_kind()}'"}
            )

        rel_schema = source._schema.get_relationship(name=data.get("name"))
        if rel_schema.cardinality != RelationshipCardinality.MANY:
            raise ValidationError({"name": f"'{data.get('name')}' must be a relationship of cardinality Many"})

        # Query the node in the database and validate that all of them exist and are if the correct kind
        node_ids: List[str] = [node_data.get("id") for node_data in data.get("nodes")]
        nodes = await NodeManager.get_many(db=db, ids=node_ids, fields={"display_label": None}, branch=branch, at=at)

        _, _, in_list2 = compare_lists(list1=list(nodes.keys()), list2=node_ids)
        if in_list2:
            for node_id in in_list2:
                raise ValidationError(f"{node_id!r}: Unable to find the node in the database.")

        for node_id, node in nodes.items():
            if rel_schema.peer in RELATIONSHIP_PEERS_TO_IGNORE:
                continue
            if rel_schema.peer not in node.get_labels():
                raise ValidationError(f"{node_id!r} {node.get_kind()!r} is not a valid peer for '{rel_schema.peer}'")

        # The nodes that are already present in the db
        query = await RelationshipGetPeerQuery.init(
            db=db,
            source=source,
            at=at,
            rel=Relationship(schema=rel_schema, branch=branch, node=source),
        )
        await query.execute(db=db)
        existing_peers: Dict[str, RelationshipPeerData] = {peer.peer_id: peer for peer in query.get_peers()}

        if cls.__name__ == "RelationshipAdd":
            for node_data in data.get("nodes"):
                if node_data.get("id") not in existing_peers.keys():
                    rel = Relationship(schema=rel_schema, branch=branch, at=at, node=source)
                    await rel.new(db=db, data=node_data)
                    await rel.save(db=db)

        elif cls.__name__ == "RelationshipRemove":
            for node_data in data.get("nodes"):
                if node_data.get("id") in existing_peers.keys():
                    # TODO once https://github.com/opsmill/infrahub/issues/792 has been fixed
                    # we should use RelationshipDataDeleteQuery to delete the relationship
                    # it would be more query efficient
                    rel = Relationship(schema=rel_schema, branch=branch, at=at, node=source)
                    await rel.load(db=db, data=existing_peers[node_data.get("id")])
                    await rel.delete(db=db)

        return cls(ok=True)


class RelationshipAdd(RelationshipMixin, Mutation):
    class Arguments:
        data = RelationshipNodesInput(required=True)

    ok = Boolean()


class RelationshipRemove(RelationshipMixin, Mutation):
    class Arguments:
        data = RelationshipNodesInput(required=True)

    ok = Boolean()
