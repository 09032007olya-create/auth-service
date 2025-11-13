from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.jwt import verify_password, get_password_hash
from schemas.user import ChangePassword, ChangeLogin, UserResponse
from models.user import User, AuthHistory

router = APIRouter()

@router.patch("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверяем текущий пароль
    if not verify_password(password_data.password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль"
        )
    
    # Проверяем совпадение новых паролей
    if password_data.new_password != password_data.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новые пароли не совпадают"
        )
    
    # Хешируем и сохраняем новый пароль
    hashed_new_password = get_password_hash(password_data.new_password)
    current_user.password = hashed_new_password
    db.commit()
    
    return {"message": "Пароль успешно изменен"}

@router.patch("/change-login")
async def change_login(
    login_data: ChangeLogin,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Проверяем, не занят ли новый логин
    existing_user = db.query(User).filter(User.login == login_data.new_login).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует"
        )
    
    # Обновляем логин
    current_user.login = login_data.new_login
    db.commit()
    
    return {"message": "Логин успешно изменен"}

@router.get("/auth-history")
async def get_auth_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Получаем историю авторизаций пользователя
    history = db.query(AuthHistory).filter(
        AuthHistory.user_id == current_user.id
    ).order_by(AuthHistory.login_time.desc()).all()
    
    return {
        "history": [
            {
                "login_time": entry.login_time,
                "user_agent": entry.user_agent
            }
            for entry in history
        ]
    }

@router.get("/user-info", response_model=UserResponse)
async def get_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user
