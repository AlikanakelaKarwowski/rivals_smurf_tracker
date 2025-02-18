from sqlmodel import SQLModel, Field, Session, create_engine, select
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
    def create(cls, session: Session, username: str, password: str, uuid: str, level: int, rank: str, rank_value: int) -> "User":
        """Create and save a new user."""
        user = cls(username=username, password=password, uuid=uuid, level=level, rank=rank, rank_value=rank_value)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @classmethod
    def get_by_username(cls, session: Session, search_query: str)  -> list[tuple[str,str,str]]:
        """Search for users by username (case-insensitive)."""
        statement = select(cls).where(cls.username.ilike(f"%{search_query}%"))
        results = session.exec(statement).all()
        return [(user.username, user.password, user.uuid, user.level, user.rank) for user in results]
    
    @classmethod
    def get_by_rank(cls, session: Session, search_query: list[int]) -> list[tuple[str, str, str]]:
        """Search for users by rank value."""
        statement = select(cls).where(cls.rank_value.in_(search_query))
        results = session.exec(statement).all()
        return [(user.username, user.password, user.uuid, user.level, user.rank) for user in results]

engine = create_engine("sqlite:///users.db")

def init_db() -> None: 
    SQLModel.metadata.create_all(engine)
        
def update_db(username: str, o_username: str, password: str, o_password: str, uuid: str, o_uuid: str, level: int, o_level: int, rank: str, o_rank: str, rank_value: int, o_rank_value: int, custom_engine=None) -> None:
    active_engine = custom_engine or engine
    with Session(active_engine) as session:
        statement = select(User).where(User.username == o_username, User.password == o_password, User.uuid == o_uuid, User.level == o_level, User.rank == o_rank, User.rank_value == o_rank_value)
        user = session.exec(statement).first()
        user.username = username
        user.password = password
        user.uuid = uuid
        user.level = level
        user.rank = rank
        user.rank_value = rank_value
        session.add(user)
        session.commit()

def delete_db(username: str, password: str, uuid: str, level: int, rank: str, rank_value: int, custom_engine=None) -> None:
    active_engine = custom_engine or engine
    with Session(active_engine) as session:
        statement = select(User).where(
            User.username == username,
            User.password == password,
            User.uuid == uuid,
            User.level == level,
            User.rank == rank,
            User.rank_value == rank_value
            
        )
        user = session.exec(statement).first()
        session.delete(user)
        session.commit()
        