"""Main application module for the PM API.

This module configures and initializes the Litestar application with all necessary
middleware, plugins, and routing configurations.
"""

from typing import Any

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.logging import StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin, SwaggerRenderPlugin
from litestar.openapi.spec import Server
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin

from app.api.accounts.auth.security import create_oauth2_auth
from app.api.accounts.router import accounts_router
from app.config import Settings, settings
from app.db import create_sqlalchemy_plugin


def create_app(
    app_settings: Settings | None = None,
    title: str = "App API",
    *,
    enable_structlog: bool = True,
    pool_size: int | None = None,
    max_overflow: int | None = None,
) -> Litestar:
    """Create and configure a Litestar application instance.

    This function creates a Litestar app with all necessary configurations
    including OpenAPI, CORS, authentication, and plugins. It can be used
    for both production and testing scenarios.

    Args:
        app_settings: Settings instance to use. If None, uses global settings.
        title: Title for the OpenAPI documentation
        enable_structlog: Whether to enable structlog logging plugin
        pool_size: Database connection pool size. If None, uses SQLAlchemy default.
        max_overflow: Database connection pool max overflow. If None, uses SQLAlchemy default.

    Returns:
        Configured Litestar application instance

    """
    if app_settings is None:
        app_settings = settings

    app_sqlalchemy_plugin = create_sqlalchemy_plugin(
        app_settings,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )
    app_sqlalchemy_config = app_sqlalchemy_plugin.config[0]

    openapi_config = OpenAPIConfig(
        title=title,
        version="0.1.0",
        render_plugins=[ScalarRenderPlugin(), SwaggerRenderPlugin()],
        servers=[Server(url="")],
    )

    structlog_plugin = StructlogPlugin(
        config=StructlogConfig(
            structlog_logging_config=StructLoggingConfig(
                log_exceptions="always",
                disable_stack_trace={404},
            ),
            enable_middleware_logging=app_settings.debug,
            middleware_logging_config=LoggingMiddlewareConfig(
                response_log_fields=("status_code", "cookies", "headers"),
            ),
        ),
    )

    cors_config = CORSConfig(
        allow_origins=app_settings.cors_allowed_origins,
        allow_credentials=True,
    )

    # Configure OAuth2 authentication
    oauth2_auth = create_oauth2_auth(app_settings)

    on_app_init: list[Any] = [app_sqlalchemy_plugin.on_app_init, oauth2_auth.on_app_init]
    plugins: list[Any] = [app_sqlalchemy_plugin]
    if enable_structlog:
        plugins.append(structlog_plugin)

    litestar_app = Litestar(
        route_handlers=[accounts_router],
        openapi_config=openapi_config,
        cors_config=cors_config,
        on_app_init=on_app_init,
        plugins=plugins,
        debug=app_settings.debug,
    )

    # Store config in app state
    litestar_app.state.sqlalchemy_config = app_sqlalchemy_config
    litestar_app.state.app_settings = app_settings
    litestar_app.state.oauth2_auth = oauth2_auth

    return litestar_app


app = create_app()
