# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig


class FastStreamServiceContext(BaseServiceContext):
    """Test context for a FastStream service."""

    def __init__(
        self,
        app_file: str,
        name: str | None = None,
        nats_url: str = "nats://localhost:4222",
    ) -> None:
        config = ServiceConfig(
            name=name,
            # uv run faststream run src/pac0/service/validation_metier/main:app
            # command=["uv", "fastapi", "dev", "app1/main.py"],
            # command=["uv", "run", "faststream", "run", "src/pac0/service/validation_metier/main:app"],
            command=[
                "uv",
                "run",
                "faststream",
                "run",
                app_file,
                "--port={PORT}",
            ],
            port=0,
            allow_ConnectionRefusedError=True,
            health_check_path=None,
            env_var_extra={
                "NATS_URL": nats_url,
            },
        )
        super().__init__(config)
