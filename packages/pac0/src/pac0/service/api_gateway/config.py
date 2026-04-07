# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
        env_prefix="PAC0_PROXY_",
        env_nested_delimiter="__",
        nested_model_conversion=True,
    )

    json_schema: str = Field(
        default="https://raw.githubusercontent.com/entzmann/pac0/main/packages/pac0/src/pac0/service/api_gateway/config.schema.json",
        description="JSON schema for configuration validation",
        exclude=True,
        alias="$schema",
    )

    proxy: ProxyConfig = Field(
        default_factory=ProxyConfig, description="Proxy configuration"
    )

    @classmethod
    def load_from_yaml(cls, config_path: str = "pac0_proxy.conf.yaml") -> "Settings":
        """Load settings from a YAML configuration file."""
        path = Path(config_path)
        if not path.exists():
            return cls()

        import yaml

        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}

        # Merge environment variables into config
        settings = cls(**data)
        return settings
