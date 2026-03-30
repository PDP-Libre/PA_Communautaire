# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
objectifs:
    - utiliser jetstream pour capturer/récupérer les messages publiés
    - capturer/récupérer en synchrone
    - definir le ou les streams utiles

voir:
* https://natsbyexample.com/examples/jetstream/limits-stream/python
* https://docs.nats.io/nats-concepts/jetstream/streams



"""

import asyncio
from typing import Any, Dict, List

from nats import connect
from nats.js import JetStreamContext
from nats.server import run
from pytest import mark

STREAM_NAME = "my-stream"


async def connect_js(nats_url: str) -> JetStreamContext:
    # Connect to NATS
    nc = await connect(nats_url)

    # Create JetStream context
    js = nc.jetstream()

    # Ensure stream exists (create if it doesn't)
    try:
        stream_info = await js.stream_info(STREAM_NAME)
        print(f"Stream '{STREAM_NAME}' already exists")
    except Exception:
        # Create the stream
        await js.add_stream(
            name=STREAM_NAME,
            # subjects=[subject.replace(">", "*")] if ">" in subject else [subject],
            # subjects=["events.>"],
            subjects=[f"{STREAM_NAME}.>"],
        )
        print(f"Created stream '{STREAM_NAME}'")

    return js


def run_async(coro):
    """Helper function to run async code synchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def read_all_messages_simple(
    stream_name: str,
    subject: str,
    nats_url: str,
) -> List[Dict[str, Any]]:
    """Simpler version to read all messages from a stream"""

    async def _read():
        js = await connect_js(nats_url)

        # Create a consumer to read from the beginning
        sub = await js.pull_subscribe(
            subject=subject,
            stream=stream_name,
            durable=f"temp-consumer-{stream_name}",
        )

        messages = []
        batch_size = 100

        while True:
            try:
                # Fetch a batch of messages
                msgs = await sub.fetch(batch_size, timeout=1)

                for msg in msgs:
                    messages.append(
                        {
                            "subject": msg.subject,
                            "data": msg.data.decode(),
                            "sequence": msg.metadata.sequence.stream
                            if msg.metadata
                            else None,
                        }
                    )
                    await msg.ack()

            except Exception:
                # No more messages or timeout
                break

        await nc.close()
        return messages

    return run_async(_read())


def main():
    messages = read_all_messages_simple("mystream", "mystream.>")
    for msg in messages:
        print(msg)


def create_data(): ...


async def test_js_simple():
    """NATS JS in context manager"""
    async with await run(port=0, jetstream=True) as server:
        assert server.is_running is True
        assert server.port > 0

        # nats_url = f"nats://localhost:{server.port}"
        nats_url = f"nats://localhost:{server.port}"

        js = await connect_js(nats_url)

        await js.publish("toto", b"Hello world !")
        await js.publish(f"{STREAM_NAME}.sub1", b"Hello world !")
        await js.publish(f"{STREAM_NAME}.sub2", b"Hello world !")

        messages = read_all_messages_simple("mystream", f"{STREAM_NAME}.>", nats_url)
        for msg in messages:
            print(msg)

    # Server should be shutdown after context exit
    assert server.is_running is False


async def test_stream1():
    """
    Créer un stream, publier, relire
    """
    # lancer une instance nats js
    async with await run(port=0, jetstream=True) as server:
        assert server.is_running is True
        assert server.port > 0

        # Connect to NATS
        nats_url = f"nats://localhost:{server.port}"
        nc = await connect(nats_url)

        # Create JetStream context
        js = nc.jetstream()

        # définir le stream si inexistant
        # Create the stream
        await js.add_stream(
            name="S1",
            # subjects=[subject.replace(">", "*")] if ">" in subject else [subject],
            # subjects=["events.>"],
            subjects=[".>"],
        )

        # publier quelques messages
        await js.publish("toto", b"Hello world !")
        await js.publish("toto", b"Hello world2 !")

        # se deconnecter
        # se connecter
        # accéde au stream
        # lire tous les messages
        # comparer avec les messages publiés
        #

    # raise NotImplementedError()
