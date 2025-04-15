# 🎬 Система управления фильмами

Ссылка на репозиторий фронтенда: https://REDACTED/team-7/frontend

https://prod-team-7-s35as4hl.REDACTED/

OpenAPI: https://prod-team-7-s35as4hl.REDACTED/api/schema/openapi.json

Swagger UI: https://prod-team-7-s35as4hl.REDACTED/api/schema/swagger

Полнофункциональное решение для управления фильмами, списками просмотра, рекомендациями и подборками фильмов.

Список пользователей: `test_users.md`

## 📋 О проекте

Данная система предоставляет инфраструктуру для:
- Создания и редактирования фильмов
- Управления списками просмотра (watchlists)
- Получения персонализированных рекомендаций
- Создания подборок (миксов) фильмов

Система разработана для работы с несколькими клиентами:
- Веб-фронтенд (SPA или классический веб-клиент)
- Мобильное приложение
- Телеграм-бот

## 🏗️ Архитектура системы

### Детальное описание архитектуры

#### Основные компоненты системы

1. **Backend Service (Основной сервис)** - монолитное ядро системы, которое:
   - Экспонирует REST API для клиентов (веб и мобильных)
   - Взаимодействует с базой данных PostgreSQL
   - Интегрируется с внешними сервисами (TMDB/Kinopoisk, GPT)
   - Управляет хранением файлов в S3-совместимом хранилище
   - Обрабатывает бизнес-логику приложения

2. **Telegram Bot** - дополнительный компонент, реализующий аутентификацию через Telegram.

3. **Инфраструктурные компоненты**:
   - **PostgreSQL** - реляционная база данных для хранения структурированных данных
   - **S3-совместимое хранилище** (MinIO/AWS S3) - для хранения медиаконтента
   - **Внешние API** - TMDB/Kinopoisk для данных о фильмах, OpenAI-comp для рекомендаций
   - **Docker/Compose** - контейнеризация и оркестрация сервисов
   - **GitLab CI/CD** - автоматизация сборки и деплоя

#### Архитектурный стиль и принципы

Система построена на основе **Domain-Driven Design (DDD)**, что обеспечивает четкое разделение ответственности и улучшает поддержку и масштабирование кода. Архитектура включает следующие слои:

##### 1. Domain Layer (Слой предметной области)

Этот слой содержит чистые объекты предметной области, бизнес-правила и логику:
- **Сущности** (Film, User, Watchlist, Genre, Mood, Mix и др.)
- **Value Objects** (FilmId, UserId, WatchlistId, различные типы и перечисления)
- Не имеет зависимостей от инфраструктурных фреймворков или внешних сервисов
- Представляет собой ядро системы с бизнес-логикой

##### 2. Application Layer (Слой приложения)

Оркестрирует взаимодействие между различными компонентами:
- **Интерфейсы репозиториев** (FilmRepository, UserRepository, WatchlistRepository и др.)
- **Сервисы приложения** и сценарии использования
- **Committer** для управления транзакциями
- Определяет, что нужно сделать, но не как именно это сделать

##### 3. Infrastructure Layer (Слой инфраструктуры)

Содержит конкретные реализации и интеграции с внешними системами:
- **Реализации репозиториев** (SQLAlchemyFilmRepository, SQLAlchemyUserRepository и др.)
- **Модели ORM** и маппинги между доменными объектами и моделями БД
- **Миграции** базы данных (Alembic)
- **Сервисы для внешних API**:
  - TMDBService для работы с API фильмов
  - GPTService для рекомендаций
  - S3Service для работы с файловым хранилищем
- **IoC-контейнер** (dishka) для внедрения зависимостей

##### 4. Presentation Layer (Слой представления)

Отвечает за взаимодействие с клиентами:
- **REST-контроллеры** (Litestar Controllers)
- **Схемы валидации** для входящих и исходящих данных
- **JWT-авторизация** и безопасность
- **OpenAPI-спецификации** для документирования API

