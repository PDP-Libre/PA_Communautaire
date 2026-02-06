# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig


# TODO: use envvar for already running service
class FastApiServiceContext(BaseServiceContext):
    """Test context for a FastAPI service."""

    def __init__(
        self,
        name: str = "api_gateway",
        nats_url: str = "nats://localhost:4222",
        external_svc: str | None = None,
    ) -> None:
        config = ServiceConfig(
            name=name,
            command=[
                "uv",
                "run",
                "fastapi",
                "run",  # "dev",
                "src/pac0/service/api_gateway/main.py",
            ],
            port=0,
            # allow_ConnectionRefusedError=True,
            health_check_path="/healthcheck",
            env_var_extra={
                "NATS_URL": nats_url,
            },
            external_svc=external_svc,
            env_var="PAC0_API_URL",
        )
        super().__init__(config)

