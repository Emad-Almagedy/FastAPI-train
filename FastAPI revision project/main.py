from fastapi import FastAPI
from contextlib import asynccontextmanager
from core import engine, create_db_and_tables
import models # so that sqlmodels registers tables
from routers import users, donations

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
    
app = FastAPI(lifespan=lifespan) 

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(donations.router, prefix="/donations", tags=["Donations"])
   