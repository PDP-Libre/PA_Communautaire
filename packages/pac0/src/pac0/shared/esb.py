# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import logging
import os
from dataclasses import dataclass
from typing import Any, Callable, Optional

from faststream import ContextRepo, FastStream
from faststream.nats import JStream, NatsBroker, NatsRouter
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# TODO: we will use NATS queue to have pool of instances
QUEUE = "q"


class SettingsServeur(BaseSettings):
    """
    les settings du serveur 02-esb
    """

    # répertoire des data NATS
    # Si None on utilise un répertoire temporaire unique
    data_path: str | None = None


class SettingsService(BaseSettings):
    """
    les settings d'un service de base (brique)
    """

    nats_url: str = "nats://localhost:4222"


@dataclass
class CtxService:
    prefix: str
    queue: str
    broker: Any
    subject_in: str
    subject_out: str
    subject_err: str
    publisher_out: Any
    publisher_err: Any


def init_esb_app(
    prefix: str,
    process: Optional[Callable] = None,
):
    global broker

    _broker = NatsBroker(get_nats_url())

    app = FastStream(_broker)
    _broker.include_router(router)

    broker = _broker

    subject_in = f"{prefix}-IN"
    subject_out = f"{prefix}-OUT"
    subject_err = f"{prefix}-ERR"

    ctx = CtxService(
        prefix=prefix,
        queue=QUEUE,
        broker=_broker,
        subject_in=subject_in,
        subject_out=subject_out,
        subject_err=subject_err,
        publisher_out=_broker.publisher(subject_out),
        publisher_err=_broker.publisher(subject_err),
    )

    # TODO: add on_startup behaviour to annonce the new service instance
    # @app.on_startup
    # async def setup(context: ContextRepo, env: str = ".env"):
    #    print("setup pac0 service ...")
    #    settings = SettingsService(_env_file=env)
    #    context.set_global("settings", settings)

    # @app.on_startup
    @app.after_startup
    async def _():
        await broker.publish(f"startup {prefix}", "service")

    @app.on_shutdown
    # @app.after_shutdown
    async def _():
        await broker.publish(f"shutdown {prefix}", "service")

    @router.subscriber("healthcheck")
    async def healthcheck_sub():
        """
        respond to tell the service is alive
        """
        await broker.publish(f"{prefix} is alive", "healthcheck_resp")

    @router.subscriber("ping", "ping-pong")
    async def ping(message):
        """
        respond to ping with a pong
        """
        await broker.publish(f"Pong from {prefix}", "pong")

    # You MUST return broker and app separatly
    return ctx, _broker, app


def get_nats_url():
    # TODO: deprecate in favor of SettingsService
    url = os.environ.get("NATS_URL", "nats://localhost:4222")
    # TODO: logger.info() ne marche pas ici
    print(f"Connecting to NATS {url} ...")
    return url


# ====================================================================
# common esb service features (must be included in each service)

router = NatsRouter(prefix="")

# will be set by when you import this module
broker = None

# https://natsbyexample.com/examples/jetstream/workqueue-stream/go
stream_cold = JStream(name="pac0-stream-cold")
stream_hot = JStream(name="pac0-stream-hot")
stream_external = JStream(name="pac0-stream-external")
stream_log = JStream(name="pac0-stream-log")
stream_store = JStream(name="pac0-stream-store")
