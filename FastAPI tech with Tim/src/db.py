"""
db.py
"""
from collections.abc import AsyncGenerator
import uuid

# importing important sqlalchemy libraries
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

# sepcify the database path
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass

# relationship between the post and the user( one user having many posts)
class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")

    # post database model
class Post(Base):
    __tablename__= "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="posts")
        
# creat a connection engine to the database     
engine = create_async_engine(DATABASE_URL)
# to produce sesions
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# creates the table in the database 
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# gives a sesion to work with the db and close automatically 
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        # the code done before  yield is setup and after it is cleanup
        yield session

# connects the session to the fastapi user
# adapter for user database to perform CRUD SQLAlchemyUserDatabase using the session
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
        
        
    
