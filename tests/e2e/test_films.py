import pytest
import requests
import time
import uuid
import random
import string
import os
from urllib.parse import quote


BASE_URL = "http://REDACTED/api/v1"



def random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))



@pytest.fixture(scope="session")
def auth_token():

    timestamp = int(time.time())
    email = f"filmtest_{timestamp}@example.com"
    username = f"filmtest_{timestamp}"
    password = "Password123!"

    register_url = f"{BASE_URL}/auth/register"
    register_data = {"username": username, "email": email, "password": password}

    register_response = requests.post(register_url, json=register_data)

    
    login_url = f"{BASE_URL}/auth/login"
    login_data = {"email": email, "password": password}

    login_response = requests.post(login_url, json=login_data)

    if login_response.status_code != 201:
        pytest.skip(f"Failed to login: {login_response.status_code}, {login_response.text}")

    return login_response.json().get("token")


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def genre_id(auth_headers):
    genres_url = f"{BASE_URL}/genres"

    response = requests.get(genres_url, headers=auth_headers)

    if response.status_code != 200 or not response.json():
        pytest.skip("Failed to get genres")

    return response.json()[0]["id"]


@pytest.fixture(scope="session")
def test_film_data(genre_id):
    timestamp = int(time.time())
    return {
        "title": f"Test Film {timestamp}",
        "description": f"Test film description created during testing {timestamp}",
        "genres_ids": [genre_id],
        "country": "Test Country",
        "release_year": 2023,
    }


@pytest.fixture(scope="session")
def created_film(auth_headers, test_film_data):
    create_url = f"{BASE_URL}/films"

    response = requests.post(create_url, json=test_film_data, headers=auth_headers)

    if response.status_code != 201:
        pytest.skip(f"Failed to create film: {response.status_code}, {response.text}")

    return response.json()


class TestFilmsAPI:

    def test_create_film(self, auth_headers, test_film_data):
        create_url = f"{BASE_URL}/films"

        response = requests.post(create_url, json=test_film_data, headers=auth_headers)

        assert response.status_code == 201, f"Failed to create film: {response.status_code}, {response.text}"

        film_data = response.json()
        assert "id" in film_data, "No film ID in response"
        assert "title" in film_data, "No title in response"
        assert film_data["title"] == test_film_data["title"], "Title doesn't match"
        assert film_data["description"] == test_film_data["description"], "Description doesn't match"

        
        assert uuid.UUID(film_data["id"], version=4), "Invalid film ID format"

    def test_get_film_by_id(self, auth_headers, created_film):
        get_url = f"{BASE_URL}/films/{created_film['id']}"

        response = requests.get(get_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get film: {response.status_code}, {response.text}"

        film_data = response.json()
        assert film_data["id"] == created_film["id"], "Film ID doesn't match"
        assert film_data["title"] == created_film["title"], "Title doesn't match"

    def test_get_nonexistent_film(self, auth_headers):

        nonexistent_id = str(uuid.uuid4())
        get_url = f"{BASE_URL}/films/{nonexistent_id}"

        response = requests.get(get_url, headers=auth_headers)

        assert response.status_code == 404, f"Expected 404 for nonexistent film, got {response.status_code}"

    def test_update_film(self, auth_headers, created_film, genre_id):
        update_url = f"{BASE_URL}/films/{created_film['id']}"

        
        timestamp = int(time.time())
        updated_data = {
            "title": f"Updated Film {timestamp}",
            "description": f"Updated description {timestamp}",
            "genres_ids": [genre_id],
            "country": "Updated Country",
            "release_year": 2024,
        }

        response = requests.put(update_url, json=updated_data, headers=auth_headers)

        assert response.status_code == 200, f"Failed to update film: {response.status_code}, {response.text}"

        updated_film = response.json()
        assert updated_film["id"] == created_film["id"], "Film ID changed after update"
        assert updated_film["title"] == updated_data["title"], "Title not updated"
        assert updated_film["description"] == updated_data["description"], "Description not updated"
        assert updated_film["country"] == updated_data["country"], "Country not updated"
        assert updated_film["release_year"] == updated_data["release_year"], "Release year not updated"

    def test_update_nonexistent_film(self, auth_headers, genre_id):

        nonexistent_id = str(uuid.uuid4())
        update_url = f"{BASE_URL}/films/{nonexistent_id}"

        update_data = {
            "title": "Should Not Update",
            "description": "This film doesn't exist",
            "genres_ids": [genre_id],
            "country": "Nowhere",
            "release_year": 2025,
        }

        response = requests.put(update_url, json=update_data, headers=auth_headers)

        
        assert response.status_code in [403, 404], (
            f"Expected 404 for nonexistent film update, got {response.status_code}"
        )

    def test_upload_poster(self, auth_headers, created_film):
        upload_url = f"{BASE_URL}/films/{created_film['id']}/poster"

        
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img.png")

        
        if not os.path.exists(image_path):
            pytest.skip(f"Test image file not found at {image_path}")

        
        with open(image_path, "rb") as img_file:
            files = {"file": ("img.png", img_file, "image/png")}

            
            upload_headers = {"Authorization": f"Bearer {auth_headers['Authorization']}"}

            response = requests.put(upload_url, headers=upload_headers, files=files)

        assert response.status_code == 204, f"Failed to upload poster: {response.status_code}, {response.text}"

        
        get_url = f"{BASE_URL}/films/{created_film['id']}"
        get_response = requests.get(get_url, headers=auth_headers)

        if get_response.status_code == 200:
            film_data = get_response.json()
            assert film_data.get("poster_url") is not None, "Poster URL is not set after upload"

    def test_delete_poster(self, auth_headers, created_film):
        delete_url = f"{BASE_URL}/films/{created_film['id']}/poster"

        response = requests.delete(delete_url, headers=auth_headers)

        assert response.status_code == 204, f"Failed to delete poster: {response.status_code}, {response.text}"

        
        get_url = f"{BASE_URL}/films/{created_film['id']}"
        get_response = requests.get(get_url, headers=auth_headers)

        if get_response.status_code == 200:
            film_data = get_response.json()
            assert film_data.get("poster_url") is None, "Poster URL is still set after deletion"

    def test_search_films_by_description(self, auth_headers, created_film):

        words = created_film["description"].split()
        search_term = words[2] if len(words) > 2 else words[0]  
        search_url = f"{BASE_URL}/films/search?description={quote(search_term)}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to search by description: {response.status_code}, {response.text}"

        search_results = response.json()
        assert isinstance(search_results, list), "Search results should be a list"

        
        

    def test_search_films_with_limit(self, auth_headers):
        search_url = f"{BASE_URL}/films/search?title=test&limit=1"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to search with limit: {response.status_code}, {response.text}"

        search_results = response.json()
        assert isinstance(search_results, list), "Search results should be a list"
        assert len(search_results) <= 1, f"Search returned {len(search_results)} results, expected at most 1"

    def test_empty_search(self, auth_headers):
        search_url = f"{BASE_URL}/films/search?title="

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400], f"Empty search failed: {response.status_code}, {response.text}"

        
        if response.status_code == 200:
            search_results = response.json()
            assert isinstance(search_results, list), "Search results should be a list"
