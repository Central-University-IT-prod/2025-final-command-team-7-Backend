#!/usr/bin/env python
"""
Скрипт для создания миксов фильмов из JSON файла.
Парсит JSON с готовыми данными о фильмах и создает миксы в базе данных.
"""

import asyncio
import datetime
import json
import os
import random
import sys
import uuid
from typing import Dict, List, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Добавляем корневую директорию проекта в путь для импорта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Импортируем модели и константы
from backend.infrastructure.persistence.models.base import BaseORM
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.persistence.models.mix import MixORM
from backend.infrastructure.persistence.models.mix_item import MixItemORM
from backend.constant import GRADIENTS


async def get_or_create_film(session: AsyncSession, film_data: Dict[str, Any]) -> FilmORM:
    """
    Получить существующий фильм или создать новый на основе данных из JSON.
    """
    # Проверяем, существует ли фильм с таким tmdb_id
    if film_data.get("tmdb_id"):
        stmt = select(FilmORM).where(FilmORM.tmdb_id == film_data["tmdb_id"])
        result = await session.execute(stmt)
        existing_film = result.scalar_one_or_none()
        if existing_film:
            return existing_film

    # Создаем новый фильм
    film = FilmORM(
        id=uuid.uuid4(),
        title=film_data["title"],
        description=film_data["description"],
        country=film_data["country"],
        release_year=film_data["release_year"],
        poster_url=film_data["poster_url"],
        tmdb_id=film_data["tmdb_id"],
        owner_id=None  # У системных фильмов нет владельца
    )
    session.add(film)
    return film


async def create_mix_from_data(session: AsyncSession, genre_name: str, mix_data: Dict[str, Any]) -> None:
    """
    Создать микс и добавить в него фильмы на основе данных из JSON.
    """
    print(f"Создание микса для жанра: {genre_name}")

    # Проверяем, существует ли уже микс с таким названием
    stmt = select(MixORM).where(MixORM.title == mix_data["title"])
    result = await session.execute(stmt)
    existing_mix = result.scalar_one_or_none()

    if existing_mix:
        print(f"Микс '{mix_data['title']}' уже существует, пропускаем")
        return

    # Создаем новый микс
    mix_id = uuid.uuid4()

    # Используем градиенты из данных или случайный градиент
    color1 = mix_data.get("color1")
    color2 = mix_data.get("color2")
    color3 = mix_data.get("color3")

    if not (color1 and color2 and color3):
        gradient = random.choice(GRADIENTS)
        color1, color2, color3 = gradient

    mix = MixORM(
        id=mix_id,
        title=mix_data["title"],
        color1=color1,
        color2=color2,
        color3=color3
    )
    session.add(mix)

    # Добавляем фильмы в микс
    film_count = 0
    for film_data in mix_data.get("films", []):
        if not film_data:
            continue

        # Получаем или создаем фильм
        film = await get_or_create_film(session, film_data)

        # Проверяем, существует ли уже связь между миксом и фильмом
        stmt = select(MixItemORM).where(
            MixItemORM.mix_id == mix.id,
            MixItemORM.film_id == film.id
        )
        result = await session.execute(stmt)
        existing_mix_item = result.scalar_one_or_none()

        # Если связи нет, создаем её
        if not existing_mix_item:
            mix_item = MixItemORM(
                mix_id=mix.id,
                film_id=film.id,
                added_at=datetime.datetime.now(datetime.UTC)
            )
            session.add(mix_item)
            film_count += 1

    print(f"В микс '{mix.title}' добавлено {film_count} фильмов")


async def create_mixes_from_json(json_file_path: str):
    """
    Основная функция для создания миксов из JSON файла.
    """
    # Проверяем существование файла
    if not os.path.isfile(json_file_path):
        print(f"Ошибка: Файл {json_file_path} не найден")
        return

    # Получаем DSN базы данных из переменной окружения
    db_url = os.environ.get("POSTGRES_DSN")
    if not db_url:
        print("Ошибка: Не найдена переменная окружения POSTGRES_DSN")
        return

    # Читаем данные из JSON файла
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            mixes_data = json.load(f)
    except Exception as e:
        print(f"Ошибка при чтении JSON файла: {e}")
        return

    # Создаем движок SQLAlchemy
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    try:
        async with async_session() as session:
            for genre_name, mix_data in mixes_data.items():
                await create_mix_from_data(session, genre_name, mix_data)

            # Сохраняем все изменения
            await session.commit()
            print("Все миксы успешно созданы и сохранены в базе данных")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    # Регистрируем все модели ORM
    from backend.infrastructure.persistence.models.base import register_orm

    register_orm()

    # Определяем путь к JSON файлу
    json_file = "movies_by_genre.json"

    # Если указан аргумент командной строки, используем его как путь к файлу
    if len(sys.argv) > 1:
        json_file = sys.argv[1]

    asyncio.run(create_mixes_from_json(json_file))