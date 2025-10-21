# 🚢 Titanic Microservices API

Система микросервисов на основе данных пассажиров легендарного лайнера RMS Titanic. Этот проект представляет собой **продвинутый учебный стенд** для практики работы с распределенными системами, написания автотестов и изучения микросервисной архитектуры.

## 🎯 Особенности проекта

- 🔐 **JWT аутентификация** - полноценная система регистрации и логина
- 👥 **Роли пользователей** - admin и user с разными правами доступа
- 📊 **Расширенная статистика** - 5 различных статистических endpoints
- 🔍 **Поиск по имени** - найдите любого пассажира
- 📚 **Улучшенная Swagger документация** - с примерами и подробными описаниями
- 🎬 **Пасхалки из фильма "Титаник"** - Jack и Rose с особыми правилами!

## 🏗️ Архитектура

Система состоит из **четырех** независимых микросервисов:

1. **API Gateway** (порт 8000) - единая точка входа для всех внешних запросов
2. **Auth Service** (порт 8003) - аутентификация и управление пользователями (JWT)
3. **Passenger Service** (порт 8001) - управление данными пассажиров (CRUD + поиск)
4. **Statistics Service** (порт 8002) - расчет и предоставление статистики

```
┌─────────────────────────────────────────────┐
│         API Gateway :8000                   │
│    (Entry Point + Request Routing)          │
└──────┬─────────────┬─────────────┬──────────┘
       │             │             │
┌──────▼──────┐  ┌──▼─────────┐  ┌▼─────────────────┐
│ Auth        │  │ Passenger  │  │ Statistics       │
│ Service     │◄─┤ Service    │◄─┤ Service          │
│ :8003       │  │ :8001      │  │ :8002            │
│ (JWT)       │  │ (Data)     │  │ (Aggregator)     │
└─────────────┘  └────────────┘  └──────────────────┘
```

## 🛠️ Технологический стек

- **Язык**: Python 3.11
- **Фреймворк**: FastAPI
- **HTTP Client**: httpx
- **Валидация**: Pydantic v2
- **Контейнеризация**: Docker & Docker Compose
- **Хранилище**: In-memory (с предзагрузкой из CSV)
- **Аутентификация**: JWT (python-jose, PyJWT)
- **Хеширование паролей**: bcrypt (passlib)

## 📦 Структура проекта

```
titanic/
├── api_gateway/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py              # Маршрутизация + CORS + Auth proxy
│   ├── Dockerfile
│   └── requirements.txt
├── auth_service/                 # 🆕 Новый сервис!
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # Auth endpoints
│   │   ├── models.py            # User, Token модели
│   │   ├── storage.py           # In-memory хранилище пользователей
│   │   ├── security.py          # JWT + bcrypt
│   │   └── dependencies.py      # Auth middleware
│   ├── Dockerfile
│   └── requirements.txt
├── passenger_service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # API endpoints + Swagger
│   │   ├── models.py            # Pydantic модели (+ created_by)
│   │   ├── storage.py           # In-memory + валидация пасхалок
│   │   └── dependencies.py      # JWT verification
│   ├── data/
│   │   └── titanic.csv          # 102 пассажира (+ Jack & Rose!)
│   ├── Dockerfile
│   └── requirements.txt
├── statistics_service/
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py              # 5 статистических endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml           # Оркестрация 4 сервисов
├── .env.example                 # 🔐 Шаблон для production
├── .gitignore                   # Git ignore rules
├── SECURITY.md                  # 🛡️ Безопасность и best practices
├── README.md                    # Этот файл
└── REQUIREMENTS.md              # Подробная спецификация
```

## 🚀 Быстрый старт

### Требования

- Docker 20.10+
- Docker Compose 2.0+

### Запуск системы

Запустите все четыре микросервиса одной командой:

```bash
docker-compose up --build
```

Система будет готова через несколько секунд:

- **API Gateway**: http://localhost:8000
- **Swagger UI (главный)**: http://localhost:8000/docs 🌟
- **Auth Service**: http://localhost:8003/docs
- **Passenger Service**: http://localhost:8001/docs (внутренний)
- **Statistics Service**: http://localhost:8002/docs (внутренний)

### Остановка системы

```bash
docker-compose down
```

Для полного удаления контейнеров и сети:

```bash
docker-compose down -v
```

## 📚 API Документация

### 🏠 Главная страница

```bash
curl http://localhost:8000/
```

### 🏥 Health Check

```bash
curl http://localhost:8000/health
```

Возвращает статус всех сервисов (healthy/unhealthy/unavailable), включая Auth Service.

---

## 🔐 Аутентификация (JWT)

Система использует **JWT токены** для аутентификации. Операции изменения данных требуют валидный `Bearer` токен в заголовке `Authorization`.

### 📝 Регистрация нового пользователя

👑 **Важно:** Первый зарегистрированный пользователь автоматически становится **admin** (полный доступ)!  
Все последующие пользователи получают роль **user** (создание/редактирование, но не удаление).

```bash
# Первый пользователь - станет admin
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "boss",
    "password": "mypassword123",
    "email": "admin@example.com"
  }'

# Второй и последующие - будут user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "password123",
    "email": "john@example.com"
  }'
```

**Ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

### 🔑 Вход в систему

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "boss",
    "password": "mypassword123"
  }'
```

**Ответ:** То же, что и при регистрации - access и refresh токены.

### 🔄 Обновление токена

Access token действует 15 минут. Для получения нового используйте refresh token (действует 7 дней):

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

### 👤 Получить информацию о себе

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@titanic.local",
  "role": "admin",
  "is_active": true,
  "created_at": "2025-10-21T10:00:00"
}
```

### 📝 Обновить профиль

```bash
curl -X PUT http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com"
  }'
```

### 🚪 Выход из системы

```bash
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

## 👥 Работа с пассажирами

### 📋 Получить список пассажиров (без авторизации)

```http
GET /api/passengers
```

**Параметры фильтрации:**
- `pclass` (int): Класс билета (1, 2 или 3)
- `sex` (str): Пол (`male` или `female`)
- `embarked` (str): Порт посадки (`Southampton`, `Cherbourg`, `Queenstown`)
- `limit` (int, default=100): Количество записей (1-1000)
- `offset` (int, default=0): Смещение для пагинации

**Примеры:**

```bash
# Все пассажиры
curl http://localhost:8000/api/passengers

# Женщины из Cherbourg
curl "http://localhost:8000/api/passengers?sex=female&embarked=Cherbourg"

# Первые 10 пассажиров 1-го класса
curl "http://localhost:8000/api/passengers?pclass=1&limit=10"

# Пагинация: следующие 20 записей
curl "http://localhost:8000/api/passengers?offset=20&limit=20"
```

### 🔍 Поиск пассажиров по имени (без авторизации)

```http
GET /api/passengers/search?name={query}
```

**Пример:**

```bash
# Найти Джека
curl "http://localhost:8000/api/passengers/search?name=Jack"

# Найти Розу
curl "http://localhost:8000/api/passengers/search?name=Rose"
```

### ➕ Создать пассажира (требуется JWT токен)

```bash
# Сначала логин
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Создаем пассажира
curl -X POST http://localhost:8000/api/passengers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smith, Mr. John",
    "pclass": 2,
    "sex": "male",
    "age": 30,
    "fare": 25.50,
    "embarked": "Southampton",
    "destination": "New York",
    "cabin": "D45",
    "ticket": "PC 12345"
  }'
```

**Поле `created_by`** автоматически заполнится username текущего пользователя.

### 🔄 Обновить пассажира (требуется JWT токен)

```bash
curl -X PUT http://localhost:8000/api/passengers/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Smith, Mr. John Updated",
    "pclass": 1,
    "sex": "male",
    "age": 31,
    "fare": 50.00,
    "embarked": "Southampton",
    "destination": "New York",
    "cabin": "A12",
    "ticket": "PC 12345"
  }'
```

### ❌ Удалить пассажира (требуется роль admin!)

```bash
# Логин под admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# Удаление (только admin может!)
curl -X DELETE http://localhost:8000/api/passengers/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**⚠️ Важно:** Удаление может выполнить только пользователь с ролью `admin`. Пользователи с ролью `user` получат ошибку `403 Forbidden`.

---

## 📊 Статистика

Все статистические endpoints **не требуют авторизации**.

### 📈 Общая статистика

```bash
curl http://localhost:8000/api/stats
```

**Ответ:**
```json
{
  "total_passengers": 102,
  "average_age": 29.85,
  "average_fare": 32.45,
  "most_expensive_ticket": 512.33,
  "most_popular_destination": "New York"
}
```

### 🎟️ Статистика по классам

```bash
curl http://localhost:8000/api/stats/by-class
```

### 🚢 Статистика по портам посадки

```bash
curl http://localhost:8000/api/stats/by-port
```

### 🌍 Популярные направления

```bash
curl http://localhost:8000/api/stats/destinations
```

### 👶 Возрастное распределение

```bash
curl http://localhost:8000/api/stats/age-distribution
```

---

## 🎬 Пасхалки из фильма "Титаник"

### 1. Jack Dawson и Rose DeWitt Bukater

В датасете присутствуют персонажи из фильма:

```bash
curl "http://localhost:8000/api/passengers/search?name=Jack"
curl "http://localhost:8000/api/passengers/search?name=Rose"
```

### 2. Правило каюты (Jack & Rose Easter Egg)

**Джек (3-й класс) и Роза (1-й класс) не могут быть в одной каюте!** 🎭

Если попытаетесь поселить их вместе, получите специальное сообщение:

```bash
# Попробуйте создать или обновить Джека в каюту Розы
curl -X POST http://localhost:8000/api/passengers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dawson, Mr. Jack",
    "pclass": 3,
    "sex": "male",
    "age": 20,
    "fare": 0.0,
    "embarked": "Southampton",
    "destination": "Adventure and Freedom",
    "cabin": "B52",  # Каюта Розы!
    "ticket": "A/5 21171"
  }'
```

**Ответ:**
```json
{
  "detail": "Different social classes cannot share cabins on Titanic. Jack (3rd class) and Rose (1st class) must remain separate... for now. 🎭🚢"
}
```

