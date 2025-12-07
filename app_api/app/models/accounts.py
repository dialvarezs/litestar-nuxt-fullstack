"""Account-related database models.

This module defines the database models for user authentication and authorization,
including User, Role, and UserRole association models.
"""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from uuid import UUID  # noqa: TC003

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes, UUIDv7AuditBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(UUIDv7AuditBase):
    """User model for authentication and user management."""

    __tablename__ = "accounts_users"

    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    fullname: Mapped[str]
    password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")
    last_login: Mapped[datetime | None]

    roles: Mapped[list[Role]] = relationship(
        secondary="accounts_users_roles",
        back_populates="users",
        lazy="selectin",
        order_by="Role.name",
    )


class Role(UUIDv7AuditBase):
    """Role model for role-based access control."""

    __tablename__ = "accounts_roles"

    name: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    description: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")

    users: Mapped[list[User]] = relationship(
        secondary="accounts_users_roles",
        back_populates="roles",
        lazy="noload",
    )
    permissions: Mapped[list[Permission]] = relationship(
        secondary="accounts_roles_permissions",
        back_populates="roles",
        lazy="selectin",
        order_by="Permission.name",
    )


class UserRole(CommonTableAttributes, AdvancedDeclarativeBase, AsyncAttrs):
    """Association model for User-Role many-to-many relationship."""

    __tablename__ = "accounts_users_roles"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("accounts_users.id"), primary_key=True)
    role_id: Mapped[UUID] = mapped_column(ForeignKey("accounts_roles.id"), primary_key=True)


class Permission(UUIDv7AuditBase):
    """Permission model for granular access control."""

    __tablename__ = "accounts_permissions"

    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    resource: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(32), index=True)
    description: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, server_default="1")

    roles: Mapped[list[Role]] = relationship(
        secondary="accounts_roles_permissions",
        back_populates="permissions",
        lazy="noload",
    )


class RolePermission(CommonTableAttributes, AdvancedDeclarativeBase, AsyncAttrs):
    """Association model for Role-Permission many-to-many relationship."""

    __tablename__ = "accounts_roles_permissions"

    role_id: Mapped[UUID] = mapped_column(ForeignKey("accounts_roles.id"), primary_key=True)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("accounts_permissions.id"), primary_key=True)
