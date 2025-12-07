"""Tests for permission-based access control guards.

This module tests that guards correctly enforce permission-based access control
across different endpoints and operations.
"""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from litestar.testing.client import AsyncTestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.api.accounts.users.services import password_hasher
from app.models.accounts import Permission, Role, User

# Test data for permission-based access control
TEST_PERMISSIONS_DATA = {
    "users:list": {"name": "users:list", "resource": "users", "action": "list"},
    "users:read": {"name": "users:read", "resource": "users", "action": "read"},
    "users:create": {"name": "users:create", "resource": "users", "action": "create"},
    "users:update": {"name": "users:update", "resource": "users", "action": "update"},
    "users:delete": {"name": "users:delete", "resource": "users", "action": "delete"},
    "roles:list": {"name": "roles:list", "resource": "roles", "action": "list"},
    "roles:create": {"name": "roles:create", "resource": "roles", "action": "create"},
}


async def _create_user_with_permissions(
    engine: AsyncEngine,
    username: str,
    password: str,
    permission_names: list[str],
) -> tuple[User, str]:
    """Create a user with specific permissions."""
    async with AsyncSession(engine) as session:
        # Create permissions
        permissions = []
        for perm_name in permission_names:
            perm_data = TEST_PERMISSIONS_DATA[perm_name]
            permission = Permission(
                name=perm_data["name"],
                resource=perm_data["resource"],
                action=perm_data["action"],
                is_active=True,
            )
            session.add(permission)
            permissions.append(permission)

        # Create role with permissions
        role = Role(name=f"{username}_role", description="Test role", is_active=True, permissions=permissions)
        session.add(role)

        # Create user with role
        user = User(
            username=username,
            email=f"{username}@test.com",
            fullname=f"Test {username}",
            password=password_hasher.hash(password),
            is_active=True,
            roles=[role],
        )
        session.add(user)

        await session.commit()
        await session.refresh(user)

        return user, password


