from fastapi import Depends, HTTPException, status, Header
from typing import Optional, Dict
import httpx
import os

# URL Auth Service
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8003")


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict:
    """
    Получение текущего пользователя через Auth Service
    
    Args:
        authorization: Заголовок Authorization (Bearer <token>)
        
    Returns:
        dict: Данные пользователя из Auth Service
        
    Raises:
        HTTPException: 401 если токен отсутствует или невалидный
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing. Please provide: Authorization: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Делаем запрос к Auth Service для проверки токена
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/me",
                headers={"Authorization": authorization}
            )
            
            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Auth service unavailable"
                )
            
            user_data = response.json()
            return user_data
    
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to Auth Service"
        )


async def require_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """
    Требование роли admin
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        dict: Пользователь с ролью admin
        
    Raises:
        HTTPException: 403 если пользователь не admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Only administrators can perform this action."
        )
    return current_user

