from typing import Dict, Optional, Set
from datetime import datetime
from .models import User, UserInDB, UserRole, RegisterRequest
from .security import hash_password


class UserStorage:
    """In-memory хранилище пользователей"""
    
    def __init__(self):
        self.users: Dict[int, UserInDB] = {}
        self.users_by_username: Dict[str, UserInDB] = {}
        self.refresh_tokens: Set[str] = set()  # Активные refresh токены
        self.next_id: int = 1
        self._create_default_users()
    
    def _create_default_users(self):
        """Создание дефолтных пользователей для тестирования"""
        # Admin пользователь
        admin = UserInDB(
            id=1,
            username="admin",
            email="admin@titanic.local",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
            created_at=datetime.utcnow()
        )
        self.users[admin.id] = admin
        self.users_by_username[admin.username] = admin
        
        # Обычный пользователь
        user = UserInDB(
            id=2,
            username="testuser",
            email="user@titanic.local",
            password_hash=hash_password("user123"),
            role=UserRole.USER,
            is_active=True,
            created_at=datetime.utcnow()
        )
        self.users[user.id] = user
        self.users_by_username[user.username] = user
        
        self.next_id = 3
        print(f"✅ Created default users: admin (admin123), testuser (user123)")
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Получение пользователя по имени"""
        return self.users_by_username.get(username.lower())
    
    def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        """Получение пользователя по ID"""
        return self.users.get(user_id)
    
    def create_user(self, user_data: RegisterRequest, role: UserRole = UserRole.USER) -> UserInDB:
        """
        Создание нового пользователя
        
        Args:
            user_data: Данные для регистрации
            role: Роль пользователя (по умолчанию USER)
            
        Returns:
            UserInDB: Созданный пользователь
            
        Raises:
            ValueError: Если пользователь с таким username уже существует
        """
        username_lower = user_data.username.lower()
        
        if username_lower in self.users_by_username:
            raise ValueError(f"User with username '{user_data.username}' already exists")
        
        user = UserInDB(
            id=self.next_id,
            username=username_lower,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role=role,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        self.users[user.id] = user
        self.users_by_username[username_lower] = user
        self.next_id += 1
        
        return user
    
    def update_user(self, user_id: int, email: Optional[str] = None) -> Optional[UserInDB]:
        """
        Обновление пользователя
        
        Args:
            user_id: ID пользователя
            email: Новый email (опционально)
            
        Returns:
            UserInDB: Обновленный пользователь или None
        """
        user = self.users.get(user_id)
        if not user:
            return None
        
        if email is not None:
            # Создаем обновленную копию
            updated_user = UserInDB(
                id=user.id,
                username=user.username,
                email=email,
                password_hash=user.password_hash,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at
            )
            self.users[user_id] = updated_user
            self.users_by_username[user.username] = updated_user
            return updated_user
        
        return user
    
    def add_refresh_token(self, token: str):
        """Добавление refresh токена в список активных"""
        self.refresh_tokens.add(token)
    
    def remove_refresh_token(self, token: str):
        """Удаление refresh токена (logout)"""
        self.refresh_tokens.discard(token)
    
    def is_refresh_token_valid(self, token: str) -> bool:
        """Проверка, активен ли refresh токен"""
        return token in self.refresh_tokens
    
    def count(self) -> int:
        """Возвращает количество пользователей"""
        return len(self.users)


# Глобальный экземпляр хранилища
storage = UserStorage()

