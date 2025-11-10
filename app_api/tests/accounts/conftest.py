"""
Fixtures and test data for accounts module.

This module contains reusable test data and fixtures specific to accounts functionality.
"""

from collections.abc import AsyncIterator
from typing import Any

import pytest_asyncio
from litestar.testing.client import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.api.accounts.users.services import password_hasher
from app.models.accounts import Permission, Role, User

TEST_ROLES = {
    "admin": {
        "id": "00000011-89ab-cdef-0123-456789abcdef",
        "name": "admin",
        "description": "Administrator role",
    },
    "user": {
        "id": "00000011-89ab-cdef-0123-456789abcde0",
        "name": "user",
        "description": "Regular user role",
    },
    "guest": {
        "id": "00000011-89ab-cdef-0123-456789abcde1",
        "name": "guest",
        "description": None,
    },  # No description
}

TEST_USERS = {
    "admin": {
        "id": "00000012-89ab-cdef-0123-456789abcdef",
        "username": "admin_user",
        "email": "admin@example.com",
        "fullname": "Admin User",
        "password": "admin123",
        "roles": ["admin"],
    },
    "regular": {
        "id": "00000012-89ab-cdef-0123-456789abcde0",
        "username": "regular_user",
        "email": "user@example.com",
        "fullname": "Regular User",
        "password": "user123",
        "roles": ["user"],
    },
    "multi": {
        "id": "00000012-89ab-cdef-0123-456789abcde1",
        "username": "multi_role_user",
        "email": "multi@example.com",
        "fullname": "Multi Role User",
        "password": "multi123",
        "roles": ["user", "admin"],
    },
}

TEST_PERMISSIONS = {
    "view_users": {
        "id": "00000013-89ab-cdef-0123-456789abcdef",
        "name": "users:view",
        "resource": "users",
        "action": "view",
        "description": "Allow viewing users",
    },
    "manage_roles": {
        "id": "00000013-89ab-cdef-0123-456789abcde0",
        "name": "roles:manage",
        "resource": "roles",
        "action": "manage",
        "description": "Allow managing roles",
    },
}


async def _populate_roles(engine: Any) -> None:
    """Add test roles to database."""
    from uuid import UUID

    async with AsyncSession(engine) as session:
        roles = [
            Role(id=UUID(str(role["id"])), name=str(role["name"]), description=role["description"])
            for role in TEST_ROLES.values()
        ]
        session.add_all(roles)
        await session.commit()


async def _populate_accounts(engine: Any) -> None:
    """Add test users and roles to database."""
    from uuid import UUID

    async with AsyncSession(engine) as session:
        # Create roles first
        role_objects: dict[str, Role] = {}
        for role_data in TEST_ROLES.values():
            role = Role(
                id=UUID(str(role_data["id"])), name=role_data["name"], description=role_data["description"]
            )
            session.add(role)
            role_name = str(role_data["name"])
            role_objects[role_name] = role

        await session.flush()  # Get role IDs

        # Create users with roles
        for user_data in TEST_USERS.values():
            user_role_names = user_data["roles"]
            assert isinstance(user_role_names, list)
            user_roles = [role_objects[str(role_name)] for role_name in user_role_names]
            user = User(
                id=UUID(str(user_data["id"])),
                username=str(user_data["username"]),
                email=str(user_data["email"]),
                fullname=str(user_data["fullname"]),
                password=password_hasher.hash(str(user_data["password"])),
                roles=user_roles,
            )
            session.add(user)

        await session.commit()


async def _populate_permissions(engine: Any) -> None:
    """Add test permissions to database."""
    from uuid import UUID

    async with AsyncSession(engine) as session:
        permissions = [
            Permission(
                id=UUID(str(permission["id"])),
                name=str(permission["name"]),
                resource=str(permission["resource"]),
                action=str(permission["action"]),
                description=permission["description"],
            )
            for permission in TEST_PERMISSIONS.values()
        ]
        session.add_all(permissions)
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def client_with_roles(
    client: AsyncTestClient, session_database: dict[str, str]
) -> AsyncIterator[AsyncTestClient]:
    """Create a test client with pre-populated roles."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        await _populate_roles(engine)
        yield client
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client_with_accounts(
    client: AsyncTestClient, session_database: dict[str, str]
) -> AsyncIterator[AsyncTestClient]:
    """Create a test client with pre-populated users and roles."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        await _populate_accounts(engine)
        yield client
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def authenticated_client(
    client: AsyncTestClient, session_database: dict[str, str]
) -> AsyncIterator[AsyncTestClient]:
    """Create a test client with pre-populated users and roles, and authenticate a user."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        await _populate_accounts(engine)

        # Log in a test user to authenticate the client
        test_user = TEST_USERS["admin"]
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"],
        }

        # Login to set the JWT token in a cookie
        await client.post(
            "/accounts/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client_with_permissions(
    authenticated_client: AsyncTestClient, session_database: dict[str, str]
) -> AsyncIterator[AsyncTestClient]:
    """Create a test client with pre-populated users, roles, and permissions."""

    engine = create_async_engine(session_database["url"], echo=False)
    try:
        await _populate_permissions(engine)
        yield authenticated_client
    finally:
        await engine.dispose()
