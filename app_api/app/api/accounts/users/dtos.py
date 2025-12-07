"""User data transfer objects (DTOs).

This module defines the DTOs for user-related operations, providing
different configurations for various CRUD operations and specialized
functionality like password changes and username availability checks.
"""

from dataclasses import dataclass

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DataclassDTO

from app.models.accounts import User


class UserDTO(SQLAlchemyDTO[User]):
    """DTO for reading user data."""

    config = SQLAlchemyDTOConfig(exclude={"password", "roles.0.created_at", "roles.0.updated_at"})


class UserWriteDTO(SQLAlchemyDTO[User]):
    """DTO for creating users."""

    config = SQLAlchemyDTOConfig(include={"username", "email", "fullname", "password", "roles.0.id"})


class UserUpdateDTO(SQLAlchemyDTO[User]):
    """DTO for updating users."""

    config = SQLAlchemyDTOConfig(
        include={"username", "email", "fullname", "password", "is_active", "roles.0.id"},
        partial=True,
    )


@dataclass
class PasswordChange:
    """Password change data."""

    current_password: str
    new_password: str


class PasswordChangeDTO(DataclassDTO[PasswordChange]):
    """DTO for password changes."""


@dataclass
class UsernameAvailable:
    """Username availability data."""

    username: str
    available: bool = False


class UsernameAvailableDTO(DataclassDTO[UsernameAvailable]):
    """DTO for username availability."""
