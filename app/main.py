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

    for err in exc.errors():
        champ_tech = err["loc"][-1]
        champ = CHAMPS_FR.get(champ_tech, champ_tech)
        type_erreur = err["type"]

        if type_erreur == "missing":
            message = f"Le champ '{champ}' est obligatoire"
        elif type_erreur == "string_too_short":
            message = f"Le champ '{champ}' est trop court"
        elif type_erreur == "value_error.email":
            message = "Email invalide"
        elif type_erreur == "string_pattern_mismatch":
            message = f"Le champ '{champ}' contient des caractères invalides"
        else:
            message = f"Valeur invalide pour '{champ}'"

        erreurs.append({
            "champ": champ_tech,  # utile pour le frontend
            "message": message
        })

    return JSONResponse(
        status_code=422,
        content={"erreurs": erreurs}
    )