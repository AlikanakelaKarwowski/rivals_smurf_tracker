import pytest
from sqlmodel import SQLModel, Session, create_engine, select, and_
from utils.dbo import User, init_db
from utils.UserError import UserError
import logging

# Capture logs during tests
logging.basicConfig(level=logging.INFO)

# init_db test group
def test_init_db_success(caplog):
    """Test that init_db initializes the database without errors."""
    with caplog.at_level(logging.INFO):
        init_db()
        assert "Database initialized successfully" in caplog.text

def test_init_db_invalid_connection(caplog):
    """Test that init_db logs an error with an invalid connection string."""
    invalid_engine = create_engine("sqlite:///invalid_path/users.db")
    
    with caplog.at_level(logging.ERROR):
        try:
            init_db(engine=invalid_engine)
        except Exception:
            pass
        assert "Error initializing database" in caplog.text

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
        # Test Normal create user
        User.create_user(session, "test_user", "test_pass", "Eternal 1", 0, uid="test_uid", level=1)
        statement = select(User).where(User.username == "test_user")
        user = session.exec(statement).first()

        assert user is not None
        assert user.username == "test_user"
        assert user.password == "test_pass"
        assert user.uid == "test_uid"
        assert user.level == 1
        assert user.rank == "Eternal 1"
        assert user.rank_value == 0

        # Test create user without uid
        User.create_user(session, "test_user2", "test_pass2", "Eternal 2", 1, level=2)
        statement = select(User).where(User.username == "test_user2")
        user = session.exec(statement).first()

        assert user is not None
        assert user.username == "test_user2"
        assert user.password == "test_pass2"
        assert user.uid is None
        assert user.level == 2
        assert user.rank == "Eternal 2"
        assert user.rank_value == 1

        # Test create user without level
        User.create_user(session, "test_user3", "test_pass3","Eternal 3", 2, uid="test_uid3")
        statement = select(User).where(User.username == "test_user3")
        user = session.exec(statement).first()

        assert user is not None
        assert user.username == "test_user3"
        assert user.password == "test_pass3"
        assert user.uid == "test_uid3"
        assert user.level is None
        assert user.rank == "Eternal 3"
        assert user.rank_value == 2

        # Test create user without uid/level
        User.create_user(session, "test_user4", "test_pass4", "Eternal 3", 2)
        statement = select(User).where(User.username == "test_user4")
        user = session.exec(statement).first()

        assert user is not None
        assert user.username == "test_user4"
        assert user.password == "test_pass4"
        assert user.uid is None
        assert user.level is None
        assert user.rank == "Eternal 3"
        assert user.rank_value == 2

        # Test create user without uid/level/rank/rank_value
        # Add error assertion for test case where username is None
        with pytest.raises(TypeError):
            User.create_user(session, "test_user5", "test_pass5")
        
def test_create_duplicate_user(in_memory_db):
    """Test that creating a user with a duplicate username and uid is handled correctly."""
    with Session(in_memory_db) as session:

        user1 = User.create_user(session, "test_user", "test_pass", "Eternal 1", 0, uid="test_uid", level=1)
        assert user1 is not None 

        # Assert to create a duplicate user
        with pytest.raises(UserError, match="A user with this username already exists."):
            User.create_user(session, "test_user", "test_pass2", "Eternal 2", 1, uid="test_uid", level=2)

        # Assert that None is not considered unique if no value is passed in for uid
        user3 = User.create_user(session, "test_user1", "test_pass3", "Eternal 3", 2)
        assert user3 is not None

        user4 = User.create_user(session, "test_user2", "test_pass3", "Eternal 4", 3)
        assert user4 is not None

        # Assert that username is unique
        with pytest.raises(UserError, match="A user with this username already exists."):
            User.create_user(session, "test_user1", "test_pass4", "Eternal 5", 4)

        # Assert that uid is unique
        with pytest.raises(UserError, match="A user with this uid already exists."):
             User.create_user(session, "test_user19", "test_pass2", "Eternal 2", 1, uid="test_uid", level=2)
             
        # Assert that only one user exists in the database
        users = session.exec(select(User).where(User.username == "test_user")).all()
        assert len(users) == 1
        assert users[0].username == "test_user"
        assert users[0].uid == "test_uid"

