import sqlite3
def init_db() -> None:
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            uuid TEXT,
            level INTEGER,
            rank TEXT,
            rank_value INTEGER
        )
    """)
    conn.commit()
    conn.close()

def store_to_db(username: str, password: str, uuid: str, level: int, rank: str, rank_value: int,  db_connection=None) -> None:
    conn = db_connection or sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, uuid, level, rank, rank_value) VALUES (?, ?, ?, ?, ?, ?)",
                   (username, password, uuid, level, rank, rank_value))
    conn.commit()
    if db_connection is None:  
        conn.close()

def search_rank_db(search_query:str, db_connection=None) -> list[tuple[str,str,str]]:
    conn = db_connection or sqlite3.connect("users.db")
    cursor = conn.cursor()
   
    cursor.execute("SELECT username, password, uuid, level, rank FROM users WHERE rank_value IN ({})".format(
        ",".join(map(str, search_query))))
        
    results = cursor.fetchall()
    if db_connection is None:  
        conn.close()
    return results

def search_user_db(search_query:str, db_connection=None) -> list[tuple[str,str,str]]:
    conn = db_connection or sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, uuid, level, rank FROM users WHERE username LIKE ?", (f"%{search_query}%",))
    results = cursor.fetchall()
    if db_connection is None:  
        conn.close()
    return results

def update_db(username:str, o_username:str, password:str, o_password:str, uuid:str, o_uuid:str, level:int, o_level:int, rank:str, o_rank:str, rank_value:int, o_rank_value:int,  db_connection=None) -> None:
    conn = db_connection or sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username = ?, password = ?, uuid = ?, level = ?, rank = ?, rank_value = ? WHERE username = ? AND password = ? AND uuid = ? AND level = ? AND rank = ? AND rank_value = ?",
                    (username, password, uuid, level, rank, rank_value, o_username, o_password, o_uuid, o_level, o_rank, o_rank_value))
    conn.commit()
    if db_connection is None:
        conn.close()

def delete_db(username: str, password: str, rank: str, rank_value: int, db_connection=None) -> None:
    conn = db_connection or sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = ? AND password = ? AND rank = ? AND rank_value = ?",
                    (username, password, rank, rank_value),)
    conn.commit()
    if db_connection is None:
        conn.close()
