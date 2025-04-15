import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx

from backend.infrastructure.services.tmdb import TMDBService


class TestTMDBService:
    @pytest.fixture
    def mock_client(self):
        client = AsyncMock()
        return client

    @pytest.fixture
    def tmdb_service(self, mock_client):
        service = TMDBService()
        service.client = mock_client
        return service

    @pytest.mark.asyncio
    async def test_search_multi(self, tmdb_service, mock_client):
        
        expected_result = {"results": [{"id": 1, "title": "Test Movie"}]}
        response_mock = MagicMock()
        response_mock.raise_for_status = AsyncMock()
        response_mock.json.return_value = expected_result
        mock_client.get.return_value = response_mock

        
        result = await tmdb_service.search_multi("test query")

        
        assert result == expected_result
        mock_client.get.assert_called_once()
        assert "query=test query" in str(mock_client.get.call_args)

    @pytest.mark.asyncio
    async def test_get_movie_details(self, tmdb_service, mock_client):
        
        movie_id = 12345
        expected_result = {"id": movie_id, "title": "Test Movie", "overview": "Test overview"}
        response_mock = MagicMock()
        response_mock.raise_for_status = AsyncMock()
        response_mock.json.return_value = expected_result
        mock_client.get.return_value = response_mock

        
        result = await tmdb_service.get_movie_details(movie_id)

        
        assert result == expected_result
        mock_client.get.assert_called_once()
        assert f"movie/{movie_id}" in str(mock_client.get.call_args)

    @pytest.mark.asyncio
    async def test_get_tv_details(self, tmdb_service, mock_client):
        
        tv_id = 12345
        expected_result = {"id": tv_id, "name": "Test TV Show", "overview": "Test overview"}
        response_mock = MagicMock()
        response_mock.raise_for_status = AsyncMock()
        response_mock.json.return_value = expected_result
        mock_client.get.return_value = response_mock

        
        result = await tmdb_service.get_tv_details(tv_id)

        
        assert result == expected_result
        mock_client.get.assert_called_once()
        assert f"tv/{tv_id}" in str(mock_client.get.call_args)

    @pytest.mark.asyncio
    async def test_format_movie_data(self, tmdb_service):
        
        movie_details = {
            "id": 12345,
            "title": "Test Movie",
            "overview": "Test overview",
            "poster_path": "/test_poster.jpg",
            "release_date": "2023-01-01",
            "production_countries": [{"name": "United States"}],
            "genres": [
                {"id": 1, "name": "Action"},
                {"id": 2, "name": "Comedy"}
            ]
        }

        
        result = await tmdb_service.format_movie_data(movie_details)

        
        assert result["title"] == "Test Movie"
        assert result["description"] == "Test overview"
        assert result["country"] == "United States"
        assert result["release_year"] == 2023
        assert result["poster_url"] is not None
        assert result["tmdb_id"] == 12345
        assert len(result["genres"]) == 2
        assert {"id": 1, "name": "Action"} in result["genres"]

    @pytest.mark.asyncio
    async def test_format_tv_data(self, tmdb_service):
        
        tv_details = {
            "id": 12345,
            "name": "Test TV Show",
            "overview": "Test overview",
            "poster_path": "/test_poster.jpg",
            "first_air_date": "2023-01-01",
            "production_countries": [{"name": "United Kingdom"}],
            "genres": [
                {"id": 1, "name": "Drama"},
                {"id": 2, "name": "Thriller"}
            ]
        }

        
        result = await tmdb_service.format_tv_data(tv_details)

        
        assert result["title"] == "Test TV Show"
        assert result["description"] == "Test overview"
        assert result["country"] == "United Kingdom"
        assert result["release_year"] == 2023
        assert result["poster_url"] is not None
        assert result["tmdb_id"] == 12345
        assert len(result["genres"]) == 2
        assert {"id": 1, "name": "Drama"} in result["genres"]

    @pytest.mark.asyncio
    async def test_search_all_and_get_details(self, tmdb_service):
        
        with patch.object(tmdb_service, 'search_multi') as mock_search, \
                patch.object(tmdb_service, '_get_movie_details_and_format') as mock_movie_details, \
                patch.object(tmdb_service, '_get_tv_details_and_format') as mock_tv_details:
            
            mock_search.return_value = {
                "total_results": 2,
                "results": [
                    {"id": 1, "media_type": "movie", "title": "Test Movie"},
                    {"id": 2, "media_type": "tv", "name": "Test TV Show"}
                ]
            }

            movie_details = {
                "title": "Test Movie",
                "description": "Test description",
                "country": "United States",
                "release_year": 2023,
                "poster_url": "http://example.com/poster.jpg",
                "tmdb_id": 1,
                "genres": [{"id": 1, "name": "Action"}]
            }

            tv_details = {
                "title": "Test TV Show",
                "description": "Test description",
                "country": "United Kingdom",
                "release_year": 2023,
                "poster_url": "http://example.com/poster.jpg",
                "tmdb_id": 2,
                "genres": [{"id": 2, "name": "Drama"}]
            }

            mock_movie_details.return_value = movie_details
            mock_tv_details.return_value = tv_details

            
            results = await tmdb_service.search_all_and_get_details("test query")

            
            assert len(results) == 2
            assert results[0] == movie_details
            assert results[1] == tv_details
            mock_search.assert_called_once_with("test query", limit=20)
            mock_movie_details.assert_called_once_with(1)
            mock_tv_details.assert_called_once_with(2)

    def test_get_poster_url(self, tmdb_service):
        
        assert tmdb_service.get_poster_url("/test_poster.jpg") == "https://image.tmdb.org/t/p/w500/test_poster.jpg"

        
        assert tmdb_service.get_poster_url(None) is None

        
        assert tmdb_service.get_poster_url("/test_poster.jpg",
                                           "original") == "https://image.tmdb.org/t/p/original/test_poster.jpg"