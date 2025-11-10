"""
Tests for authentication functionality.

This module contains integration tests for login and logout operations.
"""

import pytest
from litestar.testing.client import AsyncTestClient

from .conftest import TEST_USERS


@pytest.mark.asyncio
async def test_login_success(client_with_accounts: AsyncTestClient) -> None:
    """Test successful user login."""
    test_user = TEST_USERS["admin"]
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }

    response = await client_with_accounts.post(
        "/accounts/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == 200
    data = response.json()

    # Should return token information
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"

    # Should set authentication cookie
    assert "token" in response.cookies


@pytest.mark.parametrize(
    "username,password,expected_status,error_message",
    [
        ("nonexistent_user", "anypassword", 401, "Invalid username or password"),
        ("admin_user", "wrong_password", 401, "Invalid username or password"),
    ],
    ids=["invalid_username", "invalid_password"],
)
@pytest.mark.asyncio
async def test_login_invalid_credentials(
    client_with_accounts: AsyncTestClient,
    username: str,
    password: str,
    expected_status: int,
    error_message: str,
) -> None:
    """Test login with invalid credentials."""
    login_data = {"username": username, "password": password}

    response = await client_with_accounts.post(
        "/accounts/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert response.status_code == expected_status
    error_data = response.json()
    assert error_message in error_data["detail"]


@pytest.mark.parametrize(
    "login_data,expected_status",
    [
        ({"password": "somepassword"}, 500),
        ({"username": "someuser"}, 500),
    ],
    ids=["missing_username", "missing_password"],
)
@pytest.mark.asyncio
async def test_login_missing_credentials(
    client_with_accounts: AsyncTestClient, login_data: dict, expected_status: int
) -> None:
    """Test login with missing credentials."""
    response = await client_with_accounts.post(
        "/accounts/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_logout(authenticated_client: AsyncTestClient) -> None:
    """Test user logout."""
    response = await authenticated_client.post("/accounts/auth/logout")

    assert response.status_code == 200

    # Check that token cookie is deleted/cleared
    # The response should either not have a token cookie or have one marked for deletion
    if "token" in response.cookies:
        # Cookie should be marked for deletion (empty value or expired)
        token_cookie = response.cookies["token"]
        assert token_cookie == "" or "expires" in str(response.cookies)


@pytest.mark.asyncio
async def test_login_updates_last_login(authenticated_client: AsyncTestClient) -> None:
    """Test that successful login updates the last_login timestamp."""
    test_user_data = TEST_USERS["admin"]

    # Get current last_login for the test user
    response = await authenticated_client.get(f"/accounts/users/{test_user_data['id']}")
    test_user = response.json()
    original_last_login = test_user.get("last_login")

    # Login again to trigger last_login update
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"],
    }

    login_response = await authenticated_client.post(
        "/accounts/auth/login", data=login_data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    assert login_response.status_code == 200

    # Check that last_login was updated using authenticated client
    updated_user_response = await authenticated_client.get(f"/accounts/users/{test_user['id']}")
    updated_user = updated_user_response.json()
    assert updated_user["last_login"] != original_last_login


@pytest.mark.parametrize(
    "request_method,expected_status_range",
    [
        ("json", [400, 415, 422, 500]),
        ("form", [200]),
    ],
    ids=["json_content_type", "form_content_type"],
)
@pytest.mark.asyncio
async def test_login_with_different_content_types(
    client_with_accounts: AsyncTestClient, request_method: str, expected_status_range: list[int]
) -> None:
    """Test that login only works with correct content type."""
    # Create a test user
    test_user = TEST_USERS["regular"]
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }

    if request_method == "json":
        response = await client_with_accounts.post("/accounts/auth/login", json=login_data)
    else:  # form
        response = await client_with_accounts.post(
            "/accounts/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    assert response.status_code in expected_status_range
