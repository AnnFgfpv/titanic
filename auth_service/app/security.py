from datetime import datetime, timedelta
from typing import Optional
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from .models import TokenData

# JWT конфигурация
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "titanic-super-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Контекст для хеширования паролей (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Хеширование пароля с помощью bcrypt
    
    Args:
        password: Пароль в открытом виде
        
    Returns:
        str: Хеш пароля
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля
    
    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хеш пароля
        
    Returns:
        bool: True если пароль верный
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT access токена
    
    Args:
        data: Данные для включения в токен (username, user_id, role)
        expires_delta: Время жизни токена (по умолчанию 15 минут)
        
    Returns:
        str: JWT токен
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Создание JWT refresh токена
    
    Args:
        data: Данные для включения в токен
        
    Returns:
        str: JWT refresh токен
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """
    Декодирование JWT токена
    
    Args:
        token: JWT токен
        
    Returns:
        TokenData: Данные из токена или None если токен невалидный
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None:
            return None
            
        token_data = TokenData(
            username=username,
            user_id=user_id,
            role=role
        )
        return token_data
    except JWTError:
        return None


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    Проверка типа токена (access или refresh)
    
    Args:
        token: JWT токен
        expected_type: Ожидаемый тип ("access" или "refresh")
        
    Returns:
        bool: True если тип совпадает
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        return token_type == expected_type
    except JWTError:
        return False

