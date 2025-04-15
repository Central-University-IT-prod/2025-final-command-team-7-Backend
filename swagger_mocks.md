# API для сервиса фильмов

## Содержание

- [Общее описание и запуск Swagger UI](#общее-описание-и-запуск-swagger-ui)
- [Аутентификация](#аутентификация)
- [Основные эндпоинты](#эндпоинты)
  - [Фильмы (films)](#фильмы-films)
  - [Постер к фильму (poster)](#постер-к-фильму-poster)
  - [Поиск фильмов (search)](#поиск-фильмов-search)
  - [Подборки (mix)](#подборки-mix)
  - [Профиль пользователя (me)](#профиль-пользователя-me)
  - [Избранное/Просмотрено/Список желаний (watchlists)](#watchlists-избранноепросмотреножелания)
  - [Жанры (genres)](#жанры-genres)
  - [Настроения (moods)](#настроения-moods)
  - [Аутентификация (auth)](#аутентификация-auth)
  - [Рекомендации (recommend)](#рекомендации-recommend)
- [Модели (Schemas)](#модели-schemas)
- [Примеры запросов и ответов (mock data)](#примеры-запросов-и-ответов-mock-data)

## Общее описание и запуск Swagger UI

Swagger UI — это визуальный интерфейс, в котором автоматически отображается спецификация OpenAPI.

- Как правило, Swagger UI доступен по пути, например, `/docs` или `/swagger` (зависит от настроек вашего проекта).
- Открыв Swagger UI в браузере, вы увидите разделы (tags) и список эндпоинтов. При нажатии на любой эндпоинт появится форма для ввода параметров и отправки тестового запроса.

> **Совет:** Перед тем как обращаться к закрытым эндпоинтам, убедитесь, что вы внесли Bearer-токен (JWT) в поле Authorize справа в Swagger UI.

## Аутентификация

Используется схема аутентификации Bearer token.

Чтобы воспользоваться авторизованными эндпоинтами (где это требуется), необходимо:

1. Получить токен (JWT) с помощью эндпоинта Login или LoginWithTelegram.
2. Нажать кнопку Authorize в правом верхнем углу Swagger UI.
3. Ввести в поле Authorization значение:
   ```
   Bearer <ВАШ_ТОКЕН>
   ```
4. Подтвердить.

После этого все эндпоинты, где прописана защита BearerToken, будут доступными для отправки запросов.

## Эндпоинты

Ниже перечислены все эндпоинты, каждый пункт из спецификации Swagger (OpenAPI). Для удобства сгруппируем по тегам.

### Фильмы (films)

#### `POST /api/v1/films`

Создание нового фильма.

Tags: films

Тело запроса:
```json
{
  "title": "string",
  "description": "string",
  "genres_ids": ["uuid1", "uuid2"],
  "country": "string",
  "release_year": 2020
}
```

Пример успешного ответа (201):
```json
{
  "id": "some-uuid",
  "title": "string",
  "description": "string",
  "country": "string",
  "release_year": 2020,
  "poster_url": null,
  "tmdb_id": null,
  "owner_id": "user-uuid",
  "is_liked": false,
  "is_wish": false,
  "is_watched": false
}
```

Ошибки:
- 400 — Validation Exception (например, не указано обязательное поле).

#### `GET /api/v1/films/{film_id}`

Получение фильма по ID.

Tags: films

Параметры пути: film_id (UUID фильма)

Пример успешного ответа (200):
```json
{
  "id": "some-uuid",
  "title": "string",
  "description": "string",
  "country": "string",
  "release_year": 2020,
  "poster_url": null,
  "tmdb_id": null,
  "owner_id": "user-uuid",
  "is_liked": false,
  "is_wish": false,
  "is_watched": false
}
```

Ошибки:
- 404 — фильм не найден
- 400 — неверный формат запроса

#### `PUT /api/v1/films/{film_id}`

Обновление (редактирование) фильма.

Tags: films

Параметры пути: film_id

Тело запроса (такое же, как при создании фильма):
```json
{
  "title": "string",
  "description": "string",
  "genres_ids": ["uuid1","uuid2"],
  "country": "string",
  "release_year": 2020
}
```

Пример успешного ответа (200):
```json
{
  "id": "some-uuid",
  "title": "Обновлённый заголовок",
  "description": "Обновлённое описание",
  "country": "string",
  "release_year": 2021,
  "poster_url": "string",
  "tmdb_id": null,
  "owner_id": "user-uuid",
  "is_liked": false,
  "is_wish": false,
  "is_watched": false
}
```

Ошибки:
- 403 — запрещено (например, не хватает прав)
- 400 — неверный формат запроса

### Постер к фильму (poster)

#### `PUT /api/v1/films/{film_id}/poster`

Загрузка постера к фильму.

Tags: films

Параметры пути: film_id

Тип Content-Type: multipart/form-data
- file: binary

Пример успешного ответа (204): пустое тело, статус No Content.

#### `DELETE /api/v1/films/{film_id}/poster`

Удаление постера у фильма.

Tags: films

Параметры пути: film_id

Пример успешного ответа (204): пустое тело.

### Поиск фильмов (search)

#### `GET /api/v1/films/search`

Поиск фильмов с возможностью фильтрации.

Tags: films

Query-параметры:
- title (string | null) — поиск по названию
- description (string | null) — поиск по описанию
- limit (integer, default=10) — ограничение числа результатов

Пример успешного ответа (200):
```json
[
  {
    "id": "film-uuid",
    "title": "string",
    "description": "string",
    "country": "string",
    "release_year": 2020,
    "poster_url": "string",
    "tmdb_id": null,
    "owner_id": "user-uuid",
    "is_liked": false,
    "is_wish": false,
    "is_watched": false
  }
]
```

### Подборки (mix)

#### `GET /api/v1/mix`

Получение списка всех подборок.

Tags: mix

Пример успешного ответа (200):
```json
[
  {
    "id": "mix-uuid",
    "title": "Подборка 1",
    "color1": "#FFFFFF",
    "color2": "#000000",
    "color3": "#FF0000"
  },
  {
    "id": "mix-uuid2",
    "title": "Подборка 2",
    "color1": "#AAAAAA",
    "color2": "#BBBBBB",
    "color3": "#CCCCCC"
  }
]
```

#### `GET /api/v1/mix/{mix_id}`

Получение подборки по ID.

Tags: mix

Параметры пути: mix_id

Пример успешного ответа (200):
```json
{
  "id": "mix-uuid",
  "title": "Подборка 1",
  "color1": "#FFFFFF",
  "color2": "#000000",
  "color3": "#FF0000"
}
```

Ошибки:
- 404 — не найдено

#### `GET /api/v1/mix/{mix_id}/items`

Получение фильмов, входящих в подборку.

Tags: mix

Параметры пути: mix_id

Пример успешного ответа (200):
```json
[
  {
    "id": "film-uuid",
    "title": "string",
    "description": "string",
    "country": "string",
    "release_year": 2020,
    "poster_url": "string",
    "tmdb_id": null,
    "owner_id": "user-uuid",
    "is_liked": false,
    "is_wish": false,
    "is_watched": false
  }
]
```

Ошибки:
- 404 — подборка не найдена

### Профиль пользователя (me)

#### `GET /api/v1/me`

Получение текущего пользователя (если пользователь авторизован).

Tags: me

Пример успешного ответа (200):
```json
{
  "id": "user-uuid",
  "email": "test@example.com",
  "hashed_password": null,
  "telegram_id": 123456789,
  "username": "UserName"
}
```

### Watchlists (Избранное/Просмотрено/Желания)

#### `GET /api/v1/me/watchlists`

Список всех вочлистов (пользовательских списков).

Tags: me

Пример успешного ответа (200):
```json
[
  {
    "id": "watchlist-uuid",
    "user_id": "user-uuid",
    "title": "Мой кастомный список",
    "type": "custom",
    "color1": "#FFFFFF",
    "color2": "#000000",
    "color3": "#FF0000"
  }
]
```

#### `POST /api/v1/me/watchlists`

Создание кастомного вочлиста.

Tags: me

Тело запроса:
```json
{
  "title": "Новый список"
}
```

Пример успешного ответа (201):
```json
{
  "id": "watchlist-uuid",
  "user_id": "user-uuid",
  "title": "Новый список",
  "type": "custom",
  "color1": "#FFFFFF",
  "color2": "#000000",
  "color3": "#FF0000"
}
```

#### `GET /api/v1/me/watchlists/{watchlist_id}`

Получение конкретного вочлиста по его UUID.

Tags: me

Параметры пути: watchlist_id

Пример успешного ответа (200):
```json
{
  "id": "watchlist-uuid",
  "user_id": "user-uuid",
  "title": "Название листа",
  "type": "custom",
  "color1": "#FFFFFF",
  "color2": "#000000",
  "color3": "#FF0000"
}
```

Ошибки:
- 403 — нет прав на получение (чужой список)
- 404 — не найден

#### `DELETE /api/v1/me/watchlists/{watchlist_id}`

Удаление вочлиста.

Tags: me

Параметры пути: watchlist_id

Пример успешного ответа (204): пустое тело

#### `GET /api/v1/me/watchlists/{watchlist_id}/items`

Получение списка фильмов внутри вочлиста.

Tags: me

Параметры пути: watchlist_id

Пример успешного ответа (200):
```json
[
  {
    "id": "film-uuid",
    "title": "string",
    "description": "string",
    "country": "string",
    "release_year": 2020,
    "poster_url": null,
    "tmdb_id": null,
    "owner_id": "user-uuid",
    "is_liked": false,
    "is_wish": false,
    "is_watched": false
  }
]
```

Ошибки:
- 403 — нет прав на получение
- 404 — не найдено

##### Добавление фильма в разные списки:

Все операции выполняются PUT запросом на эндпоинты:
- Liked `/api/v1/me/watchlists/liked/items/add`
- Watched `/api/v1/me/watchlists/watched/items/add`
- Wish `/api/v1/me/watchlists/wish/items/add`
- Custom `/api/v1/me/watchlists/{watchlist_id}/items/add`

Тело запроса:
```json
{
  "film_id": "film-uuid"
}
```

Пример успешного ответа (204): пустое тело

##### Удаление фильма из разных списков:

Все операции выполняются DELETE запросом на эндпоинты:
- Liked: `/api/v1/me/watchlists/liked/items/{film_id}`
- Watched: `/api/v1/me/watchlists/watched/items/{film_id}`
- Wish: `/api/v1/me/watchlists/wish/items/{film_id}`
- Custom: `/api/v1/me/watchlists/{watchlist_id}/items/{film_id}`

Пример успешного ответа (204): пустое тело

##### Специальные эндпоинты для получения системных (не кастомных) списков и их фильмов:

- `GET /api/v1/me/watchlists/liked` — получение самого списка "Liked"
- `GET /api/v1/me/watchlists/liked/items` — получение фильмов из "Liked"
- `GET /api/v1/me/watchlists/watched` — получение самого списка "Watched"
- `GET /api/v1/me/watchlists/watched/items` — получение фильмов из "Watched"
- `GET /api/v1/me/watchlists/wish` — получение самого списка "Wish"
- `GET /api/v1/me/watchlists/wish/items` — получение фильмов из "Wish"

### Жанры (genres)

#### `GET /api/v1/genres`

Получение всех жанров.

Tags: genre

Query-параметры:
- moods_ids (array of UUIDs | null) — фильтрация по настроениям

Пример успешного ответа (200):
```json
[
  {
    "id": "genre-uuid",
    "name": "Комедия"
  },
  {
    "id": "genre-uuid2",
    "name": "Боевик"
  }
]
```

#### `GET /api/v1/genres/{genre_id}`

Получение жанра по ID.

Tags: genre

Параметры пути: genre_id

Пример успешного ответа (200):
```json
{
  "id": "genre-uuid",
  "name": "Комедия"
}
```

Ошибки:
- 400 — неверный ID формата

### Настроения (moods)

#### `GET /api/v1/moods`

Список всех "настроений" (moods).

Tags: mood

Пример успешного ответа (200):
```json
[
  {
    "id": "mood-uuid",
    "name": "Радость"
  },
  {
    "id": "mood-uuid2",
    "name": "Грусть"
  }
]
```

#### `GET /api/v1/moods/{mood_id}`

Получение настроения по ID.

Tags: mood

Параметры пути: mood_id

Пример успешного ответа (200):
```json
{
  "id": "mood-uuid",
  "name": "Радость"
}
```

### Аутентификация (auth)

#### `POST /api/v1/auth/register`

Регистрация пользователя.

Tags: auth

Тело запроса:
```json
{
  "email": "test@example.com",
  "password": "string",
  "username": "string"
}
```

Пример успешного ответа (201):
```json
{
  "id": "user-uuid",
  "email": "test@example.com",
  "telegram_id": null,
  "username": "string"
}
```

Ошибки:
- 400 — Validation Exception
- 409 — Пользователь уже существует

#### `POST /api/v1/auth/login`

Авторизация пользователя по email и паролю.

Tags: auth

Тело запроса:
```json
{
  "email": "test@example.com",
  "password": "string"
}
```

Пример успешного ответа (201):
```json
{
  "id": "user-uuid",
  "username": "string",
  "email": "test@example.com",
  "telegram_id": null,
  "token": "<jwt-token>"
}
```

Ошибки:
- 401 — неправильный логин или пароль
- 400 — Validation Exception

#### `POST /api/v1/auth/telegram/get_auth_key`

Получение auth_key для дальнейшей Telegram-аутентификации.

Tags: auth

Пример успешного ответа (201):
```json
{
  "auth_key": "string"
}
```

#### `POST /api/v1/auth/telegram/check_auth_key`

Проверка, действительно ли tg_code соответствует валидному auth_key.

Tags: auth

Тело запроса:
```json
{
  "tg_code": "some-code"
}
```

Пример успешного ответа (201):
```json
{
  "result": "some check result (может быть просто пустой json)"
}
```

#### `POST /api/v1/auth/telegram/login`

Авторизация через Telegram (получение JWT).

Tags: auth

Тело запроса:
```json
{
  "tg_code": "some-code"
}
```

Пример успешного ответа (201):
```json
{
  "id": "user-uuid",
  "username": null,
  "email": null,
  "telegram_id": 123456,
  "token": "<jwt-token>"
}
```

### Рекомендации (recommend)

#### `POST /api/v1/recommend`

Рекомендовать фильм, учитывая жанры, настроения, тип.

Tags: recommend

Query-параметры:
- moods_ids: массив UUID или null
- genres_ids: массив UUID или null
- movie_type: string или null

Пример успешного ответа (201):
```json
{
  "id": "film-uuid",
  "title": "Рекомендованный фильм",
  "description": "Описание...",
  "country": "string",
  "release_year": 2021,
  "poster_url": null,
  "tmdb_id": null,
  "owner_id": "user-uuid",
  "is_liked": false,
  "is_wish": false,
  "is_watched": false
}
```

Ошибки:
- 400 — Validation Exception

## Модели (Schemas)

В спецификации описано несколько основных сущностей (Models). Ниже — краткое описание ключевых:

### FilmCreate
Параметры для создания (или обновления) фильма:
```json
{
  "title": "string",
  "description": "string",
  "genres_ids": ["uuid1","uuid2"],
  "country": "string or null",
  "release_year": 2020 or null
}
```

### FilmResponse
Структура ответа о фильме:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "country": "string or null",
  "release_year": 2020 or null,
  "poster_url": "string or null",
  "tmdb_id": "integer or null",
  "owner_id": "uuid or null",
  "is_liked": false,
  "is_wish": false,
  "is_watched": false
}
```

### UserRegister, UserLogin, UserLoginResponse, RegisterUserResponseBody
Отвечают за логику регистрации и логина (JWT, email, пароль).

### Watchlist, WatchlistType (liked, wish, watched, custom)
Сущность списка (watchlist).

### Genre, Mood
Описывают жанры и настроения.

## Примеры запросов и ответов (mock data)

Ниже приведены некоторые примерные данные для быстрой проверки (mock):

### 1. Создание фильма
Запрос:
```json
{
  "title": "Мой новый фильм",
  "description": "Очень интересный фильм",
  "genres_ids": ["123e4567-e89b-12d3-a456-426614174000"],
  "country": "USA",
  "release_year": 2022
}
```

Примерный ответ:
```json
{
  "id": "333e4567-e89b-12d3-a456-426614174111",
  "title": "Мой новый фильм",
  "description": "Очень интересный фильм",
  "country": "USA",
  "release_year": 2022,
  "poster_url": null,
  "tmdb_id": null,
  "owner_id": "111e4567-e89b-12d3-a456-426614174000",
  "is_liked": false,
  "is_wish": false,
  "is_watched": false
}
```

### 2. Регистрация пользователя
Запрос:
```json
{
  "email": "test@example.com",
  "password": "123456",
  "username": "TestUser"
}
```

Ответ:
```json
{
  "id": "222e4567-e89b-12d3-a456-426614174000",
  "email": "test@example.com",
  "telegram_id": null,
  "username": "TestUser"
}
```

### 3. Авторизация пользователя
Запрос:
```json
{
  "email": "test@example.com",
  "password": "123456"
}
```

Ответ:
```json
{
  "id": "222e4567-e89b-12d3-a456-426614174000",
  "username": "TestUser",
  "email": "test@example.com",
  "telegram_id": null,
  "token": "REDACTED..."
}
```

### 4. Создание кастомного watchlist
Запрос:
```json
{
  "title": "Комедии, которые хочу посмотреть"
}
```

Ответ:
```json
{
  "id": "444e4567-e89b-12d3-a456-426614174999",
  "user_id": "222e4567-e89b-12d3-a456-426614174000",
  "title": "Комедии, которые хочу посмотреть",
  "type": "custom",
  "color1": "#FFFFFF",
  "color2": "#000000",
  "color3": "#FF0000"
}
```