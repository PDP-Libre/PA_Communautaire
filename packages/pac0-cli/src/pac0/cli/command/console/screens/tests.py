from textual.screen import Screen
from textual.widgets import DataTable, Label, Footer
from textual.containers import Container


class TestsScreen(Screen):
    """Écran d'affichage des résultats de tests"""

    BINDINGS = [
        ("escape", "app.pop_screen", "Retour"),
    ]

    def compose(self):
        yield Container(
            Label("Résultats des tests", id="title"),
            DataTable(id="tests-table"),
            id="tests-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialisation de l'écran"""
        table = self.query_one(DataTable)
        table.add_columns("Test", "Statut", "Durée", "Message")

        # Données de démonstration
        tests_data = [
            ("test_api_gateway", "PASS", "0.2s", "Tous les endpoints fonctionnent"),
            ("test_auth_service", "FAIL", "0.1s", "Échec d'authentification"),
            ("test_database", "PASS", "0.5s", "Connexion réussie"),
        ]

        for test in tests_data:
            table.add_row(*test)
