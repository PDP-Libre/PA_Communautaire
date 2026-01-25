from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer


class GreenScreen(Screen):
    #BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        yield Header()
        self.styles.background = "green"
        yield Label("green ...", id="question")

        #yield Button("Main Screen", id="main")
        yield Footer()

    #@on(Button.Pressed, "#main")
    #def on_main(self) -> None:
    #    self.dismiss()
