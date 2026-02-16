# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import logging
from typing import Any, Self

from faststream import FastStream, Context

from faststream.nats import NatsBroker
from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: remove the spy feature
class NatsServiceContext(BaseServiceContext):
    """Test context for a NATS service."""

    def __init__(
        self,
        name: str | None = None,
        spy: bool = True,
        spy_log_max=1000,
    ) -> None:
        config = ServiceConfig(
            name=name or "esb",
            command=["nats-server", "--port={PORT}"],
            port=0,
            protocol="nats",
            allow_ConnectionRefusedError=True,
            health_check_path=None,
            env_var="NATS_URL",
        )
        super().__init__(config)

        logger.info(f"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx {self.url=}")
        print(f"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx {self.url=}")

        self.spy = spy
        self.spy_log = []
        self.spy_log_max = spy_log_max
        self.spy_broker: NatsBroker | None = None

    # @property
    # def url(self) -> str:
    #    return f"nats://{self.config.host}:{self.config.port}"

    # @property
    # def client(self) -> str:
    #    return f"nats://{self.config.host}:{self.config.port}"

    async def __aenter__(self) -> Self:
        print("KKKKKKKKKKKKKKKKKKKKK 3")

        result = await super().__aenter__()

        if self.spy:
            # self.spy_broker = NatsBroker(self.url)
            # broker = self.spy_broker = NatsBroker("nats://localhost:4222")
            broker = NatsBroker(f"nats://localhost:{self.config.port}")
            self.spy_broker = broker
            print(f"iiiiiiiii00 {self.config.port=}")

            await asyncio.sleep(2)

            # on écoute tout
            # @self.spy_broker.subscriber(">")
            @broker.subscriber(">")
            async def handle_msg(
                msg_body,
                # m: str = Context("message"),
                s: str = Context("message.raw_message.subject"),
            ):
                print(f"yyyyyyyyyyyyy spy recieved a msg on subject {s}....")
                if len(self.spy_log) >= self.spy_log_max:
                    self.spy_log = self.spy_log[-(self.spy_log_max + 1) :]
                self.spy_log.append(
                    {
                        "subject": s,
                        "body": "???",
                    }
                )

            await broker.start()

        return result

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if self.spy_broker:
                await self.spy_broker.stop()
        finally:
            return await super().__aexit__(exc_type, exc_val, exc_tb)

    async def spy_assert(self):
        await asyncio.sleep(5)