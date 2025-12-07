"""Database configuration module.

This module sets up the SQLAlchemy database configuration and plugin
for the Litestar application using async SQLAlchemy support.
"""

from advanced_alchemy.config import AsyncSessionConfig
from advanced_alchemy.extensions.litestar import (
    AlembicAsyncConfig,
    EngineConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)

from app.config import Settings, settings


def create_sqlalchemy_config(
    app_settings: Settings | None = None,
    pool_size: int | None = None,
    max_overflow: int | None = None,
) -> SQLAlchemyAsyncConfig:
    """Create SQLAlchemy configuration with the given settings.

    Args:
        app_settings: Settings instance to use. If None, uses global settings.
        pool_size: Size of the connection pool. If None, uses SQLAlchemy default.
        max_overflow: Maximum overflow size. If None, uses SQLAlchemy default.

    Returns:
        SQLAlchemy async configuration instance

    """
    if app_settings is None:
        app_settings = settings

    engine_config_kwargs: dict = {"echo": False}
    if pool_size is not None:
        engine_config_kwargs["pool_size"] = pool_size
    if max_overflow is not None:
        engine_config_kwargs["max_overflow"] = max_overflow

    return SQLAlchemyAsyncConfig(
        connection_string=app_settings.database_url.unicode_string(),
        engine_config=EngineConfig(**engine_config_kwargs),
        session_config=AsyncSessionConfig(expire_on_commit=False),
        before_send_handler="autocommit",
        alembic_config=AlembicAsyncConfig(
            toml_file="pyproject.toml",
        ),
    )


def create_sqlalchemy_plugin(
    app_settings: Settings | None = None,
    pool_size: int | None = None,
    max_overflow: int | None = None,
) -> SQLAlchemyPlugin:
    """Create SQLAlchemy plugin with the given settings.

    Args:
        app_settings: Settings instance to use. If None, uses global settings.
        pool_size: Size of the connection pool. If None, uses SQLAlchemy default.
        max_overflow: Maximum overflow size. If None, uses SQLAlchemy default.

    Returns:
        SQLAlchemy plugin instance (config accessible via plugin.config[0])

    """
    config = create_sqlalchemy_config(app_settings, pool_size=pool_size, max_overflow=max_overflow)
    return SQLAlchemyPlugin(config=config)


sqlalchemy_config = create_sqlalchemy_config()
