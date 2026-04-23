from sqlmodel import SQLModel, Field
from pydantic import BaseModel
class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str
    prenoms: str | None = None
    email: str
    sexe : str | None = None
    localisation : str | None = None
    password: str
    disabled: bool = False
    

