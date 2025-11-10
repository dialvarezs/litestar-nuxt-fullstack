"""
Database configuration module.

This module sets up the SQLAlchemy database configuration and plugin
for the Litestar application using async SQLAlchemy support.
"""

from advanced_alchemy.config import AsyncSessionConfig
from advanced_alchemy.extensions.litestar import (
    EngineConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyPlugin,
)

from app.config import Settings, settings


def create_sqlalchemy_config(app_settings: Settings | None = None) -> SQLAlchemyAsyncConfig:
    """
    Create SQLAlchemy configuration with the given settings.

    Args:
        app_settings: Settings instance to use. If None, uses global settings.

    Returns:
        SQLAlchemy async configuration instance
    """
    if app_settings is None:
        app_settings = settings

    return SQLAlchemyAsyncConfig(
        connection_string=app_settings.database_url.unicode_string(),
        engine_config=EngineConfig(echo=False),
        session_config=AsyncSessionConfig(expire_on_commit=False),
        before_send_handler="autocommit",
    )


def create_sqlalchemy_plugin(app_settings: Settings | None = None) -> SQLAlchemyPlugin:
    """
    Create SQLAlchemy plugin with the given settings.

    Args:
        app_settings: Settings instance to use. If None, uses global settings.

    Returns:
        SQLAlchemy plugin instance (config accessible via plugin.config[0])
    """
    config = create_sqlalchemy_config(app_settings)
    return SQLAlchemyPlugin(config=config)


sqlalchemy_config = create_sqlalchemy_config()
