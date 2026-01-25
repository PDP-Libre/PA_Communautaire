from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer, DataTable


ROWS = [
    ("#", "test", "statut"),
    (1, "test_scenario::test_peppol", "OK"),
    (2, "test_scenario::test_metier", "FAIL"),
    (3, "test_scenario::test_peppol", "FAIL"),
]


class TestsScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Tests ...", id="question")
        yield DataTable()
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])
