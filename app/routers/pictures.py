from fastapi import APIRouter, Depends, UploadFile, File
from sqlmodel import Session
import os
import uuid
from datetime import datetime
from typing import Annotated
from app.database import get_db
from app.models import PlantImage, Users
from app.dependencies import get_current_user

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_db)]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_plant_image(
    session: SessionDep,
    current_user: Users = Depends(get_current_user),
    file: UploadFile = File(...)
):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 1. sauvegarde fichier
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # 2. création DB (EN DEHORS DU WITH)
    plant = PlantImage(
        image_path=file_path,
        user_id=current_user.id,
        created_at=datetime.utcnow(),
        disease_name=None
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