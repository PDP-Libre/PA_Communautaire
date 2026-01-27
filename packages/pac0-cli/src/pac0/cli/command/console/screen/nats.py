# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer, DataTable
from textual.containers import HorizontalGroup, VerticalScroll
from ..palette import CustomCommand

from faststream.nats import NatsBroker
from faststream import FastStream, Context


ROWS = [
    ("sujet", "message", "divers"),
]


# TODO: move to conf/settings
# TODO: move to ebs.py
broker = NatsBroker("nats://localhost:4222")


class NatsScreen(Screen):
    TITLE = "NATS - PAC0 Console"
    BINDINGS = [("z", "do_reset()", "RAZ")]
    COMMANDS = App.COMMANDS | {CustomCommand}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("NATS ...", id="question")
        yield VerticalScroll(
            HorizontalGroup(
                Button("ping", id="ping", variant="success")  ,
                Button("healthcheck", id="healthcheck", variant="error"),
            ),
            DataTable(),
        )

        yield Footer()



    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])

        # voir https://docs.nats.io/nats-concepts/subjects#wildcards
        # voir https://faststream.ag2.ai/latest/nats/message/#headers-access
        @broker.subscriber(">")  # subject name
        async def _(
                msg_body,
                subject: str = Context("message.raw_message.subject"),
        ):
            table = self.query_one(DataTable)
            table.add_row(subject, msg_body, "")

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


    async def action_do_reset(self) -> None:
        table = self.query_one(DataTable)
        table.clear()


