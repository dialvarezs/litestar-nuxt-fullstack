"""
Permission checking utilities.

This module provides helper functions for programmatically checking user permissions
within application code, complementing the guard-based approach for route handlers.
"""

from app.models.accounts import User


def user_has_permission(user: User, resource: str, action: str) -> bool:
    """
    Check if a user has a specific permission.

    Args:
        user: The user to check
        resource: The resource name (e.g., "users", "roles")
        action: The action name (e.g., "create", "read", "update", "delete", "list")

    Returns:
        True if user has the permission, False otherwise

    Example:
        if user_has_permission(current_user, "users", "delete"):
            # Perform deletion
            ...
    """
    for role in user.roles:
        if not role.is_active:
            continue
        for permission in role.permissions:
            if permission.is_active and permission.resource == resource and permission.action == action:
                return True
    return False


def user_has_any_permission(user: User, *permissions: tuple[str, str]) -> bool:
    """
    Check if a user has any of the specified permissions.

    Args:
        user: The user to check
        *permissions: Variable number of (resource, action) tuples

    Returns:
        True if user has at least one of the permissions, False otherwise

    Example:
        if user_has_any_permission(current_user, ("users", "read"), ("users", "list")):
            # Show user list
            ...
    """
    user_permissions = get_user_permissions(user)
    return any((resource, action) in user_permissions for resource, action in permissions)


def user_has_all_permissions(user: User, *permissions: tuple[str, str]) -> bool:
    """
    Check if a user has all of the specified permissions.

    Args:
        user: The user to check
        *permissions: Variable number of (resource, action) tuples

    Returns:
        True if user has all permissions, False otherwise

    Example:
        if user_has_all_permissions(current_user, ("users", "update"), ("roles", "update")):
            # Allow complex operation
            ...
    """
    user_permissions = get_user_permissions(user)
    return all((resource, action) in user_permissions for resource, action in permissions)


def get_user_permissions(user: User) -> set[tuple[str, str]]:
    """
    Get all permissions for a user as (resource, action) tuples.

    Args:
        user: The user to get permissions for

    Returns:
        Set of (resource, action) tuples representing all active permissions
        from all active roles assigned to the user

    Example:
        permissions = get_user_permissions(current_user)
        if ("users", "delete") in permissions:
            # User can delete
            ...
    """
    permissions = set()
    for role in user.roles:
        if not role.is_active:
            continue
        for permission in role.permissions:
            if permission.is_active:
                permissions.add((permission.resource, permission.action))
    return permissions


def user_has_role(user: User, *role_names: str) -> bool:
    """
    Check if a user has any of the specified roles.

    Args:
        user: The user to check
        *role_names: Variable number of role names

    Returns:
        True if user has at least one of the specified roles, False otherwise

    Example:
        if user_has_role(current_user, "admin", "superuser"):
            # Show admin features
            ...
    """
    user_role_names = {role.name for role in user.roles if role.is_active}
    return any(role_name in user_role_names for role_name in role_names)