### Схема взаимодействия компонентов

```mermaid
graph TD
    subgraph "Система"
        A[Telegram Bot] -->|HTTP| B[Backend Service]
        B -->|SQL| C[(Database)]
        B -->|HTTP| D[TMDB API]
        B -->|S3 Protocol| E[S3 Storage]
        B -->|HTTP| F[GPT API]
    end

    subgraph "Telegram Bot"
        A1[Handlers] --> A2[Middlewares]
        A2 --> A3[Adapters]
        A3 -->|HTTP| B
    end

    subgraph "Backend Service"
        B1[Controllers] --> B2[Application Layer]
        B2 --> B3[Repositories]
        B2 --> B4[Services]
        B3 -->|SQL| C
        B4 -->|HTTP| D
        B4 -->|S3| E
        B4 -->|HTTP| F
    end

    U[Пользователь] -->|Telegram| A
    U -->|HTTP| B
```

### Высокоуровневая схема (C4-диаграмма: уровень Container)

```mermaid
flowchart LR
    A[Веб-клиент / Мобильное приложение] -- REST HTTP --> B(Backend Service)
    A_2[Telegram] -- Telegram API --> C[Telegram Bot]

    C -- HTTP --> B
    
    B -- SQL --> D[(PostgreSQL)]
    B -- "S3 protocol" --> E[S3-хранилище]
    B -- HTTP --> F[TMDB/Kinopoisk API]
    B -- HTTP --> G[GPT API]

    subgraph DevOps / CI-CD
        H[Docker / Compose / GitLab CI]
    end

    H --> B
    H --> C
    H --> D
    H --> E
```

## 💾 Архитектура базы данных

### Основные таблицы

- `users` - пользователи системы
- `films` - фильмы и их метаданные
- `genres` - жанры фильмов
- `moods` - настроения для рекомендаций
- `watchlists` - списки просмотра
- `watchlist_item` - элементы списков просмотра
- `recommended_film` - рекомендованные фильмы
- `auth_token` - токены авторизации
- `mixes` - подборки фильмов
- `mix_item` - элементы подборок

### ER-диаграмма

```mermaid
erDiagram
    users {
        uuid id PK
        string username
        string email
        string password
    }
    films {
        uuid id PK
        string title
        string description
        string country

        int release_year
        string poster_url
        int tmdb_id

        uuid owner_id
    }
    watchlists {
        uuid id PK
        uuid user_id FK
        string title
        string type
        string color1
        string color2
        string color3
    }

    watchlist_item {
        uuid watchlist_id FK
        uuid film_id FK

        datetime added_at
    }
    recommended_film {
        uuid id PK
        uuid film_id FK
        uuid user_id FK
        datetime recommended_at
    }
    auth_token {
        uuid id PK
        string token
        bool activated
        bool declined
        datetime created_at
    }
    genres {
        uuid id PK
        string name
    }

    moods {
        uuid id PK
        string name
    }
    film_genre {
        uuid film_id FK
        uuid genre_id FK
    }
    genre_mood {
        uuid genre_id FK
        uuid mood_id FK
    }
    mixes {
        uuid id PK
        string title
        string color1
        string color2
        string color3
    }
    mix_item {

        uuid mix_id FK
        uuid film_id FK
        datetime added_at
    }

    users ||--o{ watchlists : "owns"
    watchlists ||--o{ watchlist_item : "contains"
    films ||--o{ watchlist_item : "is_in"
    users ||--o{ recommended_film : "has"
    films ||--o{ recommended_film : "recommended"
    films ||--o{ film_genre : "has"
    genres ||--o{ film_genre : "associated"
    genres ||--o{ genre_mood : "has"
    moods ||--o{ genre_mood : "associated"

    mixes ||--o{ mix_item : "has"
    films ||--o{ mix_item : "is_in"
    users ||--o{ auth_token : "has"
```

