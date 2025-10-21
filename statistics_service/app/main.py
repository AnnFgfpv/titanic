from fastapi import FastAPI, HTTPException
import httpx
import os
from typing import Dict, List
from collections import Counter

tags_metadata = [
    {
        "name": "Health",
        "description": "Проверка работоспособности сервиса"
    },
    {
        "name": "Statistics",
        "description": "Статистические данные по пассажирам Титаника"
    },
]

app = FastAPI(
    title="Titanic Statistics Service",
    description="""
    ## 📊 Сервис статистики по пассажирам Титаника
    
    Этот микросервис предоставляет различную статистику о пассажирах легендарного лайнера.
    
    ### Возможности:
    - 📈 Общая статистика по всем пассажирам
    - 🎫 Анализ по классам билетов
    - ⚓ Статистика по портам посадки
    - 🗺️ Популярные направления путешествий
    - 👥 Возрастное распределение
    
    **Примечание:** Этот сервис получает данные от Passenger Service через HTTP.
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

# URL Passenger Service
PASSENGER_SERVICE_URL = os.getenv("PASSENGER_SERVICE_URL", "http://passenger-service:8001")


async def fetch_all_passengers() -> List[Dict]:
    """Вспомогательная функция для получения всех пассажиров"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{PASSENGER_SERVICE_URL}/passengers",
                params={"limit": 1000, "offset": 0}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Error communicating with Passenger Service: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Passenger Service: {str(e)}"
        )


@app.get("/", tags=["Health"])
async def root():
    """Проверка работоспособности сервиса"""
    return {
        "service": "Titanic Statistics Service",
        "status": "running",
        "version": "2.0.0"
    }


@app.get(
    "/stats", 
    tags=["Statistics"],
    summary="Общая статистика",
    description="""
    Возвращает общую позитивную статистику по всем пассажирам Титаника.
    
    Включает:
    - Общее количество пассажиров
    - Средний возраст
    - Среднюю стоимость билета
    - Самый дорогой билет
    - Самое популярное направление
    """,
    responses={
        200: {
            "description": "Успешный ответ со статистикой",
            "content": {
                "application/json": {
                    "example": {
                        "total_passengers": 102,
                        "average_age": 29.85,
                        "average_fare": 35.62,
                        "most_expensive_ticket": 512.33,
                        "most_popular_destination": "New York"
                    }
                }
            }
        },
        502: {"description": "Ошибка связи с Passenger Service"},
        503: {"description": "Passenger Service недоступен"}
    }
)
async def get_statistics():
    """Рассчитывает и возвращает общую статистику по всем пассажирам"""
    passengers = await fetch_all_passengers()
    
    if not passengers:
        return {
            "total_passengers": 0,
            "average_age": None,
            "average_fare": 0.0,
            "most_expensive_ticket": 0.0,
            "most_popular_destination": None
        }
    
    # Расчет статистики
    total_passengers = len(passengers)
    
    # Средний возраст (только для пассажиров с указанным возрастом)
    ages = [p['age'] for p in passengers if p.get('age') is not None]
    average_age = round(sum(ages) / len(ages), 2) if ages else None
    
    # Средняя стоимость билета
    fares = [p['fare'] for p in passengers if p.get('fare')]
    average_fare = round(sum(fares) / len(fares), 2) if fares else 0.0
    
    # Самый дорогой билет
    most_expensive_ticket = round(max(fares), 2) if fares else 0.0
    
    # Популярное направление
    destinations = [p['destination'] for p in passengers if p.get('destination')]
    destination_counter = Counter(destinations)
    most_popular_destination = destination_counter.most_common(1)[0][0] if destination_counter else None
    
    return {
        "total_passengers": total_passengers,
        "average_age": average_age,
        "average_fare": average_fare,
        "most_expensive_ticket": most_expensive_ticket,
        "most_popular_destination": most_popular_destination
    }


@app.get(
    "/stats/by-class",
    tags=["Statistics"],
    summary="Статистика по классам",
    description="Распределение пассажиров и средние показатели по классам билетов.",
    responses={
        200: {
            "description": "Статистика по каждому классу",
            "content": {
                "application/json": {
                    "example": {
                        "class_1": {"total": 22, "average_fare": 84.15, "average_age": 38.2},
                        "class_2": {"total": 18, "average_fare": 20.66, "average_age": 29.9},
                        "class_3": {"total": 62, "average_fare": 13.68, "average_age": 25.1}
                    }
                }
            }
        }
    }
)
async def get_stats_by_class():
    """Статистика по классам билетов"""
    passengers = await fetch_all_passengers()
    
    stats = {}
    for pclass in [1, 2, 3]:
        class_passengers = [p for p in passengers if p.get('pclass') == pclass]
        
        if class_passengers:
            ages = [p['age'] for p in class_passengers if p.get('age') is not None]
            fares = [p['fare'] for p in class_passengers if p.get('fare')]
            
            stats[f"class_{pclass}"] = {
                "total": len(class_passengers),
                "average_fare": round(sum(fares) / len(fares), 2) if fares else 0.0,
                "average_age": round(sum(ages) / len(ages), 2) if ages else None
            }
        else:
            stats[f"class_{pclass}"] = {
                "total": 0,
                "average_fare": 0.0,
                "average_age": None
            }
    
    return stats


