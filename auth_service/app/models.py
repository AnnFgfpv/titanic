from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    USER = "user"


class UserBase(BaseModel):
    """Базовая модель пользователя"""
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: Optional[str] = Field(None, description="Email пользователя")
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username может содержать только буквы, цифры, _ и -')
        return v.lower()


class RegisterRequest(UserBase):
    """Запрос на регистрацию"""
    password: str = Field(..., min_length=6, max_length=100, description="Пароль (минимум 6 символов)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "newuser",
                "password": "password123",
                "email": "user@example.com"
            }
        }


class LoginRequest(BaseModel):
    """Запрос на вход"""
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }


class RefreshRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNzM3NDY0MDAwfQ.example_refresh_token_signature"
            }
        }


class TokenResponse(BaseModel):
    """Ответ с токенами"""
    access_token: str = Field(..., description="JWT Access Token")
    refresh_token: str = Field(..., description="JWT Refresh Token")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни access token в секундах")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }


class User(UserBase):
    """Полная модель пользователя"""
    id: int = Field(..., description="Уникальный идентификатор")
    role: UserRole = Field(default=UserRole.USER, description="Роль пользователя")
    is_active: bool = Field(default=True, description="Активен ли пользователь")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Дата создания")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@titanic.local",
                "role": "admin",
                "is_active": True,
                "created_at": "2025-10-21T10:00:00"
            }
        }


class UserInDB(User):
    """Пользователь в БД (с хешем пароля)"""
    password_hash: str = Field(..., description="Хеш пароля")


class UserUpdate(BaseModel):
    """Обновление профиля пользователя"""
    email: Optional[str] = Field(None, description="Новый email")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com"
            }
        }


class TokenData(BaseModel):
    """Данные из JWT токена"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

