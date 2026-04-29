from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from datetime import datetime
from typing import Annotated
from app.database import get_db
from app.models import PlantImage, Users
from app.dependencies import get_current_user
import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET")
)

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db)]


@router.post("/upload")
def save_plant_image(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
    file: UploadFile = File(...),
    disease_name: str = Form(...)
):
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="plants",
            resource_type="image"
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'upload de l'image"
        )

    image_url = result["secure_url"]

    plant = PlantImage(
        image_path=image_url,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        disease_name=disease_name
    )

    session.add(plant)
    session.commit()
    session.refresh(plant)

    return {
        "message": "Image uploadée avec succès",
        "id": plant.id,
        "path": plant.image_path
    }