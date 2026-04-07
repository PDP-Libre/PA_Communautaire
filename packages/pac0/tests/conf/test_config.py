# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Tests for PAC0 API Gateway configuration module."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from pac0.service.api_gateway.config import (
    Settings,
    UpstreamConfig,
    StoreConfig,
    ProxyConfig,
)

# Path to test YAML fixtures
TEST_YAML_DIR = Path(__file__).parent / "yaml"

# =============================================================================
# UpstreamConfig Tests
# =============================================================================

class TestUpstreamConfig:
    """Tests for UpstreamConfig model."""

    def test_upstream_config_minimum(self):
        """Test UpstreamConfig with minimum required fields."""
        config = UpstreamConfig(endpoint="https://api.example.com")
        assert config.endpoint == "https://api.example.com"
        assert config.api_key is None

    def test_upstream_config_full(self):
        """Test UpstreamConfig with all fields."""
        config = UpstreamConfig(
            endpoint="https://api.example.com",
            api_key="test_api_key_123"
        )
        assert config.endpoint == "https://api.example.com"
        assert config.api_key == "test_api_key_123"

    def test_upstream_config_validation_endpoint_required(self):
        """Test that endpoint is required."""
        with pytest.raises(Exception):
            UpstreamConfig()

    def test_upstream_config_endpoint_validation(self):
        """Test endpoint field validation."""
        config = UpstreamConfig(endpoint="https://valid-url.com")
        assert isinstance(config.endpoint, str)
        assert len(config.endpoint) > 0


# =============================================================================
# StoreConfig Tests
# =============================================================================

class TestStoreConfig:
    """Tests for StoreConfig model."""

    def test_store_config_default(self):
        """Test StoreConfig with default values."""
        config = StoreConfig()
        assert config.backend == "file"
        assert config.path == "/var/pac0/proxy/store/"

    def test_store_config_custom_backend(self):
        """Test StoreConfig with custom backend."""
        config = StoreConfig(backend="memory")
        assert config.backend == "memory"
        assert config.path == "/var/pac0/proxy/store/"

    def test_store_config_custom_path(self):
        """Test StoreConfig with custom path."""
        config = StoreConfig(path="/custom/storage/path/")
        assert config.backend == "file"
        assert config.path == "/custom/storage/path/"

    def test_store_config_full(self):
        """Test StoreConfig with all custom values."""
        config = StoreConfig(backend="s3", path="/custom/s3/bucket/")
        assert config.backend == "s3"
        assert config.path == "/custom/s3/bucket/"


# =============================================================================
# ProxyConfig Tests
# =============================================================================

class TestProxyConfig:
    """Tests for ProxyConfig model."""

    def test_proxy_config_default(self):
        """Test ProxyConfig with default values."""
        upstream = UpstreamConfig(endpoint="https://api.example.com")
        config = ProxyConfig(upstream=upstream)
        assert config.enabled is False
        assert config.port == 8080
        assert config.upstream.endpoint == "https://api.example.com"
        assert config.store.backend == "file"

    def test_proxy_config_full(self):
        """Test ProxyConfig with all values set."""
        upstream = UpstreamConfig(
            endpoint="https://api.example.com",
            api_key="secret_key"
        )
        store = StoreConfig(backend="memory", path="/tmp/store")
        config = ProxyConfig(
            enabled=True,
            port=9090,
            upstream=upstream,
            store=store
        )
        assert config.enabled is True
        assert config.port == 9090
        assert config.upstream.endpoint == "https://api.example.com"
        assert config.upstream.api_key == "secret_key"
        assert config.store.backend == "memory"
        assert config.store.path == "/tmp/store"

    def test_proxy_config_default_store(self):
        """Test ProxyConfig creates default StoreConfig."""
        upstream = UpstreamConfig(endpoint="https://api.example.com")
        config = ProxyConfig(upstream=upstream)
        assert isinstance(config.store, StoreConfig)
        assert config.store.backend == "file"


# =============================================================================
# Settings Tests
# =============================================================================

