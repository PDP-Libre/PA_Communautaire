# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer, Label
from textual.containers import Horizontal, VerticalScroll

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


class AccueilScreen(Screen):
    #BINDINGS = [("escape", "app.pop_screen", "Pop screen")]
    COMMANDS = App.COMMANDS | {CustomCommand}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Acceuil ...")
        yield Label("Utilisez également la palette (ctrl-p) ...")

        with Horizontal():
            for mode in self.app.MODES:
                yield Button(mode, id=mode, action=f"app.switch_mode('{mode}')")

        yield Footer()

    #@on(Button.Pressed, "#main")
    #def on_main(self) -> None:
    #    self.dismiss()

    #async def on_button_pressed(self, event: Button.Pressed) -> None:
    #    self.app.switch_mode(event.button.id)