@pytest_asyncio.fixture(scope="function")
async def client_with_list_permission(
    client: AsyncTestClient,
    session_database: dict[str, str],
) -> AsyncIterator[AsyncTestClient]:
    """Create authenticated client with only users:list permission."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        user, password = await _create_user_with_permissions(
            engine,
            "list_user",
            "password123",
            ["users:list"],
        )

        # Authenticate
        await client.post(
            "/accounts/auth/login",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client_with_read_permission(
    client: AsyncTestClient,
    session_database: dict[str, str],
) -> AsyncIterator[AsyncTestClient]:
    """Create authenticated client with only users:read permission."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        user, password = await _create_user_with_permissions(
            engine,
            "read_user",
            "password123",
            ["users:read"],
        )

        # Authenticate
        await client.post(
            "/accounts/auth/login",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client_with_create_permission(
    client: AsyncTestClient,
    session_database: dict[str, str],
) -> AsyncIterator[AsyncTestClient]:
    """Create authenticated client with only users:create permission."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        user, password = await _create_user_with_permissions(
            engine,
            "create_user",
            "password123",
            ["users:create"],
        )

        # Authenticate
        await client.post(
            "/accounts/auth/login",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client_with_full_user_permissions(
    client: AsyncTestClient,
    session_database: dict[str, str],
) -> AsyncIterator[AsyncTestClient]:
    """Create authenticated client with all user permissions."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        user, password = await _create_user_with_permissions(
            engine,
            "full_user",
            "password123",
            ["users:list", "users:read", "users:create", "users:update", "users:delete"],
        )

        # Authenticate
        await client.post(
            "/accounts/auth/login",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client_with_no_permissions(
    client: AsyncTestClient,
    session_database: dict[str, str],
) -> AsyncIterator[AsyncTestClient]:
    """Create authenticated client with no permissions."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        user, password = await _create_user_with_permissions(engine, "no_perms_user", "password123", [])

        # Authenticate
        await client.post(
            "/accounts/auth/login",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


# Tests for guards blocking access without permissions


@pytest.mark.asyncio
async def test_list_users_denied_without_permission(client_with_no_permissions: AsyncTestClient) -> None:
    """Test that listing users is denied without users:list permission."""
    response = await client_with_no_permissions.get("/accounts/users/")

    assert response.status_code == 403
    assert "Permission denied" in response.text


@pytest.mark.asyncio
async def test_create_user_denied_without_permission(client_with_list_permission: AsyncTestClient) -> None:
    """Test that creating users is denied without users:create permission."""
    user_data = {
        "username": "newuser",
        "email": "new@test.com",
        "fullname": "New User",
        "password": "password123",
        "roles": [],
    }
    response = await client_with_list_permission.post("/accounts/users/", json=user_data)

    assert response.status_code == 403
    assert "Permission denied" in response.text


@pytest.mark.asyncio
async def test_update_user_denied_without_permission(client_with_read_permission: AsyncTestClient) -> None:
    """Test that updating users is denied without users:update permission."""
    # Use a dummy UUID
    user_id = "00000000-0000-0000-0000-000000000001"
    update_data = {"fullname": "Updated Name"}

    response = await client_with_read_permission.patch(f"/accounts/users/{user_id}", json=update_data)

    assert response.status_code == 403
    assert "Permission denied" in response.text


@pytest.mark.asyncio
async def test_delete_user_denied_without_permission(client_with_read_permission: AsyncTestClient) -> None:
    """Test that deleting users is denied without users:delete permission."""
    # Use a dummy UUID
    user_id = "00000000-0000-0000-0000-000000000001"

    response = await client_with_read_permission.delete(f"/accounts/users/{user_id}")

    assert response.status_code == 403
    assert "Permission denied" in response.text


# Tests for guards allowing access with correct permissions


@pytest.mark.asyncio
async def test_list_users_allowed_with_permission(client_with_list_permission: AsyncTestClient) -> None:
    """Test that listing users is allowed with users:list permission."""
    response = await client_with_list_permission.get("/accounts/users/")

    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)


@pytest.mark.asyncio
async def test_create_user_allowed_with_permission(client_with_create_permission: AsyncTestClient) -> None:
    """Test that creating users is allowed with users:create permission."""
    user_data = {
        "username": "newuser_allowed",
        "email": "allowed@test.com",
        "fullname": "Allowed User",
        "password": "password123",
        "roles": [],
    }
    response = await client_with_create_permission.post("/accounts/users/", json=user_data)

    assert response.status_code == 201
    created_user = response.json()
    assert created_user["username"] == user_data["username"]


@pytest.mark.asyncio
async def test_full_crud_with_all_permissions(client_with_full_user_permissions: AsyncTestClient) -> None:
    """Test that a user with all permissions can perform all CRUD operations."""
    # List users
    response = await client_with_full_user_permissions.get("/accounts/users/")
    assert response.status_code == 200

    # Create user
    user_data = {
        "username": "full_crud_user",
        "email": "fullcrud@test.com",
        "fullname": "Full CRUD User",
        "password": "password123",
        "roles": [],
    }
    response = await client_with_full_user_permissions.post("/accounts/users/", json=user_data)
    assert response.status_code == 201
    created_user = response.json()
    user_id = created_user["id"]

    # Read specific user
    response = await client_with_full_user_permissions.get(f"/accounts/users/{user_id}")
    assert response.status_code == 200
    fetched_user = response.json()
    assert fetched_user["username"] == user_data["username"]

    # Update user
    update_data = {"fullname": "Updated Full CRUD User"}
    response = await client_with_full_user_permissions.patch(f"/accounts/users/{user_id}", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["fullname"] == update_data["fullname"]

    # Delete user
    response = await client_with_full_user_permissions.delete(f"/accounts/users/{user_id}")
    assert response.status_code == 204

    # Verify user is deleted (should return 404)
    response = await client_with_full_user_permissions.get(f"/accounts/users/{user_id}")
    assert response.status_code == 404


# Tests for inactive permissions/roles


@pytest_asyncio.fixture(scope="function")
async def client_with_inactive_permission(
    client: AsyncTestClient,
    session_database: dict[str, str],
) -> AsyncIterator[AsyncTestClient]:
    """Create authenticated client with inactive permission."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        async with AsyncSession(engine) as session:
            # Create inactive permission
            permission = Permission(
                name="users:list",
                resource="users",
                action="list",
                is_active=False,  # Inactive!
            )
            session.add(permission)

            # Create role with inactive permission
            role = Role(
                name="inactive_perm_role",
                description="Test role",
                is_active=True,
                permissions=[permission],
            )
            session.add(role)

            # Create user
            user = User(
                username="inactive_perm_user",
                email="inactive@test.com",
                fullname="Inactive Permission User",
                password=password_hasher.hash("password123"),
                is_active=True,
                roles=[role],
            )
            session.add(user)

            await session.commit()

        # Authenticate
        await client.post(
            "/accounts/auth/login",
            data={"username": "inactive_perm_user", "password": "password123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_inactive_permission_denied(client_with_inactive_permission: AsyncTestClient) -> None:
    """Test that inactive permissions are not honored."""
    response = await client_with_inactive_permission.get("/accounts/users/")

    assert response.status_code == 403
    assert "Permission denied" in response.text


# Tests for different resources (roles)


@pytest_asyncio.fixture(scope="function")
async def client_with_role_permissions(
    client: AsyncTestClient,
    session_database: dict[str, str],
) -> AsyncIterator[AsyncTestClient]:
    """Create authenticated client with role permissions."""
    engine = create_async_engine(session_database["url"], echo=False)
    try:
        user, password = await _create_user_with_permissions(
            engine,
            "role_user",
            "password123",
            ["roles:list", "roles:create"],
        )

        # Authenticate
        await client.post(
            "/accounts/auth/login",
            data={"username": user.username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        yield client
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_list_roles_with_permission(client_with_role_permissions: AsyncTestClient) -> None:
    """Test that listing roles works with roles:list permission."""
    response = await client_with_role_permissions.get("/accounts/roles/")

    assert response.status_code == 200
    roles = response.json()
    assert isinstance(roles, list)


@pytest.mark.asyncio
async def test_list_roles_without_permission(client_with_list_permission: AsyncTestClient) -> None:
    """Test that listing roles is denied without roles:list permission."""
    response = await client_with_list_permission.get("/accounts/roles/")

    assert response.status_code == 403
    assert "Permission denied" in response.text
