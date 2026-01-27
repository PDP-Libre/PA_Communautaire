# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer, DataTable

# from .. import esb

from faststream.nats import NatsBroker
from faststream import FastStream

from ..palette import CustomCommand

# TODO: move to conf/settings
# TODO: move to ebs.py
broker = NatsBroker("nats://localhost:4222")


ROWS = [
    ("#", "brique", "IN", "OUT"),
    (1, "api-gateway", 0, 0),
    (2, "esb-central", 0, 0),
    (3, "controle-formats", 0, 0),
    (4, "validation-metier", 0, 0),
    (5, "conversion-formats", 0, 0),
    (6, "annuaire-local", 0, 0),
    (7, "routage", 0, 0),
    (8, "transmission-fiscale", 0, 0),
    (9, "gestion-cycle-vie", 0, 0),
    (10, "stockage", "N/A", "N/A"),
]


class BriquesScreen(Screen):
    TITLE = "briques"
    BINDINGS = [("h", "do_healthcheck()", "healthcheck")]
    COMMANDS = App.COMMANDS | {CustomCommand}

    def compose(self) -> ComposeResult:
        self.styles.background = "yellow"
        yield Header()
        yield Label("briques...", id="question")

        yield DataTable()

        # yield Button("Main Screen", id="main")
        yield Footer()

    # @on(Button.Pressed, "#main")
    # def on_main(self) -> None:
    #    self.dismiss()

    async def action_do_healthcheck(self) -> None:
        await broker.publish("healthcheck from CLI", "healthcheck")

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

        @broker.subscriber("*")  # subject name
        async def handle_msg(msg_body):
            # print("recieved ....", msg_body)
            ...

        await broker.start()
        await broker.publish("Hello from CLI", "healthcheck")

    async def on_unmount(self) -> None:
        """Stop the process when app exits."""
        await broker.publish("bye from CLI", "healthcheck")
        await broker.stop()


def handle_msg(
    screen: BriquesScreen,
    msg,
):
    table = screen.query_one(DataTable)
    table.add_row(8, str(msg), 0, 0)
