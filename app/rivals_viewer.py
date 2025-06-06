from textual.app import App, ComposeResult
from textual.widgets import Input, Button, Select, DataTable, Header, Footer, Static
from textual.containers import Horizontal, Container
from textual.coordinate import Coordinate
from app.utils.dbo import User, engine, init_db
from app.utils.rank_utils import get_valid_ranks
from app.utils.error_screen import ErrorScreen
from app.utils.stretchy_datatable import StretchyDataTable
from sqlmodel import Session
from app.utils.User_Error import UserError
from app.utils.logger import logger

# Rank Mapping from highest to lowest
RANKS = [
    "Celestial 1", "Celestial 2", "Celestial 3",
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
    Screen{
        width: 100vw;
        height: 100vh;
    }
    .container {
        layout: grid;
        grid-size: 3;
        grid-columns: 1fr 1fr 0.5fr;
        grid-rows: auto;
        grid-gutter:  1 1;
        padding: 1 3;
        content-align: center middle;
        width: 100%;
        height:auto;
    }
    .col-span-2{
        column-span: 2;
    }
    .col-span-3{
        column-span: 3;
    }
    .container > *{
        width:100%;
    }
    #datatable_container{
        padding: 1 3;
        height: auto;
        width: 100%;
    }
    .button--container{
        height: auto;
    }
    Button{ 
        height: auto;
        padding: 1 0;
        min-height: 3; 
        color: white;
        text-style:bold;
        min-width: 10;
    }
    Button:hover, 
    Button:focus {
        outline: wide #0178D4 !important;
    }
     #search_btn {
        background: darkblue;
        outline: wide darkblue;
    }
    #submit_btn, #save_edit{
        background: #004225;
        outline: wide #004225; 
    }
    #delete {
        background: maroon;
        outline: wide maroon;
    }
    .buttons{
        width:50%;
        height:auto;
    }
    .ml-2{
        margin-left:2
    }
    Input{
        border: wide white;
        padding: 1 0;
        height: auto;
        text-align: center;
        color: white;
    }
    Input:hover,  Select:hover > SelectCurrent, Select:focus > SelectCurrent , Input:focus{
        border: wide  #0178D4;
    }
     Select > SelectCurrent {
        border: wide white;
        padding: 1 0;
        width: 100%;
        height: auto;
    }
    .datatable {
        min-height: 10vh;
        width: 100%;
        height: 30vh;
        overflow-x: hidden;
    }
   #create_user_prompt, #edit_user_prompt{
        width: 100%;
        max-height: 12vh;
        margin: 1 0;
        text-align: left;
    }
    #edit_user_prompt{
        margin-bottom: 3;
    }

    """
    BINDINGS = [("ctrl+q", "quit", "CTRL+Q to Quit")]

    def compose(self) -> ComposeResult:

        yield Header()

        with Container(id="create_user_container", classes="container"):
            
            # Create user content
            yield Static("Fill in the details below to create a new user entry. Username, password, and rank are required fields. You can also search for existing users using the search box.", id="create_user_prompt", classes="col-span-3")

            username_input = Input(placeholder="Enter your username", id="username", classes="username-border")
            username_input.border_title = "Username"
            yield username_input
           
            user_password = Input(placeholder="Enter your password", id="password", password=True, classes="userpass")
            user_password.border_title ="Password"
            yield  user_password

            userrank_selection = Select([(rank, rank) for rank in RANKS], prompt="Select ", id="rank", classes="selection")
            userrank_selection.border_title="Rank"
            yield userrank_selection

            user_uid = Input(placeholder ="Enter your UID", id="uid", classes="useruid")
            user_uid.border_title="UID"
            yield  user_uid

            user_level = Input(placeholder="Enter your level", id="level", classes="userlevel")
            user_level.border_title = "Level"
            yield user_level

            yield Button("Submit", id="submit_btn", classes="submit ")
 
            search_input = Input(placeholder="Search by username or rank", id="search", classes="search col-span-2")
            search_input.border_title = "Search"
            yield search_input

            yield Button("Search", id="search_btn", classes="search ")
            
        # Search content
        with Container(id="datatable_container"):
            yield Static("Click on the row you would like to edit or delete.", id="edit_user_prompt", classes="col-span-3")

            yield StretchyDataTable(id="results", cursor_type="row", classes="datatable")

        with Container(id="edit_container", classes="container"):
            edit_username = Input(placeholder="Edit Username", id="edit_username", classes="edit")
            edit_username.border_title = "Edit Username"
            yield edit_username

            edit_password = Input(placeholder="Edit Password", id="edit_password", password=True, classes="edit")
            edit_password.border_title = "Edit Password"
            yield edit_password

            edit_rank = Select([(rank, rank) for rank in RANKS], id="edit_rank", classes="editrank")
            edit_rank.border_title = "Edit Rank"
            yield edit_rank  

            edit_uid = Input(placeholder="Edit UID", id="edit_uid", classes="edit")
            edit_uid.border_title = "Edit UID"
            yield edit_uid

            edit_level = Input(placeholder="Edit Level", id="edit_level", classes="edit")
            edit_level.border_title = "Edit Level"
            yield edit_level

            yield Static() #Empty grid cell 

            yield Static()

            with Horizontal(classes="button--container"):
                yield Button("Save Changes", id="save_edit", classes="edit buttons")
                yield Button("Delete", id="delete", classes="edit buttons ml-2")

        yield Footer()

    def on_mount(self) -> None:

        user_rank_select = self.query_one("#rank", Select)
        user_rank_current = user_rank_select.query_one("SelectCurrent")
        user_rank_current.border_title ="Rank"

        edit_rank_select = self.query_one("#edit_rank", Select)
        edit_rank_current = edit_rank_select.query_one("SelectCurrent")
        edit_rank_current.border_title = "Edit Rank"

        table = self.query_one(DataTable)
        table.add_column("Username", width=25)
        table.add_column("Password", width=25)
        table.add_column("UID", width=25)
        table.add_column("Level", width=25)
        table.add_column("Rank", width=25)

    def on_button_pressed(self, event) -> None:
        if event.button.id == "submit_btn":
            self.store_entry()
        elif event.button.id == "search_btn":
            self.search_entries()
        elif event.button.id == "save_edit":
            self.save_edit()
        elif event.button.id == "delete":
            self.delete_entry()

    def on_data_table_row_selected(self, event: StretchyDataTable.RowSelected) -> None:
        
        self.query_one("#edit_container").display = True

        username = self.query_one("#edit_username")
        username.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 0)))

        password = self.query_one("#edit_password")
        password.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 1)))

        uid = self.query_one("#edit_uid")
        uid.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 2)) or "")

        level = self.query_one("#edit_level")
        level.value = str(self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 3)) or "")

        rank = self.query_one("#edit_rank")
        rank.value = self.query_one(DataTable).get_cell_at(Coordinate(event.cursor_row, 4)) or Select.BLANK
        
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
                rank_match = None
                for rank in RANK_MAP:
                    if rank.lower() == search_query.lower():
                        rank_match = rank
                        break
                if rank_match:
                    rank_value = RANK_MAP[rank_match]
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
        self.query_one("#edit_container").display = False

def main_run() -> None:
    try:
        init_db()
    except Exception as e:
        logger.error(f"Failed to initialize the database: {e}")
        exit(1)
        
    RivalsSmurfTracker().run()
