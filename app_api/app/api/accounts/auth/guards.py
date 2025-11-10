"""
Permission-based access control guards.

This module provides guard functions for Litestar route handlers to enforce
permission-based access control using the existing Permission model.
"""

from typing import Any, Callable

from litestar.connection import ASGIConnection
from litestar.exceptions import PermissionDeniedException
from litestar.handlers.base import BaseRouteHandler

from app.config import Settings
from app.models.accounts import User

from .permissions import get_user_permissions


def _get_authenticated_user(connection: ASGIConnection[Any, Any, Any, Any]) -> User:
    """
    Get the authenticated user from the connection.

    Args:
        connection: The ASGI connection

    Returns:
        The authenticated user

    Raises:
        PermissionDeniedException: If no user is authenticated
    """
    user: User = connection.user
    if not user:
        raise PermissionDeniedException("Authentication required")
    return user


def _is_superuser(connection: ASGIConnection[Any, Any, Any, Any], user: User) -> bool:
    """
    Check if the user has the superuser role.

    Args:
        connection: The ASGI connection (to access settings)
        user: The user to check

    Returns:
        True if the user has the superuser role, False otherwise
    """
    settings: Settings = connection.app.state.app_settings
    user_role_names = {role.name for role in user.roles if role.is_active}
    return settings.superuser_role_name in user_role_names


def has_permission(
    resource: str, action: str
) -> Callable[[ASGIConnection[Any, Any, Any, Any], BaseRouteHandler], None]:
    """
    Create a guard function that checks if user has specific permission.

    Args:
        resource: The resource name (e.g., "users", "roles", "permissions")
        action: The action name (e.g., "create", "read", "update", "delete", "list")

    Returns:
        A guard function that can be used in Litestar route handlers

    Example:
        @get("/users", guards=[has_permission("users", "list")])
        async def list_users() -> list[User]:
            ...
    """

    def guard(connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
        """Check if the authenticated user has the required permission."""
        user = _get_authenticated_user(connection)

        if _is_superuser(connection, user):
            return

        user_permissions = get_user_permissions(user)
        if (resource, action) not in user_permissions:
            raise PermissionDeniedException(f"Permission denied: requires '{resource}:{action}'")

    return guard


def has_any_permission(
    *permissions: tuple[str, str],
) -> Callable[[ASGIConnection[Any, Any, Any, Any], BaseRouteHandler], None]:
    """
    Create a guard that checks if user has ANY of the specified permissions.

    Args:
        *permissions: Variable number of (resource, action) tuples

    Returns:
        A guard function for Litestar route handlers

    Example:
        @get("/users", guards=[has_any_permission(("users", "read"), ("users", "list"))])
        async def get_users() -> list[User]:
            ...
    """

    def guard(connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
        """Check if user has any of the required permissions."""
        user = _get_authenticated_user(connection)

        if _is_superuser(connection, user):
            return

        user_permissions = get_user_permissions(user)
        for resource, action in permissions:
            if (resource, action) in user_permissions:
                return

        permissions_str = ", ".join(f"'{r}:{a}'" for r, a in permissions)
        raise PermissionDeniedException(f"Permission denied: requires one of [{permissions_str}]")

    return guard


def has_all_permissions(
    *permissions: tuple[str, str],
) -> Callable[[ASGIConnection[Any, Any, Any, Any], BaseRouteHandler], None]:
    """
    Create a guard that checks if user has ALL specified permissions.

    Args:
        *permissions: Variable number of (resource, action) tuples

    Returns:
        A guard function for Litestar route handlers

    Example:
        @post("/admin/critical", guards=[has_all_permissions(("admin", "access"), ("critical", "write"))])
        async def critical_operation() -> dict:
            ...
    """

    def guard(connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
        """Check if user has all required permissions."""
        user = _get_authenticated_user(connection)

        if _is_superuser(connection, user):
            return

        user_permissions = get_user_permissions(user)
        missing_permissions = []
        for resource, action in permissions:
            if (resource, action) not in user_permissions:
                missing_permissions.append(f"{resource}:{action}")

        if missing_permissions:
            missing_str = ", ".join(f"'{p}'" for p in missing_permissions)
            raise PermissionDeniedException(f"Permission denied: missing [{missing_str}]")

    return guard


def has_role(
    *role_names: str,
) -> Callable[[ASGIConnection[Any, Any, Any, Any], BaseRouteHandler], None]:
    """
    Create a guard that checks if user has any of the specified roles.

    Args:
        *role_names: Variable number of role names

    Returns:
        A guard function for Litestar route handlers

    Example:
        @get("/admin", guards=[has_role("admin", "superuser")])
        async def admin_panel() -> dict:
            ...
    """

    def guard(connection: ASGIConnection[Any, Any, Any, Any], _: BaseRouteHandler) -> None:
        """Check if user has any of the required roles."""
        user = _get_authenticated_user(connection)

        # Superuser role bypasses role requirements
        if _is_superuser(connection, user):
            return

        # Check if user has any of the required roles
        user_role_names = {role.name for role in user.roles if role.is_active}
        for role_name in role_names:
            if role_name in user_role_names:
                return

        roles_str = ", ".join(f"'{r}'" for r in role_names)
        raise PermissionDeniedException(f"Permission denied: requires one of roles [{roles_str}]")

    return guard
