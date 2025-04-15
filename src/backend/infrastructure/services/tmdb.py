import asyncio
import random
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from backend.config.settings import Settings

COUNTRY_CODE_LOCALIZATION_DICT = {
    "AD": "Андорра",
    "AE": "ОАЭ",
    "AG": "Антигуа и Барбуда",
    "AL": "Албания",
    "AO": "Ангола",
    "AR": "Аргентина",
    "AT": "Австрия",
    "AU": "Австралия",
    "AZ": "Азербайджан",
    "BA": "Босния и Герцеговина",
    "BB": "Барбадос",
    "BE": "Бельгия",
    "BF": "Буркина-Фасо",
    "BG": "Болгария",
    "BH": "Бахрейн",
    "BM": "Бермудские о-ва",
    "BO": "Боливия",
    "BR": "Бразилия",
    "BS": "Багамские о-ва",
    "BY": "Беларусь",
    "BZ": "Белиз",
    "CA": "Канада",
    "CD": "Конго - Киншаса",
    "CH": "Швейцария",
    "CI": "Кот-д’Ивуар",
    "CL": "Чили",
    "CM": "Камерун",
    "CO": "Колумбия",
    "CR": "Коста-Рика",
    "CU": "Куба",
    "CV": "Кабо-Верде",
    "CY": "Кипр",
    "CZ": "Чехия",
    "DE": "Германия",
    "DK": "Дания",
    "DO": "Доминиканская Республика",
    "DZ": "Алжир",
    "EC": "Эквадор",
    "EE": "Эстония",
    "EG": "Египет",
    "ES": "Испания",
    "FI": "Финляндия",
    "FJ": "Фиджи",
    "FR": "Франция",
    "GB": "Великобритания",
    "GF": "Французская Гвиана",
    "GH": "Гана",
    "GI": "Гибралтар",
    "GP": "Гваделупа",
    "GQ": "Экваториальная Гвинея",
    "GR": "Греция",
    "GT": "Гватемала",
    "GY": "Гайана",
    "HK": "Гонконг (особый район)",
    "HN": "Гондурас",
    "HR": "Хорватия",
    "HU": "Венгрия",
    "ID": "Индонезия",
    "IE": "Ирландия",
    "IL": "Израиль",
    "IN": "Индия",
    "IQ": "Ирак",
    "IS": "Исландия",
    "IT": "Италия",
    "JM": "Ямайка",
    "JO": "Иордания",
    "JP": "Япония",
    "KE": "Кения",
    "KR": "Республика Корея",
    "KW": "Кувейт",
    "LB": "Ливан",
    "LC": "Сент-Люсия",
    "LI": "Лихтенштейн",
    "LT": "Литва",
    "LU": "Люксембург",
    "LV": "Латвия",
    "LY": "Ливия",
    "MA": "Марокко",
    "MC": "Монако",
    "MD": "Молдова",
    "ME": "Черногория",
    "MG": "Мадагаскар",
    "MK": "Македония",
    "ML": "Мали",
    "MT": "Мальта",
    "MU": "Маврикий",
    "MW": "Малави",
    "MX": "Мексика",
    "MY": "Малайзия",
    "MZ": "Мозамбик",
    "NE": "Нигер",
    "NG": "Нигерия",
    "NI": "Никарагуа",
    "NL": "Нидерланды",
    "NO": "Норвегия",
    "NZ": "Новая Зеландия",
    "OM": "Оман",
    "PA": "Панама",
    "PE": "Перу",
    "PF": "Французская Полинезия",
    "PG": "Папуа – Новая Гвинея",
    "PH": "Филиппины",
    "PK": "Пакистан",
    "PL": "Польша",
    "PS": "Палестинские территории",
    "PT": "Португалия",
    "PY": "Парагвай",
    "QA": "Катар",
    "RO": "Румыния",
    "RS": "Сербия",
    "RU": "Россия",
    "SA": "Саудовская Аравия",
    "SC": "Сейшельские о-ва",
    "SE": "Швеция",
    "SG": "Сингапур",
    "SI": "Словения",
    "SK": "Словакия",
    "SM": "Сан-Марино",
    "SN": "Сенегал",
    "SV": "Сальвадор",
    "TC": "О-ва Тёркс и Кайкос",
    "TD": "Чад",
    "TH": "Таиланд",
    "TN": "Тунис",
    "TR": "Турция",
    "TT": "Тринидад и Тобаго",
    "TW": "Тайвань",
    "TZ": "Танзания",
    "UA": "Украина",
    "UG": "Уганда",
    "US": "Соединенные Штаты",
    "UY": "Уругвай",
    "VA": "Ватикан",
    "VE": "Венесуэла",
    "XK": "Косово",
    "YE": "Йемен",
    "ZA": "ЮАР",
    "ZM": "Замбия",
    "ZW": "Зимбабве"
}

