from typing import Sequence
from uuid import UUID

from advanced_alchemy.filters import CollectionFilter
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.accounts.permissions.repositories import PermissionRepository
from app.models.accounts import Permission


class PermissionService(SQLAlchemyAsyncRepositoryService[Permission, PermissionRepository]):
    """Business logic wrapper for permission operations."""

    repository_type = PermissionRepository
    match_fields = ["id", "name"]

    async def list_by_ids(self, permission_ids: list[UUID | str]) -> Sequence[Permission]:
        """Fetch a set of permissions by identifier.

        Args:
            permission_ids: Collection of UUIDs (or string UUIDs) to resolve.

        Returns:
            Ordered list of :class:`~app.models.accounts.Permission` records that
            match the provided identifiers.
        """

        return await self.list(CollectionFilter(field_name="id", values=permission_ids))


async def provide_permission_service(db_session: AsyncSession) -> PermissionService:
    """Build a :class:`PermissionService` instance for dependency injection.

    Args:
        db_session: Async SQLAlchemy session for the request scope.

    Returns:
        Configured :class:`PermissionService`.
    """

    return PermissionService(session=db_session)
