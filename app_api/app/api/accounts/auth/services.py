"""Authentication service module.

This module provides business logic for authentication operations including
credential validation and login tracking.
"""

import datetime as dt

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.accounts.users.repositories import UserRepository, provide_user_repository
from app.api.accounts.users.services import password_hasher
from app.models.accounts import User


class AuthService:
    """Authentication service for business logic abstraction.

    Handles credential validation, password verification, and login tracking.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the authentication service.

        Args:
            user_repository: Repository for user data access

        """
        self.user_repository = user_repository

    async def authenticate_user(self, username: str, password: str) -> User | None:
        """Authenticate a user with username and password.

        Validates credentials and updates the last login timestamp on successful
        authentication.

        Args:
            username: Username to authenticate
            password: Plain text password to verify

        Returns:
            The authenticated user if credentials are valid, None otherwise

        """
        user = await self.user_repository.get_one_or_none(username=username)

        if not user or not password_hasher.verify(password, user.password):
            return None

        # Update last login timestamp
        user.last_login = dt.datetime.now(dt.UTC)
        return await self.user_repository.update(user)


async def provide_auth_service(db_session: AsyncSession) -> AuthService:
    """Dependency injection provider for authentication service.

    Args:
        db_session: Async SQLAlchemy session for the request scope

    Returns:
        Configured AuthService instance

    """
    user_repository = await provide_user_repository(db_session)
    return AuthService(user_repository=user_repository)
