"""
Authentication security module.

This module provides JWT-based authentication security configuration
and user retrieval functions for the application.
"""

from datetime import timedelta
from typing import Any
from uuid import UUID

from advanced_alchemy.exceptions import NotFoundError
from litestar.connection import ASGIConnection
from litestar.exceptions import ClientException
from litestar.security.jwt import OAuth2PasswordBearerAuth, Token

from app.config import Settings
from app.models.accounts import User

from ..users.repositories import UserRepository


async def current_user_from_token(
    token: Token,
    connection: ASGIConnection[Any, Any, Any, Any],
) -> User:
    """
    Retrieve the current user from a JWT token.

    Extracts the user ID from the token subject and fetches the corresponding
    user from the database using the app's database configuration.

    Args:
        token: JWT token containing user identification
        connection: ASGI connection containing app state with database config

    Returns:
        User object for the authenticated user

    Raises:
        NotFoundException: If the user is not found in the database
    """
    app_sqlalchemy_config = connection.app.state.sqlalchemy_config
    async with app_sqlalchemy_config.get_session() as session:
        repo = UserRepository(session=session)
        try:
            return await repo.get_one(id=UUID(token.sub))
        except NotFoundError as e:
            raise ClientException("Token user not found") from e
        except ValueError as e:
            raise ClientException("Invalid user ID in token") from e


def create_oauth2_auth(app_settings: Settings) -> OAuth2PasswordBearerAuth[User]:
    """Create OAuth2 authentication configuration using provided settings."""
    return OAuth2PasswordBearerAuth[User](
        retrieve_user_handler=current_user_from_token,
        token_secret=app_settings.secret_key.get_secret_value(),
        token_url="/accounts/auth/login",
        exclude=["/accounts/auth/", "/schema"],
        default_token_expiration=timedelta(days=1),
    )
