import csv
from typing import List, Optional, Dict
from pathlib import Path
from .models import Passenger, PassengerCreate


class PassengerStorage:
    """In-memory хранилище для пассажиров"""
    
    def __init__(self):
        self.passengers: Dict[int, Passenger] = {}
        self.next_id: int = 1
    
    def load_from_csv(self, csv_path: str) -> None:
        """Загрузка данных из CSV файла"""
        path = Path(csv_path)
        if not path.exists():
            print(f"Warning: CSV file {csv_path} not found. Starting with empty storage.")
            return
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Парсим возраст - округляем дробные значения
                    age_value = None
                    if row['Age'] and row['Age'].strip():
                        try:
                            age_value = int(float(row['Age']))  # float -> int для дробных значений
                        except ValueError:
                            age_value = None
                    
                    passenger = Passenger(
                        id=int(row['PassengerId']),
                        name=row['Name'],
                        pclass=int(row['Pclass']),
                        sex=row['Sex'],
                        age=age_value,
                        fare=float(row['Fare']),
                        embarked=row['Embarked'],
                        destination=row['Destination'],
                        cabin=row['Cabin'] if row['Cabin'] and row['Cabin'].strip() else None,
                        ticket=row['Ticket']
                    )
                    self.passengers[passenger.id] = passenger
                    self.next_id = max(self.next_id, passenger.id + 1)
                except (ValueError, KeyError) as e:
                    print(f"Error loading row: {row}, error: {e}")
                    continue
    
    def get_all(
        self, 
        pclass: Optional[int] = None,
        sex: Optional[str] = None,
        embarked: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Passenger]:
        """Получение всех пассажиров с фильтрацией и пагинацией"""
        filtered = list(self.passengers.values())
        
        # Применяем фильтры
        if pclass is not None:
            filtered = [p for p in filtered if p.pclass == pclass]
        if sex is not None:
            filtered = [p for p in filtered if p.sex == sex]
        if embarked is not None:
            filtered = [p for p in filtered if p.embarked == embarked]
        
        # Применяем пагинацию
        return filtered[offset:offset + limit]
    
    def search_by_name(self, name: str, limit: int = 100) -> List[Passenger]:
        """Поиск пассажиров по имени (case-insensitive)"""
        name_lower = name.lower()
        found = [
            p for p in self.passengers.values() 
            if name_lower in p.name.lower()
        ]
        return found[:limit]
    
    def get_by_id(self, passenger_id: int) -> Optional[Passenger]:
        """Получение пассажира по ID"""
        return self.passengers.get(passenger_id)
    
    def _is_jack(self, name: str) -> bool:
        """Проверка, является ли пассажир Джеком"""
        name_lower = name.lower()
        return 'jack' in name_lower or 'dawson' in name_lower
    
    def _is_rose(self, name: str) -> bool:
        """Проверка, является ли пассажир Розой"""
        name_lower = name.lower()
        return 'rose' in name_lower or 'dewitt' in name_lower or 'bukater' in name_lower
    
    def validate_cabin_assignment(self, passenger_name: str, cabin: Optional[str], exclude_id: Optional[int] = None) -> None:
        """
        Пасхалка: проверка, что Джек и Роза не в одной каюте!
        Raises ValueError если нарушено правило.
        """
        if not cabin:
            return  # Если каюты нет, проверка не нужна
        
        is_jack = self._is_jack(passenger_name)
        is_rose = self._is_rose(passenger_name)
        
        if not (is_jack or is_rose):
            return  # Обычный пассажир, проверка не нужна
        
        # Проверяем других пассажиров в этой каюте
        for pid, passenger in self.passengers.items():
            if exclude_id and pid == exclude_id:
                continue  # Пропускаем самого пассажира при обновлении
            
            if passenger.cabin == cabin:
                # Нашли кого-то в этой каюте
                if is_jack and self._is_rose(passenger.name):
                    raise ValueError(
                        "Different social classes cannot share cabins on Titanic. "
                        "Jack (3rd class) and Rose (1st class) must remain separate... for now. 🎭🚢"
                    )
                if is_rose and self._is_jack(passenger.name):
                    raise ValueError(
                        "I'm sorry, Jack and Rose cannot share the same cabin. "
                        "They're from different worlds! 💔🚢"
                    )
    
    def create(self, passenger_data: PassengerCreate) -> Passenger:
        """Создание нового пассажира"""
        # Проверяем пасхалку с каютой
        self.validate_cabin_assignment(passenger_data.name, passenger_data.cabin)
        
        passenger = Passenger(
            id=self.next_id,
            **passenger_data.dict()
        )
        self.passengers[passenger.id] = passenger
        self.next_id += 1
        return passenger
    
    def update(self, passenger_id: int, passenger_data: PassengerCreate) -> Optional[Passenger]:
        """Обновление существующего пассажира"""
        if passenger_id not in self.passengers:
            return None
        
        # Проверяем пасхалку с каютой (исключаем текущего пассажира)
        self.validate_cabin_assignment(passenger_data.name, passenger_data.cabin, exclude_id=passenger_id)
        
        passenger = Passenger(
            id=passenger_id,
            **passenger_data.dict()
        )
        self.passengers[passenger_id] = passenger
        return passenger
    
    def delete(self, passenger_id: int) -> bool:
        """Удаление пассажира"""
        if passenger_id in self.passengers:
            del self.passengers[passenger_id]
            return True
        return False
    
    def count(self) -> int:
        """Возвращает общее количество пассажиров"""
        return len(self.passengers)


# Глобальный экземпляр хранилища
storage = PassengerStorage()

