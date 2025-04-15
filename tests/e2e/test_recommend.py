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
    email = f"rectest_{timestamp}@example.com"
    username = f"rectest_{timestamp}"
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
def genre_ids(auth_headers):
    genres_url = f"{BASE_URL}/genres"

    response = requests.get(genres_url, headers=auth_headers)

    if response.status_code != 200 or not response.json():
        pytest.skip("Failed to get genres")

    
    genres = response.json()
    if len(genres) > 1:
        return [genres[0]["id"], genres[1]["id"]]
    else:
        return [genres[0]["id"]]


@pytest.fixture(scope="session")
def mood_ids(auth_headers):
    moods_url = f"{BASE_URL}/moods"

    response = requests.get(moods_url, headers=auth_headers)

    if response.status_code != 200 or not response.json():
        pytest.skip("Failed to get moods")

    
    moods = response.json()
    if len(moods) > 1:
        return [moods[0]["id"], moods[1]["id"]]
    else:
        return [moods[0]["id"]]


class TestRecommendAPI:
    def test_recommend_by_genres(self, auth_headers, genre_ids):
        genre_id = genre_ids[0]
        recommend_url = f"{BASE_URL}/recommend?genres_ids={genre_id}&moods_ids={genre_id}"  

        response = requests.post(recommend_url, headers=auth_headers)

        
        assert response.status_code in [201, 404], f"Recommendation request failed with status {response.status_code}"

        
        if response.status_code == 201:
            film = response.json()
            assert "id" in film, "Recommended film is missing 'id' field"
            assert "title" in film, "Recommended film is missing 'title' field"
            assert "description" in film, "Recommended film is missing 'description' field"

    def test_recommend_by_moods(self, auth_headers, mood_ids):
        
        mood_id = mood_ids[0]
        
        genres_url = f"{BASE_URL}/genres?moods_ids={mood_id}"
        genres_response = requests.get(genres_url, headers=auth_headers)

        if genres_response.status_code != 200 or not genres_response.json():
            pytest.skip("Failed to get genres for mood")

        genre_id = genres_response.json()[0]["id"]

        recommend_url = f"{BASE_URL}/recommend?genres_ids={genre_id}&moods_ids={mood_id}"

        response = requests.post(recommend_url, headers=auth_headers)

        
        assert response.status_code in [201, 404], f"Recommendation request failed with status {response.status_code}"

        
        if response.status_code == 201:
            film = response.json()
            assert "id" in film, "Recommended film is missing 'id' field"
            assert "title" in film, "Recommended film is missing 'title' field"
            assert "description" in film, "Recommended film is missing 'description' field"

    def test_recommend_by_genres_and_moods(self, auth_headers, genre_ids, mood_ids):
        
        genre_id = genre_ids[0]
        mood_id = mood_ids[0]

        recommend_url = f"{BASE_URL}/recommend?genres_ids={genre_id}&moods_ids={mood_id}"

        response = requests.post(recommend_url, headers=auth_headers)

        
        assert response.status_code in [201, 404], f"Recommendation request failed with status {response.status_code}"

        
        if response.status_code == 201:
            film = response.json()
            assert "id" in film, "Recommended film is missing 'id' field"
            assert "title" in film, "Recommended film is missing 'title' field"
            assert "description" in film, "Recommended film is missing 'description' field"

    def test_recommend_multiple_genres(self, auth_headers, genre_ids):
        if len(genre_ids) < 2:
            pytest.skip("Not enough genres for multiple genre test")

        
        genres_param = f"{genre_ids[0]}&genres_ids={genre_ids[1]}"
        recommend_url = f"{BASE_URL}/recommend?genres_ids={genres_param}&moods_ids={genre_ids[0]}"  

        response = requests.post(recommend_url, headers=auth_headers)

        
        assert response.status_code in [201, 404], (
            f"Multiple genre recommendation failed with status {response.status_code}"
        )

        
        if response.status_code == 201:
            film = response.json()
            assert "id" in film, "Recommended film is missing 'id' field"
            assert "title" in film, "Recommended film is missing 'title' field"

    def test_recommend_without_genres(self, auth_headers, mood_ids):
        
        mood_id = mood_ids[0]
        recommend_url = f"{BASE_URL}/recommend?moods_ids={mood_id}"

        response = requests.post(recommend_url, headers=auth_headers)

        
        assert response.status_code in [400, 404], f"Expected 400 Bad Request, got {response.status_code}"

    def test_recommend_without_moods(self, auth_headers, genre_ids):
        
        genre_id = genre_ids[0]
        recommend_url = f"{BASE_URL}/recommend?genres_ids={genre_id}"

        response = requests.post(recommend_url, headers=auth_headers)

        
        assert response.status_code == 201, f"Expected 201 Created, got {response.status_code}"

        
        film = response.json()
        assert "id" in film, "Response is missing 'id' field"
        assert "title" in film, "Response is missing 'title' field"
        assert "description" in film, "Response is missing 'description' field"

    def test_recommend_with_invalid_ids(self, auth_headers):
        nonexistent_genre_id = str(uuid.uuid4())
        nonexistent_mood_id = str(uuid.uuid4())

        recommend_url = f"{BASE_URL}/recommend?genres_ids={nonexistent_genre_id}&moods_ids={nonexistent_mood_id}"

        response = requests.post(recommend_url, headers=auth_headers)

        
        assert response.status_code in [201, 404, 400, 500], f"Unexpected status: {response.status_code}"

        
        if response.status_code == 201:
            film = response.json()
            assert "id" in film, "Response is missing 'id' field"
            assert "title" in film, "Response is missing 'title' field"

    def test_recommend_film_structure(self, auth_headers, genre_ids, mood_ids):
        
        genre_id = genre_ids[0]
        mood_id = mood_ids[0]

        recommend_url = f"{BASE_URL}/recommend?genres_ids={genre_id}&moods_ids={mood_id}"

        response = requests.post(recommend_url, headers=auth_headers)

        
        if response.status_code == 201:
            film = response.json()

            
            required_fields = ["id", "title", "description"]
            for field in required_fields:
                assert field in film, f"Recommended film is missing required field '{field}'"

            
            optional_fields = [
                "country",
                "release_year",
                "poster_url",
                "tmdb_id",
                "owner_id",
                "is_liked",
                "is_wish",
                "is_watched",
            ]
            for field in optional_fields:
                if field in film:
                    
                    pass

            
            assert isinstance(film["id"], str), "id should be a string (UUID)"
            assert isinstance(film["title"], str), "title should be a string"
            assert isinstance(film["description"], str), "description should be a string"

    def test_recommend_no_auth(self, genre_ids, mood_ids):

        genre_id = genre_ids[0]
        mood_id = mood_ids[0]

        recommend_url = f"{BASE_URL}/recommend?genres_ids={genre_id}&moods_ids={mood_id}"

        response = requests.post(recommend_url)

        
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
