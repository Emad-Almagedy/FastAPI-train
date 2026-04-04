from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid
from sqlmodel import SQLModel, Field, Relationship

class DonationType(str, Enum):
    shoes = "shoes"
    clothes = "clothes"
    electronics = "electronics"
    furniture = "furniture"
    other = "other"


class DonationStatus(str, Enum):
    submitted = "submitted"
    processing = "processing"
    processed = "processed"


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

class Donation(SQLModel, table=True):
    __tablename__ = "donations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    mobile_number: str = Field(nullable=False)
    area: str = Field(nullable=False)
    neighbourhood: str = Field(nullable=False)
    donation_type: DonationType = Field(nullable=False)
    status: DonationStatus = DonationStatus.submitted 

    user: Optional[User] = Relationship(back_populates="donations")