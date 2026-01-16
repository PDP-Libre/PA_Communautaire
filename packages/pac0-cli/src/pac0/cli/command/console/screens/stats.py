from textual.screen import Screen
from textual.widgets import Label, Footer
from textual.containers import Container


class StatsScreen(Screen):
    """Écran d'affichage des statistiques"""

    BINDINGS = [
        ("escape", "app.pop_screen", "Retour"),
    ]

    def compose(self):
        yield Container(
            Label("Statistiques PAC", id="title"),
            Label("Factures reçues: 1250", id="invoices-received"),
            Label("Factures traitées: 1120", id="invoices-processed"),
            Label("Erreurs: 5", id="errors"),
            id="stats-container",
        )
        yield Footer()
