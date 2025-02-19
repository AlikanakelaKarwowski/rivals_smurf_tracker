from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Select, DataTable, Header, Footer, Static
from textual.containers import Horizontal
from textual.coordinate import Coordinate
from utils.dbo import User, engine, init_db
from utils.rank_utils import get_valid_ranks
from sqlmodel import Session


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
    
        with Session(engine) as session:
            new_user = User.create_user(session, username=username, password=password, uuid=uuid, level=level, rank=rank, rank_value=RANK_MAP[rank])
            print(f"User Created: {new_user.username}")

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
        with Session(engine) as session:
            if search_query in RANK_MAP:
                rank_value = RANK_MAP[search_query]
                valid_ranks = get_valid_ranks(rank_value, RANK_MAP, RANKS)
                results = User.get_users_by_ranks(session, valid_ranks)
            else:
                results = User.get_users_by_username(session, search_query)
        
        table = self.query_one(DataTable)
        table.clear()
        for row in results:
            table.add_row(
                row.username,
                row.password,
                row.uuid,
                row.level,
                row.rank
            )

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
        
        with Session(engine) as session:
            update_user = User.update_user(
                session, 
                o_username, username, 
                o_password, password, 
                o_uuid, uuid, 
                o_level, level, 
                o_rank, rank, 
                o_rank_value, rank_value
            )
        if update_user:
            print(f"Updated User: {update_user.username}")
        else:
            print(f"Failed to update User: {o_username}")

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
            rank = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 4))
            rank_value = RANK_MAP[rank]

            with Session(engine) as session:
                if User.delete_user(session, username, password, uuid, level, rank, rank_value):
                    print(f"Deleted User: {username}")
                else:
                    print(f"Failed to delete User: {username}")

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
        level.value = ""
        rank = self.query_one("#edit_rank")
        rank.display = False
        self.query_one("#save_edit").display = False
        self.query_one("#delete").display = False

if __name__ == "__main__":
    init_db()
    RivalsSmurfTracker().run()
