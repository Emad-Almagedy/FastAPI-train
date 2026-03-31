import uuid
from typing import Optional
from sqlalchemy import select
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy
)
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from src.db import User,get_user_db
import secrets
from dotenv import load_dotenv 
import os 

load_dotenv()
# for signing token and token verification
SECRET = os.getenv("SECRET")

# class that manager registration, password reset , email verification etc
# UUIDIDMixin tells that the IDs are UUIDs instead of integers 
# use the same secret for password reset and email verification to sign JWT tokens
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET
    
    # callbacks triggered automatically by fastapi_users when acctions happens ( sent to email or as message)
    async def on_after_register(self, user: User, request: Optional[Request] = None):
        result = await self.user_db.session.execute(select(User))
        users = result.scalars().all()
        if len(users) == 1:
            await self.user_db.update(user, {"is_admin": True})

        print(f"User {user.id} registered")
        #print(f"User {user.id} has forgot their password. reset token: {token}")
        
    async def on_after_forgot_password(self, user: User, token: str, request:Optional[Request] = None):
        print(f"User {user.id} has forgot their password. reset token : {token}")
    
    async def on_after_request_verify(self, user: User, token: str, request:Optional[Request] = None):
        print(f"Verification requested for user {user.id}. verification token : {token}")  
        
# give the Usermanage access to the database
async def get_user_manager (user_db:SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy():
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
     transport=bearer_transport,
     get_strategy=get_jwt_strategy
)       

# fastapiusers provides endpoints for login , registration etc
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager,[auth_backend])
current_active_user = fastapi_users.current_user(active=True)       
        