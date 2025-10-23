from pydantic import BaseModel, Field, validator
from typing import Optional


class PassengerBase(BaseModel):
    """Базовая модель пассажира для создания и обновления"""
    name: str = Field(..., min_length=1, max_length=200, description="Имя пассажира")
    pclass: int = Field(..., ge=1, le=3, description="Класс билета (1, 2 или 3)")
    sex: str = Field(..., description="Пол пассажира (male/female)")
    age: Optional[int] = Field(None, ge=0, le=150, description="Возраст пассажира")
    fare: float = Field(..., ge=0, description="Стоимость билета")
    embarked: str = Field(..., description="Порт посадки (Southampton, Cherbourg, Queenstown)")
    destination: str = Field(..., min_length=1, max_length=200, description="Пункт назначения")
    cabin: Optional[str] = Field(None, max_length=50, description="Номер каюты (опционально)")
    ticket: str = Field(..., min_length=1, max_length=50, description="Номер билета")
    created_by: Optional[str] = Field(None, description="Username пользователя, создавшего запись")

    @validator('sex')
    def validate_sex(cls, v):
        if v not in ['male', 'female']:
            raise ValueError('sex must be either "male" or "female"')
        return v
    
    @validator('embarked')
    def validate_embarked(cls, v):
        valid_ports = ['Southampton', 'Cherbourg', 'Queenstown']
        if v not in valid_ports:
            raise ValueError(f'embarked must be one of: {", ".join(valid_ports)}')
        return v


class PassengerCreate(PassengerBase):
    """Модель для создания нового пассажира"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Dawson, Mr. Jack",
                "pclass": 3,
                "sex": "male",
                "age": 20,
                "fare": 8.05,
                "embarked": "Southampton",
                "destination": "Pursue dreams in America",
                "cabin": None,
                "ticket": "A/5 21171"
            }
        }


class PassengerUpdate(PassengerBase):
    """Модель для обновления пассажира"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "DeWitt Bukater, Miss. Rose",
                "pclass": 1,
                "sex": "female",
                "age": 17,
                "fare": 211.34,
                "embarked": "Southampton",
                "destination": "New York",
                "cabin": "B52",
                "ticket": "PC 17599"
            }
        }


class Passenger(PassengerBase):
    """Полная модель пассажира с ID"""
    id: int = Field(..., description="Уникальный идентификатор пассажира")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Braund, Mr. Owen Harris",
                "pclass": 3,
                "sex": "male",
                "age": 22,
                "fare": 7.25,
                "embarked": "Southampton",
                "destination": "New York",
                "cabin": None,
                "ticket": "A/5 21171"
            }
        }

