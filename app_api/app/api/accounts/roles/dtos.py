"""
Role data transfer objects (DTOs).

This module defines the DTOs for role-related operations, providing
different configurations for various CRUD operations on role data.
"""

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models.accounts import Role


class RoleDTO(SQLAlchemyDTO[Role]):
    """Base role DTO."""

    config = SQLAlchemyDTOConfig(exclude={"users", "permissions.0.roles"})


class RoleCreateDTO(RoleDTO):
    """DTO for role creation."""

    config = SQLAlchemyDTOConfig(include={"name", "description", "permissions.0.id"})


class RoleUpdateDTO(RoleDTO):
    """DTO for role updates."""

    config = SQLAlchemyDTOConfig(
        include={"name", "description", "is_active", "permissions.0.id"},
        partial=True,
    )
