from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import HTTPBearer
from typing import List, Optional, Dict
from .models import Passenger, PassengerCreate, PassengerUpdate
from .storage import storage
from .dependencies import get_current_user, require_admin

# Security scheme для Swagger
security = HTTPBearer()

# Улучшенная метаинформация для Swagger
tags_metadata = [
    {
        "name": "Health",
        "description": "Проверка работоспособности сервиса"
    },
    {
        "name": "Passengers",
        "description": "CRUD операции с пассажирами Титаника. **Операции изменения данных требуют JWT токен в заголовке Authorization.**"
    },
]

app = FastAPI(
    title="Titanic Passenger Service",
    description="""
    ## 🚢 Сервис управления пассажирами Титаника
    
    Этот микросервис отвечает за хранение и управление данными пассажиров легендарного лайнера RMS Titanic.
    
    ### Особенности:
    - 📋 Полный CRUD для пассажиров
    - 🔍 Поиск по имени
    - 🎯 Фильтрация по классу, полу, порту посадки
    - 📄 Пагинация результатов
    - 🔐 JWT авторизация для операций изменения данных
    - 🎬 Пасхалки из фильма "Титаник"
    - 👤 Отслеживание автора записи (created_by)
    
    ### Авторизация:
    Для создания, обновления и удаления пассажиров требуется JWT токен.
    
    **Получение токена:**
    1. Зарегистрируйтесь: `POST /api/auth/register`
    2. Или войдите: `POST /api/auth/login`
    3. Используйте полученный access_token в заголовке: `Authorization: Bearer <token>`
    
    **Дефолтные пользователи для тестов:**
    - `admin` / `admin123` (роль: admin - может удалять)
    - `testuser` / `user123` (роль: user - может создавать/редактировать)
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


@app.on_event("startup")
async def startup_event():
    """Загрузка данных из CSV при старте сервиса"""
    storage.load_from_csv("/app/data/titanic.csv")
    print(f"✅ Loaded {storage.count()} passengers from CSV")


@app.get(
    "/", 
    tags=["Health"],
    summary="Проверка работоспособности",
    response_description="Статус сервиса и количество пассажиров"
)
async def root():
    """Проверка работоспособности сервиса"""
    return {
        "service": "Titanic Passenger Service",
        "status": "running",
        "version": "3.0.0",
        "passengers_count": storage.count(),
        "auth": "JWT Bearer Token"
    }


@app.get(
    "/passengers", 
    response_model=List[Passenger], 
    tags=["Passengers"],
    summary="Получить список пассажиров",
    description="""
    Возвращает список пассажиров с возможностью фильтрации и пагинации.
    
    **Примеры использования:**
    - Все пассажиры: `/passengers`
    - Пассажиры 1-го класса: `/passengers?pclass=1`
    - Женщины из Саутгемптона: `/passengers?sex=female&embarked=Southampton`
    - Первые 20 записей: `/passengers?limit=20`
    
    **🔓 Не требует авторизации**
    """,
    responses={
        200: {
            "description": "Успешный ответ со списком пассажиров"
        },
        400: {"description": "Некорректные параметры запроса"}
    }
)
async def get_passengers(
    pclass: Optional[int] = Query(None, ge=1, le=3, description="Класс билета (1, 2 или 3)", example=1),
    sex: Optional[str] = Query(None, description="Пол (male или female)", example="female"),
    embarked: Optional[str] = Query(None, description="Порт посадки", example="Southampton"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей", example=10),
    offset: int = Query(0, ge=0, description="Смещение для пагинации", example=0)
):
    """Получение списка всех пассажиров с фильтрацией и пагинацией"""
    if sex and sex not in ['male', 'female']:
        raise HTTPException(status_code=400, detail="sex must be 'male' or 'female'")
    
    if embarked and embarked not in ['Southampton', 'Cherbourg', 'Queenstown']:
        raise HTTPException(
            status_code=400, 
            detail="embarked must be one of: Southampton, Cherbourg, Queenstown"
        )
    
    passengers = storage.get_all(
        pclass=pclass,
        sex=sex,
        embarked=embarked,
        limit=limit,
        offset=offset
    )
    return passengers


@app.get(
    "/passengers/search",
    response_model=List[Passenger],
    tags=["Passengers"],
    summary="Поиск пассажиров по имени",
    description="""
    Поиск пассажиров по имени (регистронезависимый).
    
    **🎬 Пасхалка:** Попробуйте найти `Jack` или `Rose`!
    
    **🔓 Не требует авторизации**
    """,
    responses={
        200: {"description": "Список найденных пассажиров"}
    }
)
async def search_passengers(
    name: str = Query(..., min_length=1, description="Часть имени для поиска", example="Jack"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество результатов")
):
    """Поиск пассажиров по имени (case-insensitive)"""
    passengers = storage.search_by_name(name, limit)
    return passengers


@app.post(
    "/passengers", 
    response_model=Passenger, 
    status_code=201, 
    tags=["Passengers"],
    summary="Создать нового пассажира 🔐",
    description="""
    Создание нового пассажира. **Требуется JWT авторизация.**
    
    Поле `created_by` будет автоматически заполнено username текущего пользователя.
    
    **🎭 Пасхалка:** Попробуйте поселить Джека и Розу в одну каюту! 
    """,
    responses={
        201: {"description": "Пассажир успешно создан"},
        400: {"description": "Ошибка валидации данных или пасхалка с Джеком и Розой! 🎬"},
        401: {"description": "Отсутствует или невалидный JWT токен"}
    }
)
async def create_passenger(
    passenger: PassengerCreate,
    current_user: Dict = Depends(get_current_user)
):
    """Создание нового пассажира (требуется JWT токен)"""
    try:
        # Добавляем информацию о создателе
        passenger.created_by = current_user.get("username")
        new_passenger = storage.create(passenger)
        return new_passenger
    except ValueError as e:
        # Пасхалка с Джеком и Розой
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/passengers/{passenger_id}", 
    response_model=Passenger, 
    tags=["Passengers"],
    summary="Получить пассажира по ID",
    description="""
    Возвращает информацию о конкретном пассажире.
    
    **🔓 Не требует авторизации**
    """,
    responses={
        200: {"description": "Пассажир найден"},
        404: {"description": "Пассажир с указанным ID не найден"}
    }
)
async def get_passenger(passenger_id: int):
    """Получение информации о конкретном пассажире по ID"""
    passenger = storage.get_by_id(passenger_id)
    if passenger is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Passenger with id {passenger_id} not found"
        )
    return passenger


@app.put(
    "/passengers/{passenger_id}", 
    response_model=Passenger, 
    tags=["Passengers"],
    summary="Обновить данные пассажира 🔐",
    description="""
    Обновление данных пассажира. **Требуется JWT авторизация.**
    
    **🎭 Пасхалка:** Джек и Роза не могут быть в одной каюте!
    """,
    responses={
        200: {"description": "Пассажир успешно обновлен"},
        400: {"description": "Ошибка валидации или пасхалка с каютой"},
        401: {"description": "Отсутствует или невалидный JWT токен"},
        404: {"description": "Пассажир не найден"}
    }
)
async def update_passenger(
    passenger_id: int,
    passenger: PassengerUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Обновление данных пассажира (требуется JWT токен)"""
    try:
        # Сохраняем created_by при обновлении
        existing = storage.get_by_id(passenger_id)
        if existing and existing.created_by:
            passenger.created_by = existing.created_by
        
        updated_passenger = storage.update(passenger_id, passenger)
        if updated_passenger is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Passenger with id {passenger_id} not found"
            )
        return updated_passenger
    except ValueError as e:
        # Пасхалка с Джеком и Розой
        raise HTTPException(status_code=400, detail=str(e))


@app.delete(
    "/passengers/{passenger_id}", 
    status_code=204, 
    tags=["Passengers"],
    summary="Удалить пассажира 🔐👑",
    description="""
    Удаление пассажира из системы. **Требуется JWT авторизация с ролью admin.**
    
    Только администраторы могут удалять пассажиров.
    """,
    responses={
        204: {"description": "Пассажир успешно удален"},
        401: {"description": "Отсутствует или невалидный JWT токен"},
        403: {"description": "Недостаточно прав (требуется роль admin)"},
        404: {"description": "Пассажир не найден"}
    }
)
async def delete_passenger(
    passenger_id: int,
    current_user: Dict = Depends(require_admin)
):
    """Удаление пассажира (требуется роль admin)"""
    success = storage.delete(passenger_id)
    if not success:
        raise HTTPException(
            status_code=404, 
            detail=f"Passenger with id {passenger_id} not found"
        )
    return None
