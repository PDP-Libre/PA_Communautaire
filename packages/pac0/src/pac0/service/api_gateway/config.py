# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later
import logging
import os
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class UpstreamConfig(BaseModel):
    """Configuration for upstream API endpoint."""

    endpoint: str = Field(..., description="Upstream API endpoint URL")
    api_key: Optional[str] = Field(
        None, description="API key for upstream authentication"
    )


class StoreConfig(BaseModel):
    """Configuration for request storage backend."""

    backend: str = Field(default="file", description="Storage backend type")
    path: str = Field(default="/var/pac0/proxy/store/", description="Storage path")


class ProxyConfig(BaseModel):
    """Configuration for the proxy service."""

    enabled: bool = Field(default=False, description="Enable proxy mode")
    port: int = Field(default=8080, description="Proxy server port")
    upstream: UpstreamConfig = Field(
        default_factory=lambda: UpstreamConfig(endpoint=""),
        description="Upstream API configuration",
    )
    store: StoreConfig = Field(
        default_factory=StoreConfig, description="Storage configuration"
    )


class Settings(BaseSettings):
    """Main application settings loaded from configuration file."""

    model_config = SettingsConfigDict(
        env_prefix="PAC0_",
        env_nested_delimiter="__",
        nested_model_conversion=True,
    )

    json_schema: str = Field(
        default="https://raw.githubusercontent.com/entzmann/pac0/main/packages/pac0/src/pac0/service/api_gateway/config.schema.json",
        description="JSON schema for configuration validation",
        exclude=True,
        alias="$schema",
    )
    log_level: str = "INFO"
    proxy: ProxyConfig = Field(
        default_factory=ProxyConfig, description="Proxy configuration"
    )

    @classmethod
    def load_from_yaml(cls, config_path: Path) -> "Settings":
        """Load settings from a YAML configuration file."""
        with config_path.open() as f:
            data = yaml.safe_load(f) or {}
        logger.info(f"Configuration file found at {config_path}")
        # Reminder: environment variables will be merged into config
        settings = cls(**data)
        return settings

    @classmethod
    def load(cls) -> "Settings":
        """
        Load settings from those location (first match win):
        - PAC0_CONF_PATH environment variable
        - ./pac0.conf.yaml
        - ~/.config/pac0/pac0.conf.yaml
        - /etc/pac0/pac0.conf.yaml
        Each value from the conf is merged with environment variables PAC0_*.
        """
        locations = []
        if conf_path := os.environ.get("PAC0_CONF_PATH"):
            locations.append(conf_path)
        locations.extend(
            [
                "./pac0.conf.yaml",
                "~/.config/pac0/pac0.conf.yaml",
                "/etc/pac0/pac0.conf.yaml",
            ]
        )
        for location in locations:
            locationPath = Path(location).expanduser().resolve()
            if locationPath.exists():
                return cls.load_from_yaml(locationPath)
            else:
                logger.warning(
                    f"Configuration file not found at {location} -> {locationPath}"
                )
        return cls()