## 📁 Структура проекта

Проект следует принципам Domain-Driven Design (DDD) и имеет четкую модульную структуру:

```
src/
  ├── backend/
  │   ├── main/                # Точка входа приложения
  │   │   └── app.py           # Инициализация Litestar приложения
  │   ├── domain/              # Бизнес-логика и сущности
  │   │   ├── film.py          # Сущность Film
  │   │   ├── user.py          # Сущность User
  │   │   ├── genre.py         # Сущность Genre
  │   │   └── ...              # Другие сущности (mood, watchlist и т.д.)
  │   ├── application/         # Прикладная логика
  │   │   ├── repositories/    # Интерфейсы репозиториев
  │   │   │   ├── film.py      # Интерфейс FilmRepository
  │   │   │   └── ...
  │   │   └── committer.py     # Логика фиксации транзакций
  │   ├── infrastructure/      # Реализация инфраструктуры
  │   │   ├── persistence/     # Работа с базой данных
  │   │   │   ├── models/      # Модели SQLAlchemy
  │   │   │   ├── mappers/     # Преобразование моделей в доменные сущности
  │   │   │   ├── repositories/ # Реализация репозиториев
  │   │   │   └── migrations/  # Миграции базы данных (Alembic)
  │   │   ├── services/        # Интеграция с внешними сервисами
  │   │   │   ├── tmdb.py      # Интеграция с TMDB
  │   │   │   ├── s3.py        # Интеграция с S3
  │   │   │   └── gpt.py       # Интеграция с GPT
  │   │   └── ioc.py           # IoC-контейнер для зависимостей
  │   ├── presentation/        # Слой представления (API)
  │   │   ├── controllers/     # Контроллеры REST API
  │   │   │   ├── film.py      # Эндпоинты для фильмов
  │   │   │   ├── auth.py      # Эндпоинты для авторизации
  │   │   │   └── ...
  │   │   ├── schemas.py       # Схемы данных (валидация)
  │   │   └── jwt.py           # Логика JWT
  │   └── config/              # Конфигурация
  │       └── settings.py      # Настройки приложения
  ├── bot/                     # Telegram-бот (опционально)
  │   ├── handlers/            # Обработчики команд
  │   ├── middlewares/         # Промежуточные слои
  │   ├── database/            # Логика работы с базой для бота
  │   └── ...
  └── tests/                   # Тесты
      └── e2e/                 # End-to-End тесты
```

### Ключевые файлы

- `alembic.ini` и каталог `migrations/` — для управления схемой БД
- `Dockerfile` — сборка Docker-образа
- `compose.yaml` — Docker Compose конфигурация
- `.gitlab-ci.yml` — скрипты CI/CD
- `uv.lock`, `pyproject.toml` — управление зависимостями

## 🔍 Подробное описание компонентов

### Backend Service

Бэкенд реализован на Python 3.13 с использованием асинхронного фреймворка Litestar, что обеспечивает высокую производительность и масштабируемость. Ключевые аспекты:

- **Асинхронная обработка** - использование async/await для всех операций ввода-вывода
- **ORM SQLAlchemy** - для типобезопасной работы с базой данных
- **Миграции Alembic** - для управления схемой базы данных
- **Dependency Injection** - использование Dishka для внедрения зависимостей
- **JWT-аутентификация** - безопасная авторизация пользователей
- **OpenAPI** - автоматическая генерация документации API

Структура эндпоинтов организована логически по ресурсам:
- `/films` - управление фильмами (создание, поиск, обновление)
- `/me` - пользовательская информация и управление списками просмотра
- `/recommend` - получение персонализированных рекомендаций
- `/auth` - регистрация и аутентификация
- `/mix` - работа с готовыми подборками фильмов
- `/genres` и `/moods` - работа с жанрами и настроениями для рекомендаций

### Интеграция с внешними сервисами

#### TMDB/Kinopoisk API

