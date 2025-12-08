"""Role management controller module."""

from collections.abc import Sequence
from typing import Any
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
    """Role management controller for CRUD operations.

    Provides endpoints for creating, reading, updating, and managing
    user roles in the system's role-based access control.
    """

    path = "/roles"
    tags = ("accounts / roles",)
    return_dto = RoleDTO
    dependencies = {"role_service": Provide(provide_role_service)}  # noqa: RUF012
    exception_handlers = {NotFoundError: not_found_error_handler}  # noqa: RUF012

    @get(
        "/",
        summary="ListRoles",
        guards=[has_permission("roles", "list")],
    )
    async def list(self, role_service: RoleService) -> Sequence[Role]:
        """List all roles in the system.

        This endpoint requires the 'roles:list' permission.
        """
        return await role_service.list()

    @post(
        "/",
        summary="CreateRole",
        dto=RoleCreateDTO,
        guards=[has_permission("roles", "create")],
    )
    async def create(self, data: Role, role_service: RoleService) -> Role:
        """Create a new role with associated permissions.

        Creates a new role with the provided data and assigns any specified
        permissions. Requires the 'roles:create' permission.
        """
        try:
            return await role_service.create_role_with_permissions(data)
        except ValueError as exc:
            raise HTTPException(detail=str(exc), status_code=400) from exc

    @get(
        "/{role_id:uuid}",
        summary="FetchRole",
        guards=[has_permission("roles", "read")],
    )
    async def fetch(self, role_id: UUID, role_service: RoleService) -> Role:
        """Fetch a specific role by its UUID.

        Requires the 'roles:read' permission.
        """
        return await role_service.get(role_id)

    @patch(
        "/{role_id:uuid}",
        summary="UpdateRole",
        dto=RoleUpdateDTO,
        guards=[has_permission("roles", "update")],
    )
    async def update(self, role_id: UUID, data: DTOData[Role], role_service: RoleService) -> Role:
        """Update an existing role's data and permissions.

        Updates the specified role's information and permission assignments
        with the provided data. Requires the 'roles:update' permission.
        """
        try:
            return await role_service.update_role_with_permissions(role_id, data.as_builtins())
        except ValueError as exc:
            raise HTTPException(detail=str(exc), status_code=400) from exc
