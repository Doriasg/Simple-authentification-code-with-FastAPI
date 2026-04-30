from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlmodel import Session, select


from app.schemas import UserCreate, UserUpdate
from app.models import Users
from app.database import get_db
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user
from fastapi.security import OAuth2PasswordRequestForm  
from app.schemas import LoginRequest, UpdatePasswordRequest


from typing import List
from app.models import PlantImage

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
@router.post("/login")
def login(
    session: SessionDep, data: LoginRequest
    
):
    user = session.exec(
        select(Users).where(Users.email == data.email)
    ).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect"
        )
    access_token = create_access_token({"sub": user.email})
    

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
from fastapi.security import OAuth2PasswordRequestForm

@router.post("/token")
def token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
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
@router.put("/update_password")
def update_password(
    session: SessionDep, data: UpdatePasswordRequest,
    current_user: Annotated[Users, Depends(get_current_user)],
):
    user = session.exec(
        select(Users).where(Users.id == current_user.id)
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    if not verify_password(data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")

    if data.new_password != data.new_password_confirm:
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")

    user.password = hash_password(data.new_password)
    session.commit()
    session.refresh(user)

    return {"message": "Mot de passe mis à jour avec succès"}