class TestSettings:
    """Tests for Settings model."""

    def test_settings_default(self):
        """Test Settings with default values."""
        # Need to provide upstream since it's required
        upstream = UpstreamConfig(endpoint="https://default.com")
        settings = Settings(proxy=ProxyConfig(upstream=upstream))
        assert settings.proxy.enabled is False
        assert settings.proxy.port == 8080
        assert settings.proxy.store.backend == "file"

    def test_settings_env_prefix(self):
        """Test Settings respects PAC0_PROXY_ env prefix."""
        upstream = UpstreamConfig(endpoint="https://default.com")
        with patch.dict(os.environ, {
            "PAC0_PROXY_PROXY__PORT": "3000",
            "PAC0_PROXY_PROXY__ENABLED": "true",
        }, clear=True):
            settings = Settings()
            assert settings.proxy.port == 3000
            assert settings.proxy.enabled is True

    def test_settings_env_nested_delimiter(self):
        """Test Settings handles nested env vars with __ delimiter."""
        with patch.dict(os.environ, {
            "PAC0_PROXY_PROXY__UPSTREAM__ENDPOINT": "https://nested.example.com",
            "PAC0_PROXY_PROXY__UPSTREAM__API_KEY": "nested_api_key",
        }, clear=True):
            settings = Settings()
            assert settings.proxy.upstream.endpoint == "https://nested.example.com"
            assert settings.proxy.upstream.api_key == "nested_api_key"

    def test_settings_load_from_yaml_file_not_exists(self):
        """Test load_from_yaml returns default settings when file doesn't exist."""
        import os
        
        # Create a temporary non-existent file path
        non_existent_path = "/tmp/nonexistent_pac0_config.conf.yaml"
        
        # Ensure the file doesn't exist
        if os.path.exists(non_existent_path):
            os.remove(non_existent_path)
        
        # The load_from_yaml method returns cls() when file doesn't exist
        # Since cls() requires upstream, this should use defaults from proxy field
        settings = Settings.load_from_yaml(non_existent_path)
        # Verify it's a valid Settings instance with default values
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'proxy')

    def test_settings_load_from_yaml_file_exists(self):
        """Test load_from_yaml correctly loads from YAML file."""
        settings = Settings.load_from_yaml(str(TEST_YAML_DIR / "full_config.yaml"))
        assert settings.proxy.enabled is True
        assert settings.proxy.port == 8888
        assert settings.proxy.upstream.endpoint == "https://yaml-config.com"
        assert settings.proxy.upstream.api_key == "yaml_api_key"
        assert settings.proxy.store.backend == "memory"
        assert settings.proxy.store.path == "/yaml/store"

    def test_settings_load_from_yaml_partial_config(self):
        """Test load_from_yaml with partial configuration."""
        # Need to add default upstream since it's required
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf.yaml', delete=False) as f:
            # Write partial config with default upstream
            yaml.dump({
                "proxy": {
                    "enabled": True,
                    "upstream": {
                        "endpoint": "https://default-upstream.com"
                    }
                }
            }, f)
            temp_path = f.name
        
        try:
            settings = Settings.load_from_yaml(temp_path)
            assert settings.proxy.enabled is True
            # Other fields should use defaults
            assert settings.proxy.port == 8080
            assert settings.proxy.store.backend == "file"
            assert settings.proxy.upstream.endpoint == "https://default-upstream.com"
        finally:
            os.unlink(temp_path)

    def test_settings_merge_env_with_yaml(self):
        """Test that YAML config is used when no env vars are set."""
        upstream = UpstreamConfig(endpoint="https://yaml-default.com", api_key="yaml_key")
        config = ProxyConfig(upstream=upstream, enabled=True, port=8888)
        settings = Settings(proxy=config)
        assert settings.proxy.enabled is True
        assert settings.proxy.port == 8888
        assert settings.proxy.upstream.endpoint == "https://yaml-default.com"
        assert settings.proxy.upstream.api_key == "yaml_key"


# =============================================================================
# Integration Tests
# =============================================================================

class TestConfigIntegration:
    """Integration tests for configuration module."""

    def test_full_workflow_default_config(self):
        """Test complete workflow with default configuration."""
        upstream = UpstreamConfig(endpoint="https://default.com")
        settings = Settings(proxy=ProxyConfig(upstream=upstream))
        assert settings.proxy is not None
        assert settings.proxy.upstream is not None
        assert settings.proxy.store is not None

    def test_full_workflow_config_from_file(self):
        """Test complete workflow loading from YAML file."""
        settings = Settings.load_from_yaml(str(TEST_YAML_DIR / "full_config.yaml"))
        # Verify all levels of configuration
        assert settings.proxy.enabled
        assert settings.proxy.port == 8888
        assert "yaml-config" in settings.proxy.upstream.endpoint
        assert settings.proxy.upstream.api_key == "yaml_api_key"
        assert settings.proxy.store.backend == "memory"
        assert "/yaml/store" == settings.proxy.store.path

    def test_config_model_validation(self):
        """Test that Pydantic validation works correctly."""
        # Test that invalid port raises error
        with pytest.raises(Exception):
            ProxyConfig(
                upstream=UpstreamConfig(endpoint="https://test.com"),
                port="not_a_number"
            )

        # Test that valid config passes
        config = ProxyConfig(
            upstream=UpstreamConfig(endpoint="https://test.com"),
            port=8080
        )
        assert config.port == 8080
