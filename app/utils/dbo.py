from sqlmodel import SQLModel, Field, Session, create_engine, select, and_, or_
from typing import Optional
import logging
from utils.UserError import UserError

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    uid: str | None = Field(index=True, unique=True, nullable=True)
    level: int | None = Field(default=None, nullable=True)
    rank: str
    rank_value: int
    
    def save(self, session: Session) -> None:
        session.add(self)
        session.commit()

    @classmethod
    def does_user_exists(cls, session: Session, username: str = None, uid: str = None) -> bool:
        """Check if a user with the given username or uid exists."""
        if not username and not uid:
            return False  
        
        try:
            statement = select(cls).where(
                or_(cls.username == username if username else False,
                    cls.uid == uid if uid else False)
            )
            return session.exec(statement).first() is not None
        except Exception as e:
            logging.error(f"Error in does_user_exists: {e}")
            return False

    @classmethod
    def create_user(cls, session: Session, username: str, password: str, rank: str, rank_value: int, uid: str | None = None, level: int | None = None,) -> Optional["User"]:
        """Create and save a new user."""
        try:
            if uid:
                uid = uid.strip()
                
            if cls.does_user_exists(session, username=username):
                raise UserError("A user with this username already exists.")

            if uid and cls.does_user_exists(session, uid=uid):
                raise UserError("A user with this uid already exists.")

            user = cls(username=username, password=password, uid=uid, level=level, rank=rank, rank_value=rank_value)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except (UserError) as u_e:
            session.rollback()
            logging.error(f"UserError in create_user: {u_e}")
            raise 
        except (Exception) as e:
            session.rollback()
            logging.error(f"Unexpected error in create_user: {e}")
            return None

    @classmethod
    def get_user_by_username(cls, session: Session, username: str, uid:str | None = None) -> Optional["User"]:
        """Retrieve a user by username and uid."""
        try: 
            statement = select(cls).where(and_(cls.username == username, cls.uid == uid))
            return session.exec(statement).first()
        except Exception as e:
           logging.error(f"Error in get_user_by_username: {e}")
           return None
    
    @classmethod
    def get_users_by_username(cls, session: Session, search_query: str)  -> list["User"]:
        """Search for users by username (case-insensitive)."""
        try:
            statement = select(cls).where(cls.username.ilike(f"%{search_query}%"))
            return session.exec(statement).all()
        except Exception as e:
            logging.error(f"Error in get_user_by_username: {e}")
            return []
    
    @classmethod
    def get_users_by_ranks(cls, session: Session, search_query: list[int]) -> list["User"]:
        """Search for users by rank value."""
        try:
            statement = select(cls).where(cls.rank_value.in_(search_query))
            return  session.exec(statement).all()
        except Exception as e:
            logging.error(f"Error in get_users_by_ranks: {e}")
            return []

    def update_user(self, session: Session, username: str, password: str, rank: str, rank_value: int, uid: str | None = None, level: int | None = None)  -> None:
        """Update user attributes."""
        try:
            self.username = username
            self.password = password
            if uid:
                uid = uid.strip()
            self.uid = uid
            self.level = level
            self.rank = rank
            self.rank_value = rank_value

            session.add(self)
            session.commit()
            session.refresh(self)
        except Exception as e:
            session.rollback()
            logging.error(f"Error updating user {self.username}: {e}")
            raise
    
    @classmethod
    def delete_user(cls, session: Session, username: str, password: str, rank: str, rank_value: int, uid: str | None = None, level: int | None = None,) -> bool:
        """Delete a user from the database by matching all attributes."""
        try:
            if uid:
                uid = uid.strip()
            statement = select(cls).where(
                cls.username == username,
                cls.password == password,
                cls.uid == uid,
                cls.level == level,
                cls.rank == rank,
                cls.rank_value == rank_value
            )
            user = session.exec(statement).first()
            if not user:
                return False 
            
            session.delete(user)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logging.error(f"Error deleting user {username}: {e}")
            return False
            

engine = create_engine("sqlite:///users.db")

def init_db(engine=engine) -> None: 
    """Initialize the database"""
    if engine is None:
        raise ValueError("Database engine is not initialized.")
    try:
        SQLModel.metadata.create_all(engine)
        logging.info("Database initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
