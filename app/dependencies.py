from datetime import timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.schemas import UserInDB, forgotPassword
from app.database import SessionLocal
import resend
from datetime import datetime, timedelta
import random
import os
import secrets
from sqlmodel import Session, select
from app.models import Users 
from brevo.core.api_error import ApiError
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem,
)
from brevo import AsyncBrevo
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
client = AsyncBrevo(api_key= BREVO_API_KEY)



async def send_code_by_email(data, db):
    
    from datetime import datetime, timedelta

    code = secrets.randbelow(900000) + 100000

    user = get_user_by_email(data.email, db)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.reset_code = hash_password(str(code))
    user.reset_code_expires_at = datetime.utcnow() + timedelta(minutes=15)

    db.commit()
    db.refresh(user)

    try:
        result = await client.transactional_emails.send_transac_email(
            subject="Code de réinitialisation de mot de passe",
            html_content=f"""
            <html>
              <body>
                <p>
                  Code de réinitialisation :<br>
                  <b>{code}</b><br>
                  Expire dans 15 minutes.
                </p>
              </body>
            </html>
            """,
            sender=SendTransacEmailRequestSender(
                name="Mon App",
                email="assogbadoriane3@gmail.com",
            ),
            to=[
                SendTransacEmailRequestToItem(
                    email=data.email,
                    name=user.nom if user.nom else "Cher utilisateur",
                )
            ],
        )

        print("EMAIL SENT:", result)

    except ApiError as e:
        print("BREVO ERROR:", e.status_code)
        print(e.body)
        raise e
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_by_email(email: str, db: Session) -> Users | None:
    statement = select(Users).where(Users.email == email)
    result = db.exec(statement)
    return result.first()


from fastapi import Depends, HTTPException
from jose import JWTError
from sqlmodel import Session, select
from app.database import get_db
from app.security import decode_token, hash_password
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