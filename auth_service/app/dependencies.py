from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from .models import User, UserRole
from .security import decode_token
from .storage import storage


async def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    """
    Получение текущего пользователя из JWT токена
    
    Args:
        authorization: Заголовок Authorization (Bearer <token>)
        
    Returns:
        User: Данные пользователя
        
    Raises:
        HTTPException: 401 если токен отсутствует или невалидный
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Парсим "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    token_data = decode_token(token)
    
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    user = storage.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    
    # Возвращаем User без password_hash
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Проверка, что пользователь активен
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        User: Активный пользователь
        
    Raises:
        HTTPException: 403 если пользователь неактивен
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Требование роли admin
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        User: Пользователь с ролью admin
        
    Raises:
        HTTPException: 403 если пользователь не admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

