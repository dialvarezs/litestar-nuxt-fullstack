"""Permission management controller module."""

from collections.abc import Sequence
from typing import Any, ClassVar
from uuid import UUID

from advanced_alchemy.exceptions import NotFoundError
from litestar import Controller, Request, Response, delete, get, patch, post
from litestar.di import Provide
from litestar.dto import DTOData

from app.api.accounts.auth.guards import has_permission
from app.models.accounts import Permission

from .dtos import PermissionCreateDTO, PermissionDTO, PermissionUpdateDTO
from .services import PermissionService, provide_permission_service


def not_found_error_handler(_: Request[Any, Any, Any], __: NotFoundError) -> Response[Any]:
    """Handle permission not found errors by returning a 404 response."""
    return Response(status_code=404, content={"status_code": 404, "detail": "Permission not found"})


class PermissionController(Controller):
    """Controller providing CRUD endpoints for permissions."""

    path = "/permissions"
    tags = ("accounts / permissions",)
    return_dto = PermissionDTO
    dependencies: ClassVar = {"permission_service": Provide(provide_permission_service)}
    exception_handlers: ClassVar = {NotFoundError: not_found_error_handler}

    @get(
        "/",
        summary="ListPermissions",
        guards=[has_permission("permissions", "list")],
    )
    async def list(self, permission_service: PermissionService) -> Sequence[Permission]:
        """List all permissions in the system.

        This endpoint requires the 'permissions:list' permission.
        """
        return await permission_service.list()

    @post(
        "/",
        summary="CreatePermission",
        dto=PermissionCreateDTO,
        guards=[has_permission("permissions", "create")],
    )
    async def create(self, data: Permission, permission_service: PermissionService) -> Permission:
        """Create a new permission.

        Creates a new permission with the provided resource and action data.
        Requires the 'permissions:create' permission.
        """
        return await permission_service.create(data)

    @get(
        "/{permission_id:uuid}",
        summary="FetchPermission",
        guards=[has_permission("permissions", "read")],
    )
    async def fetch(self, permission_id: UUID, permission_service: PermissionService) -> Permission:
        """Fetch a specific permission by its UUID.

        Requires the 'permissions:read' permission.
        """
        return await permission_service.get(permission_id)

    @patch(
        "/{permission_id:uuid}",
        summary="UpdatePermission",
        dto=PermissionUpdateDTO,
        guards=[has_permission("permissions", "update")],
    )
    async def update(
        self,
        permission_id: UUID,
        data: DTOData[Permission],
        permission_service: PermissionService,
    ) -> Permission:
        """Update an existing permission's data.

        Requires the 'permissions:update' permission.
        """
        return await permission_service.update(item_id=permission_id, data=data.as_builtins())

    @delete(
        "/{permission_id:uuid}",
        summary="DeletePermission",
        status_code=204,
        guards=[has_permission("permissions", "delete")],
    )
    async def delete(self, permission_id: UUID, permission_service: PermissionService) -> None:
        """Delete a permission from the system.

        Requires the 'permissions:delete' permission.
        """
        await permission_service.delete(permission_id)
