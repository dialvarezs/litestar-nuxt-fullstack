"""Test configuration and fixtures for pytest."""

from collections.abc import AsyncIterator
from typing import cast

import pytest
import pytest_asyncio
from litestar.testing.client import AsyncTestClient
from pytest_databases.docker.postgres import PostgresService
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from app.config import Settings

pytest_plugins = ["pytest_databases.docker.postgres"]


@pytest_asyncio.fixture(scope="session")
async def session_database(
    postgres_service: PostgresService,
    postgres_user: str,
    postgres_password: str,
    request: pytest.FixtureRequest,
) -> AsyncIterator[dict[str, str]]:
    """Create a session-scoped database per worker."""
    import os

    from app.db import sqlalchemy_config

    # Create test database URL with unique database name
    worker_id = getattr(request.config, "workerinput", {}).get("workerid", "main")
    db_name = f"session_db_{worker_id}_{os.getpid()}"
    base_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@localhost:{postgres_service.port}"
    test_db_url = f"{base_url}/{db_name}"

    # Connect to default postgres db to create our session test database
    default_engine = create_async_engine(
        f"{base_url}/postgres",
        echo=False,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        async with default_engine.connect() as conn:
            await conn.execute(text(f"CREATE DATABASE {db_name}"))
    finally:
        await default_engine.dispose()

    # Create database tables
    engine = create_async_engine(test_db_url, echo=False, poolclass=NullPool)
    try:
        async with engine.begin() as conn:
            assert sqlalchemy_config.metadata is not None
            await conn.run_sync(sqlalchemy_config.metadata.create_all)
    finally:
        await engine.dispose()

    # Yield the database info for the session
    yield {"url": test_db_url, "db_name": db_name, "base_url": base_url}

    # Drop the session test database
    cleanup_engine = create_async_engine(
        f"{base_url}/postgres",
        echo=False,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    try:
        async with cleanup_engine.connect() as conn:
            # Terminate connections to the test database first
            await conn.execute(
                text(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{db_name}' AND pid <> pg_backend_pid()
            """),
            )
            await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
    finally:
        await cleanup_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def clean_database(session_database: dict[str, str]) -> AsyncIterator[None]:
    """Clean database between tests by truncating all tables.

    Uses two engines to avoid connection leaks:
    1. terminator_engine: Kills orphaned connections to test DB (connects to postgres db)
    2. clean_engine: Performs TRUNCATE operations (connects to test db)
    """
    from app.db import sqlalchemy_config

    terminator_engine = create_async_engine(
        f"{session_database['base_url']}/postgres",
        echo=False,
        isolation_level="AUTOCOMMIT",
        poolclass=NullPool,
    )
    clean_engine = create_async_engine(session_database["url"], echo=False, poolclass=NullPool)

    try:
        # Terminate stray connections from previous tests to prevent connection pool exhaustion
        async with terminator_engine.connect() as conn:
            query = (
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{session_database['db_name']}' AND pid <> pg_backend_pid()"
            )
            await conn.execute(text(query))

        # Clean tables before the test
        async with clean_engine.begin() as conn:
            assert sqlalchemy_config.metadata is not None
            for table in reversed(sqlalchemy_config.metadata.sorted_tables):
                await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))

        yield

    finally:
        await clean_engine.dispose()
        await terminator_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(session_database: dict[str, str], clean_database: None) -> AsyncIterator[AsyncTestClient]:
    """Create a test client."""
    from pydantic import AnyUrl, SecretStr
    from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

    from app.main import create_app

    _ = clean_database

    class TestSettings(Settings):
        """Test-specific settings that don't use TOML config."""

        model_config = SettingsConfigDict(extra="ignore")

        @classmethod
        def settings_customise_sources(
            cls,
            _settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            _ = env_settings
            _ = dotenv_settings
            _ = file_secret_settings
            return (init_settings,)

    test_settings = cast(
        "Settings",
        TestSettings(
            database_url=AnyUrl(session_database["url"]),
            secret_key=SecretStr("test_secret_key_for_testing_only"),
            debug=True,
            cors_allowed_origins=["http://localhost:3000", "http://testserver"],
        ),
    )

    test_app = create_app(
        app_settings=test_settings,
        title="Test PM API",
        enable_structlog=False,
        pool_size=1,
        max_overflow=0,
    )

    async with AsyncTestClient(app=test_app) as test_client:
        yield test_client
