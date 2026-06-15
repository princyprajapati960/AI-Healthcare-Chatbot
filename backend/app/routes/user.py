from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.auth.security import get_current_user
from backend.app.database.connection import get_db
from backend.app.models.schemas_api import PatientProfileIn, PatientProfileOut
from backend.app.models.schemas_db import PatientProfile, User

router = APIRouter(prefix="/api/user", tags=["user"])


@router.get("/profile", response_model=PatientProfileOut | None)
def get_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    return profile


@router.put("/profile", response_model=PatientProfileOut)
def upsert_profile(
    data: PatientProfileIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    if not profile:
        profile = PatientProfile(user_id=user.id)
        db.add(profile)
    profile.full_name = data.full_name
    profile.age = data.age
    profile.gender = data.gender
    profile.address = data.address
    profile.phone = data.phone
    profile.medical_history = data.medical_history
    profile.language = data.language
    profile.onboarding_complete = True
    if not user.name or user.name == user.email.split("@")[0]:
        user.name = data.full_name
    db.commit()
    db.refresh(profile)
    return profile
