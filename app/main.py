from fastapi import FastAPI
from fastapi import Depends, FastAPI
from sqlmodel import create_engine
from .routers import users
from .database import create_db_and_tables


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()  # ← appelé après que les modèles sont importés

app.include_router(users.router)