COUNTRY_LOCALIZATION_DICT = {
    "Andorra": "Андорра",
    "United Arab Emirates": "ОАЭ",
    "Antigua and Barbuda": "Антигуа и Барбуда",
    "Albania": "Албания",
    "Angola": "Ангола",
    "Argentina": "Аргентина",
    "Austria": "Австрия",
    "Australia": "Австралия",
    "Azerbaijan": "Азербайджан",
    "Bosnia and Herzegovina": "Босния и Герцеговина",
    "Barbados": "Барбадос",
    "Belgium": "Бельгия",
    "Burkina Faso": "Буркина-Фасо",
    "Bulgaria": "Болгария",
    "Bahrain": "Бахрейн",
    "Bermuda": "Бермудские о-ва",
    "Bolivia": "Боливия",
    "Brazil": "Бразилия",
    "Bahamas": "Багамские о-ва",
    "Belarus": "Беларусь",
    "Belize": "Белиз",
    "Canada": "Канада",
    "Congo": "Конго - Киншаса",
    "Switzerland": "Швейцария",
    "Cote D'Ivoire": "Кот-д’Ивуар",
    "Chile": "Чили",
    "Cameroon": "Камерун",
    "Colombia": "Колумбия",
    "Costa Rica": "Коста-Рика",
    "Cuba": "Куба",
    "Cape Verde": "Кабо-Верде",
    "Cyprus": "Кипр",
    "Czech Republic": "Чехия",
    "Germany": "Германия",
    "Denmark": "Дания",
    "Dominican Republic": "Доминиканская Республика",
    "Algeria": "Алжир",
    "Ecuador": "Эквадор",
    "Estonia": "Эстония",
    "Egypt": "Египет",
    "Spain": "Испания",
    "Finland": "Финляндия",
    "Fiji": "Фиджи",
    "France": "Франция",
    "United Kingdom": "Великобритания",
    "French Guiana": "Французская Гвиана",
    "Ghana": "Гана",
    "Gibraltar": "Гибралтар",
    "Guadaloupe": "Гваделупа",
    "Equatorial Guinea": "Экваториальная Гвинея",
    "Greece": "Греция",
    "Guatemala": "Гватемала",
    "Guyana": "Гайана",
    "Hong Kong": "Гонконг (особый район)",
    "Honduras": "Гондурас",
    "Croatia": "Хорватия",
    "Hungary": "Венгрия",
    "Indonesia": "Индонезия",
    "Ireland": "Ирландия",
    "Israel": "Израиль",
    "India": "Индия",
    "Iraq": "Ирак",
    "Iceland": "Исландия",
    "Italy": "Италия",
    "Jamaica": "Ямайка",
    "Jordan": "Иордания",
    "Japan": "Япония",
    "Kenya": "Кения",
    "South Korea": "Республика Корея",
    "Kuwait": "Кувейт",
    "Lebanon": "Ливан",
    "St. Lucia": "Сент-Люсия",
    "Liechtenstein": "Лихтенштейн",
    "Lithuania": "Литва",
    "Luxembourg": "Люксембург",
    "Latvia": "Латвия",
    "Libyan Arab Jamahiriya": "Ливия",
    "Morocco": "Марокко",
    "Monaco": "Монако",
    "Moldova": "Молдова",
    "Montenegro": "Черногория",
    "Madagascar": "Мадагаскар",
    "Macedonia": "Македония",
    "Mali": "Мали",
    "Malta": "Мальта",
    "Mauritius": "Маврикий",
    "Malawi": "Малави",
    "Mexico": "Мексика",
    "Malaysia": "Малайзия",
    "Mozambique": "Мозамбик",
    "Niger": "Нигер",
    "Nigeria": "Нигерия",
    "Nicaragua": "Никарагуа",
    "Netherlands": "Нидерланды",
    "Norway": "Норвегия",
    "New Zealand": "Новая Зеландия",
    "Oman": "Оман",
    "Panama": "Панама",
    "Peru": "Перу",
    "French Polynesia": "Французская Полинезия",
    "Papua New Guinea": "Папуа – Новая Гвинея",
    "Philippines": "Филиппины",
    "Pakistan": "Пакистан",
    "Poland": "Польша",
    "Palestinian Territory": "Палестинские территории",
    "Portugal": "Португалия",
    "China": "Китай",
    "Paraguay": "Парагвай",
    "Qatar": "Катар",
    "Romania": "Румыния",
    "Serbia": "Сербия",
    "Russia": "Россия",
    "Saudi Arabia": "Саудовская Аравия",
    "Seychelles": "Сейшельские о-ва",
    "Sweden": "Швеция",
    "Singapore": "Сингапур",
    "Slovenia": "Словения",
    "Slovakia": "Словакия",
    "San Marino": "Сан-Марино",
    "Senegal": "Сенегал",
    "El Salvador": "Сальвадор",
    "Turks and Caicos Islands": "О-ва Тёркс и Кайкос",
    "Chad": "Чад",
    "Thailand": "Таиланд",
    "Tunisia": "Тунис",
    "Turkey": "Турция",
    "Trinidad and Tobago": "Тринидад и Тобаго",
    "Taiwan": "Тайвань",
    "Tanzania": "Танзания",
    "Ukraine": "Украина",
    "Uganda": "Уганда",
    "United States of America": "Соединенные Штаты",
    "Uruguay": "Уругвай",
    "Holy See": "Ватикан",
    "Venezuela": "Венесуэла",
    "Kosovo": "Косово",
    "Yemen": "Йемен",
    "South Africa": "ЮАР",
    "Zambia": "Замбия",
    "Zimbabwe": "Зимбабве"
}


