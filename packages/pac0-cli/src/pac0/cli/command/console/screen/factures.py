from typing import Iterable
from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer, DataTable
from textual.command import Hit, Hits, Provider
from textual.app import App, SystemCommand


ROWS = [
    ("#", "eid", "montant", "statut"),
    ("FA-354-001", "009:12345678", 250, "XX-----"),
    ("FA-354-00@", "009:12345678", 34.5, "XXX----"),
    ("FA-354-00#", "009:12345678", 1340, "XXXXX--"),
]


class FacturesScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Factures ...", id="question")
        yield DataTable()
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*ROWS[0])
        table.add_rows(ROWS[1:])
