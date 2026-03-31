from pydantic import BaseModel, constr
from fastapi_users import schemas
from typing import Optional
from enum import Enum
from datetime import datetime
import uuid

# creating the schemas for the Creating a donation

# schemas for fastapi_users
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

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
    mobile_number: constr(min_length=9, max_length=9)
    neighbourhood: str
    donation_type: DonationType
    
    
class DonationCreate(DonationBase):
    class Config:
        extra = "forbid"
    
# not used for now (for the user)    
class DonationUpdate(BaseModel):
    mobile_number: Optional[constr(min_length=9, max_length=9)] = None
    neighbourhood: Optional[str] = None
    donation_type: Optional[DonationType] = None
    class Config:
        extra = "forbid"
    
class DonationAdminUpdate(BaseModel):
    mobile_number: Optional[constr(min_length=9, max_length=9)] = None
    neighbourhood: Optional[str] = None
    donation_type: Optional[DonationType] = None
    status: Optional[DonationStatus] = None
        
    class Config:
        extra = "forbid"


#response schema for get data 
class DonationRead(BaseModel):
    mobile_number: str
    area: str
    neighbourhood: str
    donation_type: DonationType
    created_at: datetime

    # read data from objects too not only dictionaries 
    #allowed to convert ORM objects (like SQLAlchemy models) into this schema
    class Config:
        from_attributes = True         

class DonationAdminRead(BaseModel):
    id: uuid.UUID
    mobile_number: str
    area: str
    neighbourhood: str
    donation_type: DonationType
    status: DonationStatus
    created_at: datetime
    user_id: uuid.UUID

    class Config:
        from_attributes = True    