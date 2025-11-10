"""
Application configuration module.

This module defines the application settings using Pydantic BaseSettings
for configuration management with support for TOML files.
"""

from pathlib import Path

from pydantic import AnyUrl, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class Settings(BaseSettings):
    """
    Application settings configuration class.

    Manages all configuration values for the application including database,
    security, and CORS settings. Values can be loaded from TOML files,
    environment variables, or use default values.
    """

    model_config = SettingsConfigDict(
        extra="ignore",
    )

    debug: bool = False
    database_url: AnyUrl = AnyUrl("postgresql+asyncpg:///appdb")
    secret_key: SecretStr = SecretStr("secret")
    cors_allowed_origins: list[str] = ["http://localhost:3000"]
    superuser_role_name: str = "admin"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize the sources for settings loading.

        Prioritizes TOML config file, then init settings, then environment variables.

        Returns:
            Tuple of settings sources in priority order
        """
        return (
            TomlConfigSettingsSource(settings_cls, toml_file=Path("config.toml").resolve()),
            init_settings,
            env_settings,
        )


# Global settings instance
settings = Settings()
