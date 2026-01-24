# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from textual.app import App
from textual import events
from faststream.nats import NatsBroker
from faststream import FastStream

broker = NatsBroker("nats://localhost:4222")


@broker.subscriber("test")  # subject name
async def handle_msg(msg_body):
    print("recieved ....")


class ConsoleApp(App):
    COLORS = [
        "white",
        "maroon",
        "red",
        "purple",
        "fuchsia",
        "olive",
        "yellow",
        "navy",
        "teal",
        "aqua",
    ]

    async def on_mount(self) -> None:
        self.screen.styles.background = "darkblue"

    async def on_key(self, event: events.Key) -> None:
        if event.key.isdecimal():
            self.screen.styles.background = self.COLORS[int(event.key)]


async def main():
    app_console = ConsoleApp()
    app = FastStream(broker)

    await asyncio.gather(app_console.run(), app.run())


if __name__ == "__main__":
    asyncio.run(main())
