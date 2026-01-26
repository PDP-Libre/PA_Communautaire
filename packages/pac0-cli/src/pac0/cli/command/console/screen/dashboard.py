# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer, Label

import asyncio
from typing import Any
from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer
from textual.command import Provider, Hit
from rich.style import Style
from functools import partial

from ..palette import CustomCommand


class DashboardScreen(Screen):
    #BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    COMMANDS = App.COMMANDS | {CustomCommand}

    def compose(self) -> ComposeResult:
        #self.screen.styles.background = "darkblue"
        yield Header()
        yield Label("Dashboard ...", id="question")
        # self.styles.background = "darkblue"
        #yield Button("dashboard", id="main")
        yield Footer()

    #@on(Button.Pressed, "#main")
    #def on_main(self) -> None:
    #    self.dismiss()
