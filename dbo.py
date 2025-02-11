import sqlite3
from utils.rank_utils import get_valid_ranks
def init_db() -> None:
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

def store_to_db(username:str, password:str, rank:str, rank_value:int) -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, rank, rank_value) VALUES (?, ?, ?, ?)",
                    (username, password, rank, rank_value))
    conn.commit()
    conn.close()

def search_db(search_query:str, RANK_MAP: dict[str,int], RANKS: list[str]) -> list[tuple[str,str,str]]:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    if search_query in RANK_MAP:
        rank_value = RANK_MAP[search_query]
        valid_ranks = get_valid_ranks(rank_value, RANK_MAP, RANKS)
        cursor.execute("SELECT username, password, rank FROM users WHERE rank_value IN ({})".format(
            ",".join(map(str, valid_ranks))))
    else:
        cursor.execute("SELECT username, password, rank FROM users WHERE username LIKE ?", (f"%{search_query}%",))
        
    results = cursor.fetchall()
    conn.close()
    return results

def update_db(username:str, o_username:str, password:str, o_password:str, rank:str, o_rank:str, rank_value:int, o_rank_value:int,) -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, password = ?, rank = ?, rank_value = ? WHERE username = ? AND password = ? AND rank = ? AND rank_value = ?",
                    (username, password, rank, rank_value, o_username, o_password, o_rank, o_rank_value))
    conn.commit()
    conn.close()

def delete_db(username:str, password:str, rank:str, rank_value:int) -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ? AND password = ? AND rank = ? AND rank_value = ?",
                    (username, password, rank, rank_value))
    conn.commit()
    conn.close()
