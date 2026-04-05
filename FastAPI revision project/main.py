from fastapi import FastAPI
from contextlib import asynccontextmanager
from core import engine, create_db_and_tables
import models # so that sqlmodels registers tables
from routers import users, donations
from core import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    engine.dispose()
    

app = FastAPI(lifespan=lifespan) 

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(donations.router, prefix="/donations", tags=["Donations"])
   