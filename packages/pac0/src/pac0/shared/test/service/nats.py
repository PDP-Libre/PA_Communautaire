# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
import logging
from typing import Any, Self

from faststream import Context, FastStream
from faststream.nats import NatsBroker

from pac0.shared.test.service.base import BaseServiceContext, ServiceConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class NatsSpy:
    def __init__(
        self,
        url: str | None,
        spy_log_max=1000,
    ):
        self.url = url
        self.log: list[Any] = []
        self.log_max = spy_log_max
        self.broker: NatsBroker | None = None

    async def __aenter__(self) -> Self:
        # broker = NatsBroker(f"nats://localhost:{self.config.port}")
        broker = NatsBroker(self.url)
        self.broker = broker

        await asyncio.sleep(2)

        # on écoute tout
        @broker.subscriber(">")
        async def handle_msg(
            msg_body,
            # m: str = Context("message"),
            s: str = Context("message.raw_message.subject"),
        ):
            if len(self.log) >= self.log_max:
                self.log = self.log[-(self.log_max + 1) :]
            self.log.append(
                {
                    "subject": s,
                    "body": "???",
                }
            )

        await broker.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.broker:
            await self.broker.stop()

    async def wait_for(
        self,
        nb_message: int = 1,
        timeout: float = 2.0,
    ) -> None:
        """
        Wait for broker recieving `nb_message` new messages
        Raise an Exception if timeout is execeeded
        """
        nb_start = len(self.log)
        start_time = asyncio.get_event_loop().time()
        while len(self.log) < nb_start + nb_message:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise asyncio.TimeoutError(
                    f"Timeout waiting for {nb_message} messages. "
                    f"Only received {len(self.log)} messages."
                )
            await asyncio.sleep(0.3)

    async def wait_for_subject(
        self,
        message_subject: str,
        timeout: float = 2.0,
    ) -> None:
        """
        Wait for broker recieving a new message in a given subject
        Raise an Exception if timeout is execeeded
        """
        nb_pos = len(self.log)
        found = False
        start_time = asyncio.get_event_loop().time()
        while not found:
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise asyncio.TimeoutError(
                    f"Timeout waiting for message subject {message_subject}. "
                )
            found = any(msg.subject == message_subject for msg in self.log[nb_pos:])
            nb_pos = len(self.log)
            await asyncio.sleep(0.3)


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

        self.spy: NatsSpy | None = None
        if spy:
            # l'url sera indiqué plus tard
            self.spy = NatsSpy(url=None, spy_log_max=spy_log_max)

    # @property
    # def url(self) -> str:
    #    return f"nats://{self.config.host}:{self.config.port}"

    # @property
    # def client(self) -> str:
    #    return f"nats://{self.config.host}:{self.config.port}"

    async def __aenter__(self) -> Self:
        result = await super().__aenter__()

        if self.spy:
            # url = f"nats://localhost:{self.config.port}"
            self.spy.url = self.url
            await self.spy.__aenter__()

        return result

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            if self.spy:
                await self.spy.stop()
        finally:
            return await super().__aexit__(exc_type, exc_val, exc_tb)

    async def spy_assert(self):
        await asyncio.sleep(5)
