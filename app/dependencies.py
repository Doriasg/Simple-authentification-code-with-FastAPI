from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserInDB
from app.database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from sqlmodel import Session, select
from app.models import Users 

def get_user_by_email(email: str, db: Session) -> Users | None:
    statement = select(Users).where(Users.email == email)
    result = db.exec(statement)
    return result.first()


from fastapi import Depends, HTTPException
from jose import JWTError
from sqlmodel import Session, select
from app.database import get_db
from app.security import decode_token
from app.models import Users

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    payload = decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Token invalide")

    email = payload.get("sub")

    if email is None:
        raise HTTPException(status_code=401, detail="Token invalide")

    user = db.query(Users).filter(Users.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    return user