"""Role repository module.

This module provides data access layer functionality for role management,
including database operations and dependency injection providers.
"""

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import Role


class RoleRepository(SQLAlchemyAsyncRepository[Role]):
    """Repository for role data access operations.

    Provides CRUD operations for Role entities using SQLAlchemy async repository.
    """

    model_type = Role


async def provide_role_repository(db_session: AsyncSession) -> RoleRepository:
    """Dependency injection provider for role repository.

    Creates a RoleRepository instance with a database session and
    default ordering by role name.

    Args:
        db_session: Async database session

    Returns:
        Configured RoleRepository instance

    """
    return RoleRepository(session=db_session, statement=select(Role).order_by(Role.name))
