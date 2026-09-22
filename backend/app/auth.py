from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException
from firebase_admin import auth, credentials, get_app, initialize_app
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .models import AllowedUser


@dataclass(frozen=True)
class User: uid: str


def current_user(authorization: str | None = Header(None), x_demo_user: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    settings=get_settings()
    if settings.demo_auth and settings.app_env != "production": uid=x_demo_user or "demo-user"
    else:
        if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401, "Kimlik doğrulama gerekli")
        try:
            try: get_app()
            except ValueError: initialize_app(credentials.ApplicationDefault(), {"projectId": settings.firebase_project_id})
            uid=auth.verify_id_token(authorization.removeprefix("Bearer "))["uid"]
        except Exception as exc: raise HTTPException(401, "Geçersiz kimlik belirteci") from exc
    allowed=db.get(AllowedUser, uid)
    if not allowed or not allowed.active: raise HTTPException(403, "Bu kullanıcıya yönetici erişimi verilmemiş")
    return User(uid)

