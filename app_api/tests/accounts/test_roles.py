"""Tests for role management functionality.

This module contains integration tests for role creation and management.
"""

from uuid import uuid4

import pytest
from litestar.testing.client import AsyncTestClient

from tests.accounts.conftest import TEST_PERMISSIONS, TEST_ROLES


@pytest.mark.asyncio
async def test_create_role(authenticated_client: AsyncTestClient) -> None:
    """Test successful role creation."""
    role_data = {"name": "new_role", "description": "New role", "permissions": []}
    response = await authenticated_client.post("/accounts/roles/", json=role_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "new_role"
    assert data["description"] == "New role"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_list_roles(authenticated_client: AsyncTestClient) -> None:
    """Test listing roles endpoint."""
    response = await authenticated_client.get("/accounts/roles/")

    assert response.status_code == 200
    roles_list = response.json()
    assert isinstance(roles_list, list)
    assert len(roles_list) > 0  # Should have some roles

    # Check that roles have proper structure
    for role in roles_list:
        assert "id" in role
        assert "name" in role
        assert "is_active" in role
        assert "created_at" in role
        assert isinstance(role["is_active"], bool)


@pytest.mark.asyncio
async def test_get_role_by_id(authenticated_client: AsyncTestClient) -> None:
    """Test retrieving a specific role by ID."""
    test_role = TEST_ROLES["admin"]

    response = await authenticated_client.get(f"/accounts/roles/{test_role['id']}")

    assert response.status_code == 200
    role_data = response.json()
    for key in ["id", "name", "is_active", "created_at"]:
        assert key in role_data


@pytest.mark.asyncio
async def test_update_role(authenticated_client: AsyncTestClient) -> None:
    """Test updating a role."""
    test_role = TEST_ROLES["guest"]

    # Update the role
    update_data = {"name": "updated_name", "description": "Updated description", "is_active": False}
    response = await authenticated_client.patch(f"/accounts/roles/{test_role['id']}", json=update_data)

    assert response.status_code == 200
    updated_role = response.json()
    for key, value in update_data.items():
        assert updated_role[key] == value

    # Get the updated role to verify changes
    get_response = await authenticated_client.get(f"/accounts/roles/{test_role['id']}")
    assert get_response.status_code == 200
    get_role_data = get_response.json()
    for key, value in update_data.items():
        assert get_role_data[key] == value


@pytest.mark.asyncio
async def test_create_role_with_permissions(client_with_permissions: AsyncTestClient) -> None:
    """Roles can be created with associated permissions."""
    permission = TEST_PERMISSIONS["view_users"]

    role_payload = {
        "name": f"role-{uuid4().hex[:8]}",
        "description": "Role with permissions",
        "permissions": [{"id": permission["id"]}],
    }

    response = await client_with_permissions.post("/accounts/roles/", json=role_payload)

    assert response.status_code == 201
    created_role = response.json()
    assert created_role["name"] == role_payload["name"]
    assert created_role["permissions"], "Expected permissions to be returned in payload"
    returned_permission = created_role["permissions"][0]
    assert returned_permission["id"] == permission["id"]
    assert returned_permission["name"] == permission["name"]


@pytest.mark.asyncio
async def test_update_role_permissions(client_with_permissions: AsyncTestClient) -> None:
    """Roles can update their permission assignments."""
    initial_permission = TEST_PERMISSIONS["view_users"]
    new_permission = TEST_PERMISSIONS["manage_roles"]

    role_payload = {
        "name": f"role-update-{uuid4().hex[:8]}",
        "description": "Role to update permissions",
        "permissions": [{"id": initial_permission["id"]}],
    }

    create_response = await client_with_permissions.post("/accounts/roles/", json=role_payload)
    role_id = create_response.json()["id"]

    update_payload = {
        "permissions": [{"id": new_permission["id"]}],
    }

    update_response = await client_with_permissions.patch(f"/accounts/roles/{role_id}", json=update_payload)

    assert update_response.status_code == 200
    updated_role = update_response.json()
    assert len(updated_role["permissions"]) == 1
    assert updated_role["permissions"][0]["id"] == new_permission["id"]

    fetch_response = await client_with_permissions.get(f"/accounts/roles/{role_id}")
    assert fetch_response.status_code == 200
    fetched_role = fetch_response.json()
    fetched_permission_ids = {permission["id"] for permission in fetched_role["permissions"]}
    assert fetched_permission_ids == {new_permission["id"]}