Система использует API TMDB и Kinopoisk для:
- Поиска фильмов по названию и описанию
- Получения детальной информации о фильмах (описание, постеры, жанры)
- Формирования рекомендаций на основе жанров
- Реализована отказоустойчивость с переключением между API при сбоях

#### GPT API

Интеграция с GPT используется для:
- Генерации персонализированных рекомендаций на основе текстовых описаний
- Распознавания фильмов по описаниям пользователей
- Создания градиентных цветов для визуального оформления списков и миксов

#### S3 Storage

Система использует S3-совместимое хранилище для:
- Загрузки и хранения постеров фильмов
- Обеспечения масштабирования и высокой доступности медиаконтента

### Telegram Bot

Telegram-бот представляет собой дополнительный интерфейс взаимодействия с системой:
- Реализован с использованием библиотеки aiogram
- Поддерживает аутентификацию через специальный механизм auth_key

## 🚀 Запуск проекта

### Локальный запуск с Docker Compose

```bash
docker compose up -d
```

После запуска доступны:
- Бэкенд: http://localhost:8080/api/v1/...
- PostgreSQL: порт 5432
- MinIO: порт 9000

### Переменные окружения

Проект использует следующие переменные окружения (в файле `.env`):

```env
POSTGRES_DSN="postgresql+asyncpg://postgres:password@localhost:5432/postgres"
JWT_SECRET="supersecret"
TMDB_API_KEY="..."
TMDB_BASE_URL="..."
BOT_TOKEN="..."
GPT_BASE="..."
GPT_API_KEY="..."
AWS_ENDPOINT_URL="..."
AWS_KEY_ID="..."
AWS_ACCESS_KEY="..."
AWS_BUCKET_NAME="files"
FILES_BASE_URL="..."
```

## 🔐 Авторизация и безопасность

- JWT авторизация через заголовок `Authorization: Bearer <token>`
- Хэширование паролей пользователей с использованием Argon2
- Авторизация в Telegram-боте через специальный ключ
- Role-based access control для управления доступом

## 🔄 CI/CD

Проект использует GitLab CI/CD с двумя основными стадиями:
- `build` - сборка Docker-образа с использованием Kaniko
- `deploy` - автоматический деплой на сервер через SSH

## 📊 Масштабируемость и отказоустойчивость

Архитектура спроектирована с учетом требований масштабируемости:
- **Асинхронная обработка** - эффективное использование ресурсов сервера
- **Модульность** - возможность выделения компонентов в отдельные сервисы
- **Контейнеризация** - простое горизонтальное масштабирование
- **Separated concerns** - четкое разделение ответственности между компонентами

Отказоустойчивость обеспечивается:
- **Redundancy** - возможность запуска нескольких инстансов сервисов
- **Fallback mechanisms** - переключение между внешними API при сбоях
- **Transaction management** - атомарные операции с базой данных
- **Health checks** - проверка доступности сервисов

## 🛠️ Технологии

- **Backend**: Python 3.13, Litestar, SQLAlchemy, Alembic
- **База данных**: PostgreSQL
- **Хранилище**: S3-совместимое (MinIO/AWS)
- **Контейнеризация**: Docker, Docker Compose
- **CI/CD**: GitLab CI
- **Архитектура**: Domain-Driven Design
- **Внешние API**: TMDB/Kinopoisk, GPT
- **Telegram Bot**: aiogram


## Тесты

Юнит, интеграционные и e2e тесты находятся в директории `tests/`.

Описание сценариев end-to-end тестов в `e2e.md`.

Отчёт о покрытии тестами кода:

