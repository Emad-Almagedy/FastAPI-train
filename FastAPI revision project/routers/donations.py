from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, desc

import models
from core import get_db, get_current_user, admin_required
from schemas import (
    DonationCreate,
    DonationRead,
    DonationAdminRead,
    DonationAdminUpdate,
    DonationUpdate,
    DonationStatus,
)

router = APIRouter()

# create donation user
@router.post("", response_model=DonationRead, status_code=status.HTTP_201_CREATED)
async def create_donation(
    donation: DonationCreate,
    user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    new_donation = models.Donation(
        user_id=user.id,
        mobile_number=donation.mobile_number,
        neighbourhood=donation.neighbourhood,
        donation_type=donation.donation_type,
        area=donation.area,
        status=DonationStatus.submitted,
    )

    db.add(new_donation)
    await db.commit()
    await db.refresh(new_donation)

    return new_donation

@router.get("/me", response_model=list[DonationRead])
async def get_my_donations(
    user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Donation)
        .where(models.Donation.user_id == user.id)
        .order_by(desc(models.Donation.created_at))
    )

    return result.scalars().all()

@router.get("/admin", response_model=list[DonationAdminRead])
async def get_all_donations(
    admin: Annotated[models.User, Depends(admin_required)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Donation).order_by(desc(models.Donation.created_at))
    )

    return result.scalars().all()

@router.patch("/admin/{donation_id}", response_model=DonationAdminRead)
async def update_donation(
    donation_id: UUID,
    data: DonationAdminUpdate,
    admin: Annotated[models.User, Depends(admin_required)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.Donation).where(models.Donation.id == donation_id)
    )

    donation = result.scalar_one_or_none()

    if not donation:
        raise HTTPException(status_code=404, detail="Donation not found")

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

@router.patch("/admin/make-admin/{user_id}")
async def make_admin(
    user_id: UUID,
    admin: Annotated[models.User, Depends(admin_required)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await db.get(models.User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_admin = True

    await db.commit()

    return {"message": "User promoted to admin"}