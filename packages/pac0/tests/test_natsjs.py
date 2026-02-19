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
from typing import Any, Dict, List, Optional

from nats import connect


async def connect_js(nats_url: str):
    # Connect to NATS
    nc = await connect(nats_url)

    # Create JetStream context
    js = nc.jetstream()

    # Ensure stream exists (create if it doesn't)
    try:
        stream_info = await js.stream_info(stream_name)
        print(f"Stream '{stream_name}' already exists")
    except Exception:
        # Create the stream
        await js.add_stream(
            name=stream_name,
            # subjects=[subject.replace(">", "*")] if ">" in subject else [subject],
            # subjects=["events.>"],
            subjects=[">"],
        )
        print(f"Created stream '{stream_name}'")

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
    stream_name: str, subject: str, nats_url: str = "nats://localhost:4222"
) -> List[Dict[str, Any]]:
    """Simpler version to read all messages from a stream"""

    async def _read():
        js = await connect_js(nats_url)

        # Create a consumer to read from the beginning
        sub = await js.pull_subscribe(
            subject=subject, stream=stream_name, durable=f"temp-consumer-{stream_name}"
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

            except Exception as e:
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


def test_0010(): ...
