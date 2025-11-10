"""Permission repository module."""

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import Permission


class PermissionRepository(SQLAlchemyAsyncRepository[Permission]):
    """Repository for permission data access operations."""

    model_type = Permission


async def provide_permission_repository(db_session: AsyncSession) -> PermissionRepository:
    """Dependency injection provider for permission repository."""

    return PermissionRepository(session=db_session, statement=select(Permission).order_by(Permission.name))
