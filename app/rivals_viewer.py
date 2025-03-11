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
        grid-columns: 1fr 1fr 0.5fr;
        grid-rows: auto;
        grid-gutter:  1 1;
        padding: 1 3;
        content-align: center middle;
        width: 100%;
        overflow: auto;
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
    #edit_prompt,
    #edit_username,
    #edit_password,
    #edit_rank,
    #save_edit,
    #delete,
    .edit {
        display: none;
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
    #edit_buttons {
        height: auto; 
        min-height: 3; 
        padding-bottom: 1; 
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
        width: 100%;
        height: 50vh;
        min-height: 10vh; 
        overflow: auto;
    }
    #edit_user_prompt{
        padding: 2 0;
    }

   #create_user_prompt, #edit_user_prompt{
        width: 100%;
        max-height: 12vh;
        text-align: left;
    }
    """
    BINDINGS = [("ctrl+q", "quit", "CTRL+Q to Quit")]

    def compose(self) -> ComposeResult:

        yield Header()

        with Container(classes="container"):
            
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

            yield Button("Search", id="search_btn", classes="search ")
           
            search_input = Input(placeholder="Search by username or rank", id="search", classes="search col-span-2")
            search_input.border_title = "Search"
            yield search_input

        
            yield Button("Submit", id="submit_btn", classes="submit ")

            # Search content
            yield Static("Click on the row you would like to edit or delete.", id="edit_user_prompt", classes="col-span-3")

            yield DataTable(id="results", cursor_type="row", classes="datatable col-span-3")

        
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

            yield Static()
        
        yield Footer()

    def on_mount(self) -> None:

        user_rank_select = self.query_one("#rank", Select)
        user_rank_current = user_rank_select.query_one("SelectCurrent")
        user_rank_current.border_title =" Rank"

        edit_rank_select = self.query_one("#edit_rank", Select)
        edit_rank_current = edit_rank_select.query_one("SelectCurrent")
        edit_rank_current.border_title = "Edit Rank"

        table = self.query_one(DataTable)
        table.add_column("Username")
        table.add_column("Password")
        table.add_column("UID")
        table.add_column("Level")
        table.add_column("Rank")

    def on_button_pressed(self, event) -> None:
        if event.button.id == "submit_btn":
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
