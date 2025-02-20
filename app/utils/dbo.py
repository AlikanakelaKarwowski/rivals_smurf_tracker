from sqlmodel import SQLModel, Field, Session, create_engine, select, and_
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str
    uuid: str = Field(index=True)
    level: int
    rank: str
    rank_value: int
    
    def save(self, session: Session) -> None:
        session.add(self)
        session.commit()

    @classmethod
    def create_user(cls, session: Session, username: str, password: str, uuid: str, level: int, rank: str, rank_value: int) -> "User":
        """Create and save a new user."""
        user = cls(username=username, password=password, uuid=uuid, level=level, rank=rank, rank_value=rank_value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @classmethod
    def get_user_by_username(cls, session: Session, username: str, uuid:str) -> Optional["User"]:
        """Retrieve a user by username and uuid."""
        statement = select(cls).where(and_(cls.username == username, cls.uuid == uuid))
        return session.exec(statement).first()
    
    @classmethod
    def get_users_by_username(cls, session: Session, search_query: str)  -> list["User"]:
        """Search for users by username (case-insensitive)."""
        statement = select(cls).where(cls.username.ilike(f"%{search_query}%"))
        return session.exec(statement).all()
    
    @classmethod
    def get_users_by_ranks(cls, session: Session, search_query: list[int]) -> list["User"]:
        """Search for users by rank value."""
        statement = select(cls).where(cls.rank_value.in_(search_query))
        return  session.exec(statement).all()


    def update_user(self, session: Session, username: str, password: str, uuid: str, level: int, rank: str, rank_value: int)  -> None:
        """Update user attributes."""
        self.username = username
        self.password = password
        self.uuid = uuid
        self.level = level
        self.rank = rank
        self.rank_value = rank_value

        session.add(self)
        session.commit()
        session.refresh(self)
    
    @classmethod
    def delete_user(cls, session: Session, username: str, password: str, uuid: str, level: int, rank: str, rank_value: int) -> bool:
        """Delete a user from the database by matching all attributes."""
        statement = select(cls).where(
            cls.username == username,
            cls.password == password,
            cls.uuid == uuid,
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

engine = create_engine("sqlite:///users.db")

def init_db() -> None: 
    SQLModel.metadata.create_all(engine)
        