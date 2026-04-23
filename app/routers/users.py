from fastapi import APIRouter
from app.schemas import UserInDB, UserCreate, UserUpdate
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from app.dependencies import get_current_user
from sqlmodel import Session
from typing import Annotated
from app.schemas import UserInDB
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Field, Session, SQLModel, create_engine, select
# from app.security import hash_password, verify_password, create_token
from app.models import Users  # IMPORTANT
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token

DATABASE_URL = "postgresql+psycopg2://postgres:password123@localhost:5432/rice_db"
engine = create_engine(DATABASE_URL)

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
# -------------------------
# REGISTER
# -------------------------


@router.post("/register")
def create_user(user: UserCreate, session: SessionDep):

    # Vérifier si l'utilisateur existe déjà en base
    existing_user = session.exec(
        select(Users).where(Users.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Utilisateur déjà existant"
        )

    hashed = hash_password(user.password)

    new_user = Users(
        nom=user.nom,
        prenoms=user.prenoms,
        email=user.email,
        sexe = user.sexe,
        localisation = user.localisation,
        password=hashed,
        disabled=False
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"msg": "Utilisateur créé avec succès"}
# LOGIN
# -------------------------
@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):

    statement = select(Users).where(Users.email == form_data.username)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[Users, Depends(get_current_user)],
):
    return current_user

@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.exec(
        select(Users).where(Users.email == form_data.username)
    ).first()

    if not user or user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Email ou mot de passe incorrect")

    return {
        "access_token": f"token-{user.email}",
        "token_type": "bearer"
    }

@router.put("/users/me")
def update_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    
    user = db.query(Users).filter(Users.id == current_user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if user_update.nom:
        user.nom = user_update.nom

    if user_update.prenoms:
        user.prenoms = user_update.prenoms
    db.commit()
    db.refresh(user)

    return {"message": "Utilisateur mis à jour", "user": user}