```
Name                                                                      Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------------------------
src/backend/__init__.py                                                       0      0   100%
src/backend/application/__init__.py                                           0      0   100%
src/backend/application/committer.py                                          4      1    75%   6
src/backend/application/errors.py                                            18      0   100%
src/backend/application/password_hasher.py                                    6      2    67%   6, 9
src/backend/application/repositories/__init__.py                              0      0   100%
src/backend/application/repositories/auth_token.py                           17      6    65%   10, 13, 16, 19, 22, 25
src/backend/application/repositories/film.py                                 13      4    69%   10, 13, 16, 19
src/backend/application/repositories/genre.py                                10      2    80%   11, 14
src/backend/application/repositories/mix.py                                  17      5    71%   12, 15, 18, 21, 24
src/backend/application/repositories/mood.py                                  9      2    78%   10, 13
src/backend/application/repositories/recommended_film.py                     10      2    80%   11, 14
src/backend/application/repositories/user.py                                 12      4    67%   9, 12, 15, 18
src/backend/application/repositories/watchlist.py                            27      9    67%   14, 17, 20, 23, 26, 29, 32, 35, 38
src/backend/config/__init__.py                                                0      0   100%
src/backend/config/settings.py                                               13      0   100%
src/backend/constant.py                                                       1      0   100%
src/backend/domain/__init__.py                                                0      0   100%
src/backend/domain/auth_token.py                                             12      0   100%
src/backend/domain/auth_token_id.py                                           3      0   100%
src/backend/domain/film.py                                                   13      0   100%
src/backend/domain/film_id.py                                                 3      0   100%
src/backend/domain/genre.py                                                   6      0   100%
src/backend/domain/genre_id.py                                                3      0   100%
src/backend/domain/mix.py                                                    10      0   100%
src/backend/domain/mix_id.py                                                  3      0   100%
src/backend/domain/mix_item.py                                                9      0   100%
src/backend/domain/mood.py                                                    6      0   100%
src/backend/domain/mood_id.py                                                 3      0   100%
src/backend/domain/recommended_film.py                                       11      0   100%
src/backend/domain/user.py                                                    9      0   100%
src/backend/domain/user_id.py                                                 3      0   100%
src/backend/domain/watchlist.py                                              14      0   100%
src/backend/domain/watchlist_id.py                                            3      0   100%
src/backend/domain/watchlist_item.py                                          9      0   100%
src/backend/domain/watchlist_type.py                                          7      0   100%
src/backend/infrastructure/__init__.py                                        0      0   100%
src/backend/infrastructure/argon2_password_hasher.py                         12      2    83%   18-19
src/backend/infrastructure/ioc.py                                            62      2    97%   38, 61
src/backend/infrastructure/persistence/__init__.py                            0      0   100%
src/backend/infrastructure/persistence/committer.py                           7      0   100%
src/backend/infrastructure/persistence/mappers/__init__.py                    0      0   100%
src/backend/infrastructure/persistence/mappers/auth_token.py                  8      0   100%
src/backend/infrastructure/persistence/mappers/film.py                        8      0   100%
src/backend/infrastructure/persistence/mappers/genre.py                       7      1    86%   11
src/backend/infrastructure/persistence/mappers/mix.py                         7      2    71%   7, 17
src/backend/infrastructure/persistence/mappers/mix_item.py                    8      2    75%   8, 16
src/backend/infrastructure/persistence/mappers/mood.py                        7      1    86%   11
src/backend/infrastructure/persistence/mappers/recommended_film.py            8      0   100%
src/backend/infrastructure/persistence/mappers/user.py                        7      0   100%
src/backend/infrastructure/persistence/mappers/watchlist.py                   8      0   100%
src/backend/infrastructure/persistence/mappers/watchlist_item.py              8      0   100%
src/backend/infrastructure/persistence/models/__init__.py                     0      0   100%
src/backend/infrastructure/persistence/models/auth_token.py                  15      0   100%
src/backend/infrastructure/persistence/models/base.py                        17     12    29%   10-21
src/backend/infrastructure/persistence/models/film.py                        15      0   100%
src/backend/infrastructure/persistence/models/film_genre.py                   7      0   100%
src/backend/infrastructure/persistence/models/genre.py                        7      0   100%
src/backend/infrastructure/persistence/models/genre_mood.py                   7      0   100%
src/backend/infrastructure/persistence/models/mix.py                         10      0   100%
src/backend/infrastructure/persistence/models/mix_item.py                    13      0   100%
src/backend/infrastructure/persistence/models/mood.py                         7      0   100%
src/backend/infrastructure/persistence/models/recommended_film.py            14      0   100%
src/backend/infrastructure/persistence/models/user.py                        11      0   100%
src/backend/infrastructure/persistence/models/watchlist.py                   15      0   100%
src/backend/infrastructure/persistence/models/watchlist_item.py              13      0   100%
src/backend/infrastructure/persistence/repositories/__init__.py               0      0   100%
src/backend/infrastructure/persistence/repositories/auth_token.py            58     32    45%   26, 29-33, 38-40, 43-48, 51-59, 62-69
src/backend/infrastructure/persistence/repositories/film.py                  45     13    71%   28, 33-35, 41-43, 49-54
src/backend/infrastructure/persistence/repositories/genre.py                 31      5    84%   34, 38, 43-45
src/backend/infrastructure/persistence/repositories/mix.py                   48     16    67%   36, 41-43, 46-51, 54-55, 58-61
src/backend/infrastructure/persistence/repositories/mood.py                  25      4    84%   26, 31-33
src/backend/infrastructure/persistence/repositories/recommended_film.py      25      3    88%   31, 40-41
src/backend/infrastructure/persistence/repositories/user.py                  38     13    66%   25, 30-32, 37-39, 42-47
src/backend/infrastructure/persistence/repositories/watchlist.py             69     19    72%   42, 47-49, 54-60, 64-66, 71-72, 108, 115-117, 121-122
src/backend/infrastructure/services/__init__.py                               0      0   100%
src/backend/infrastructure/services/gpt.py                                  115     66    43%   17-18, 42-44, 46-51, 65-79, 83-89, 96-102, 109-142, 182-195
src/backend/infrastructure/services/s3.py                                    28     13    54%   20-29, 32-45
src/backend/infrastructure/services/tmdb.py                                 319    189    41%   169-171, 184-190, 202-208, 211-236, 239-244, 247-252, 256, 260-261, 274, 276, 284-286, 289, 303, 324-326, 334, 348-404, 407-431, 434-458, 462-486, 489-519, 528, 545-548, 561, 575, 582-584, 587-623, 648-650
src/backend/main/__init__.py                                                  0      0   100%
src/backend/main/app.py                                                      23      0   100%
src/backend/presentation/__init__.py                                          0      0   100%
src/backend/presentation/controllers/__init__.py                              0      0   100%
src/backend/presentation/controllers/auth.py                                 48     16    67%   51-64, 78-92
src/backend/presentation/controllers/film.py                                245    144    41%   39, 42, 57-58, 71, 74, 81-86, 104-105, 111-114, 117-152, 155-176, 199-226, 230-233, 239, 255-262, 299-304, 317-343, 357-368, 381-383, 398-412
src/backend/presentation/controllers/genre.py                                22      2    91%   30-31
src/backend/presentation/controllers/me.py                                  204     98    52%   35-40, 65-66, 88-89, 101-105, 118-132, 150-162, 180-193, 212-219, 232-238, 252-263, 281-287, 299-305, 317-330, 348-355, 367-373, 384-389
src/backend/presentation/controllers/mix.py                                  55     24    56%   30-56, 84-85, 97-108
src/backend/presentation/controllers/mood.py                                 23      2    91%   35-36
src/backend/presentation/controllers/recommend.py                            96     47    51%   40-47, 80-88, 91-92, 97-109, 116, 123, 126, 149-174
src/backend/presentation/controllers/telegram_auth.py                        46     16    65%   38-40, 50-64, 79-97
src/backend/presentation/jwt.py                                              22      3    86%   16, 27-28
src/backend/presentation/schemas.py                                          78      0   100%
-------------------------------------------------------------------------------------------------------
TOTAL                                                                      2255    784    65%
```

