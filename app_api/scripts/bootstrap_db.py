import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.accounts.users.services import password_hasher
from app.db import sqlalchemy_config
from app.models.accounts import Permission, Role, User

DEFAULT_USERNAME = "admin"
DEFAULT_FULLNAME = "Administrator"
DEFAULT_PASSWORD = "admin"
DEFAULT_ROLE = "admin"

# Standard permissions available for assignment to other roles
STANDARD_PERMISSIONS = [
    # Users
    ("users:list", "users", "list", "List all users"),
    ("users:read", "users", "read", "View user details"),
    ("users:create", "users", "create", "Create new users"),
    ("users:update", "users", "update", "Update user information"),
    ("users:delete", "users", "delete", "Delete users"),
    # Roles
    ("roles:list", "roles", "list", "List all roles"),
    ("roles:read", "roles", "read", "View role details"),
    ("roles:create", "roles", "create", "Create new roles"),
    ("roles:update", "roles", "update", "Update role information"),
    ("roles:delete", "roles", "delete", "Delete roles"),
    # Permissions
    ("permissions:list", "permissions", "list", "List all permissions"),
    ("permissions:read", "permissions", "read", "View permission details"),
    ("permissions:create", "permissions", "create", "Create new permissions"),
    ("permissions:update", "permissions", "update", "Update permission information"),
    ("permissions:delete", "permissions", "delete", "Delete permissions"),
]


async def main():
    async with sqlalchemy_config.get_session() as session:
        existing_users = await session.scalar(select(func.count(User.id)))

        if existing_users == 0:
            await bootstrap_db(session)
        else:
            print(f"Database already contains {existing_users} user(s). Skipping bootstrap.")


async def bootstrap_db(session: AsyncSession):
    print("Bootstrapping database with default user and role...")

    # Create all standard permissions for use with other roles
    for name, resource, action, description in STANDARD_PERMISSIONS:
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description,
        )
        session.add(permission)

    print(f"Created {len(STANDARD_PERMISSIONS)} standard permissions")

    # Create admin role (no permissions needed - has full access by default)
    role = Role(
        name=DEFAULT_ROLE,
        description="Administrator role",
    )
    session.add(role)
    print(f"Created role '{DEFAULT_ROLE}' (full access)")

    # Create admin user with admin role
    user = User(
        username=DEFAULT_USERNAME,
        fullname=DEFAULT_FULLNAME,
        password=password_hasher.hash(DEFAULT_PASSWORD),
        roles=[role],
    )
    session.add(user)
    print(f"Created user '{DEFAULT_USERNAME}' with role '{DEFAULT_ROLE}'")

    await session.commit()
    print("Database bootstrap completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
