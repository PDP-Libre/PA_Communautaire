# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer

from faststream.nats import NatsBroker
from faststream import FastStream

from .screen.green import GreenScreen
from .screen.briques import BriquesScreen
from .screen.dashboard import DashboardScreen


broker = NatsBroker("nats://localhost:4222")


@broker.subscriber("test")  # subject name
async def handle_msg(msg_body):
    print("recieved ....")



class ConsoleApp(App):
    TITLE = "PAC0 Console"
    SUB_TITLE = "Plateforme Agréée Communautaire"

    CSS_PATH = "app.tcss"

    MODES = {
        "dashboard": DashboardScreen,
        "briques_screen": BriquesScreen,
        "green_screen": GreenScreen,
    }

    BINDINGS = [
        ("d", "switch_mode('dashboard')", "dashboard"),
        ("b", "switch_mode('briques_screen')", "briques"),
        ("g", "switch_mode('green_screen')", "green"),
        # ("t", "switch_screen('stats')", "Statistiques"),
        # ("e", "switch_screen('tests')", "Tests"),
        ("q", "quit", "Quitter"),
    ]

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
        self.switch_mode("dashboard")

    async def on_key(self, event: events.Key) -> None:
        if event.key.isdecimal():
            self.screen.styles.background = self.COLORS[int(event.key)]

    def compose(self) -> ComposeResult:
        yield Header()
        # yield Container()
        yield Button("Switch", id="switch")
        yield Footer()

    @on(Button.Pressed, "#switch")
    def on_switch(self) -> None:
        self.push_screen(GreenScreen())


async def main():
    app_console = ConsoleApp()
    app = FastStream(broker)

    await asyncio.gather(app_console.run(), app.run())


if __name__ == "__main__":
    asyncio.run(main())
