# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig


class FastApiServiceContext(BaseServiceContext):
    """Test context for a FastAPI service."""

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        config = ServiceConfig(
            name=name,
            # command=["uv", "fastapi", "dev", "app1/main.py"],
            command=[
                "uv",
                "run",
                "fastapi",
                "run", #"dev",
                "src/pac0/service/api_gateway/main.py",
            ],
            port=0,
            allow_ConnectionRefusedError=True,
            health_check_path="/healthcheck",
        )
        super().__init__(config)
