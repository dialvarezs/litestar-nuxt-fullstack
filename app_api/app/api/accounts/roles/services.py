"""Role service module for business logic and data access."""

from typing import Any
from uuid import UUID

from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.accounts.permissions.services import PermissionService
from app.api.accounts.roles.repositories import RoleRepository
from app.models.accounts import Permission, Role


class RoleService(SQLAlchemyAsyncRepositoryService[Role, RoleRepository]):
    """Role service."""

    repository_type = RoleRepository
    match_fields = "id"

    def __init__(self, **repo_kwargs: Any) -> None:  # noqa: ANN401
        """Initialize role service with repository configuration.

        Args:
            **repo_kwargs: Arguments to pass to the repository.

        """
        super().__init__(**repo_kwargs)
        self.permission_service: PermissionService | None = None

    def set_permission_service(self, permission_service: "PermissionService") -> None:
        """Inject the permission service dependency.

        Args:
            permission_service: Service used to resolve permission identifiers.

        """
        self.permission_service = permission_service

    async def assign_permissions(self, role: Role, permissions: list[dict[str, Any]]) -> Role:
        """Replace the role's permissions with the validated collection.

        Args:
            role: Role to mutate.
            permissions: Permission payloads with identifiers.

        Returns:
            ``role`` with ``permissions`` refreshed to match the IDs provided.

        """
        role.permissions = await self._validate_and_get_permissions(permissions)
        return role

    async def create_role_with_permissions(self, data: Role) -> Role:
        """Create a new role with validated permissions.

        Normalizes permission data, creates the role, and assigns permissions
        in a single transaction.

        Args:
            data: Role data including permissions list.

        Returns:
            Created role with assigned permissions.

        Raises:
            ValueError: If permission validation fails.

        """
        raw_permissions = getattr(data, "permissions", None) or []
        permissions_payload = self._normalize_permissions(raw_permissions)

        # Clear permissions to avoid unintended inserts during role creation
        data.permissions = []

        # Create the role first
        role = await self.create(data)

        # Assign permissions if provided
        if permissions_payload:
            role = await self.assign_permissions(role, permissions_payload)

        return role

    async def update_role_with_permissions(self, role_id: UUID, data: dict[str, Any]) -> Role:
        """Update a role with optional permission reassignment.

        Extracts permission data from update payload, updates role attributes,
        and optionally replaces the role's permissions.

        Args:
            role_id: UUID of the role to update.
            data: Update data including optional permissions list.

        Returns:
            Updated role with new permissions if provided.

        Raises:
            ValueError: If permission validation fails.

        """
        permissions_payload = data.pop("permissions", None)

        # Update base role attributes
        updated_role = await self.update(item_id=role_id, data=data)

        # Update permissions if provided
        if permissions_payload is not None:
            normalized_permissions = self._normalize_permissions(permissions_payload)
            updated_role = await self.assign_permissions(updated_role, normalized_permissions)

        return updated_role

    @staticmethod
    def _normalize_permissions(raw_permissions: list[Any]) -> list[dict[str, Any]]:
        """Normalize permission payloads from various formats.

        Handles both dict and object formats for permission data, extracting
        the ID field regardless of input structure.

        Args:
            raw_permissions: List of permissions in various formats (objects or dicts).

        Returns:
            List of normalized permission dicts with ``id`` keys.

        """
        normalized_permissions: list[dict[str, Any]] = []

        for permission in raw_permissions:
            if isinstance(permission, dict):
                permission_id = permission.get("id")
            else:
                permission_id = getattr(permission, "id", None)

            if permission_id is not None:
                normalized_permissions.append({"id": permission_id})

        return normalized_permissions

    async def _validate_and_get_permissions(self, permissions: list[dict[str, Any]]) -> list[Permission]:
        """Validate provided permission payloads and return ORM instances.

        Args:
            permissions: Sequence of dict payloads containing an ``id``.

        Returns:
            List of :class:`app.models.accounts.Permission` resolved from the IDs.

        Raises:
            ValueError: If the dependency is missing or an ID is unknown.

        """
        if not self.permission_service:
            msg = "Permission service not configured"
            raise ValueError(msg)

        permission_ids: list[UUID | str] = [
            permission["id"] for permission in permissions if "id" in permission
        ]
        if len(permission_ids) == 0:
            return []

        validated_permissions = await self.permission_service.list_by_ids(permission_ids)

        # Identify invalid permission and raise error if any
        resolved_ids = {str(permission.id) for permission in validated_permissions}
        missing_ids = [
            str(permission_id) for permission_id in permission_ids if str(permission_id) not in resolved_ids
        ]
        if missing_ids:
            missing = ", ".join(missing_ids)
            msg = f"Unknown permission identifiers: {missing}"
            raise ValueError(msg)

        return list(validated_permissions)


async def provide_role_service(db_session: AsyncSession) -> RoleService:
    """Dependency injection provider for role service.

    Args:
        db_session: Async SQLAlchemy session for the request scope.

    Returns:
        :class:`RoleService` wired with a :class:`PermissionService`.

    """
    role_service = RoleService(session=db_session)
    permission_service = PermissionService(session=db_session)
    role_service.set_permission_service(permission_service)
    return role_service