# CI/CD Pipeline

В проекте используется двухэтапный GitLab-пайплайн с этапами `build` и `deploy`. Ниже описано, как он устроен и что делает.

## 1. Этап `build`
1. **Исполняющая среда**  
   - Для сборки образа в GitLab используется контейнер [gcr.io/kaniko-project/executor:debug](https://github.com/GoogleContainerTools/kaniko).  
   - Kaniko позволяет собирать Docker-образы внутри контейнера без доступа к демону Docker на хосте.

2. **Авторизация в реестре**  
   - В пайплайне создаётся файл `config.json` с данными аутентификации: логином и паролем к GitLab Registry, чтобы Kaniko смог пушить собранный образ обратно в реестр.
   - Переменные `CI_REGISTRY_USER` и `CI_REGISTRY_PASSWORD` предоставляет GitLab Runner.

3. **Сборка Docker-образа**  
   - Командой:
     ```bash
     /kaniko/executor \
       --context "${CI_PROJECT_DIR}" \
       --dockerfile "${CI_PROJECT_DIR}/Dockerfile" \
       --destination "${CI_REGISTRY_IMAGE}:latest" \
       --cache=True
     ```
     Kaniko:
     - Получает исходный код из `$CI_PROJECT_DIR`.
     - Использует ваш `Dockerfile` для сборки образа.
     - Пушит собранный образ в реестр GitLab по адресу, например `REDACTED:5050/team-7/backend:latest`.
     - `--cache=True` включает кэширование слоёв для ускорения повторных сборок.

4. **Результат**  
   - Успешно собранный образ доступен во вкладке «Packages & Registries → Container Registry» в нашем проекте GitLab под нужным тегом (здесь `:latest`).

## 2. Этап `deploy`
1. **Подготовка к деплою**  
   - Запускается только после успешного `build`.
   - Переменные окружения (`ENV_SSH_USER`, `ENV_SSH_HOST`, `ENV_PRIVATE_KEY_BASE64`) содержат данные для SSH-доступа к удалённому серверу, где разворачивается приложение.

2. **SSH и Docker Compose**  
   - В `before_script` пайплайн добавляет приватный ключ для SSH, отключает `StrictHostKeyChecking`.  
   - Выполняет `docker login`, используя переменную `CI_REGISTRY_PASSWORD`, чтобы тянуть образы из реестра GitLab.

3. **Обновление и запуск**  
   - `docker compose pull` стягивает свежесобранный образ `:latest` на удалённый сервер.
   - `docker compose up -d` перезапускает сервисы в фоновом режиме, используя новый образ.
   - Приложение обновляется автоматически без ручных действий.

4. **Очистка**  
   - Выполняется `docker image prune -f`, чтобы удалить неиспользуемые образы и освободить место.

## Дополнительные детали
- **Переменные окружения**  
  - В файле `.env` и (или) в настройках GitLab (CI/CD Variables) хранятся чувствительные данные: пароли к БД, ключи TMDB/GPT и т. д.
  - Docker Compose подтягивает их в контейнер при старте.

- **Alembic**  
  - Перед запуском основного контейнера сервис `migrations` из `compose.yaml` выполняет:
    ```bash
    alembic upgrade head
    ```
    накатывая миграции в PostgreSQL, чтобы база всегда была в актуальном состоянии.

- **Проверка здоровья**  
  - Сервисы `postgres` и `minio` в `compose.yaml` имеют `healthcheck`, чтобы остальные сервисы запускались только после того, как БД и MinIO будут готовы.

Таким образом, пайплайн выглядит так:
1. **Build**: собирает и публикует образ в реестр.
2. **Deploy**: скачивает новый образ и разворачивает его на сервере при помощи Docker Compose.

В итоге процесс сборки и деплоя полностью автоматизирован.
