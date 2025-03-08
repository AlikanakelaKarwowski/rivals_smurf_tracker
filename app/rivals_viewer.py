from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Select, DataTable, Header, Footer, Static
from textual.containers import Horizontal, Vertical, Container, HorizontalGroup
from textual.coordinate import Coordinate
from utils.dbo import User, engine, init_db
from utils.rank_utils import get_valid_ranks
from utils.error_screen import ErrorScreen
from sqlmodel import Session
from utils.UserError import UserError
from utils.logger import logger

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
    .container {
        layout: grid;
        grid-size: 3;
        grid-columns: 3fr 3fr 3fr;
        grid-rows: auto auto auto;
        grid-gutter: 2 2;
        padding: 2;
        content-align: center middle;
        width: 100vw;
        height: 100vh;
        max-width: 100vw;
    }
    .col-span-2{
        column-span: 2;
    }
    .col-span-3{
        column-span: 3;
    }
    Select{
        min-width: 40;
        width:90%;
    }
    .container > *{
        width:100%;
    }
    
    #edit_prompt,
    #edit_username,
    #edit_password,
    #edit_rank,
    #save_edit,
    #delete,
    .edit {
        display: none;
    }

    #save_edit {
        background: green;
    }

    #delete {
        background: maroon;
    }

    #edit_buttons {
        height: auto; 
        min-height: 3; 
        padding-bottom: 1; 
    }
    #submit {
        background: green;
        color: white;
    }
    #search_btn {
        background: blue;
        color: white;
    }
    .button--container{
        align: center middle;
    }
    .button--container> *{
        width:100%;
    }
    .buttons{
        width:15%;
        height:auto;
    }
    .ml-2{
        margin-left:2
    }
  
    """
    BINDINGS = [("ctrl+q", "quit", "CTRL+Q to Quit")]

    def compose(self) -> ComposeResult:

        yield Header()

        with Container(classes="container"):
            # create user content
            
            #ROW1
            yield Input(placeholder="Enter your username", id="username", classes="username")
            yield Input(placeholder="Enter your password", id="password", password=True, classes="userpass")
            yield Select([(rank, rank) for rank in RANKS], prompt="Select a rank", id="rank", classes="selection")

            #ROW2
            yield Input(placeholder ="Enter your UID", id="uid", classes="useruid")
            yield Input(placeholder="Enter your level", id="level", classes="userlevel")
            yield Static()
           
        
            #ROW3
            yield Input(placeholder="Search by username or rank", id="search", classes="search col-span-2")
            yield Static()

            with Horizontal(classes="col-span-3 button--container"):
                yield Button("Search", id="search_btn", classes="search buttons")
                yield Button("Submit", id="submit", classes="selection buttons ml-2")

            # Search content
            yield DataTable(id="results", cursor_type="row", classes="results col-span-3")
            yield Static("Click an entry to edit", id="edit_prompt", classes="results col-span-3")

            # row 1
            yield Input(placeholder="Edit Username", id="edit_username", classes="edit")
            yield Input(placeholder="Edit Password", id="edit_password", password=True, classes="edit")
            yield Select([(rank, rank) for rank in RANKS], id="edit_rank", classes="editrank")

            #row 2
            yield Input(placeholder="Edit uid", id="edit_uid", classes="edit")
            yield Input(placeholder="Edit Level", id="edit_level", classes="edit")
            yield Static()
            
            with Horizontal(classes="col-span-3 button--container"):
                yield Button("Save Changes", id="save_edit", classes="edit buttons")
                yield Button("Delete", id="delete", classes="edit buttons ml-2")
        
        yield Footer()

    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns("Username", "Password", "UID", "Level", "Rank")

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
