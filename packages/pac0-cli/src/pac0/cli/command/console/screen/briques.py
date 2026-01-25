from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Label, Header, Footer


class BriquesScreen(Screen):
    #BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:        
        self.styles.background = "yellow"
        yield Header()
        yield Label("briques...", id="question")

        #yield Button("Main Screen", id="main")
        yield Footer()

    #@on(Button.Pressed, "#main")
    #def on_main(self) -> None:
    #    self.dismiss()
