# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer, DataTable
from ..palette import CustomCommand

from faststream.nats import NatsBroker
from faststream import FastStream


ROWS = [
    ("#", "test", "statut"),
    (1, "test_scenario::test_peppol", "OK"),
    (2, "test_scenario::test_metier", "FAIL"),
    (3, "test_scenario::test_peppol", "FAIL"),
]


# TODO: move to conf/settings
# TODO: move to ebs.py
broker = NatsBroker("nats://localhost:4222")


class NatsScreen(Screen):
    COMMANDS = App.COMMANDS | {CustomCommand}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("NATS ...", id="question")
        yield DataTable()
        yield Button("ping", id="msg1", variant="success")  
        yield Button("healthcheck", id="msg2", variant="error")

        yield Footer()



    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

        @broker.subscriber("*")  # subject name
        async def handle_msg(msg_body):
            # print("recieved ....", msg_body)
            handle_msg(msg_body)

        await broker.start()
        await broker.publish("Hello from CLI", "healthcheck")

    async def on_unmount(self) -> None:
        """Stop the process when app exits."""
        await broker.publish("bye from CLI", "healthcheck")
        await broker.stop()



    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        if event.button.id == "ping":
            #self.add_class("started")
            await broker.publish("ping from CLI", "ping")

        elif event.button.id == "healthcheck":
            self.remove_class("started")
            await broker.publish("healthcheck from CLI", "healthcheck")

