from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import httpx
import os

security = HTTPBearer()

tags_metadata = [
    {
        "name": "Gateway",
        "description": "Информация о Gateway и проверка работоспособности"
    },
    {
        "name": "Authentication",
        "description": "Регистрация, вход и управление токенами (проксируется к Auth Service)"
    },
    {
        "name": "Passengers",
        "description": "Операции с пассажирами (проксируется к Passenger Service). **Для POST/PUT/DELETE требуется JWT токен**"
    },
    {
        "name": "Statistics",
        "description": "Статистика по пассажирам (проксируется к Statistics Service)"
    },
]

app = FastAPI(
    title="🚢 Titanic API Gateway",
    description="""
    ## Единая точка входа в микросервисную систему Титаник
    
    API Gateway обеспечивает централизованный доступ ко всем микросервисам системы.
    
    ### 📋 Доступные сервисы:
    
    #### 1. Auth Service 🔐
    Аутентификация и авторизация:
    - **POST** `/api/auth/register` - регистрация нового пользователя
    - **POST** `/api/auth/login` - вход и получение JWT токенов
    - **POST** `/api/auth/refresh` - обновление access token
    - **GET** `/api/auth/me` - информация о текущем пользователе 🔐
    - **PUT** `/api/auth/me` - обновление профиля 🔐
    - **POST** `/api/auth/logout` - выход 🔐
    
    #### 2. Passenger Service
    Управление данными пассажиров:
    - **GET** `/api/passengers` - список пассажиров с фильтрацией
    - **GET** `/api/passengers/search` - поиск по имени (🎬 найдите Джека и Розу!)
    - **GET** `/api/passengers/{id}` - получить пассажира
    - **POST** `/api/passengers` - создать пассажира 🔐
    - **PUT** `/api/passengers/{id}` - обновить пассажира 🔐
    - **DELETE** `/api/passengers/{id}` - удалить пассажира 🔐👑 (только admin)
    
    #### 3. Statistics Service
    Статистика и аналитика:
    - **GET** `/api/stats` - общая статистика
    - **GET** `/api/stats/by-class` - по классам
    - **GET** `/api/stats/by-port` - по портам посадки
    - **GET** `/api/stats/destinations` - популярные направления
    - **GET** `/api/stats/age-distribution` - возрастное распределение
    
    ### 🔐 Аутентификация (JWT)
    
    Система использует JWT токены для аутентификации.
    
    **Шаг 1: Регистрация или вход**
    ```bash
    # Регистрация
    POST /api/auth/register
    {
      "username": "myuser",
      "password": "mypassword123",
      "email": "user@example.com"
    }
    
    # Или вход
    POST /api/auth/login
    {
      "username": "admin",
      "password": "admin123"
    }
    ```
    
    **Шаг 2: Получите токены**
    ```json
    {
      "access_token": "eyJhbGc...",
      "refresh_token": "eyJhbGc...",
      "token_type": "bearer",
      "expires_in": 900
    }
    ```
    
    **Шаг 3: Используйте access token**
    ```
    Authorization: Bearer eyJhbGc...
    ```
    
    **Access token** (15 минут) - используется для API запросов  
    **Refresh token** (7 дней) - для обновления access token
    
    ### 👥 Дефолтные пользователи для тестирования:
    ```
    admin / admin123 (роль: admin - полный доступ)
    testuser / user123 (роль: user - создание/редактирование)
    ```
    
    ### 🎬 Пасхалки
    - Попробуйте найти Джека Доусона и Розу ДеВитт Букатер!
    - Попробуйте поселить их в одну каюту... 😏
    """,
    version="3.0.0",
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

# CORS middleware для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# URLs внутренних сервисов
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8003")
PASSENGER_SERVICE_URL = os.getenv("PASSENGER_SERVICE_URL", "http://passenger-service:8001")
STATS_SERVICE_URL = os.getenv("STATS_SERVICE_URL", "http://stats-service:8002")


@app.get("/", tags=["Gateway"])
async def root():
    """Главная страница API Gateway"""
    return {
        "service": "Titanic API Gateway",
        "version": "3.0.0",
        "status": "running",
        "documentation": "/docs",
        "auth": "JWT Bearer Token",
        "services": {
            "auth_service": {
                "base_url": "/api/auth",
                "description": "Аутентификация и авторизация"
            },
            "passenger_service": {
                "base_url": "/api/passengers",
                "description": "Управление пассажирами"
            },
            "statistics_service": {
                "base_url": "/api/stats",
                "description": "Статистика и аналитика"
            }
        },
        "easter_eggs": "🎬 Try to find Jack and Rose!"
    }


@app.get("/health", tags=["Gateway"])
async def health_check():
    """
    Проверка работоспособности Gateway и всех подключенных сервисов.
    
    Возвращает статус каждого сервиса: healthy, unhealthy или unavailable.
    """
    health_status = {
        "gateway": "healthy",
        "version": "3.0.0",
        "services": {}
    }
    
    # Проверка Auth Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{AUTH_SERVICE_URL}/")
            health_status["services"]["auth_service"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": AUTH_SERVICE_URL
            }
    except Exception as e:
        health_status["services"]["auth_service"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    # Проверка Passenger Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{PASSENGER_SERVICE_URL}/")
            health_status["services"]["passenger_service"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": PASSENGER_SERVICE_URL
            }
    except Exception as e:
        health_status["services"]["passenger_service"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    # Проверка Statistics Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{STATS_SERVICE_URL}/")
            health_status["services"]["stats_service"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "url": STATS_SERVICE_URL
            }
    except Exception as e:
        health_status["services"]["stats_service"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    return health_status


async def proxy_request(
    request: Request,
    target_url: str,
    method: str = "GET"
) -> Response:
    """
    Универсальная функция для проксирования запросов к внутренним сервисам
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Подготовка параметров запроса
            headers = dict(request.headers)
            # Удаляем headers, которые не нужно передавать
            headers.pop('host', None)
            
            # Выполняем запрос к целевому сервису
            if method == "GET":
                response = await client.get(
                    target_url,
                    params=request.query_params,
                    headers=headers
                )
            elif method == "POST":
                body = await request.body()
                response = await client.post(
                    target_url,
                    content=body,
                    headers=headers
                )
            elif method == "PUT":
                body = await request.body()
                response = await client.put(
                    target_url,
                    content=body,
                    headers=headers
                )
            elif method == "DELETE":
                response = await client.delete(
                    target_url,
                    headers=headers
                )
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            # Возвращаем ответ от сервиса
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            status_code=e.response.status_code,
            content={"detail": f"Service error: {e.response.text}"}
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )


# === Маршруты для Auth Service ===

@app.post(
    "/api/auth/register",
    tags=["Authentication"],
    summary="Регистрация нового пользователя",
    description="Создание нового пользователя и получение JWT токенов"
)
async def register(request: Request):
    """Регистрация (проксирование к Auth Service)"""
    target_url = f"{AUTH_SERVICE_URL}/register"
    return await proxy_request(request, target_url, "POST")


@app.post(
    "/api/auth/login",
    tags=["Authentication"],
    summary="Вход в систему",
    description="""
    Аутентификация и получение JWT токенов.

    """
)
async def login(request: Request):
    """Вход (проксирование к Auth Service)"""
    target_url = f"{AUTH_SERVICE_URL}/login"
    return await proxy_request(request, target_url, "POST")


@app.post(
    "/api/auth/refresh",
    tags=["Authentication"],
    summary="Обновить access token",
    description="Получение нового access token с помощью refresh token"
)
async def refresh(request: Request):
    """Обновление токена (проксирование к Auth Service)"""
    target_url = f"{AUTH_SERVICE_URL}/refresh"
    return await proxy_request(request, target_url, "POST")


@app.get(
    "/api/auth/me",
    tags=["Authentication"],
    summary="Получить информацию о текущем пользователе 🔐",
    description="Требуется JWT токен в заголовке Authorization"
)
async def get_me(request: Request):
    """Информация о пользователе (проксирование к Auth Service)"""
    target_url = f"{AUTH_SERVICE_URL}/me"
    return await proxy_request(request, target_url, "GET")


@app.put(
    "/api/auth/me",
    tags=["Authentication"],
    summary="Обновить профиль 🔐",
    description="Обновление email пользователя. Требуется JWT токен."
)
async def update_me(request: Request):
    """Обновление профиля (проксирование к Auth Service)"""
    target_url = f"{AUTH_SERVICE_URL}/me"
    return await proxy_request(request, target_url, "PUT")


@app.post(
    "/api/auth/logout",
    tags=["Authentication"],
    summary="Выход из системы 🔐",
    description="Инвалидация refresh token. Требуется JWT токен."
)
async def logout(request: Request):
    """Выход (проксирование к Auth Service)"""
    target_url = f"{AUTH_SERVICE_URL}/logout"
    return await proxy_request(request, target_url, "POST")


# === Маршруты для Passenger Service ===

@app.get(
    "/api/passengers", 
    tags=["Passengers"],
    summary="Получить список пассажиров",
    description="Возвращает список пассажиров с фильтрацией по классу, полу, порту посадки и пагинацией."
)
async def get_passengers(request: Request):
    """Получение списка пассажиров (проксирование к Passenger Service)"""
    target_url = f"{PASSENGER_SERVICE_URL}/passengers"
    return await proxy_request(request, target_url, "GET")


@app.get(
    "/api/passengers/search",
    tags=["Passengers"],
    summary="Поиск пассажиров по имени",
    description="""
    Поиск пассажиров по имени (регистронезависимый).
    
    **🎬 Пасхалка:** Попробуйте `?name=Jack` или `?name=Rose`!
    """
)
async def search_passengers(request: Request):
    """Поиск пассажиров по имени (проксирование к Passenger Service)"""
    target_url = f"{PASSENGER_SERVICE_URL}/passengers/search"
    return await proxy_request(request, target_url, "GET")


@app.post(
    "/api/passengers", 
    tags=["Passengers"],
    summary="Создать нового пассажира 🔐",
    description="""
    Создание нового пассажира. **Требуется JWT токен!**
    
    **🎭 Пасхалка:** Попробуйте поселить Джека и Розу в одну каюту!
    """
)
async def create_passenger(request: Request):
    """Создание нового пассажира (проксирование к Passenger Service)"""
    target_url = f"{PASSENGER_SERVICE_URL}/passengers"
    return await proxy_request(request, target_url, "POST")


@app.get(
    "/api/passengers/{passenger_id}", 
    tags=["Passengers"],
    summary="Получить пассажира по ID",
    description="Возвращает информацию о конкретном пассажире."
)
async def get_passenger(passenger_id: int, request: Request):
    """Получение информации о пассажире (проксирование к Passenger Service)"""
    target_url = f"{PASSENGER_SERVICE_URL}/passengers/{passenger_id}"
    return await proxy_request(request, target_url, "GET")


@app.put(
    "/api/passengers/{passenger_id}", 
    tags=["Passengers"],
    summary="Обновить данные пассажира 🔐",
    description="Обновление данных пассажира. **Требуется JWT токен!**"
)
async def update_passenger(passenger_id: int, request: Request):
    """Обновление данных пассажира (проксирование к Passenger Service)"""
    target_url = f"{PASSENGER_SERVICE_URL}/passengers/{passenger_id}"
    return await proxy_request(request, target_url, "PUT")


@app.delete(
    "/api/passengers/{passenger_id}", 
    tags=["Passengers"],
    summary="Удалить пассажира 🔐👑",
    description="Удаление пассажира. **Требуется JWT токен с ролью admin!**"
)
async def delete_passenger(passenger_id: int, request: Request):
    """Удаление пассажира (проксирование к Passenger Service)"""
    target_url = f"{PASSENGER_SERVICE_URL}/passengers/{passenger_id}"
    return await proxy_request(request, target_url, "DELETE")


# === Маршруты для Statistics Service ===

@app.get(
    "/api/stats", 
    tags=["Statistics"],
    summary="Общая статистика",
    description="Общая позитивная статистика по всем пассажирам: количество, средний возраст, средняя стоимость билета и т.д."
)
async def get_statistics(request: Request):
    """Получение общей статистики (проксирование к Statistics Service)"""
    target_url = f"{STATS_SERVICE_URL}/stats"
    return await proxy_request(request, target_url, "GET")


@app.get(
    "/api/stats/by-class",
    tags=["Statistics"],
    summary="Статистика по классам",
    description="Распределение пассажиров и средние показатели по классам билетов."
)
async def get_stats_by_class(request: Request):
    """Статистика по классам (проксирование к Statistics Service)"""
    target_url = f"{STATS_SERVICE_URL}/stats/by-class"
    return await proxy_request(request, target_url, "GET")


@app.get(
    "/api/stats/by-port",
    tags=["Statistics"],
    summary="Статистика по портам посадки",
    description="Количество пассажиров и средняя стоимость билетов для каждого порта (Southampton, Cherbourg, Queenstown)."
)
async def get_stats_by_port(request: Request):
    """Статистика по портам (проксирование к Statistics Service)"""
    target_url = f"{STATS_SERVICE_URL}/stats/by-port"
    return await proxy_request(request, target_url, "GET")


@app.get(
    "/api/stats/destinations",
    tags=["Statistics"],
    summary="Популярные направления",
    description="""
    Топ направлений, куда направлялись пассажиры.
    
    **🎬 Пасхалка:** Найдите уникальное направление Джека!
    """
)
async def get_destinations(request: Request):
    """Популярные направления (проксирование к Statistics Service)"""
    target_url = f"{STATS_SERVICE_URL}/stats/destinations"
    return await proxy_request(request, target_url, "GET")


@app.get(
    "/api/stats/age-distribution",
    tags=["Statistics"],
    summary="Возрастное распределение",
    description="Распределение пассажиров по возрастным группам с процентным соотношением."
)
async def get_age_distribution(request: Request):
    """Возрастное распределение (проксирование к Statistics Service)"""
    target_url = f"{STATS_SERVICE_URL}/stats/age-distribution"
    return await proxy_request(request, target_url, "GET")
