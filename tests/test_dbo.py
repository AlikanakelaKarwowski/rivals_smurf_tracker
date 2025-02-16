import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from app.utils.dbo import (
    User,
    store_to_db,
    search_user_db,
    search_rank_db,
    update_db,
    delete_db,
)

@pytest.fixture
def in_memory_db():
    """Create an in-memory database for testing with SQLModel."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()

def test_store_to_db(in_memory_db):
    """Test if store_to_db correctly inserts data into the in-memory database."""
    store_to_db("test_user", "test_pass", "test_uuid", 1, "Eternal 1", 0, custom_engine=in_memory_db)

    with Session(in_memory_db) as session:
        statement = select(User).where(User.username == "test_user")
        user = session.exec(statement).first()

        assert user is not None
        assert user.username == "test_user"
        assert user.password == "test_pass"
        assert user.uuid == "test_uuid"
        assert user.level == 1
        assert user.rank == "Eternal 1"
        assert user.rank_value == 0

def test_search_user_db(in_memory_db):
    """Test if search_user_db retrieves users by username."""
    store_to_db("test_user1", "pass1", "uuid1", 10, "Gold 1", 5, custom_engine=in_memory_db)
    store_to_db("test_user2", "pass2", "uuid2", 20, "Silver 3", 3, custom_engine=in_memory_db)

    results = search_user_db("test_user1", custom_engine=in_memory_db)

    assert len(results) == 1
    assert results[0] == ("test_user1", "pass1", "uuid1", 10, "Gold 1")

def test_search_rank_db(in_memory_db):
    """Test if search_rank_db retrieves users by rank value."""
    store_to_db("test_user1", "pass1", "uuid1", 15, "Gold 1", 10, custom_engine=in_memory_db)
    store_to_db("test_user2", "pass2", "uuid2", 18, "Gold 2", 11, custom_engine=in_memory_db)
    store_to_db("test_user3", "pass3", "uuid3", 25, "Platinum 1", 15, custom_engine=in_memory_db)

    results = search_rank_db([10, 11], custom_engine=in_memory_db)

    assert len(results) == 2
    usernames = [r[0] for r in results]
    assert "test_user1" in usernames
    assert "test_user2" in usernames
    assert "test_user3" not in usernames

def test_update_db(in_memory_db):
    """Test if update_db correctly updates user information."""
    store_to_db("old_user", "old_pass", "old_uuid", 30, "Bronze 1", 1, custom_engine=in_memory_db)

    update_db(
        username="Chillbert",
        o_username="old_user",
        password="Chi11",
        o_password="old_pass",
        uuid="new_uuid",
        o_uuid="old_uuid",
        level=40,
        o_level=30,
        rank="Silver 2",
        o_rank="Bronze 1",
        rank_value=5,
        o_rank_value=1,
        custom_engine=in_memory_db
    )

    with Session(in_memory_db) as session:
        statement = select(User).where(User.username == "Chillbert")
        user = session.exec(statement).first()

        # Assert user has been updated
        assert user is not None
        assert user.username == "Chillbert"
        assert user.password == "Chi11"
        assert user.uuid == "new_uuid"
        assert user.level == 40
        assert user.rank == "Silver 2"
        assert user.rank_value == 5

        # Assert old user no longer exists
        old_user = session.exec(select(User).where(User.username == "old_user", User.uuid == "old_uuid")).first()
        assert old_user is None


def test_delete_db(in_memory_db):
    """Test if delete_db correctly removes a user from the database."""
    store_to_db("test_user", "del_pass", "del_uuid", 50, "Diamond 3", 13, custom_engine=in_memory_db)

    delete_db(
        username="test_user",
        password="del_pass",
        uuid="del_uuid",
        level=50,
        rank="Diamond 3",
        rank_value=13,
        custom_engine=in_memory_db
    )

    with Session(in_memory_db) as session:
        statement = select(User).where(User.username == "test_user", User.uuid == "del_uuid")
        user = session.exec(statement).first()
        assert user is None
