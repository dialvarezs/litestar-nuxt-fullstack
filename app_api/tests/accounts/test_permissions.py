"""Integration tests for permission management endpoints."""

import pytest
from litestar.testing.client import AsyncTestClient

from tests.accounts.conftest import TEST_PERMISSIONS


def _permission_payload(name: str) -> dict[str, str | bool]:
    """Generate a basic permission payload."""

    return {
        "name": name,
        "resource": "samples",
        "action": "read",
        "description": f"Permission for {name}",
        "is_active": True,
    }


@pytest.mark.asyncio
async def test_create_and_fetch_permission(client_with_permissions: AsyncTestClient) -> None:
    """Create a permission and fetch it by ID."""

    payload = _permission_payload("perm-create")
    create_response = await client_with_permissions.post("/accounts/permissions/", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()

    for field in ("id", "name", "resource", "action", "is_active", "created_at", "updated_at"):
        assert field in created

    fetch_response = await client_with_permissions.get(f"/accounts/permissions/{created['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["id"] == created["id"]
    assert fetched["name"] == payload["name"]
    assert fetched["resource"] == payload["resource"]
    assert fetched["action"] == payload["action"]


@pytest.mark.asyncio
async def test_list_permissions(client_with_permissions: AsyncTestClient) -> None:
    """List permissions returns the existing permissions."""

    list_response = await client_with_permissions.get("/accounts/permissions/")
    assert list_response.status_code == 200

    permissions = list_response.json()
    assert isinstance(permissions, list)
    returned_ids = {permission["id"] for permission in permissions}
    expected_ids = {permission["id"] for permission in TEST_PERMISSIONS.values()}
    assert expected_ids.issubset(returned_ids)


@pytest.mark.asyncio
async def test_update_permission(client_with_permissions: AsyncTestClient) -> None:
    """Update an existing permission's details."""

    permission_id = TEST_PERMISSIONS["view_users"]["id"]

    update_payload = {
        "description": "Updated description",
        "is_active": False,
    }

    update_response = await client_with_permissions.patch(
        f"/accounts/permissions/{permission_id}", json=update_payload
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["description"] == update_payload["description"]
    assert updated["is_active"] is False

    fetch_response = await client_with_permissions.get(f"/accounts/permissions/{permission_id}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["description"] == update_payload["description"]
    assert fetched["is_active"] is False
