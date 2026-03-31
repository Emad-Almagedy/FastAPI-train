from fastapi import FastAPI, HTTPException, Form, Depends
from src.db import create_db_and_tables, get_async_session, Donations, User
from uuid import UUID
# database creation
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select, desc, asc

# implement user login and authentication
from src.users import auth_backend, current_active_user, fastapi_users
from src.schemas import (
    UserCreate, UserRead, UserUpdate,
    DonationCreate, DonationUpdate, DonationAdminUpdate,
    DonationStatus, DonationRead, DonationAdminRead
)

# for admin access
from src.dependencies import admin_required

#create the database if not created 
@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield

# create fastapi application instance
app = FastAPI(lifespan=lifespan)

# registering fastAPI routes in the app under a cetian section depending on the tag 
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

# create Donation (logged user)
@app.post("/donations")
async def create_donation(
    donation: DonationCreate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    new_donation = Donations(
        user_id = user.id,
        mobile_number = donation.mobile_number,
        neighbourhood = donation.neighbourhood,
        donation_type = donation.donation_type,
        status = DonationStatus.submitted
    )
    db.add(new_donation)
    await db.commit()
    await db.refresh(new_donation)
    return new_donation

# get all donations(admin only)
@app.get("/admin/donations", response_model=list[DonationAdminRead])
async def get_all_donations(
    admin: User = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(Donations).order_by(desc(Donations.created_at)))
    donations = result.scalars().all()
    return donations

@app.patch("/admin/donations/{donation_id}")
async def update_donation(
    donation_id : UUID,
    data: DonationAdminUpdate,
    admin: User = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Donations).where(Donations.id == donation_id)
    )
    donation = result.scalar_one_or_none()
    
    # if the donation is not avaliable 
    if not donation:
        raise HTTPException(status_code=404, detail="Donation not Found")
    
    # update only the provided fields
    if data.mobile_number is not None:
        donation.mobile_number = data.mobile_number
    
    if data.neighbourhood is not None:
        donation.neighbourhood = data.neighbourhood

    if data.donation_type is not None:
        donation.donation_type = data.donation_type

    if data.status is not None:
        donation.status = data.status    
    
    await db.commit()
    await db.refresh(donation)
    return donation   

# promote a user to admin 
@app.patch("/admin/make-admin/{user_id}")
async def make_admin(
    user_id: UUID,
    admin: User = Depends(admin_required),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404)

    user.is_admin = True

    await db.commit()
    return {"message": "User promoted to admin"} 
        

# get donation donated by the user (logged in)
@app.get("/donations/me", response_model=list[DonationRead])
async def get_my_donations(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Donations)
        .where(Donations.user_id == user.id)
        .order_by(desc(Donations.created_at))
    )
    
    donations = result.scalars().all()
    return donations