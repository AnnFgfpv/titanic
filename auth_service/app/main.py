from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from datetime import timedelta
from .models import (
    RegisterRequest, LoginRequest, RefreshRequest, TokenResponse,
    User, UserUpdate, UserRole
)
from .storage import storage
from .security import (
    verify_password, create_access_token, create_refresh_token,
    decode_token, verify_token_type, ACCESS_TOKEN_EXPIRE_MINUTES
)
from .dependencies import get_current_active_user, require_admin

security = HTTPBearer()

tags_metadata = [
    {
        "name": "Authentication",
        "description": "Регистрация, вход и управление токенами"
    },
    {
        "name": "Users",
        "description": "Управление профилем пользователя"
    },
]

app = FastAPI(
    title="Titanic Auth Service",
    description="""
    ## 🔐 Сервис аутентификации и авторизации
    
    Управление пользователями и JWT токенами для системы Titanic Microservices.
    
    ### Возможности:
    - 📝 Регистрация новых пользователей
    - 🔑 Вход с получением JWT токенов
    - 🔄 Обновление access токена через refresh token
    - 👤 Управление профилем пользователя
    - 🚪 Выход с инвалидацией токена
    
    ### Токены:
    - **Access Token**: 15 минут (для API запросов)
    - **Refresh Token**: 7 дней (для обновления access token)
    
    ### Роли:
    - **admin**: Полный доступ (удаление пассажиров и т.д.)
    - **user**: Базовый доступ (создание и редактирование своих записей)
    
    ### 👑 Первый пользователь = Admin
    
    **Первый** зарегистрированный пользователь автоматически получает роль **admin**.
    Все последующие пользователи получают роль **user**.
    """,
    version="2.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Titanic Microservices Team",
        "email": "support@titanic-api.example.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)


@app.on_event("startup")
async def startup_event():
    """Инициализация при старте"""
    print(f"🔐 Auth Service started")
    print(f"📊 Total users: {storage.count()}")


@app.get("/", tags=["Authentication"])
async def root():
    """Информация о сервисе"""
    return {
        "service": "Titanic Auth Service",
        "version": "2.0.0",
        "status": "running",
        "users_count": storage.count()
    }


@app.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="Регистрация нового пользователя",
    description="""
    Регистрация нового пользователя в системе.
    
    После успешной регистрации возвращаются access и refresh токены.
    
    **Требования:**
    - Username: 3-50 символов, только буквы, цифры, _ и -
    - Password: минимум 6 символов
    - Email: опционально
    
    **Роль:** Первый зарегистрированный пользователь получает роль "admin",
    все остальные - роль "user"
    
    **Пример запроса:**
    ```json
    {
      "username": "newuser",
      "password": "password123",
      "email": "user@example.com"
    }
    ```
    """,
    responses={
        201: {
            "description": "Пользователь успешно зарегистрирован",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VyIiwidXNlcl9pZCI6Miwicm9sZSI6InVzZXIiLCJleHAiOjE3Mzc0NTUwMDB9.example_access_token_signature",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXd1c2VyIiwidXNlcl9pZCI6Miwicm9sZSI6InVzZXIiLCJ0eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNzQ2NDAwMH0.example_refresh_token_signature",
                        "token_type": "bearer",
                        "expires_in": 900
                    }
                }
            }
        },
        400: {
            "description": "Пользователь с таким username уже существует",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Username 'admin' already exists"
                    }
                }
            }
        }
    }
)
async def register(user_data: RegisterRequest):
    """Регистрация нового пользователя"""
    try:
        # Создаем пользователя (первый = admin, остальные = user)
        user = storage.create_user(user_data)
        
        # Создаем токены
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role.value},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role.value}
        )
        
        # Сохраняем refresh token
        storage.add_refresh_token(refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.post(
    "/login",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="Вход в систему",
    description="""
    Аутентификация пользователя и получение токенов.
    
    **Пример запроса:**
    ```json
    {
      "username": "admin",
      "password": "admin123"
    }
    ```
    """,
    responses={
        200: {
            "description": "Успешный вход",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTczNzQ1NTAwMH0.example_access_token_signature",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsInR5cGUiOiJyZWZyZXNoIiwiZXhwIjoxNzM3NDY0MDAwfQ.example_refresh_token_signature",
                        "token_type": "bearer",
                        "expires_in": 900
                    }
                }
            }
        },
        401: {
            "description": "Неверный username или пароль",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Incorrect username or password"
                    }
                }
            }
        }
    }
)
async def login(credentials: LoginRequest):
    """Вход в систему"""
    # Проверяем пользователя
    user = storage.get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    
    # Создаем токены
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value}
    )
    
    # Сохраняем refresh token
    storage.add_refresh_token(refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.post(
    "/refresh",
    response_model=TokenResponse,
    tags=["Authentication"],
    summary="Обновление access token",
    description="""
    Получение нового access token с помощью refresh token.
    
    Используйте этот endpoint когда access token истек (15 минут).
    Refresh token действителен 7 дней.
    
    **Пример запроса:**
    ```json
    {
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """,
    responses={
        200: {"description": "Токен успешно обновлен"},
        401: {"description": "Невалидный или истекший refresh token"}
    }
)
async def refresh_token(request: RefreshRequest):
    """Обновление access token"""
    # Проверяем тип токена
    if not verify_token_type(request.refresh_token, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Refresh token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, активен ли токен
    if not storage.is_refresh_token_valid(request.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or is invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Декодируем токен
    token_data = decode_token(request.refresh_token)
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем пользователя
    user = storage.get_user_by_username(token_data.username)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создаем новый access token
    new_access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role.value},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # Refresh token остается прежним (не ротируем для простоты)
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=request.refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.get(
    "/me",
    response_model=User,
    tags=["Users"],
    summary="Получить информацию о текущем пользователе",
    description="Возвращает данные авторизованного пользователя",
    responses={
        200: {"description": "Информация о пользователе"},
        401: {"description": "Не авторизован"}
    }
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@app.put(
    "/me",
    response_model=User,
    tags=["Users"],
    summary="Обновить профиль",
    description="""
    Обновление email пользователя.
    
    **Пример запроса:**
    ```json
    {
      "email": "newemail@example.com"
    }
    ```
    """,
    responses={
        200: {"description": "Профиль обновлен"},
        401: {"description": "Не авторизован"}
    }
)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Обновление профиля пользователя"""
    updated_user = storage.update_user(current_user.id, email=user_update.email)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return User(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        role=updated_user.role,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at
    )


@app.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Authentication"],
    summary="Выход из системы",
    description="""
    Инвалидация refresh token.
    
    После logout текущий refresh token становится недействительным.
    Access token продолжит работать до истечения срока (15 минут).
    
    **Пример запроса:**
    ```json
    {
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """,
    responses={
        204: {"description": "Успешный выход"},
        401: {"description": "Не авторизован"}
    }
)
async def logout(
    request: RefreshRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Выход из системы (инвалидация refresh token)"""
    storage.remove_refresh_token(request.refresh_token)
    return None

