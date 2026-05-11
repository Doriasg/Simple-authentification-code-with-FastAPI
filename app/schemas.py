from pydantic import BaseModel, Field, EmailStr, constr, field_validator
from typing import Optional

class UserCreate(BaseModel):
    nom: constr(min_length=3, max_length=50, pattern="^[a-zA-Z]+$") = Field(..., example="ABLAKOUA")
    prenoms: constr(min_length=3, max_length=50, pattern="^[a-zA-Z ]+$") = Field(..., example="John")
    email: EmailStr = Field(..., example="john.ablakoua@example.com")
    password: constr(min_length=4) = Field(..., example="@bl@2k26")
    sexe: Optional[str] = Field(None, example="M")
    reset_code : Optional[str] = None
    reset_code_expires_at : Optional[str] = None
    localisation: Optional[str] = Field(None, example="Lon: 1.4 , Lat: 1,8")


class UserUpdate(BaseModel):
    nom: Optional[constr(min_length=3, pattern="^[a-zA-Z]+$")] = None
    prenoms: Optional[constr(min_length=3, pattern="^[a-zA-Z ]+$")] = None

from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
class UserInDB(BaseModel):
    id: int
    nom: str
    prenoms: str
    email: EmailStr

class UploadImageRequest(BaseModel):
    disease_name: str

class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    new_password_confirm: str

class forgotPassword(BaseModel):
    email: EmailStr

class VerifyCode(BaseModel):
    code: str

class resetPassword(BaseModel):
    email: EmailStr
    code: str
    new_password: str
    new_password_confirm: str
    
class PromptRequest(BaseModel):
    prompt: str

class DiseaseData(BaseModel):
    disease_name: str