Это отличный кейс для автотестов! 😄

---

## 🧪 Тестовые сценарии

### Сценарий 1: Полный цикл регистрации и создания пассажира

```bash
# 1. Регистрация (первый пользователь = admin!)
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"captain","password":"ship123","email":"captain@titanic.com"}')

TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "Access Token: $TOKEN"

# 2. Создание пассажира
curl -X POST http://localhost:8000/api/passengers \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dawson, Mr. Jack II",
    "pclass": 3,
    "sex": "male",
    "age": 20,
    "fare": 5.0,
    "embarked": "Southampton",
    "destination": "America",
    "ticket": "LINE"
  }'

# 3. Проверка профиля
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Сценарий 2: Попытка без токена (401)

```bash
curl -X POST http://localhost:8000/api/passengers \
  -H "Content-Type: application/json" \
  -d '{...}'
# Ответ: 401 Unauthorized
```

### Сценарий 3: User пытается удалить пассажира (403)

```bash
# Регистрируем второго пользователя (будет user, не admin)
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"sailor","password":"pass123"}'

# Логин как user
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"sailor","password":"pass123"}' | jq -r '.access_token')

# Попытка удаления
curl -X DELETE http://localhost:8000/api/passengers/1 \
  -H "Authorization: Bearer $USER_TOKEN"
# Ответ: 403 Forbidden - "Admin access required"
```

### Сценарий 4: Admin удаляет пассажира (успех)

```bash
# Логин как первый пользователь (admin)
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"captain","password":"ship123"}' | jq -r '.access_token')

# Удаление
curl -X DELETE http://localhost:8000/api/passengers/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN"
# Ответ: 204 No Content (успех)
```

### Сценарий 5: Обновление токена

```bash
# Логин
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"captain","password":"ship123"}')

ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
REFRESH_TOKEN=$(echo $RESPONSE | jq -r '.refresh_token')

# Подождать 15+ минут (или изменить время в коде для теста)

# Обновить токен
NEW_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/refresh \
  -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}")

NEW_ACCESS_TOKEN=$(echo $NEW_RESPONSE | jq -r '.access_token')

# Использовать новый токен
curl http://localhost:8000/api/passengers \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN"
```

---

## 🐛 Отладка

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f auth-service
docker-compose logs -f passenger-service
docker-compose logs -f stats-service
docker-compose logs -f gateway
```

### Проверка статуса контейнеров

```bash
docker-compose ps
```

### Перезапуск отдельного сервиса

```bash
docker-compose restart auth-service
```

---

## 🔐 Конфигурация

**Для разработки:** Все работает из коробки с демо-значениями в `docker-compose.yml`.

**Для production:**
1. Скопируйте `.env.example` → `.env`
2. Сгенерируйте безопасный ключ: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
3. Установите его в `JWT_SECRET_KEY` в `.env`
4. Прочитайте [SECURITY.md](SECURITY.md) для полного чеклиста безопасности

---

## 📝 Для QA и тестировщиков

### Что тестировать:

1. **Регистрация и логин**
   - Валидация username (3-50 символов)
   - Валидация пароля (минимум 6 символов)
   - Дубликаты username

2. **JWT токены**
   - Access token работает
   - Refresh token работает
   - Expired токены отклоняются
   - Logout инвалидирует refresh token

3. **Авторизация endpoints**
   - POST/PUT требуют токен (401 без него)
   - DELETE требует admin роль (403 для user)
   - GET работает без токена

4. **CRUD пассажиров**
   - Создание с валидными данными
   - Валидация полей (возраст 0-150, pclass 1-3, embarked и т.д.)
   - Обновление
   - Удаление (только admin)
   - Поле `created_by` заполняется

5. **Пасхалки**
   - Jack и Rose в разных каютах - OK
   - Jack и Rose в одной каюте - 400 с кастомным сообщением

6. **Фильтрация и поиск**
   - Фильтр по pclass, sex, embarked
   - Поиск по имени (case-insensitive)
   - Пагинация (limit, offset)

7. **Статистика**
   - Все endpoints возвращают корректные данные
   - Работает без авторизации

### Инструменты:

- **Swagger UI**: http://localhost:8000/docs (встроенная кнопка "Authorize")
- **Postman/Insomnia**: Импортируйте OpenAPI spec
- **curl**: Примеры выше
- **pytest + requests**: Для автотестов
- **Newman**: Для коллекций Postman

---

## 🤝 Вклад в проект

Этот проект создан для обучения. Не стесняйтесь форкать и экспериментировать!

### Идеи для улучшений:

- [ ] Добавить PostgreSQL для персистентности
- [ ] Реализовать email подтверждение
- [ ] Добавить метрики (Prometheus)
- [ ] Добавить tracing (Jaeger)
- [ ] Добавить rate limiting
- [ ] CI/CD pipeline
- [ ] Kubernetes deployment

---

## 📄 Лицензия

MIT License - используйте свободно для обучения и практики!

## 📞 Контакты

Проект создан для образовательных целей. Для вопросов и предложений создавайте issues.

---

**🚢 Счастливого плавания в мире микросервисов!**
