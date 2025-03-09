from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Horizontal,Container
from textual.app import ComposeResult

class ErrorScreen(ModalScreen):
    """A modal pop-up error message centered on the screen."""

    DEFAULT_CSS = """
    ErrorScreen {
        align: center middle; 
    }
    #error_container {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 1fr ;
        grid-rows: auto auto;
        padding: 2;
        width: 100%;
        height: auto;
        min-width: 60vw;
        max-width: 80;
        max-height: 15;
        background: $surface;
        border: thick $background 80%;
        content-align:center middle;
    }
    #error_message {
        text-align: center;
        color: $text;
        padding: 1;
        column-span: 2;
    }
    #error_buttons {
        column-span: 2; 
        align: center middle;
        height: auto;
    }
    #close_button {
        width: 50%;
        padding:1 0;  
        height: auto;
        color:white;
        background: maroon;
        outline: wide maroon;
    }
    """
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="error_container"):
            yield Static(self.message, id="error_message")
            with Container(id="error_buttons"):  
                yield Button("Close", id="close_button")

    def on_button_pressed(self, event) -> None:
        if event.button.id == "close_button":
            self.app.pop_screen()
