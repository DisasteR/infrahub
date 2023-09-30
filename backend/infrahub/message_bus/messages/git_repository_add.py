from pydantic import Field

from infrahub.message_bus import InfrahubBaseMessage


class GitRepositoryAdd(InfrahubBaseMessage):
    """Clone and sync an external repository after creation."""

    location: str = Field(..., description="The external URL of the repository")
    repository_id: str = Field(..., description="The unique ID of the Repository")
    repository_name: str = Field(..., description="The name of the repository")
