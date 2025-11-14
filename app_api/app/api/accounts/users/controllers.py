"""User management controller module."""

from typing import Any, Sequence
from uuid import UUID

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, Request, Response, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import HTTPException
from litestar.security.jwt import Token  # noqa: F401

from app.api.accounts.auth.guards import has_permission
from app.api.accounts.users.dtos import (
    PasswordChange,
    PasswordChangeDTO,
    UserDTO,
    UsernameAvailable,
    UsernameAvailableDTO,
    UserUpdateDTO,
    UserWriteDTO,
)
from app.api.accounts.users.services import UserService, provide_user_service
from app.models.accounts import User


def not_found_error_handler(_: Request[Any, Any, Any], __: NotFoundError) -> Response[Any]:
    """Handle user not found errors by returning a 404 response."""
    return Response(status_code=404, content={"status_code": 404, "detail": "User not found"})


class UserController(Controller):
    """
    User management controller for comprehensive user operations.

    Provides endpoints for user CRUD operations, authentication management,
    password changes, and username availability checking.
    """

    path = "/users"
    tags = ["accounts / users"]
    return_dto = UserDTO
    dependencies = {"user_service": Provide(provide_user_service)}
    exception_handlers = {NotFoundError: not_found_error_handler}

    @get(
        "/",
        summary="ListUsers",
        guards=[has_permission("users", "list")],
    )
    async def list(self, user_service: UserService) -> Sequence[User]:
        """
        List all users in the system.

        This endpoint requires the 'users:list' permission.
        """
        return await user_service.list()

    @post(
        "/",
        summary="CreateUser",
        dto=UserWriteDTO,
        guards=[has_permission("users", "create")],
    )
    async def create(self, data: User, user_service: UserService) -> User:
        """
        Create a new user with associated roles.

        Creates a new user account with the provided user data and assigns
        any specified roles. Requires the 'users:create' permission.
        """
        try:
            return await user_service.create_user_with_roles(data)
        except ValueError as e:
            raise HTTPException(detail=str(e), status_code=409) from e

    @get("/me", summary="FetchMyUser")
    async def fetch_me(self, request: "Request[User, Token, Any]") -> User:
        """
        Fetch the currently authenticated user's profile.

        Returns the complete user profile for the currently authenticated user
        based on the JWT token provided in the request.
        """
        return request.user

    @get(
        "/{user_id:uuid}",
        summary="FetchUser",
        guards=[has_permission("users", "read")],
    )
    async def fetch(self, user_id: UUID, user_service: UserService) -> User:
        """
        Fetch a specific user by their UUID.

        Retrieves the complete user profile for a specific user identified
        by their unique UUID. Requires the 'users:read' permission.

        Args:
            user_id: The unique identifier of the user to retrieve
            user_service: The user service instance for business operations

        Returns:
            The complete user profile for the specified user

        Raises:
            NotFoundError: If no user exists with the provided UUID (handled by not_found_error_handler)
            PermissionDeniedException: If the user lacks 'users:read' permission
        """
        return await user_service.get(user_id)

    @patch(
        "/{user_id:uuid}",
        summary="UpdateUser",
        dto=UserUpdateDTO,
        guards=[has_permission("users", "update")],
    )
    async def update(self, user_id: UUID, data: DTOData[User], user_service: UserService) -> User:
        """
        Update an existing user's profile and roles.

        Updates the specified user's profile information and role assignments
        with the provided data. Requires the 'users:update' permission.
        """
        try:
            return await user_service.update_user_with_roles(user_id, data)
        except ValueError as e:
            raise HTTPException(detail=str(e), status_code=400) from e

    @post("/me/update-password", summary="UpdateMyPassword", dto=PasswordChangeDTO, status_code=204)
    async def update_my_password(
        self,
        data: DTOData[PasswordChange],
        request: "Request[User, Token, Any]",
        user_service: UserService,
    ) -> None:
        """
        Update the authenticated user's password.

        Allows the currently authenticated user to change their password by providing
        their current password and a new password. The current password is validated
        before the change is applied.
        """
        user = request.user

        try:
            await user_service.update_password(user.id, data)
        except ValueError as e:
            raise HTTPException(detail=str(e), status_code=422) from e

    @get("/username-available", summary="CheckUsernameAvailable", return_dto=UsernameAvailableDTO)
    async def username_available(self, username: str, user_service: UserService) -> UsernameAvailable:
        """
        Check if a username is available for registration.
        """
        return await user_service.check_username_availability(username)

    @delete(
        "/{user_id:uuid}",
        summary="DeleteUser",
        guards=[has_permission("users", "delete")],
    )
    async def delete(self, user_id: UUID, user_service: UserService) -> None:
        """
        Delete a user account from the system.

        Requires the 'users:delete' permission.
        """
        await user_service.delete(user_id)
