# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pydantic_settings import BaseSettings


class SettingsCLI(BaseSettings):
    """
    les settings CLI
    via .env ou variables d'environnement
    """

    api_url: str | None = None
    brique_externe: bool = False
    nats_url: str | None = None
    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_url: str | None = None
    s3_data: str | None = None
    uv_publish_token: str | None = None
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None


settings = SettingsCLI(
    _env_file=".env",
    # _env_prefix="PAC0_",
)
