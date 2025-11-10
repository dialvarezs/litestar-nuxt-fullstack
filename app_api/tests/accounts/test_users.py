"""
Tests for user management functionality.

This module contains integration tests for user operations.
"""

import pytest
from litestar.testing.client import AsyncTestClient

from tests.accounts.conftest import TEST_ROLES, TEST_USERS


@pytest.mark.asyncio
async def test_list_users(authenticated_client: AsyncTestClient) -> None:
    """Test listing users endpoint."""
    response = await authenticated_client.get("/accounts/users/")

    assert response.status_code == 200
    users_list = response.json()
    assert isinstance(users_list, list)
    assert len(users_list) >= 3  # Should have at least 3 test users

    # Check that users have proper structure
    for user in users_list:
        assert "id" in user
        assert "username" in user
        assert "fullname" in user
        assert "is_active" in user
        assert "created_at" in user
        assert isinstance(user["is_active"], bool)
        assert "password" not in user  # Password should not be exposed


@pytest.mark.asyncio
async def test_create_user(authenticated_client: AsyncTestClient) -> None:
    """Test successful user creation."""
    username = "new_user"
    email = "new_user@example.com"

    user_data = {
        "username": username,
        "email": email,
        "fullname": "Brand New User",
        "password": "newpass123",
        "roles": [],
    }
    response = await authenticated_client.post("/accounts/users/", json=user_data)

    assert response.status_code == 201
    data = response.json()
    for field in ["username", "email", "fullname"]:
        assert data[field] == user_data[field]
    assert data["is_active"] is True
    assert "password" not in data
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_user_with_roles(authenticated_client: AsyncTestClient) -> None:
    """Test user creation with role assignment."""
    username = "new_user_with_role"
    email = "new_user@example.com"

    user_role = TEST_ROLES["user"]

    user_data = {
        "username": username,
        "email": email,
        "fullname": "User With Role Unique",
        "password": "rolepass123",
        "roles": [{"id": user_role["id"]}],
    }
    response = await authenticated_client.post("/accounts/users/", json=user_data)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert len(data["roles"]) == 1
    assert data["roles"][0]["name"] == "user"


@pytest.mark.asyncio
async def test_get_user_by_id(authenticated_client: AsyncTestClient) -> None:
    """Test retrieving a specific user by ID."""
    test_user = TEST_USERS["admin"]

    # Get the specific user by ID
    response = await authenticated_client.get(f"/accounts/users/{test_user['id']}")

    assert response.status_code == 200
    user_data = response.json()
    assert user_data["id"] == test_user["id"]
    assert user_data["username"] == test_user["username"]
    assert user_data["fullname"] == test_user["fullname"]
    assert "password" not in user_data


@pytest.mark.asyncio
async def test_update_user(authenticated_client: AsyncTestClient) -> None:
    """Test updating a user."""
    user_to_update = TEST_USERS["regular"]

    # Update the user (include current roles to avoid issues)
    update_data = {
        "fullname": "Updated Full Name",
        "email": "updated@example.com",
        "is_active": False,
    }
    response = await authenticated_client.patch(f"/accounts/users/{user_to_update['id']}", json=update_data)

    assert response.status_code == 200
    updated_user = response.json()
    for key, value in update_data.items():
        assert updated_user[key] == value


@pytest.mark.asyncio
async def test_update_user_roles(authenticated_client: AsyncTestClient) -> None:
    """Test updating user roles."""
    user_to_update = TEST_USERS["regular"]
    admin_role = TEST_ROLES["admin"]

    # Update user to have admin role
    update_data = {"roles": [{"id": admin_role["id"]}]}
    response = await authenticated_client.patch(f"/accounts/users/{user_to_update['id']}", json=update_data)

    assert response.status_code == 200
    updated_user = response.json()
    assert len(updated_user["roles"]) == 1
    assert updated_user["roles"][0]["name"] == "admin"


@pytest.mark.parametrize(
    "username,expected_available",
    [
        (TEST_USERS["regular"]["username"], False),
        ("user_new_123", True),
    ],
    ids=["existing", "non_existing"],
)
@pytest.mark.asyncio
async def test_username_available(
    authenticated_client: AsyncTestClient,
    username: str,
    expected_available: bool,
) -> None:
    """Test username availability check."""
    response = await authenticated_client.get(f"/accounts/users/username-available?username={username}")
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is expected_available


@pytest.mark.asyncio
async def test_delete_user(authenticated_client: AsyncTestClient) -> None:
    """Test user deletion."""
    test_user = TEST_USERS["regular"]

    response = await authenticated_client.delete(f"/accounts/users/{test_user['id']}")
    assert response.status_code == 204

    get_response = await authenticated_client.get(f"/accounts/users/{test_user['id']}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_fetch_my_user(authenticated_client: AsyncTestClient) -> None:
    response = await authenticated_client.get("/accounts/users/me")

    assert response.status_code == 200

    # The authenticated user is the admin in this case
    test_user = TEST_USERS["admin"]

    data = response.json()
    assert data["username"] == test_user["username"]


@pytest.mark.asyncio
async def test_update_my_password_success(authenticated_client: AsyncTestClient) -> None:
    """Test successful password change for authenticated user."""
    test_user = TEST_USERS["admin"]

    password_data = {
        "current_password": test_user["password"],
        "new_password": "new_secure_password123",
    }

    response = await authenticated_client.post("/accounts/users/me/update-password", json=password_data)

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_my_password_wrong_current(authenticated_client: AsyncTestClient) -> None:
    """Test password change with incorrect current password."""
    password_data = {
        "current_password": "wrong_password",
        "new_password": "new_secure_password123",
    }

    response = await authenticated_client.post("/accounts/users/me/update-password", json=password_data)

    assert response.status_code == 422
    data = response.json()
    assert "Invalid current password" in data["detail"]


@pytest.mark.asyncio
async def test_update_password_unauthenticated(client_with_accounts: AsyncTestClient) -> None:
    """Test password change without authentication."""
    password_data = {
        "current_password": "any_password",
        "new_password": "new_secure_password123",
    }

    response = await client_with_accounts.post("/accounts/users/me/update-password", json=password_data)
    assert response.status_code == 401
    data = response.json()
    assert "No JWT token found" in data["detail"]
