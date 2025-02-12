from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Select, DataTable, Header, Footer, Static
from textual.containers import Horizontal
from textual.coordinate import Coordinate
from utils.dbo import store_to_db, init_db, search_rank_db, search_user_db, update_db, delete_db
from utils.rank_utils import get_valid_ranks


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


class RivalsSmurfTracker(App):
    CSS = """
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
        background: green;
    }
    #delete {
        display: none;
        background: maroon;
    }
    .edit {
        display: none;
    }
    """
    BINDINGS = [("ctrl+q", "quit", "CTRL+Q to Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Enter your username", id="username", classes="userpass")
        yield Input(placeholder="Enter your password", id="password", password=True, classes="userpass")
        yield Input(placeholder ="Enter your UUID", id="uuid", classes="userpass")
        yield Input(placeholder="Enter your level", id="level", classes="userpass")

        yield Select([(rank, rank) for rank in RANKS], prompt="Select a rank", id="rank", classes="selection")
        yield Button("Submit", id="submit", classes="selection")

        yield Input(placeholder="Search by username or rank", id="search", classes="search")
        yield Button("Search", id="search_btn", classes="search")


        yield DataTable(id="results", cursor_type="row", classes="results")
        yield Static("Click an entry to edit", id="edit_prompt", classes="results")

        yield Input(placeholder="Edit Username", id="edit_username", classes="edit")
        yield Input(placeholder="Edit Password", id="edit_password", password=True, classes="edit")
        yield Input(placeholder="edit UUID", id="edit_uuid", classes="edit")
        yield Input(placeholder="Edit Level", id="edit_level", classes="edit")

        yield Select([(rank, rank) for rank in RANKS], id="edit_rank", classes="editrank")
        with Horizontal(id="edit_buttons"):
            yield Button("Save Changes", id="save_edit", classes="edit")
            yield Button("Delete", id="delete", classes="edit")
        
        yield Footer()


    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns("Username", "Password", "UUID", "Level", "Rank")

    def on_button_pressed(self, event) -> None:
        if event.button.id == "submit":
            self.store_entry()
        elif event.button.id == "search_btn":
            self.search_entries()
        elif event.button.id == "save_edit":
            self.save_edit()
        elif event.button.id == "delete":
            self.delete_entry()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        
        username = self.query_one("#edit_username")
        username.display = True
        username.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 0)))
        password = self.query_one("#edit_password")
        password.display = True
        password.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 1)))
        uuid = self.query_one("#edit_uuid")
        uuid.display = True
        uuid.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 2)))

        level = self.query_one("#edit_level")
        level.display = True
        level.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 3)))
        rank = self.query_one("#edit_rank")
        rank.display = True

        self.query_one("#save_edit").display = True
        self.query_one("#delete").display = True
        


    def store_entry(self):
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value.strip()
        uuid = self.query_one("#uuid", Input).value.strip()
        level = self.query_one("#level", Input).value
        rank = self.query_one("#rank", Select).value

        if not username or not password or rank is Select.BLANK:
            return

        store_to_db(username, password, uuid, level, rank, RANK_MAP[rank])

        username_input = self.query_one("#username", Input)
        password_input = self.query_one("#password", Input)
        uuid_input = self.query_one("#uuid", Input)
        level_input = self.query_one("#level", Input)
        username_input.value = ""
        password_input.value = ""
        uuid_input.value = ""
        level_input.value = ""


    def search_entries(self):
        search_query = self.query_one("#search", Input).value.strip()
        if search_query in RANK_MAP:
            rank_value = RANK_MAP[search_query]
            valid_ranks = get_valid_ranks(rank_value, RANK_MAP, RANKS)
            results = search_rank_db(valid_ranks)
        else:
            results = search_user_db(search_query)
        
        table = self.query_one(DataTable)
        table.clear()
        for row in results:
            table.add_row(*row)

    
    
    def save_edit(self):
        selected_row = self.query_one(DataTable).cursor_row
        if selected_row is None:
            return
        else: 
            o_username = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 0))
            o_password = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 1))
            o_uuid = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 2))
            o_level = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 3))
            o_rank = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 4))
            o_rank_value = RANK_MAP[o_rank]

        username = self.query_one("#edit_username", Input).value.strip()
        password = self.query_one("#edit_password", Input).value.strip()
        uuid = self.query_one("#edit_uuid", Input).value.strip()
        level = self.query_one("#edit_level", Input).value
        rank = self.query_one("#edit_rank", Select).value
        
        if not username or not password or rank is Select.BLANK:
            return

        rank_value = RANK_MAP[rank]
        
        update_db(username, o_username, password, o_password, uuid, o_uuid, level, o_level, rank, o_rank, rank_value, o_rank_value)

        self.search_entries()

        self.hide_edit()

    def delete_entry(self):
        selected_row = self.query_one(DataTable).cursor_row
        if selected_row is None:
            return
        else:
            username = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 0))
            password = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 1))
            uuid = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 2))
            level = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 3))
            rank = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 2))
            rank_value = RANK_MAP[rank]

            delete_db(username, password, uuid, level, rank, rank_value)

        self.search_entries()
        self.hide_edit()


    def hide_edit(self):
        username = self.query_one("#edit_username")
        username.display = False
        username.value = ""
        password = self.query_one("#edit_password")
        password.display = False
        password.value = ""
        uuid = self.query_one("#edit_uuid")
        uuid.display = False
        uuid.value = ""
        level = self.query_one("#edit_level")
        level.display = False
        level.value = 0
        rank = self.query_one("#edit_rank")
        rank.display = False
        self.query_one("#save_edit").display = False
        self.query_one("#delete").display = False

if __name__ == "__main__":
    init_db()
    RivalsSmurfTracker().run()
