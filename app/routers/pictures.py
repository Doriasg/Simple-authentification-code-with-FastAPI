from routers import users
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()

@router.post("/pictures/me")
def post_picture(
    url: str,
    maladie: str | None = None,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    picture = Picture(
        url=url,
        maladie=maladie,
        user_id=current_user.id
    )
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture