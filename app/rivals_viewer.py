from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Select, DataTable, Header, Footer, Static
from textual.containers import Horizontal
from textual.coordinate import Coordinate
from app.utils.dbo import User, engine, init_db
from app.utils.rank_utils import get_valid_ranks
from app.utils.error_screen import ErrorScreen
from sqlmodel import Session
from app.utils.UserError import UserError
from app.utils.logger import logger

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
    #edit_buttons {
        height: auto; 
        min-height: 3; 
        padding-bottom: 1; 
    }

    """
    BINDINGS = [("ctrl+q", "quit", "CTRL+Q to Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Input(placeholder="Enter your username", id="username", classes="userpass")
        yield Input(placeholder="Enter your password", id="password", password=True, classes="userpass")
        yield Input(placeholder ="Enter your UID", id="uid", classes="userpass")
        yield Input(placeholder="Enter your level", id="level", classes="userpass")

        yield Select([(rank, rank) for rank in RANKS], prompt="Select a rank", id="rank", classes="selection")
        yield Button("Submit", id="submit", classes="selection")

        yield Input(placeholder="Search by username or rank", id="search", classes="search")
        yield Button("Search", id="search_btn", classes="search")


        yield DataTable(id="results", cursor_type="row", classes="results")
        yield Static("Click an entry to edit", id="edit_prompt", classes="results")

        yield Input(placeholder="Edit Username", id="edit_username", classes="edit")
        yield Input(placeholder="Edit Password", id="edit_password", password=True, classes="edit")
        yield Input(placeholder="Edit uid", id="edit_uid", classes="edit")
        yield Input(placeholder="Edit Level", id="edit_level", classes="edit")

        yield Select([(rank, rank) for rank in RANKS], id="edit_rank", classes="editrank")
        with Horizontal(id="edit_buttons"):
            yield Button("Save Changes", id="save_edit", classes="edit")
            yield Button("Delete", id="delete", classes="edit")
        
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns("Username", "Password", "uid", "Level", "Rank")

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
        uid = self.query_one("#edit_uid")
        uid.display = True
        uid.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 2)) or "")

        level = self.query_one("#edit_level")
        level.display = True
        level.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 3)) or "")
        rank = self.query_one("#edit_rank")
        rank.display = True

        self.query_one("#edit_rank").value = self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 4)) or Select.BLANK

        self.query_one("#save_edit").display = True
        self.query_one("#delete").display = True
        
    def store_entry(self):

        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value.strip()
        uid = self.query_one("#uid", Input).value.strip()
        if uid == "":
            uid = None
        level = self.query_one("#level", Input).value
        if level == "":
            level = None
        rank = self.query_one("#rank", Select).value

        if not username or not password or rank is Select.BLANK:
            self.push_screen(ErrorScreen("These fields are required: username, password and rank"))
            return
        
        with Session(engine) as session:
            try:
                new_user = User.create_user(session, username, password, rank, RANK_MAP[rank], uid=uid, level=level,)
            except UserError as e:
                self.push_screen(ErrorScreen(str(e))) 
                return
            except Exception as e:
                logger.error(f"Unexpected error during user creation: {e}")
                self.push_screen(ErrorScreen("Something went wrong. Please try again."))
                return

        username_input = self.query_one("#username", Input)
        password_input = self.query_one("#password", Input)
        uid_input = self.query_one("#uid", Input)
        level_input = self.query_one("#level", Input)
        username_input.value = ""
        password_input.value = ""
        uid_input.value = ""
        level_input.value = ""

        self.search_entries()

    def search_entries(self):
        search_query = self.query_one("#search", Input).value.strip()
        with Session(engine) as session:
         try:
            if search_query in RANK_MAP:
                rank_value = RANK_MAP[search_query]
                valid_ranks = get_valid_ranks(rank_value, RANK_MAP, RANKS)
                results = User.get_users_by_ranks(session, valid_ranks)
            else:
                results = User.get_users_by_username(session, search_query)
         except Exception as e:
                logger.error(f"Error searching for users: {e}")
                self.push_screen(ErrorScreen("An error occurred while searching. Try again."))
                return
        
        table = self.query_one(DataTable)
        table.clear()
        for row in results:
            table.add_row(
                row.username,
                row.password,
                row.uid,
                row.level,
                row.rank
            )

    def save_edit(self):
        selected_row = self.query_one(DataTable).cursor_row
        if selected_row is None:
            self.push_screen(ErrorScreen("No user selected. Please choose a row before editing."))
            return
        else: 
           o_username = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 0))
           o_uid = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 2))

        username = self.query_one("#edit_username", Input).value.strip()
        password = self.query_one("#edit_password", Input).value.strip()
        uid = self.query_one("#edit_uid", Input).value.strip()
        if uid == "":
            uid = None
        level = self.query_one("#edit_level", Input).value
        if level == "":
            level = None
        rank = self.query_one("#edit_rank", Select).value
        
        if not username or not password or rank is Select.BLANK:
            self.push_screen(ErrorScreen("Username, password, and rank are required fields!"))
            return

        rank_value = RANK_MAP[rank]
        
        with Session(engine) as session:
            try:
                user = User.get_user_by_username(session, o_username, o_uid)
                if user:
                    user.update_user(session, username, password, rank, rank_value, uid=uid, level=level)
                    print(f"Updated User: {user.username}")
                else:
                    self.push_screen(ErrorScreen(f"Failed to find user: {o_username}. Please try again."))
            except Exception as e:
                logger.error(f"Error updating user '{o_username}': {e}")
                self.push_screen(ErrorScreen("Failed to update user. Please try again."))
                return

        self.search_entries()
        
        self.hide_edit()

    def delete_entry(self):
        selected_row = self.query_one(DataTable).cursor_row
        if selected_row is None:
            self.push_screen(ErrorScreen("No user selected. Please choose a row before editing."))
            return
        else:
            username = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 0))
            password = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 1))
            uid = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 2))
            if uid == "":
                uid = None
            level = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 3))
            if level == "":
                level = None
            rank = self.query_one(DataTable).get_cell_at(Coordinate(selected_row, 4))
            rank_value = RANK_MAP[rank]

            with Session(engine) as session:
                try:
                    if not User.delete_user(session, username, password, rank, rank_value, uid=uid, level=level):
                        self.push_screen(ErrorScreen(f"Failed to delete user: {username}"))
                        return
                except Exception as e:
                    logger.error(f"Error deleting user {username}: {e}")
                    self.push_screen(ErrorScreen("An error occurred while deleting. Try again."))
                    return

        self.search_entries()
        self.hide_edit()


    def hide_edit(self):
        username = self.query_one("#edit_username")
        username.display = False
        username.value = ""
        password = self.query_one("#edit_password")
        password.display = False
        password.value = ""
        uid = self.query_one("#edit_uid")
        uid.display = False
        uid.value = ""
        level = self.query_one("#edit_level")
        level.display = False
        level.value = ""
        rank = self.query_one("#edit_rank")
        rank.display = False
        self.query_one("#save_edit").display = False
        self.query_one("#delete").display = False

if __name__ == "__main__":
    try:
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize the database: {e}")
        exit(1)
        
    RivalsSmurfTracker().run()
