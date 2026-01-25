# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio
from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer


from .screen.tests import TestsScreen
from .screen.factures import FacturesScreen
from .screen.briques import BriquesScreen
from .screen.dashboard import DashboardScreen
from .screen.config import ConfigScreen

from . import esb


class ConsoleApp(App):
    TITLE = "PAC0 Console"
    SUB_TITLE = "Plateforme Agréée Communautaire"

    CSS_PATH = "app.tcss"

    MODES = {
        "dashboard": DashboardScreen,
        "briques": BriquesScreen,
        "tests": TestsScreen,
        "factures": FacturesScreen,
        "config": ConfigScreen,
    }

    BINDINGS = [
        ("d", "switch_mode('dashboard')", "dashboard"),
        ("b", "switch_mode('briques')", "briques"),
        ("t", "switch_mode('tests')", "tests"),
        ("f", "switch_mode('factures')", "factures"),
        # ("t", "switch_screen('stats')", "Statistiques"),
        # ("e", "switch_screen('tests')", "Tests"),
        ("q", "quit", "quitter"),
    ]

    async def on_mount(self) -> None:
        self.switch_mode("dashboard")



async def main():
    app_console = ConsoleApp()
    # app_esb = esb.app_factory()
    # await esb.broker.start()
    # await esb.broker.publish("hello", "from console")

    # await asyncio.gather(app_console.run(), app_esb.run())
    await app_console.run()


if __name__ == "__main__":
    asyncio.run(main())
