import textual
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Placeholder
from textual.containers import Container
from .screens.services import ServicesScreen
from .screens.stats import StatsScreen
from .screens.tests import TestsScreen


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

    SCREENS = {
        "services": ServicesScreen,
        "stats": StatsScreen,
        "tests": TestsScreen,
    }

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
