import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy import and_
from app.utils.dbo import User

@pytest.fixture
def in_memory_db():
    """Create an in-memory database for testing with SQLModel."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()

# create_user test group
def test_create_user(in_memory_db):
    """Test if User.create correctly inserts data into the in-memory database."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user", "test_pass", "test_uuid", 1, "Eternal 1", 0)
    
        statement = select(User).where(User.username == "test_user")
        user = session.exec(statement).first()

        assert user is not None
        assert user.username == "test_user"
        assert user.password == "test_pass"
        assert user.uuid == "test_uuid"
        assert user.level == 1
        assert user.rank == "Eternal 1"
        assert user.rank_value == 0


def test_get_user_by_username(in_memory_db):
    """Test if User.get_user_by_username retrieves a single user correctly."""
    with Session(in_memory_db) as session:
        created_user = User.create_user(session, "test_user", "test_pass", "test_uuid", 25, "Gold 2", 7)

        user = User.get_user_by_username(session, "test_user", "test_uuid")

        assert user is not None
        assert user.username == created_user.username
        assert user.password == created_user.password
        assert user.uuid == created_user.uuid
        assert user.level == created_user.level
        assert user.rank == created_user.rank
        assert user.rank_value == created_user.rank_value

def test_get_users_by_username(in_memory_db):
    """Test if User.get_users_by_username retrieves users by username."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user1", "pass1", "uuid1", 10, "Gold 1", 5)
        User.create_user(session, "test_user2", "pass2", "uuid2", 20, "Silver 3", 3)
    
        results = User.get_users_by_username(session, "test_user1")
        assert len(results) == 1
        assert results[0].username == "test_user1"

def test_get_users_by_ranks(in_memory_db):
    """Test if User.get_users_by_ranks retrieves users by rank value."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user1", "pass1", "uuid1", 15, "Gold 1", 10)
        User.create_user(session, "test_user2", "pass2", "uuid2", 18, "Gold 2", 11)
        User.create_user(session, "test_user3", "pass3", "uuid3", 25, "Platinum 1", 15)
    
        results = User.get_users_by_ranks(session, [10, 11])
        assert len(results) == 2
        usernames = [r.username for r in results]
        assert "test_user1" in usernames
        assert "test_user2" in usernames
        assert "test_user3" not in usernames

def test_update_user(in_memory_db):
    """Test if User.update_user correctly updates user information."""
    with Session(in_memory_db) as session:
        user = User.create_user(session, "old_user", "old_pass", "old_uuid", 30, "Bronze 1", 1)

        user = session.exec(select(User).where(User.username == "old_user")).first()
        assert user is not None  # Assert user not None

        user.update_user(session, "Chillbert", "Chi11", "new_uuid", 40, "Silver 2", 5)

        updated_user = session.exec(select(User).where(User.uuid == "new_uuid")).first()

         # Assert user has been updated
        assert updated_user is not None
        assert updated_user.username == "Chillbert"
        assert updated_user.password == "Chi11"
        assert updated_user.uuid == "new_uuid"
        assert updated_user.level == 40
        assert updated_user.rank == "Silver 2"
        assert updated_user.rank_value == 5

        
        old_user = session.exec(select(User).where(User.username == "old_user")).first()
        assert old_user is None # Assert old user no longer exists



def test_delete_user(in_memory_db):
    """Test if User.delete_user correctly removes a user from database."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user", "del_pass", "del_uuid", 50, "Diamond 3", 13)
    
        success = User.delete_user(session, "test_user", "del_pass", "del_uuid", 50, "Diamond 3", 13)
        assert success is True
    
        statement = select(User).where(and_(User.username == "test_user", User.uuid == "del_uuid"))
        user = session.exec(statement).first()
        assert user is None
