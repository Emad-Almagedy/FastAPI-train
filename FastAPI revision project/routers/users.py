from datetime import timedelta
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func

import models
from core import (
    create_access_token,
    hash_password,
    oauth2_scheme,
    verify_access_token,
    verify_password,
    settings,
    get_db,
)
from schemas import Token, UserCreate, UserPrivate, UserPublic, UserUpdate

# intialize the router app
router = APIRouter()

# create a user 
@router.post("", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    # check username
    result = await db.execute(
        select(models.User).where(
            models.User.username.ilike(user.username)
        )
    )
    if result.scalars().first():
        raise HTTPException(400, "Username already exists")

    # check email
    result = await db.execute(
        select(models.User).where(
            models.User.email.ilike(user.email)
        )
    )
    if result.scalars().first():
        raise HTTPException(400, "Email already registered")

    new_user = models.User(
        username=user.username,
        email=user.email.lower(),
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# login logic
@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(models.User).where(
            models.User.email.ilike(form_data.username)
        )
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return Token(access_token=token, token_type="bearer")

# get current user
@router.get("/me", response_model=UserPrivate)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user_id = verify_access_token(token)

    if not user_id:
        raise HTTPException(401, "Invalid token")

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
    
    user = await db.get(models.User, user_uuid)    
    if not user:
        raise HTTPException(401, "User not found")

    return user

# get current user by ID
@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):

    user = await db.get(models.User, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    return user

# delete user
@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]):

    user = await db.get(models.User, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    await db.delete(user)
    await db.commit()
