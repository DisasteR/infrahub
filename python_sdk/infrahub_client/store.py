from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Dict, Optional

from infrahub_client.exceptions import NodeNotFound

if TYPE_CHECKING:
    from infrahub_client.node import InfrahubNode, InfrahubNodeBase, InfrahubNodeSync


class NodeStoreBase:
    """Internal Store for InfrahubNode objects.

    Often while creating a lot of new objects,
    we need to save them in order to reuse them laterto associate them with another node for example.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, InfrahubNodeBase]] = defaultdict(dict)

    def _set(self, key: str, node: InfrahubNodeBase) -> None:
        if "InfrahubNode" not in node.__class__.__name__:
            raise TypeError(f"'node' must be of type InfrahubNode, not {type(node)!r}")

        node_kind = node._schema.kind
        self._store[node_kind][key] = node

    def _get(self, key: str, kind: Optional[str] = None, raise_when_missing: bool = True) -> Optional[InfrahubNode]:
        if kind and kind not in self._store and key not in self._store[kind]:
            if not raise_when_missing:
                return None
            raise NodeNotFound(
                branch_name="n/a",
                node_type=kind,
                identifier={"key": [key]},
                message="Unable to find the node in the Store",
            )

        if kind and kind in self._store and key in self._store[kind]:
            return self._store[kind][key]

        for _, item in self._store.items():
            if key in item:
                return item[key]

        if not raise_when_missing:
            return None
        raise NodeNotFound(
            branch_name="n/a",
            node_type="n/a",
            identifier={"key": [key]},
            message=f"Unable to find the node {key!r} in the Store",
        )


class NodeStore(NodeStoreBase):
    def get(self, key: str, kind: Optional[str] = None, raise_when_missing: bool = True) -> Optional[InfrahubNode]:
        return self._get(key=key, kind=kind, raise_when_missing=raise_when_missing)

    def set(self, key: str, node: InfrahubNode) -> None:
        return self._set(key=key, node=node)


class NodeStoreSync(NodeStoreBase):
    def get(self, key: str, kind: Optional[str] = None, raise_when_missing: bool = True) -> Optional[InfrahubNodeSync]:
        return self._get(key=key, kind=kind, raise_when_missing=raise_when_missing)

    def set(self, key: str, node: InfrahubNodeSync) -> None:
        return self._set(key=key, node=node)
