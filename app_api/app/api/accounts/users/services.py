"""
User service module.

This module provides business logic abstraction, data transformation,
and validation for user management operations.
"""

from typing import Any
from uuid import UUID

from advanced_alchemy.exceptions import DuplicateKeyError
from advanced_alchemy.filters import CollectionFilter
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from litestar.dto import DTOData
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.accounts.roles.services import RoleService
from app.api.accounts.users.dtos import PasswordChange, UsernameAvailable
from app.api.accounts.users.repositories import UserRepository
from app.models.accounts import Role, User

password_hasher = PasswordHash.recommended()


class UserService(SQLAlchemyAsyncRepositoryService[User, UserRepository]):
    """
    User service for business logic abstraction.

    Provides high-level operations for user management including
    validation, transformation, and complex business rules.
    """

    repository_type = UserRepository
    match_fields = ["id"]

    def __init__(self, **repo_kwargs: Any) -> None:
        super().__init__(**repo_kwargs)
        self.role_service: RoleService | None = None

    def set_role_service(self, role_service: RoleService) -> None:
        """Set the role service dependency.

        Args:
            role_service: Service used to resolve role identifiers.
        """
        self.role_service = role_service

    async def create_user_with_roles(self, data: User) -> User:
        """
        Create a new user with role validation and password hashing.

        Args:
            data: User data including roles and password

        Returns:
            Created user with assigned roles

        Raises:
            ValueError: If roles don't exist or validation fails
            DuplicateKeyError: If username/email already exists
        """
        user = User(**data.to_dict())

        if hasattr(data, "password"):
            user.password = password_hasher.hash(data.password)

        try:
            user = await self.create(user)
            if hasattr(data, "roles"):
                user.roles = await self._validate_and_get_roles([role.to_dict() for role in data.roles])

            return user
        except DuplicateKeyError as e:
            raise ValueError("Username or email already in use") from e

    async def update_user_with_roles(self, user_id: UUID, data: DTOData[User]) -> User:
        """
        Update user with role validation and optional password hashing.

        Args:
            user_id: User to update
            data: Update data

        Returns:
            Updated user
        """
        data_dict = data.as_builtins()
        roles_data = data_dict.pop("roles", None)

        if "password" in data_dict:
            data_dict["password"] = password_hasher.hash(data_dict["password"])

        updated_user = await self.update(data=data_dict, item_id=user_id)

        if roles_data is not None:
            updated_user.roles = await self._validate_and_get_roles([role.to_dict() for role in roles_data])

        return updated_user

    async def update_password(self, user_id: UUID, password_data: DTOData[PasswordChange]) -> None:
        """
        Change user password with current password verification.

        Args:
            user_id: User whose password to change
            password_data: Current and new password data

        Raises:
            ValueError: If current password is incorrect
        """
        data = password_data.as_builtins()
        current_password = data["current_password"]
        new_password = data["new_password"]

        # Get user and verify current password
        user = await self.get(user_id)
        if not password_hasher.verify(current_password, user.password):
            raise ValueError("Invalid current password")

        password_update = {"password": password_hasher.hash(new_password)}
        await self.update(item_id=user_id, data=password_update)

    async def check_username_availability(self, username: str) -> UsernameAvailable:
        """
        Check username availability for registration.

        Args:
            username: Username to check

        Returns:
            Username availability result
        """
        exists = await self.repository.username_exists(username)
        return UsernameAvailable(username=username, available=not exists)

    async def _validate_and_get_roles(self, roles: list[dict[str, Any]]) -> list[Role]:
        """
        Validate role existence and return role objects.

        Args:
            roles: List of role objects or IDs to validate

        Returns:
            List of validated role objects

        Raises:
            ValueError: If role service not configured
        """
        if not self.role_service:
            raise ValueError("Role service not configured")

        if not roles:
            return []

        role_ids = [role["id"] for role in roles]

        validated_roles = await self.role_service.list(CollectionFilter(field_name="id", values=role_ids))

        return [role for role in validated_roles]


async def provide_user_service(db_session: AsyncSession) -> UserService:
    """Dependency injection provider for user service with role service.

    Args:
        db_session: Async SQLAlchemy session for the request scope.

    Returns:
        :class:`UserService` wired with a :class:`RoleService`.
    """
    from app.api.accounts.roles.services import RoleService

    user_service = UserService(session=db_session)
    role_service = RoleService(session=db_session)
    user_service.set_role_service(role_service)
    return user_service
