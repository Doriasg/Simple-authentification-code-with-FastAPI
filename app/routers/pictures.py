from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlmodel import Session
import os
import uuid
from datetime import datetime
from typing import Annotated
from app.database import get_db
from app.models import PlantImage, Users
from app.dependencies import get_current_user
from app.schemas import UploadImageRequest
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="dwtzbiklb",
    api_key="638477191621292",
    api_secret="qe8pS8odtkH1I2DWEr9xd06SG_Q"
)


router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db)]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def save_plant_image(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
    file: UploadFile = File(...),
    disease_name : str = Form(None)
    
):
    
    result = cloudinary.uploader.upload(file.file)
    image_url = result["secure_url"]

    # 2. création DB (EN DEHORS DU WITH)
    plant = PlantImage(
        image_path=image_url,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        disease_name= disease_name
    )

    session.add(plant)
    session.commit()
    session.refresh(plant)

    # 3. response
    return {
        "message": "Image uploadée avec succès",
        "id": plant.id,
        "path": plant.image_path
    }