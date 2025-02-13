import pytest
import sqlite3
from unittest.mock import patch
from app.utils.dbo import *

@pytest.fixture
def in_memory_db():
    """Create an database for testing."""

    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            uuid Text,
            level INTEGER,
            rank TEXT,
            rank_value INTEGER
        )
    """)
    conn.commit()
    yield conn
    conn.close()

def test_store_to_db(in_memory_db):
    """Test if store_to_db correctly inserts data"""

    store_to_db("test_user", "test_pass","test_uuid", 1,"Eternal 1", 0, in_memory_db)

    cursor =in_memory_db.cursor()
    cursor.execute("SELECT username, password, uuid, level, rank, rank_value FROM users WHERE username=?", ("test_user",))
    user = cursor.fetchone()

    assert user is not None
    assert user == ("test_user", "test_pass", "test_uuid", 1, "Eternal 1", 0)


def test_delete_db(in_memory_db):
    """Test if delete_db correctly removes data"""

    store_to_db("test_user", "test_pass", "test_uuid", 1, "Eternal 1", 0, in_memory_db)

    delete_db("test_user", "test_pass", "Eternal 1", 0, in_memory_db)

    cursor = in_memory_db.cursor()
    cursor.execute("SELECT username FROM users WHERE username=?", ("test_user",))
    user = cursor.fetchone()
    assert user is None
