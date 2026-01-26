# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer

from ..palette import CustomCommand

class ConfigScreen(Screen):
    COMMANDS = App.COMMANDS | {CustomCommand}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Config ...", id="question")

        yield Label("[ pac01 ]  pac02  pac03  pac04")

        yield Label("PAC API ____")
        yield Label("NATS ____")
        yield Label("S3 ____")

        yield Footer()
