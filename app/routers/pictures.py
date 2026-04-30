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
from dotenv import load_dotenv
import os

load_dotenv()

cloudinary.config(
  cloud_name=os.getenv("CLOUD_NAME"),
  api_key=os.getenv("API_KEY"),
  api_secret=os.getenv("API_SECRET"),
  secure=True
)

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db)]



@router.post("/upload")
def save_plant_image(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
    file: UploadFile = File(...),
    disease_name : str = Form(None)
    
):
    # Téléversez le fichier reçu vers Cloudinary
    upload_result = cloudinary.uploader.upload(file.file)
    
    # Récupérez l’URL sécurisée
    secure_url = upload_result["secure_url"]
    print("URL sécurisée de l'image téléversée :", secure_url)
    plant = PlantImage(
        image_path=secure_url,
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
