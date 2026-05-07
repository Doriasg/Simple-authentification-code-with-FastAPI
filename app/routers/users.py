from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlmodel import Session, select
from app.schemas import UserCreate, UserUpdate
from app.models import Users
from app.database import get_db
from app.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from app.models import PlantImage




router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db)]

# -------------------------
# CURRENT USER
# -------------------------
@router.get("/profil")
def read_current_user(
    current_user: Annotated[Users, Depends(get_current_user)]
):
    return current_user

# -------------------------
# UPDATE USER
# -------------------------
@router.put("/modifier")
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

@router.get("/historique")
def get_user_images(
    session: SessionDep,
    current_user: Users = Depends(get_current_user)
):
    images = session.exec(
        select(PlantImage)
        .where(PlantImage.user_id == current_user.id)
        .order_by(PlantImage.created_at.desc())
    ).all()

    return images