def test_create_user_exception_handling(in_memory_db):
    """Test that create_user handles exceptions gracefully."""
    with Session(in_memory_db) as session:
        session.close()  

        with pytest.raises(Exception):
            result = User.create_user(session, "test_user1", "pass1", "Gold 1", 10, uid="test_uid", level=1)
            assert result is None

def test_does_user_exists(in_memory_db):
    """Test if does_user_exists correctly identifies existing and non-existing users."""
    with Session(in_memory_db) as session:
       
        User.create_user(session, "test_user", "test_pass", "Eternal 1", 0, uid="test_uid", level=1)
        
        # Assert if the user exists
        exists = User.does_user_exists(session, "test_user", "test_uid")
        assert exists is True 

        # Assert if a non-existing user exists
        not_exists = User.does_user_exists(session, "non_existing_user", "non_existing_uid")
        assert not_exists is False  
      

def test_get_user_by_username(in_memory_db):
    """Test if User.get_user_by_username retrieves a single user correctly."""
    with Session(in_memory_db) as session:
        # Test with both username and uid
        created_user = User.create_user(session, "test_user", "test_pass", "Gold 2", 7, uid="test_uid", level=1)
        user = User.get_user_by_username(session, "test_user", "test_uid")

        assert user is not None
        assert user.username == created_user.username
        assert user.password == created_user.password
        assert user.uid == created_user.uid
        assert user.level == created_user.level
        assert user.rank == created_user.rank
        assert user.rank_value == created_user.rank_value

        # Test with only username
        created_user1 = User.create_user(session, "test_user1", "test_pass1", "Gold 2", 7, level=1)
        user1 = User.get_user_by_username(session, "test_user1", uid=None)

        assert user1 is not None
        assert user1.username == created_user1.username
        assert user1.password == created_user1.password
        assert user1.uid is None
        assert user1.level == created_user1.level
        assert user1.rank == created_user1.rank
        assert user1.rank_value == created_user1.rank_value

        # Test without specifying uid
        created_user2 = User.create_user(session, "test_user2", "test_pass2", "Gold 2", 7, level=1)
        user2 = User.get_user_by_username(session, "test_user2")

        assert user2 is not None
        assert user2.username == created_user2.username
        assert user2.password == created_user2.password
        assert user2.uid is None
        assert user2.level == created_user2.level
        assert user2.rank == created_user2.rank
        assert user2.rank_value == created_user2.rank_value

def test_get_user_by_username_exception_handling(in_memory_db):
    """Test that get_user_by_username handles exceptions gracefully."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user1", "pass1", "Gold 1", 10, uid="test_uid", level=1)
        session.close()  

        with pytest.raises(Exception):
            result = User.get_user_by_username(session, "test_user1", "test_uid")
            assert result is None

def test_get_users_by_username(in_memory_db):
    """Test if User.get_users_by_username retrieves users by username."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user1", "pass1", "Gold 1", 5, uid="test_uid", level=1)
        User.create_user(session, "test_user2", "pass2", "Silver 3", 3, uid="test_uid2", level=2)
    
        results = User.get_users_by_username(session, "test_user1")
        assert len(results) == 1
        assert results[0].username == "test_user1"
        results2 = User.get_users_by_username(session, "test")
        assert len(results2) == 2
        assert results2[0].username == "test_user1"
        assert results2[1].username == "test_user2"

        User.create_user(session, "test_user3", "pass1", "Gold 1", 5)
        User.create_user(session, "test_user4", "pass2", "Silver 3", 3)
    
        results3 = User.get_users_by_username(session, "test_user3")
        assert len(results3) == 1
        assert results3[0].username == "test_user3"
        results4 = User.get_users_by_username(session, "test")
        assert len(results4) == 4
        assert results4[0].username == "test_user1"
        assert results4[1].username == "test_user2"
        assert results4[2].username == "test_user3"
        assert results4[3].username == "test_user4"

        results5 = User.get_users_by_username(session, "user")
        assert len(results5) == 4
        assert results5[0].username == "test_user1"
        assert results5[1].username == "test_user2"
        assert results5[2].username == "test_user3"
        assert results5[3].username == "test_user4"

        results6 = User.get_users_by_username(session, "user5")
        assert len(results6) == 0

