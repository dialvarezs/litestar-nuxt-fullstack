# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Litestar-based API backend for a full-stack application. Uses async SQLAlchemy with PostgreSQL, JWT authentication via OAuth2 password bearer flow, and follows a modular architecture with controllers, services, repositories, and DTOs.

## Development Commands

### Running the App
```bash
just run              # Run with auto-reload using litestar
uv run litestar run --reload
```

### Database Operations
```bash
just db <args>        # Alembic operations via Litestar CLI
uv run litestar database upgrade head
uv run litestar database revision --autogenerate -m "description"
```

### Code Quality
```bash
just format           # Format code and sort imports (ruff)
just lint             # Lint and auto-fix with ruff
just ty               # Type checking with ty
just pyrefly          # Type checking with pyrefly
```

### Testing
```bash
just test             # Run all tests with pytest
just test <args>      # Pass custom pytest arguments

# Common test patterns:
PYTHONPATH=. uv run pytest tests/accounts/test_users.py::test_name -v
PYTHONPATH=. uv run pytest tests/accounts/ -v
PYTHONPATH=. uv run pytest -v --tb=no  # No traceback for clean output
```

**Important:** Always run tests with `PYTHONPATH=.` prefix or use `just test` to ensure proper module resolution.

## Architecture

### Application Structure
- **app/main.py** - Application factory (`create_app`) that assembles Litestar app with plugins, auth, CORS, and OpenAPI
- **app/config.py** - Settings management using Pydantic with TOML config file support (`config.toml`)
- **app/db.py** - SQLAlchemy async configuration and plugin creation
- **app/models/** - SQLAlchemy ORM models using Advanced Alchemy base classes
- **app/api/** - Feature modules organized by domain (e.g., `accounts/`)

### Feature Module Pattern
Each feature follows this structure (example: `app/api/accounts/users/`):
- **controllers.py** - Litestar route handlers (HTTP layer)
- **services.py** - Business logic, validation, transformations (uses repositories)
- **repositories.py** - Data access layer (extends Advanced Alchemy repositories)
- **dtos.py** - Data Transfer Objects for request/response serialization
- **__init__.py** - Exports for clean imports

### Authentication Flow
- OAuth2 password bearer auth configured in `app/api/accounts/auth/security.py`
- `create_oauth2_auth()` sets up JWT auth with 1-day token expiration
- Token endpoint: `/accounts/auth/login`
- Excludes: `/accounts/auth/`, `/schema`
- `current_user_from_token()` retrieves authenticated user from JWT
- Password hashing uses `pwdlib` with Argon2

### Permission-Based Access Control
- Guards implemented in `app/api/accounts/auth/guards.py` enforce permission-based access control
- Available guards:
  - `has_permission(resource, action)`: Check single permission (e.g., `has_permission("users", "read")`)
  - `has_any_permission(*permissions)`: Check if user has any of the specified permissions
  - `has_all_permissions(*permissions)`: Check if user has all specified permissions
  - `has_role(*role_names)`: Check if user has any of the specified roles
- **Superuser role**: The role specified in `superuser_role_name` config (default: "admin") bypasses all permission checks
- Permissions are checked through user's active roles and their associated permissions
- Example usage:
  ```python
  @get("/users", guards=[has_permission("users", "list")])
  async def list_users() -> list[User]:
      ...
  ```

### Database Models
Located in `app/models/accounts.py`:
- **User** - Username (unique), email (unique), fullname, password (hashed), is_active, last_login
- **Role** - Name (unique), description, is_active
- **UserRole** - Association table for many-to-many User↔Role relationship

All models use UUIDv7 primary keys and audit fields (created_at, updated_at) via `UUIDv7AuditBase`.

### Service Layer Patterns
Services (like `UserService`) extend `SQLAlchemyAsyncRepositoryService`:
- Handle business logic and validation
- Transform data between DTOs and models
- May depend on other services (e.g., `UserService` depends on `RoleService`)
- Dependency injection via `provide_*_service()` functions

Example: `UserService.create_user_with_roles()` validates roles exist, hashes password, then creates user.

### Testing Setup
- Uses `pytest-databases` with Docker PostgreSQL for test database
- Session-scoped database per worker (supports parallel testing with `pytest-xdist`)
- Function-scoped `clean_database` fixture truncates tables between tests
- `client` fixture provides `AsyncTestClient` with test settings
- Test settings bypass TOML config and use in-memory configuration

**Test database lifecycle:**
1. Session fixture creates unique database per worker
2. Creates all tables from metadata
3. Clean fixture truncates tables between tests
4. Teardown drops test database

## Code Style and Organization

### Method Organization in Classes
Methods within classes must be organized with private methods at the end:

1. **Public methods first** (including `__init__`, `__str__`, etc.)
   - Constructor (`__init__`)
   - Public API methods
   - Property getters/setters

2. **Private methods last** (methods starting with `_`)
   - Helper methods (`_helper_method`)
   - Internal utilities (`_validate_something`)

**Example:**
```python
class MyService:
    def __init__(self):
        pass

    def public_method(self):
        return self._private_helper()

    async def another_public_method(self):
        pass

    # Private methods at the end
    def _private_helper(self):
        pass

    def _another_private_method(self):
        pass
```

This organization improves code readability by presenting the public interface first and implementation details last.

## Configuration

Settings loaded via `app.config.Settings`:
- Prioritizes `config.toml`, then init args, then environment variables
- Key settings:
  - `debug`: Enable debug mode
  - `database_url`: PostgreSQL connection URL
  - `secret_key`: Secret key for JWT tokens
  - `cors_allowed_origins`: List of allowed CORS origins
  - `superuser_role_name`: Name of the role that has all permissions (default: "admin")
- Access via `app.state.app_settings` in request handlers

## Database Migrations

Uses Alembic configured in `pyproject.toml`:
- Migration script location: `migrations/`
- File naming: `%Y-%m-%d_<slug>_<rev>.py`
- Run via Litestar CLI: `just db upgrade head` or `uv run litestar database upgrade head`

## Key Dependencies

- **litestar** - ASGI framework with OpenAPI, dependency injection
- **advanced-alchemy** - Enhanced SQLAlchemy repositories and services
- **pwdlib[argon2]** - Password hashing
- **asyncpg** - PostgreSQL async driver
- **pytest-databases** - Docker-based test databases
