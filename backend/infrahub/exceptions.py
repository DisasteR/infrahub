from typing import Any, Dict, Optional


class Error(Exception):
    HTTP_CODE: int = 500
    DESCRIPTION: str = "Unknown Error"
    message: str = ""

    def api_response(self) -> Dict[str, Any]:
        """Return error response."""
        return {
            "data": None,
            "errors": [{"message": str(self.message) or self.DESCRIPTION, "extensions": {"code": self.HTTP_CODE}}],
        }


class InitializationError(Error):
    DESCRIPTION: str = "The application hasn't been initialized properly"


class DatabaseError(Error):
    pass


class RepositoryError(Error):
    def __init__(self, identifier, message=None):
        self.identifier = identifier
        self.message = message or f"An error occured with GitRepository '{identifier}'."
        super().__init__(self.message)


class CommitNotFoundError(Error):
    def __init__(self, identifier, commit, message=None):
        self.identifier = identifier
        self.commit = commit
        self.message = message or f"Commit {commit} not found with GitRepository '{identifier}'."
        super().__init__(self.message)


class DataTypeNotFound(Error):
    def __init__(self, name, message=None):
        self.name = name
        self.message = message or f"Unable to find the DataType '{name}'."
        super().__init__(self.message)


class FileNotFound(Error):
    def __init__(self, repository_name, location, commit, message=None):
        self.repository_name = repository_name
        self.location = location
        self.commit = commit
        self.message = message or f"Unable to find the file at '{repository_name}::{commit}::{location}'."
        super().__init__(self.message)


class TransformError(Error):
    def __init__(self, repository_name, location, commit, message=None):
        self.repository_name = repository_name
        self.location = location
        self.commit = commit
        self.message = (
            message or f"An error occured with the transform function at '{repository_name}::{commit}::{location}'."
        )
        super().__init__(self.message)


class CheckError(Error):
    def __init__(self, repository_name, location, class_name, commit, message=None):
        self.repository_name = repository_name
        self.location = location
        self.commit = commit
        self.class_name = class_name
        self.message = (
            message
            or f"An error occured with the check function at '{repository_name}::{commit}::{location}::{class_name}'."
        )
        super().__init__(self.message)


class TransformNotFoundError(TransformError):
    def __init__(self, repository_name, location, commit, message=None):
        self.message = (
            message or f"Unable to locate the transform function at '{repository_name}::{commit}::{location}'."
        )
        super().__init__(repository_name, location, commit, self.message)


class BranchNotFound(Error):
    HTTP_CODE: int = 400

    def __init__(self, identifier, message=None):
        self.identifier = identifier
        self.message = message or f"Branch: {identifier} not found."
        super().__init__(self.message)


class NodeNotFound(Error):
    HTTP_CODE: int = 404

    def __init__(self, branch_name, node_type, identifier, message=None):
        self.branch_name = branch_name
        self.node_type = node_type
        self.identifier = identifier
        self.message = message or f"Unable to find the node {identifier} / {node_type} in the database."
        super().__init__(self.message)

    def __str__(self):
        return f"""
        {self.message}
        {self.branch_name} | {self.node_type} | {self.identifier}
        """


class AuthorizationError(Error):
    HTTP_CODE: int = 401
    message: str = "Access to the requested resource was denied"

    def __init__(self, message: Optional[str] = None):
        self.message = message or self.message
        super().__init__(self.message)


class PermissionDeniedError(Error):
    HTTP_CODE: int = 403
    message: str = "The requested operation was not authorized"

    def __init__(self, message: Optional[str] = None):
        self.message = message or self.message
        super().__init__(self.message)


class SchemaNotFound(Error):
    def __init__(self, branch_name, identifier, message=None):
        self.branch_name = branch_name
        self.identifier = identifier
        self.message = message or f"Unable to find the schema {identifier} in the database."
        super().__init__(self.message)

    def __str__(self):
        return f"""
        {self.message}
        {self.branch_name} | {self.identifier}
        """


class QueryError(Error):
    def __init__(self, query, params, message="Unable to execute the CYPHER query."):
        self.query = query
        self.params = params

        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"""
        {self.message}
        {self.query}
        {self.params}
        """


class ValidationError(Error):
    def __init__(self, input_value):
        self.message = None
        self.location = None
        self.messages = {}

        if isinstance(input_value, str):
            self.message = input_value
        elif isinstance(input_value, dict) and len(input_value) == 1:
            self.message = list(input_value.values())[0]
            self.location = list(input_value.keys())[0]
        elif isinstance(input_value, dict) and len(input_value) > 1:
            for key, value in input_value.items():
                self.messages[key] = value

        elif isinstance(input_value, list):
            for item in input_value:
                if isinstance(item, self.__class__):
                    self.messages[item.location] = item.message
                elif isinstance(item, dict):
                    for key, value in item.items():
                        self.messages[key] = value

        super().__init__(self.message)

    def __str__(self):
        if self.messages:
            return ", ".join([f"{message} at {location}" for location, message in self.messages.items()])

        return f"{self.message} at {self.location or '<Undefined>'}"
