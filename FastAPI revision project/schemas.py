from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid


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
    
class DonationBase(BaseModel):
    mobile_number: str = Field(min_length=9, max_length=9)
    neighbourhood: str
    donation_type: DonationType
    area: Optional[str] = "Riyadh"   

class DonationCreate(DonationBase):
    class Config:
        extra = "forbid"   

class DonationUpdate(BaseModel):
    mobile_number: Optional[str] = Field(default=None, min_length=9, max_length=9)
    neighbourhood: Optional[str] = None
    donation_type: Optional[DonationType] = None

    class Config:
        extra = "forbid"

class DonationAdminUpdate(BaseModel):
    mobile_number: Optional[str] = Field(default=None, min_length=9, max_length=9)
    neighbourhood: Optional[str] = None
    donation_type: Optional[DonationType] = None
    status: Optional[DonationStatus] = None

    class Config:
        extra = "forbid"

class DonationRead(BaseModel):
    id: uuid.UUID
    mobile_number: str
    area: str
    neighbourhood: str
    donation_type: DonationType
    status: DonationStatus
    created_at: datetime

    class Config:
        from_attributes = True        

class DonationAdminRead(DonationRead):
    user_id: uuid.UUID        
    
    
                          

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    
    class Config:
        extra = "forbid"    
        
class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str


class UserPrivate(UserPublic):
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)


class Token(BaseModel):
    access_token: str
    token_type: str

       