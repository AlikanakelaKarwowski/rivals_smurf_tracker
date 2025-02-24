from textual.screen import ModalScreen
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal,Container
from textual.app import ComposeResult

class ErrorScreen(ModalScreen):
    """A modal pop-up error message centered on the screen."""

    DEFAULT_CSS = """
    ErrorScreen {
        align: center middle; 
    }

    #error_container {
        width: 50%;
        max-height: 30%;
        height: 20;
        background: $surface;
        border: thick $background 80%;
        padding: 2;
        align: center middle;
    }

    #error_message {
        text-align: center;
        color: $text;
        padding: 1;
    }

    #error_buttons {
        align: center middle;
    }

    #close_button {
        margin-top: 1;
        width: 30%;
        align: center middle;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="error_container"):
            yield Static(self.message, id="error_message")
            with Horizontal(id="error_buttons"): 
                yield Button("Close", id="close_button", variant="error")


    def on_button_pressed(self, event) -> None:
        if event.button.id == "close_button":
            self.app.pop_screen()
