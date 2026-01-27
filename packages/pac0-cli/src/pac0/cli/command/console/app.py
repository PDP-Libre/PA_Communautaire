# SPDX-FileCopyrightText: 2026 Philippe ENTZMANN <philippe@entzmann.name>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header


class ConsoleApp(App):
    """Application console principale"""

    TITLE = "PAC Console"
    SUB_TITLE = "Plateforme Agréée Communautaire"

    BINDINGS = [
        ("d", "toggle_dark", "Mode sombre"),
        ("s", "switch_screen('services')", "Services"),
        ("t", "switch_screen('stats')", "Statistiques"),
        ("e", "switch_screen('tests')", "Tests"),
        ("q", "quit", "Quitter"),
    ]

    # def on_mount(self) -> None:
    #    """Initialisation de l'application"""
    #    self.switch_screen("services")

    def compose(self) -> ComposeResult:
        """Création de l'interface"""
        yield Header()
        # yield Container()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """Basculer entre le mode clair et sombre"""
        self.dark = not self.dark

    def action_switch_screen(self, screen_name: str) -> None:
        """Changer d'écran"""
        self.switch_screen(screen_name)


if __name__ == "__main__":
    app = ConsoleApp()
    app.run()
