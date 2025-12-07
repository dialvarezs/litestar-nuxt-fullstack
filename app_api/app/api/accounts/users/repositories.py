"""User repository module.

This module provides basic data access layer functionality for user management.
Business logic has been moved to the service layer.
"""

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.accounts import User


class UserRepository(SQLAlchemyAsyncRepository[User]):
    """Repository for user data access operations.

    Provides basic CRUD operations. Business logic is handled by UserService.
    """

    model_type = User

    async def username_exists(self, username: str) -> bool:
        """Check if a username is already in use.

        Args:
            username: Username to check for availability

        Returns:
            True if username exists, False otherwise

        """
        return await self.exists(username=username)


async def provide_user_repository(db_session: AsyncSession) -> UserRepository:
    """Dependency injection provider for user repository.

    Creates a UserRepository instance with a database session and
    default ordering by username for consistent results.

    Args:
        db_session: Async database session

    Returns:
        Configured UserRepository instance with username ordering

    """
    return UserRepository(session=db_session, statement=select(User).order_by(User.username))
