from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel
from typing import List
from typing import Optional
class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str
    prenoms: str | None = None
    email: str
    sexe : Optional[str] | None = None
    localisation : Optional[str]  = None
    password: str
    disabled: bool = False
    images: List["PlantImage"] = Relationship(back_populates="user")
    
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class PlantImage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    image_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: int = Field(foreign_key="users.id")
    disease_name: Optional[str] = None
    user: Optional[Users] = Relationship(back_populates="images")
