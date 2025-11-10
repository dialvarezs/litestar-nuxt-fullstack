"""
Role management controller module.

This module provides CRUD operations for managing user roles
in the role-based access control system.
"""

from typing import Any, Sequence
from uuid import UUID

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, Request, Response, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData
from litestar.exceptions import HTTPException

from app.api.accounts.auth.guards import has_permission
from app.models.accounts import Role

from .dtos import RoleCreateDTO, RoleDTO, RoleUpdateDTO
from .services import RoleService, provide_role_service


def not_found_error_handler(_: Request[Any, Any, Any], __: NotFoundError) -> Response[Any]:
    """Handle role not found errors by returning a 404 response."""
    return Response(status_code=404, content={"status_code": 404, "detail": "Role not found"})


class RoleController(Controller):
    """
    Role management controller for CRUD operations.

    Provides endpoints for creating, reading, updating, and managing
    user roles in the system's role-based access control.
    """

    path = "/roles"
    tags = ["auth / roles"]
    return_dto = RoleDTO
    dependencies = {"role_service": Provide(provide_role_service)}
    exception_handlers = {NotFoundError: not_found_error_handler}

    @get("/", summary="ListRoles", guards=[has_permission("roles", "list")])
    async def list(self, role_service: RoleService) -> Sequence[Role]:
        """
        Get all roles in the system.

        Requires the 'roles:list' permission.

        Args:
            role_service: Role service for business operations

        Returns:
            List of all role objects

        Raises:
            PermissionDeniedException: If the user lacks 'roles:list' permission
        """
        return await role_service.list()

    @post("/", summary="CreateRole", dto=RoleCreateDTO, guards=[has_permission("roles", "create")])
    async def create(self, data: Role, role_service: RoleService) -> Role:
        """
        Create a new role.

        Requires the 'roles:create' permission.

        Args:
            data: Role data for creation
            role_service: Role service for business operations

        Returns:
            The created role object

        Raises:
            PermissionDeniedException: If the user lacks 'roles:create' permission
            HTTPException: If validation fails
        """
        try:
            return await role_service.create_role_with_permissions(data)
        except ValueError as exc:
            raise HTTPException(detail=str(exc), status_code=400) from exc

    @get("/{role_id:uuid}", summary="FetchRole", guards=[has_permission("roles", "read")])
    async def fetch(self, role_id: UUID, role_service: RoleService) -> Role:
        """
        Get a specific role by ID.

        Requires the 'roles:read' permission.

        Args:
            role_id: UUID of the role to retrieve
            role_service: Role service for business operations

        Returns:
            The requested role object

        Raises:
            NotFoundError: If the role is not found (handled by not_found_error_handler)
            PermissionDeniedException: If the user lacks 'roles:read' permission
        """
        return await role_service.get(role_id)

    @patch(
        "/{role_id:uuid}", summary="UpdateRole", dto=RoleUpdateDTO, guards=[has_permission("roles", "update")]
    )
    async def update(self, role_id: UUID, data: DTOData[Role], role_service: RoleService) -> Role:
        """
        Update an existing role.

        Requires the 'roles:update' permission.

        Args:
            role_id: UUID of the role to update
            data: Updated role data
            role_service: Role service for business operations

        Returns:
            The updated role object

        Raises:
            NotFoundError: If the role is not found (handled by not_found_error_handler)
            PermissionDeniedException: If the user lacks 'roles:update' permission
            HTTPException: If validation fails
        """
        try:
            return await role_service.update_role_with_permissions(role_id, data.as_builtins())
        except ValueError as exc:
            raise HTTPException(detail=str(exc), status_code=400) from exc
