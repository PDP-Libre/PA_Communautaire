from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer


class FacturesScreen(Screen):

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Factures ...", id="question")
        yield Footer()
