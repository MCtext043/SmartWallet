from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    get_user_by_phone,
)
from config import settings
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, User as UserSchema, Token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

_AVATAR_DIR = Path(__file__).resolve().parent.parent / "static" / "avatars"
_AVATAR_MAX_BYTES = 5 * 1024 * 1024
_AVATAR_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким телефоном или email
    db_user_phone = get_user_by_phone(db, phone=user.phone)
    if db_user_phone:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким телефоном уже зарегистрирован"
        )
    
    db_user_email = db.query(User).filter(User.email == user.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким email уже зарегистрирован"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(user.password)
    db_user = User(
        phone=user.phone,
        email=user.email,
        name=user.name,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_credentials.phone, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный телефон или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.phone}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=UserSchema)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/profile/avatar",
    response_model=UserSchema,
    summary="Загрузка аватара",
    responses={
        400: {"description": "Нет файла, не изображение или превышен размер (до 5 МБ)"},
        401: {"description": "Не авторизован"},
    },
)
async def upload_profile_avatar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    file: UploadFile | None = File(None, description="Файл изображения (jpeg, png, webp)"),
):
    """
    `multipart/form-data`, поле **`file`**. Допустимы `image/jpeg`, `image/png`, `image/webp`, максимум 5 МБ.
    В ответе — профиль с `avatar_url` (относительный путь `/static/avatars/...`).
    """
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ожидается multipart/form-data с полем file",
        )
    ct = (file.content_type or "").split(";")[0].strip().lower()
    if ct not in _AVATAR_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Допустимы только изображения: image/jpeg, image/png, image/webp",
        )
    body = await file.read()
    if not body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пустой файл",
        )
    if len(body) > _AVATAR_MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Размер файла не более 5 МБ",
        )

    ext = _AVATAR_TYPES[ct]
    _AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    for old in _AVATAR_DIR.glob(f"{current_user.id}.*"):
        try:
            old.unlink()
        except OSError:
            pass

    out_path = _AVATAR_DIR / f"{current_user.id}{ext}"
    out_path.write_bytes(body)

    rel = f"/static/avatars/{out_path.name}"
    current_user.avatar_url = rel
    db.commit()
    db.refresh(current_user)
    return current_user