def test_get_users_by_username_exception_handling(in_memory_db):
    """Test that get_users_by_username handles exceptions gracefully."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user1", "pass1", "Gold 1", 10, uid="test_uid", level=1)
        session.close()  

        with pytest.raises(Exception):
            results = User.get_users_by_username(session, "test_user1")
            assert results == []

def test_get_users_by_ranks(in_memory_db):
    """Test if User.get_users_by_ranks retrieves users by rank value."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user1", "pass1", "Gold 1", 10, uid="test_uid", level=1)
        User.create_user(session, "test_user2", "pass2", "Gold 2", 11, uid="test_uid2")
        User.create_user(session, "test_user3", "pass3", "Platinum 1", 15, level=20)

    
        results = User.get_users_by_ranks(session, [10, 11])
        assert len(results) == 2
        usernames = [r.username for r in results]
        assert "test_user1" in usernames
        assert "test_user2" in usernames
        assert "test_user3" not in usernames

def test_get_users_by_ranks_exception_handling(in_memory_db):
    """Test that get_users_by_ranks handles exceptions gracefully."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user1", "pass1", "Gold 1", 10, uid="test_uid", level=1)
        session.close()  

        with pytest.raises(Exception):
            results = User.get_users_by_ranks(session, [10, 11])
            assert results == []

# update_user test group
def test_update_user(in_memory_db):
    """Test if User.update_user correctly updates user information."""
    with Session(in_memory_db) as session:
        user = User.create_user(session, "old_user", "old_pass", "Bronze 1", 1, uid="old_uid", level=10)

        user = session.exec(select(User).where(User.username == "old_user")).first()
        assert user is not None  # Assert user not None

        user.update_user(session, "Chillbert", "Chi11", "Silver 2", 5, uid="new_uid", level=40)

        updated_user = session.exec(select(User).where(User.uid == "new_uid")).first()

         # Assert user has been updated
        assert updated_user is not None
        assert updated_user.username == "Chillbert"
        assert updated_user.password == "Chi11"
        assert updated_user.uid == "new_uid"
        assert updated_user.level == 40
        assert updated_user.rank == "Silver 2"
        assert updated_user.rank_value == 5

        
        old_user = session.exec(select(User).where(User.username == "old_user")).first()
        assert old_user is None # Assert old user no longer exists

def test_update_non_existent_user(in_memory_db):
    """Test that updating a non-existent user fails gracefully."""
    with Session(in_memory_db) as session:
        user = session.exec(select(User).where(User.username == "non_exist_user")).first()
        assert user is None  

        with pytest.raises(AttributeError):
            user.update_user(session, "new_user", "new_pass", "new_uid", 40, "Silver 2", 5)

def test_update_user_exception_handling(in_memory_db):
    """Test that update_user handles exceptions gracefully."""
    with Session(in_memory_db) as session:
        # Create a user to update
        user = User.create_user(session, "test_user", "test_pass", "Gold 1", 10, uid="test_uid", level=1)

        with pytest.raises(Exception):
            user.update_user(session, None, "new_pass", "Silver 2", 5, uid="new_uid", level=40)

# delete_user test group
def test_delete_user(in_memory_db):
    """Test if User.delete_user correctly removes a user from database."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user", "del_pass", "Diamond 3", 13, uid="del_uid", level=50)
    
        success = User.delete_user(session, "test_user", "del_pass", "Diamond 3", 13, uid="del_uid", level=50)
        assert success is True
    
        statement = select(User).where(and_(User.username == "test_user", User.uid == "del_uid"))
        user = session.exec(statement).first()
        assert user is None

def test_delete_non_existent_user(in_memory_db):
    """Test that deleting a non-exist user fails gracefully."""
    with Session(in_memory_db) as session:
        success = User.delete_user(session, "Im_not_real", "pass", "Rank", 0, uid="uid", level=0)
        assert success is False 


def test_delete_user_exception_handling(in_memory_db):
    """Test that delete_user handles exceptions gracefully."""
    with Session(in_memory_db) as session:
        User.create_user(session, "test_user", "test_pass", "Gold 1", 10, uid="test_uid", level=1)

        # Force an exception by closing the session before deletion
        session.close()

        with pytest.raises(Exception):
            success = User.delete_user(session, "test_user", "test_pass", "Gold 1", 10, uid="test_uid", level=1)
            assert success is False


def test_empty_database_retrieval(in_memory_db):
    """Test that retrieving users from an empty database returns an empty list."""
    with Session(in_memory_db) as session:
        users_by_username = User.get_users_by_username(session, "any_user")
        assert users_by_username == []

        users_by_ranks = User.get_users_by_ranks(session, [1, 2, 3])
        assert users_by_ranks == []