@app.get(
    "/stats/by-port",
    tags=["Statistics"],
    summary="Статистика по портам посадки",
    description="Количество пассажиров и средняя стоимость билетов для каждого порта посадки.",
    responses={
        200: {
            "description": "Статистика по портам",
            "content": {
                "application/json": {
                    "example": {
                        "Southampton": {"total": 70, "average_fare": 28.50},
                        "Cherbourg": {"total": 18, "average_fare": 52.30},
                        "Queenstown": {"total": 14, "average_fare": 11.20}
                    }
                }
            }
        }
    }
)
async def get_stats_by_port():
    """Статистика по портам посадки"""
    passengers = await fetch_all_passengers()
    
    ports = ['Southampton', 'Cherbourg', 'Queenstown']
    stats = {}
    
    for port in ports:
        port_passengers = [p for p in passengers if p.get('embarked') == port]
        
        if port_passengers:
            fares = [p['fare'] for p in port_passengers if p.get('fare')]
            stats[port] = {
                "total": len(port_passengers),
                "average_fare": round(sum(fares) / len(fares), 2) if fares else 0.0
            }
        else:
            stats[port] = {
                "total": 0,
                "average_fare": 0.0
            }
    
    return stats


@app.get(
    "/stats/destinations",
    tags=["Statistics"],
    summary="Популярные направления",
    description="""
    Топ направлений, куда направлялись пассажиры.
    
    **🎬 Пасхалка:** Обратите внимание на уникальное направление Джека!
    """,
    responses={
        200: {
            "description": "Список направлений с количеством пассажиров",
            "content": {
                "application/json": {
                    "example": {
                        "destinations": [
                            {"name": "New York", "count": 45},
                            {"name": "Immigration", "count": 20},
                            {"name": "Business trip", "count": 15},
                            {"name": "Pursue dreams in America", "count": 1}
                        ]
                    }
                }
            }
        }
    }
)
async def get_destinations():
    """Популярные направления путешествий"""
    passengers = await fetch_all_passengers()
    
    destinations = [p['destination'] for p in passengers if p.get('destination')]
    destination_counter = Counter(destinations)
    
    # Сортируем по популярности
    sorted_destinations = [
        {"name": dest, "count": count}
        for dest, count in destination_counter.most_common()
    ]
    
    return {"destinations": sorted_destinations}


@app.get(
    "/stats/age-distribution",
    tags=["Statistics"],
    summary="Возрастное распределение",
    description="Распределение пассажиров по возрастным группам.",
    responses={
        200: {
            "description": "Распределение по возрастным группам",
            "content": {
                "application/json": {
                    "example": {
                        "children_0_12": {"count": 15, "percentage": 15.0},
                        "teens_13_19": {"count": 12, "percentage": 12.0},
                        "adults_20_40": {"count": 48, "percentage": 48.0},
                        "middle_age_41_60": {"count": 20, "percentage": 20.0},
                        "seniors_61_plus": {"count": 5, "percentage": 5.0}
                    }
                }
            }
        }
    }
)
async def get_age_distribution():
    """Возрастное распределение пассажиров"""
    passengers = await fetch_all_passengers()
    
    # Фильтруем пассажиров с известным возрастом
    passengers_with_age = [p for p in passengers if p.get('age') is not None]
    total_with_age = len(passengers_with_age)
    
    if total_with_age == 0:
        return {
            "children_0_12": {"count": 0, "percentage": 0.0},
            "teens_13_19": {"count": 0, "percentage": 0.0},
            "adults_20_40": {"count": 0, "percentage": 0.0},
            "middle_age_41_60": {"count": 0, "percentage": 0.0},
            "seniors_61_plus": {"count": 0, "percentage": 0.0}
        }
    
    # Распределение по группам
    children = len([p for p in passengers_with_age if 0 <= p['age'] <= 12])
    teens = len([p for p in passengers_with_age if 13 <= p['age'] <= 19])
    adults = len([p for p in passengers_with_age if 20 <= p['age'] <= 40])
    middle_age = len([p for p in passengers_with_age if 41 <= p['age'] <= 60])
    seniors = len([p for p in passengers_with_age if p['age'] >= 61])
    
    return {
        "children_0_12": {
            "count": children,
            "percentage": round((children / total_with_age) * 100, 1)
        },
        "teens_13_19": {
            "count": teens,
            "percentage": round((teens / total_with_age) * 100, 1)
        },
        "adults_20_40": {
            "count": adults,
            "percentage": round((adults / total_with_age) * 100, 1)
        },
        "middle_age_41_60": {
            "count": middle_age,
            "percentage": round((middle_age / total_with_age) * 100, 1)
        },
        "seniors_61_plus": {
            "count": seniors,
            "percentage": round((seniors / total_with_age) * 100, 1)
        }
    }
