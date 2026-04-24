from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlmodel import Session, select


from app.schemas import UserCreate, UserUpdate
from app.models import Users
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db)]

# -------------------------
# REGISTER
# -------------------------
@router.post("/register")
def create_user(user: UserCreate, session: SessionDep):

    existing_user = session.exec(
        select(Users).where(Users.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Utilisateur déjà existant"
        )

    hashed_password = hash_password(user.password)

    new_user = Users(
        nom=user.nom,
        prenoms=user.prenoms,
        email=user.email,
        sexe=user.sexe,
        localisation=user.localisation,
        password=hashed_password,
        disabled=False
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "Utilisateur créé avec succès"}

# -------------------------
# LOGIN
# -------------------------
@router.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):

    user = session.exec(
        select(Users).where(Users.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )

    access_token = create_access_token({"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# -------------------------
# CURRENT USER
# -------------------------
@router.get("/users/me")
def read_users_me(
    current_user: Annotated[Users, Depends(get_current_user)]
):
    return current_user

# -------------------------
# UPDATE USER
# -------------------------
@router.put("/users/me")
def update_user(
    user_update: UserUpdate,
    session: SessionDep,
    current_user: Annotated[Users, Depends(get_current_user)]
):

    user = session.exec(
        select(Users).where(Users.id == current_user.id)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if user_update.nom is not None:
        user.nom = user_update.nom

    if user_update.prenoms is not None:
        user.prenoms = user_update.prenoms

    session.commit()
    session.refresh(user)

    return {
        "message": "Utilisateur mis à jour",
        "user": user
    }