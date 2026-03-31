import uuid
from collections.abc import AsyncGenerator
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

# specifying the database path 
DATABASE_URL = "sqlite+aiosqlite:///./donation.db"

# using declarativebase

class Base(DeclarativeBase):
    pass

# create tables users and donations 
class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    donations = relationship("Donations", back_populates="user")
    is_admin = Column(Boolean, default=False)
    
class Donations(Base):
    __tablename__ = "donations"
    id = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4) 
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    mobile_number = Column(String(9), nullable=False)
    area = Column(String, default="Riyadh")
    neighbourhood = Column(String, nullable=False)
    donation_type = Column(Enum("shoes", "clothes", "electronics", "furniture", "other", name="donation_types"), nullable=False)
    status = Column(Enum("submitted", "processing", "processed", name="donation_status"), nullable=False, default="submitted")
    user = relationship("User", back_populates="donations")
    
# create a connection engine to the database
engine = create_async_engine(DATABASE_URL)
# produce sessions
async_session_maker = async_sessionmaker(engine, expire_on_commit = False)

# create the table in the database
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
# gives a session to work with the db and close automatically
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
        
# adapter for user database to perfrom CRUD SQLAlchemyUserDatabase using the session created 
async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
             
