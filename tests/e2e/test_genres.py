import pytest
import requests
import time
import uuid
import random
import string


BASE_URL = "http://REDACTED/api/v1"



def random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))



@pytest.fixture(scope="session")
def auth_token():

    timestamp = int(time.time())
    email = f"genretest_{timestamp}@example.com"
    username = f"genretest_{timestamp}"
    password = "Password123!"

    register_url = f"{BASE_URL}/auth/register"
    register_data = {"username": username, "email": email, "password": password}

    requests.post(register_url, json=register_data)

    
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
def mood_id(auth_headers):
    moods_url = f"{BASE_URL}/moods"

    response = requests.get(moods_url, headers=auth_headers)

    if response.status_code != 200 or not response.json():
        pytest.skip("Failed to get moods")

    return response.json()[0]["id"]


class TestGenresAPI:

    def test_list_genres(self, auth_headers):
        genres_url = f"{BASE_URL}/genres"

        response = requests.get(genres_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to list genres: {response.status_code}, {response.text}"

        genres = response.json()
        assert isinstance(genres, list), "Genres response should be a list"

        
        assert len(genres) > 0, "Genres list is empty"

        
        first_genre = genres[0]
        assert "id" in first_genre, "Genre is missing 'id' field"
        assert "name" in first_genre, "Genre is missing 'name' field"

        
        assert uuid.UUID(first_genre["id"], version=4), "Invalid genre ID format"

    def test_get_genre_by_id(self, auth_headers, genre_id):
        genre_url = f"{BASE_URL}/genres/{genre_id}"

        response = requests.get(genre_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get genre by ID: {response.status_code}, {response.text}"

        genre = response.json()
        assert genre["id"] == genre_id, "Genre ID doesn't match"
        assert "name" in genre, "Genre is missing 'name' field"
        assert len(genre["name"]) > 0, "Genre name is empty"

    def test_get_nonexistent_genre(self, auth_headers):
        
        nonexistent_id = str(uuid.uuid4())
        genre_url = f"{BASE_URL}/genres/{nonexistent_id}"

        response = requests.get(genre_url, headers=auth_headers)

        assert response.status_code == 404, f"Expected 404 for nonexistent genre, got {response.status_code}"

    def test_list_genres_by_mood(self, auth_headers, mood_id):
        genres_url = f"{BASE_URL}/genres?moods_ids={mood_id}"

        response = requests.get(genres_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to list genres by mood: {response.status_code}, {response.text}"

        genres = response.json()
        assert isinstance(genres, list), "Filtered genres response should be a list"

        
        if len(genres) > 0:
            
            first_genre = genres[0]
            assert "id" in first_genre, "Genre is missing 'id' field"
            assert "name" in first_genre, "Genre is missing 'name' field"

    def test_list_genres_no_auth(self):
        genres_url = f"{BASE_URL}/genres"

        response = requests.get(genres_url)

        
        assert response.status_code in [200, 401, 403], f"Unexpected status code: {response.status_code}"

        if response.status_code == 200:
            genres = response.json()
            assert isinstance(genres, list), "Genres response should be a list"


class TestMoodsAPI:

    def test_list_moods(self, auth_headers):
        moods_url = f"{BASE_URL}/moods"

        response = requests.get(moods_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to list moods: {response.status_code}, {response.text}"

        moods = response.json()
        assert isinstance(moods, list), "Moods response should be a list"

        
        assert len(moods) > 0, "Moods list is empty"

        
        first_mood = moods[0]
        assert "id" in first_mood, "Mood is missing 'id' field"
        assert "name" in first_mood, "Mood is missing 'name' field"

        
        assert uuid.UUID(first_mood["id"], version=4), "Invalid mood ID format"

    def test_get_mood_by_id(self, auth_headers, mood_id):
        mood_url = f"{BASE_URL}/moods/{mood_id}"

        response = requests.get(mood_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get mood by ID: {response.status_code}, {response.text}"

        mood = response.json()
        assert mood["id"] == mood_id, "Mood ID doesn't match"
        assert "name" in mood, "Mood is missing 'name' field"
        assert len(mood["name"]) > 0, "Mood name is empty"

    def test_get_nonexistent_mood(self, auth_headers):
        
        nonexistent_id = str(uuid.uuid4())
        mood_url = f"{BASE_URL}/moods/{nonexistent_id}"

        response = requests.get(mood_url, headers=auth_headers)

        assert response.status_code == 404, f"Expected 404 for nonexistent mood, got {response.status_code}"

    def test_list_moods_no_auth(self):
        moods_url = f"{BASE_URL}/moods"

        response = requests.get(moods_url)

        
        assert response.status_code in [200, 401, 403], f"Unexpected status code: {response.status_code}"

        if response.status_code == 200:
            moods = response.json()
            assert isinstance(moods, list), "Moods response should be a list"
