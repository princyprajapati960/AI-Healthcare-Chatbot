from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.auth.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.app.config import settings
from backend.app.database.connection import get_db
from backend.app.models.schemas_api import (
    PatientProfileIn,
    PatientProfileOut,
    TokenResponse,
    UserLogin,
    UserOut,
    UserRegister,
)
from backend.app.models.schemas_db import PatientProfile, User

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _user_out(user: User, db: Session) -> UserOut:
    profile = db.query(PatientProfile).filter(PatientProfile.user_id == user.id).first()
    return UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        avatar=user.avatar,
        onboarding_complete=bool(profile and profile.onboarding_complete),
    )


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password), name=data.name)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token, user=_user_out(user, db))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token, user=_user_out(user, db))


@router.get("/google")
def google_login():
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")
    params = (
        f"client_id={settings.google_client_id}"
        f"&redirect_uri={settings.google_redirect_uri}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
        "&prompt=select_account"
    )
    return {"url": f"https://accounts.google.com/o/oauth2/v2/auth?{params}"}


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    import httpx

    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=503, detail="Google OAuth not configured")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Google token exchange failed")
        tokens = token_resp.json()
        user_resp = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Google profile")
        info = user_resp.json()

    email = info.get("email")
    google_id = info.get("id")
    name = info.get("name", "")
    avatar = info.get("picture")

    user = db.query(User).filter((User.google_id == google_id) | (User.email == email)).first()
    if not user:
        user = User(email=email, google_id=google_id, name=name, avatar=avatar)
        db.add(user)
    else:
        user.google_id = google_id
        user.name = name or user.name
        user.avatar = avatar or user.avatar
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email)
    from fastapi.responses import RedirectResponse

    return RedirectResponse(f"{settings.frontend_url}/auth/callback?token={token}")


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _user_out(user, db)