@dataclass
class TMDBService:
    api_key: str = Settings().TMDB_API_KEY
    base_url: str = Settings().TMDB_BASE_URL
    client: httpx.AsyncClient = field(default_factory=httpx.AsyncClient)
    kinopoisk_unofficial_key: str = Settings().KINOPOISK_UNOFFICIAL_KEY
    kinopoisk_unofficial_base_url: str = Settings().KINOPOISK_UNOFFICIAL_KEY
    kinopoisk_dev_key: str = Settings().KINOPOISK_DEV_KEY
    kinopoisk_dev_base_url: str = Settings().KINOPOISK_DEV_BASE_URL

    def contains_cyrillic(self, text: str) -> bool:
        return any("а" <= ch.lower() <= "я" for ch in text)

    async def format_movie_data(self, movie_details: dict[str, Any]) -> dict[str, Any]:
        title = movie_details.get("title", "")
        if not self.contains_cyrillic(title):
            kp_results = await self.search_kinopoisk_and_get_details(title, limit=1)
            if kp_results and kp_results[0].get("title"):
                kp_title = kp_results[0].get("title")
                if self.contains_cyrillic(kp_title):
                    title = kp_title
        genres = [{"id": g["id"], "name": g["name"]} for g in movie_details.get("genres", [])]
        return {
            "title": title,
            "description": movie_details.get("overview", ""),
            "country": self._get_production_country(movie_details),
            "release_year": self._extract_year(movie_details.get("release_date", "")),
            "poster_url": self.get_poster_url(movie_details.get("poster_path")),
            "tmdb_id": movie_details.get("id"),
            "genres": genres,
        }

    async def search_multi(self, query: str, limit: int = 20) -> dict[str, Any]:
        url = f"{self.base_url}/search/multi"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"query": query, "language": "ru-RU", "include_adult": "false", "page": 1}

        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_movie_details(self, movie_id: int) -> dict[str, Any]:
        url = f"{self.base_url}/movie/{movie_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"language": "ru-RU", "append_to_response": "credits,videos,images"}

        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def get_tv_details(self, tv_id: int) -> dict[str, Any]:
        url = f"{self.base_url}/tv/{tv_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"language": "ru-RU", "append_to_response": "credits,videos,images"}

        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def search_all_and_get_details(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        search_results = await self.search_multi(query, limit=limit * 2)
        if not search_results or search_results.get("total_results", 0) == 0:
            return []

        results = [
            result for result in search_results.get("results", []) if
            result.get("media_type") in ["movie", "tv"]
        ][:limit]

        detail_tasks = []
        for item in results:
            if item.get("media_type") == "movie":
                task = self._get_movie_details_and_format(item["id"])
            elif item.get("media_type") == "tv":
                task = self._get_tv_details_and_format(item["id"])
            else:
                continue
            detail_tasks.append(task)

        detailed_results = await asyncio.gather(*detail_tasks, return_exceptions=True)

        filtered_results = [
            result for result in detailed_results if not isinstance(result, Exception) and result is not None
        ]

        return filtered_results[:limit]

    async def _get_movie_details_and_format(self, movie_id: int) -> dict[str, Any] | None:
        try:
            details = await self.get_movie_details(movie_id)
            return await self.format_movie_data(details)
        except Exception as e:
            print(f"Error getting details for movie {movie_id}: {e!s}")
            return None

    async def _get_tv_details_and_format(self, tv_id: int) -> dict[str, Any] | None:
        try:
            details = await self.get_tv_details(tv_id)
            return await self.format_tv_data(details)
        except Exception as e:
            print(f"Error getting details for TV show {tv_id}: {e!s}")
            return None

    def get_poster_url(self, poster_path: str | None, size: str = "w500") -> str | None:
        if not poster_path:
            return None
        return f"https://dbpic.kekz.site/t/p/{size}{poster_path}"

    async def format_tv_data(self, tv_details: dict[str, Any]) -> dict[str, Any]:
        genres = [{"id": g["id"], "name": g["name"]} for g in tv_details.get("genres", [])]
        return {
            "title": tv_details.get("name", ""),
            "description": tv_details.get("overview", ""),
            "country": self._get_production_country(tv_details),
            "release_year": self._extract_year(tv_details.get("first_air_date", "")),
            "poster_url": self.get_poster_url(tv_details.get("poster_path")),
            "tmdb_id": tv_details.get("id"),
            "genres": genres,
        }

    def _get_production_country(self, media_details: dict[str, Any]) -> str | None:
        #print(media_details)
        if media_details.get("production_countries"):
            production_countries = media_details.get("production_countries", [])
            if production_countries:
                print(production_countries[0].get("name"))
                country = production_countries[0].get("name")
                print(country)
                print(COUNTRY_LOCALIZATION_DICT.get(country, country))
                return COUNTRY_LOCALIZATION_DICT.get(country, country)
        return None

    def _extract_year(self, release_date: str) -> int | None:
        if release_date and len(release_date) >= 4:
            try:
                return int(release_date[:4])
            except ValueError:
                pass
        return None

    async def close(self):
        await self.client.aclose()

    async def search_kinopoisk_and_get_details(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        url = f"{self.kinopoisk_dev_base_url}/v1.4/movie/search"
        headers = {"X-API-KEY": self.kinopoisk_dev_key}
        params = {"query": query, "limit": limit, "page": 1}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                kinopoisk_data = response.json()

                if not kinopoisk_data or not kinopoisk_data.get("docs"):
                    return []

                results = []
                for item in kinopoisk_data.get("docs", [])[:limit]:
                    genres = []
                    for genre in item.get("genres", []):
                        if isinstance(genre, dict) and "name" in genre:
                            genres.append({"id": len(genres) + 1, "name": genre["name"]})

                    movie_data = {
                        "title": item.get("name", ""),
                        "description": item.get("description", "") or item.get("shortDescription", ""),
                        "country": self._get_country_from_kinopoisk(item),
                        "release_year": item.get("year"),
                        "poster_url": self._get_poster_url_from_kinopoisk(item),
                        "tmdb_id": item.get("id"),
                        "genres": genres,
                    }
                    results.append(movie_data)

                return results
        except Exception as e:
            print(f"Error searching movies in Kinopoisk: {e}")
            return []

    def _get_country_from_kinopoisk(self, item: dict) -> str | None:
        countries = item.get("countries", [])
        if countries and isinstance(countries, list) and len(countries) > 0:
            country = countries[0]
            if isinstance(country, dict) and "name" in country:
                return country["name"]
        return None

    def _get_poster_url_from_kinopoisk(self, item: dict) -> str | None:
        poster = item.get("poster")
        if poster and isinstance(poster, dict) and "url" in poster:
            return poster["url"]
        return None

    async def get_random_kinopoisk_movie(
            self,
            genres: list[str] = None,
            movie_type: str = None,
            excluded_ids: list[int] = None
    ) -> dict[str, Any] | None:
        if excluded_ids is None:
            excluded_ids = []

        genre_ids = await self._get_genre_ids_by_names(genres)

        genre_param = None
        if genre_ids:
            genre_param = random.choice(genre_ids)

        kinopoisk_type = None
        if movie_type:
            type_mapping = {
                "movie": "FILM",
                "tv": "TV_SERIES",
                "mini-series": "MINI_SERIES",
                "tv-show": "TV_SHOW"
            }
            kinopoisk_type = type_mapping.get(movie_type.lower())

        try:
            total_pages = await self._get_total_pages(genre_param, kinopoisk_type)

            if total_pages == 0:
                return None

            random_page = random.randint(1, min(total_pages, 20))

            movies = await self._get_movies_from_page(genre_param, kinopoisk_type, random_page)

            filtered_movies = [m for m in movies if m.get("kinopoiskId") not in excluded_ids]

            if not filtered_movies:
                return None

            random_movie = random.choice(filtered_movies)

            kinopoisk_id = random_movie.get("kinopoiskId")
            movie_with_tmdb = await self._get_kinopoisk_movie_details(kinopoisk_id)

            if movie_with_tmdb:
                return movie_with_tmdb

            return {
                "title": random_movie.get("nameRu") or random_movie.get("nameEn") or random_movie.get("nameOriginal", ""),
                "description": "",
                "country": random_movie.get("countries", [{}])[0].get("country") if random_movie.get("countries") else None,
                "release_year": random_movie.get("year"),
                "poster_url": random_movie.get("posterUrl"),
                "tmdb_id": random_movie.get("kinopoiskId"),
                "genres": [{"id": g.get("id", 0), "name": g.get("genre", "")} for g in random_movie.get("genres", [])],
            }

        except Exception as e:
            print(f"Error getting random movie from KinopoiskUnofficial: {e}")
            return None

    async def _get_genre_ids_by_names(self, genre_names: list[str] = None) -> list[int]:
        if not genre_names:
            return []

        url = f"{self.kinopoisk_unofficial_base_url}/api/v2.2/films/filters"
        headers = {"X-API-KEY": self.kinopoisk_unofficial_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                filters_data = response.json()

                genre_mappings = {}
                for genre in filters_data.get("genres", []):
                    genre_mappings[genre.get("genre", "").lower()] = genre.get("id")

                result = []
                for name in genre_names:
                    if genre_id := genre_mappings.get(name.lower()):
                        result.append(genre_id)

                return result
        except Exception as e:
            print(f"Error getting genre IDs: {e}")
            return []

    async def _get_total_pages(self, genre_id: Optional[int] = None, movie_type: Optional[str] = None) -> int:
        url = f"{self.kinopoisk_unofficial_base_url}/api/v2.2/films"
        headers = {"X-API-KEY": self.kinopoisk_unofficial_key}

        params = {
            "order": "RATING",
            "type": movie_type or "ALL",
            "ratingFrom": 5,
            "ratingTo": 10,
            "yearFrom": 1000,
            "yearTo": 3000,
            "page": 1
        }

        if genre_id:
            params["genres"] = genre_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("totalPages", 0)
        except Exception as e:
            print(f"Error getting total pages: {e}")
            return 0

    async def _get_movies_from_page(self, genre_id: Optional[int] = None, movie_type: Optional[str] = None,
                                    page: int = 1) -> list[dict]:
        url = f"{self.kinopoisk_unofficial_base_url}/api/v2.2/films"
        headers = {"X-API-KEY": self.kinopoisk_unofficial_key}

        params = {
            "order": "RATING",
            "type": movie_type or "ALL",
            "ratingFrom": 5,
            "ratingTo": 10,
            "yearFrom": 1000,
            "yearTo": 3000,
            "page": page
        }

        if genre_id:
            params["genres"] = genre_id

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get("items", [])
        except Exception as e:
            print(f"Error getting movies from page {page}: {e}")
            return []

    async def _get_kinopoisk_movie_details(self, kinopoisk_id: int) -> dict[str, Any] | None:
        url = f"{self.kinopoisk_dev_base_url}/v1.4/movie/{kinopoisk_id}"
        headers = {"X-API-KEY": self.kinopoisk_dev_key}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()

                tmdb_id = None
                external_ids = data.get("externalId", {})
                if isinstance(external_ids, dict):
                    tmdb_id = external_ids.get("tmdb")

                genres = []
                for genre in data.get("genres", []):
                    if isinstance(genre, dict) and "name" in genre:
                        genres.append({"id": len(genres) + 1, "name": genre["name"]})

                return {
                    "title": data.get("name", ""),
                    "description": data.get("description", "") or data.get("shortDescription", ""),
                    "country": self._get_country_from_kinopoisk(data),
                    "release_year": data.get("year"),
                    "poster_url": self._get_poster_url_from_kinopoisk(data),
                    "tmdb_id": tmdb_id or kinopoisk_id,
                    "genres": genres,
                }
        except Exception as e:
            print(f"Error getting movie details for ID {kinopoisk_id}: {e}")
            return None

    async def get_random_tmdb_movie(
            self,
            genres: list[str] = None,
            movie_type: str = None,
            excluded_ids: list[int] = None
    ) -> dict[str, Any] | None:
        if excluded_ids is None:
            excluded_ids = []

        genre_ids = await self._get_tmdb_genre_ids_by_names(genres)

        params = {
            "include_adult": "false",
            "include_video": "false",
            "language": "ru-RU",
            "page": 1,
            "sort_by": "popularity.desc",
            "vote_average.gte": 5,
        }

        if genre_ids:
            params["with_genres"] = "|".join(map(str, genre_ids))

        if movie_type:
            if movie_type.lower() == "movie":
                pass
            elif movie_type.lower() == "tv":
                return await self._get_random_tmdb_tv(params, excluded_ids)

        try:
            url = f"{self.base_url}/discover/movie"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            total_pages = data.get("total_pages", 0)

            if total_pages == 0:
                return None

            random_page = random.randint(1, min(total_pages, 20))

            params["page"] = random_page
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            movies = data.get("results", [])

            filtered_movies = [m for m in movies if m.get("id") not in excluded_ids]

            if not filtered_movies:
                return None

            random_movie = random.choice(filtered_movies)

            details = await self.get_movie_details(random_movie.get("id"))

            return await self.format_movie_data(details)
        except Exception as e:
            print(f"Error getting random movie from TMDB: {e}")
            return None

    async def _get_random_tmdb_tv(self, base_params: dict, excluded_ids: list[int]) -> dict[str, Any] | None:
        try:
            params = base_params.copy()

            url = f"{self.base_url}/discover/tv"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            total_pages = data.get("total_pages", 0)

            if total_pages == 0:
                return None

            random_page = random.randint(1, min(total_pages, 20))

            params["page"] = random_page
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            tv_shows = data.get("results", [])

            filtered_tv_shows = [tv for tv in tv_shows if tv.get("id") not in excluded_ids]

            if not filtered_tv_shows:
                return None

            random_tv = random.choice(filtered_tv_shows)

            details = await self.get_tv_details(random_tv.get("id"))

            return await self.format_tv_data(details)
        except Exception as e:
            print(f"Error getting random TV show from TMDB: {e}")
            return None

    async def _get_tmdb_genre_ids_by_names(self, genre_names: list[str] = None) -> list[int]:
        if not genre_names:
            return []

        url = f"{self.base_url}/genre/movie/list"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"language": "ru-RU"}

        try:
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            genres_data = response.json()

            genre_mappings = {}
            for genre in genres_data.get("genres", []):
                genre_mappings[genre.get("name", "").lower()] = genre.get("id")

            result = []
            for name in genre_names:
                if genre_id := genre_mappings.get(name.lower()):
                    result.append(genre_id)

            return result
        except Exception as e:
            print(f"Error getting genre IDs from TMDB: {e}")
            return []
