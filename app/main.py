from fastapi import FastAPI
from fastapi import Depends, FastAPI
from .routers import users
from .database import create_db_and_tables
from app.routers import pictures
from app.routers import auth

app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()  # ← appelé après que les modèles sont importés

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(pictures.router)

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

CHAMPS_FR = {
    "nom": "nom",
    "prenoms": "prénoms",
    "email": "email",
    "password": "mot de passe",
    "sexe": "sexe",
    "localisation": "localisation"
}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erreurs = []

    

    return JSONResponse(
        status_code=422,
        content={"erreurs": erreurs}
    )
