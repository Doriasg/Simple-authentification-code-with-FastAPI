from pydantic import BaseModel

from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    id: int
    nom: str
    prenoms: str | None = None
    email: str
    sexe: str | None = None
    localisation: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    password: str

    
class UserCreate(BaseModel):
    email: str
    password: str
    nom: str
    prenoms: str | None = None
    sexe: str | None = None
    location: str | None = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserUpdate(BaseModel):
    nom: str
    prenoms: str | None = None
    sexe: str | None = None
    location: str | None = None