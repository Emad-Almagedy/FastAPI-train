from typing import List
import uuid
from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"
    
    # default factory so that a unique id is generated everytime a new object is created
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = Field(default=False)    
    donations: List["Donation"] = Relationship(
        back_populates="user",
    )
