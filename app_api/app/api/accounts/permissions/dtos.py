"""Permission data transfer objects (DTOs)."""

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig

from app.models.accounts import Permission


class PermissionDTO(SQLAlchemyDTO[Permission]):
    """DTO for reading permission data."""

    config = SQLAlchemyDTOConfig(exclude={"roles"})


class PermissionCreateDTO(PermissionDTO):
    """DTO for creating permissions."""

    config = SQLAlchemyDTOConfig(include={"name", "resource", "action", "description", "is_active"})


class PermissionUpdateDTO(PermissionDTO):
    """DTO for updating permissions."""

    config = SQLAlchemyDTOConfig(
        include={"name", "resource", "action", "description", "is_active"},
        partial=True,
    )
