from textual.app import App
from textual import events, on
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Header, Footer, Label


class DashboardScreen(Screen):
    #BINDINGS = [("escape", "app.pop_screen", "Pop screen")]

    def compose(self) -> ComposeResult:
        #self.screen.styles.background = "darkblue"
        yield Header()
        yield Label("Dashboard ...", id="question")
        # self.styles.background = "darkblue"
        #yield Button("dashboard", id="main")
        yield Footer()

    #@on(Button.Pressed, "#main")
    #def on_main(self) -> None:
    #    self.dismiss()
