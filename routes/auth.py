from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from database import get_db
from schemas.auth import Token
from schemas.user import UserLogin, UserCreate
from auth.jwt import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_token
from models.user import User, AuthHistory
from config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin, 
    response: Response, 
    request: Request,
    db: Session = Depends(get_db)
):
    # Поиск пользователя по логину или email
    user = db.query(User).filter(
        (User.login == user_data.login) | (User.email == user_data.login)
    ).first()
    
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    # Создание токенов
    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})
    
    # Сохранение в историю авторизаций
    auth_history = AuthHistory(
        user_id=user.id,
        user_agent=request.headers.get("user-agent")
    )
    db.add(auth_history)
    db.commit()
    
    # Установка refresh токена в cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@router.post("/registration")
async def registration(user_data: UserCreate, db: Session = Depends(get_db)):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароли не совпадают"
        )
    
    # Проверка существующего пользователя
    existing_user = db.query(User).filter(
        (User.login == user_data.login) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином или email уже существует"
        )
    
    # Создание нового пользователя
    hashed_password = get_password_hash(user_data.password)
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        login=user_data.login,
        email=user_data.email,
        password=hashed_password
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "Пользователь успешно зарегистрирован"}

@router.post("/refresh", response_model=Token)
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )
    
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Создаем новые токены
    new_access_token = create_access_token(data={"user_id": user.id})
    new_refresh_token = create_refresh_token(data={"user_id": user.id})
    
    # Обновляем refresh token в cookies
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax"
    )
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }
