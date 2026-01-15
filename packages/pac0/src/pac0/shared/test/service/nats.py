# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig


class NatsServiceContext(BaseServiceContext):
    """Test context for a NATS service."""

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        config = ServiceConfig(
            name=name,
            command=["nats-server", "--port={PORT}"],
            port=0,
            allow_ConnectionRefusedError=True,
            health_check_path=None,
        )

        super().__init__(config)

    @property
    def url(self) -> str:
        return f"nats://{self.config.host}:{self.config.port}"

    # @property
    # def client(self) -> str:
    #    return f"nats://{self.config.host}:{self.config.port}"
