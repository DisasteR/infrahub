from __future__ import annotations

from graphene import Field, Int, List, ObjectType, String

from .enums import PermissionDecision


class ObjectPermission(ObjectType):
    kind = Field(String, required=True, description="The kind this permission refers to.")
    view = Field(PermissionDecision, required=True, description="Indicates if the account has the read permission")
    create = Field(PermissionDecision, required=True, description="Indicates if the account has the create permission")
    update = Field(PermissionDecision, required=True, description="Indicates if the account has the update permission")
    delete = Field(PermissionDecision, required=True, description="Indicates if the account has the delete permission")


class ObjectPermissionNode(ObjectType):
    node = Field(ObjectPermission, required=True)


class PaginatedObjectPermission(ObjectType):
    count = Field(
        Int,
        required=True,
        description="The number of permissions applicable, will be 1 for normal nodes or possibly more for generics",
    )
    edges = Field(List(of_type=ObjectPermissionNode, required=True), required=True)