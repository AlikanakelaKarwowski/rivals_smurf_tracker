from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, Button, Select, Label, DataTable, Header, Footer, Static
from textual.coordinate import Coordinate
import sqlite3


# Rank Mapping from highest to lowest
RANKS = [
    "Eternal 1", "Eternal 2", "Eternal 3",
    "Grand Master 1", "Grand Master 2", "Grand Master 3",
    "Diamond 1", "Diamond 2", "Diamond 3",
    "Platinum 1", "Platinum 2", "Platinum 3",
    "Gold 1", "Gold 2", "Gold 3",
    "Silver 1", "Silver 2", "Silver 3",
    "Bronze 1", "Bronze 2", "Bronze 3"
]
RANK_MAP = {rank: i for i, rank in enumerate(reversed(RANKS))}

# Database setup
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            rank TEXT,
            rank_value INTEGER
        )
    """)
    conn.commit()
    conn.close()
class EntryWidget(Static):

    CSS = """
    . {
        layout: grid;
        grid-size: 2;
    }

    """
    
class RivalsSmurfTracker(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
    }
    #submit {
        background: green;
        color: white;
    }


    #search_btn {
        background: blue;
        color: white;
    }
    #edit_prompt {
        display: none;
    }
    #edit_username {
        display: none;
    }
    #edit_password {
        display: none;
    }
    #edit_rank {
        display: none;
    }
    #save_edit {
        display: none;
    }
    """
    BINDINGS = [("ctrl+q", "quit", "CTRL+Q to Quit")]



    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Enter your username", id="username", classes="userpass")
        yield Input(placeholder="Enter your password", id="password", password=True, classes="userpass")

        yield Select([(rank, rank) for rank in RANKS], prompt="Select a rank", id="rank", classes="selection")
        yield Button("Submit", id="submit", classes="selection")

        yield Input(placeholder="Search by username or rank", id="search", classes="search")
        yield Button("Search", id="search_btn", classes="search")


        yield DataTable(id="results", cursor_type="row", classes="results")
        yield Static("Click an entry to edit", id="edit_prompt", classes="results")

        yield Input(placeholder="Edit Username", id="edit_username", classes="edit")
        yield Input(placeholder="Edit Password", id="edit_password", password=True, classes="edit")

        yield Select([(rank, rank) for rank in RANKS], id="edit_rank", classes="editrank")
        yield Button("Save Changes", id="save_edit", classes="edit")
        yield Footer()

        


    def on_mount(self) -> None:
        init_db()
        self.query_one(DataTable).add_columns("Username", "Password", "Rank")

    def on_button_pressed(self, event) -> None:
        if event.button.id == "submit":
            self.store_entry()
        elif event.button.id == "search_btn":
            self.search_entries()
        elif event.button.id == "save_edit":
            self.save_edit()
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        
        username = self.query_one("#edit_username")
        username.display = "block"
        username.value = self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 0))
        password = self.query_one("#edit_password")
        password.display = "block"
        password.value = self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 1))
        rank = self.query_one("#edit_rank")
        rank.display = "block"
        rank.value = self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 2))

        save_edit = self.query_one("#save_edit").display = "block"


    def store_entry(self):
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value.strip()
        rank = self.query_one("#rank", Select).value
        

        if not username or not password or not rank:
            return

        rank_value = RANK_MAP[rank]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, rank, rank_value) VALUES (?, ?, ?, ?)",
                       (username, password, rank, rank_value))
        conn.commit()
        conn.close()
        username_input = self.query_one("#username", Input)
        password_input = self.query_one("#password", Input)
        username_input.value = ""
        password_input.value = ""


    def search_entries(self):
        search_query = self.query_one("#search", Input).value.strip()
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        
        if search_query in RANK_MAP:
            rank_value = RANK_MAP[search_query]
            valid_ranks = self.get_valid_ranks(rank_value)
            cursor.execute("SELECT username, password, rank FROM users WHERE rank_value IN ({})".format(
                ",".join(map(str, valid_ranks))))
        else:
            cursor.execute("SELECT username, password, rank FROM users WHERE username LIKE ?", (f"%{search_query}%",))
        
        results = cursor.fetchall()
        conn.close()

        table = self.query_one(DataTable)
        table.clear()
        for row in results:
            table.add_row(*row)

    def get_valid_ranks(self, rank_value):
        valid_ranks = []

        # If rank is in Bronze or Silver
        if RANK_MAP["Bronze 3"] <= rank_value <= RANK_MAP["Silver 1"]:
            valid_ranks.extend(range(0, 9))

        # If rank is in Gold
        elif RANK_MAP["Gold 3"] <= rank_value <= RANK_MAP["Gold 1"]:
            valid_ranks.extend(range(0, 9))
            valid_ranks.extend(range(rank_value + 1, rank_value + 4))

        # If rank is in Platinum, Diamond, or Grand Master
        elif RANK_MAP["Platinum 3"] <= rank_value <= RANK_MAP["Grand Master 1"]:
            valid_ranks.extend(range(max(rank_value - 3, 0), min(rank_value + 4, len(RANKS))))

        return valid_ranks
    
    def save_edit(self):
        selected_row = self.query_one(DataTable).cursor_row
        if selected_row is None:
            return
        else: 
            o_username = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 0))
            o_password = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 1))
            o_rank = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 2))
            old_rank_value = RANK_MAP[o_rank]

        username = self.query_one("#edit_username", Input).value.strip()
        password = self.query_one("#edit_password", Input).value.strip()
        rank = self.query_one("#edit_rank", Select).value
        
        if not username or not password or not rank:
            return

        rank_value = RANK_MAP[rank]
        
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET username = ?, password = ?, rank = ?, rank_value = ? WHERE username = ? AND password = ? AND rank = ? AND rank_value = ?",
                       (username, password, rank, rank_value, o_username, o_password, o_rank, old_rank_value))
        conn.commit()
        conn.close()

        self.search_entries()
        username = self.query_one("#edit_username")
        username.display = "none"
        username.value = ""
        password = self.query_one("#edit_password")
        password.display = "none"
        password.value = ""
        rank = self.query_one("#edit_rank")
        rank.display = "none"
        self.query_one("#save_edit").display = "none"

if __name__ == "__main__":
    RivalsSmurfTracker().run()
