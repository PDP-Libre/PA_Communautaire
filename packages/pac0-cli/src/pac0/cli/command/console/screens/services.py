from textual.screen import Screen
from textual.widgets import DataTable, Label, Footer
from textual.containers import Container


class ServicesScreen(Screen):
    """Écran d'affichage des services"""

    BINDINGS = [
        ("escape", "app.pop_screen", "Retour"),
    ]

    def compose(self):
        """
        yield Container(
            Label("Services PAC", id="title"),
            DataTable(id="services-table"),
            id="services-container",
        )
        """
        yield Footer()

    def on_mount(self) -> None:
        """Initialisation de l'écran"""
        
        table = self.query_one(DataTable)
        table.add_columns("Nom", "Statut", "Port", "Démarré le")

        # Données de démonstration
        services_data = [
            ("api-gateway", "En cours", "8000", "2026-01-16 10:30"),
            ("auth-service", "En cours", "8001", "2026-01-16 10:31"),
            ("db-service", "Arrêté", "-", "-"),
        ]

        for service in services_data:
            table.add_row(*service)
