import pytest
import requests
import time
import random
import string
import uuid
from datetime import datetime


BASE_URL = "http://REDACTED/api/v1"



def random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def generate_test_data():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "username": f"testuser_{timestamp}_{random_string(5)}",
        "email": f"testuser_{timestamp}_{random_string(5)}@example.com",
        "password": "Password123!",
    }



@pytest.fixture(scope="session")
def test_data():
    return generate_test_data()


@pytest.fixture(scope="session")
def auth_token(test_data):

    register_url = f"{BASE_URL}/auth/register"
    register_payload = {
        "username": test_data["username"],
        "email": test_data["email"],
        "password": test_data["password"],
    }

    try:
        register_response = requests.post(register_url, json=register_payload)
        
    except Exception as e:
        print(f"Registration failed: {e}, proceeding to login")

    
    login_url = f"{BASE_URL}/auth/login"
    login_payload = {"email": test_data["email"], "password": test_data["password"]}

    login_response = requests.post(login_url, json=login_payload)

    
    assert login_response.status_code == 201, f"Login failed with status {login_response.status_code}"

    token = login_response.json()["token"]
    assert token, "No token returned from login"

    user_id = login_response.json()["id"]

    
    return {"token": token, "user_id": user_id}


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token['token']}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def genres(auth_headers):
    genres_url = f"{BASE_URL}/genres"
    response = requests.get(genres_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get genres, status: {response.status_code}"

    genres_data = response.json()
    assert len(genres_data) > 0, "No genres returned"

    return genres_data


@pytest.fixture(scope="session")
def moods(auth_headers):
    moods_url = f"{BASE_URL}/moods"
    response = requests.get(moods_url, headers=auth_headers)

    assert response.status_code == 200, f"Failed to get moods, status: {response.status_code}"

    moods_data = response.json()
    
    return moods_data


@pytest.fixture(scope="session")
def created_film(auth_headers, genres):
    create_film_url = f"{BASE_URL}/films"

    
    genre_id = genres[0]["id"] if genres else None

    
    if not genre_id:
        pytest.skip("No genres available to create film")

    film_data = {
        "title": f"Test Film {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "This is a test film created via automated Python tests.",
        "genres_ids": [genre_id],
        "country": "Test Country",
        "release_year": 2023,
    }

    response = requests.post(create_film_url, json=film_data, headers=auth_headers)

    assert response.status_code == 201, f"Failed to create film, status: {response.status_code}"

    film = response.json()
    return film


@pytest.fixture(scope="session")
def second_film(auth_headers, genres):
    create_film_url = f"{BASE_URL}/films"

    
    genre_id = genres[1]["id"] if len(genres) > 1 else genres[0]["id"]

    film_data = {
        "title": f"Second Test Film {datetime.now().strftime('%Y%m%d%H%M%S')}",
        "description": "This is a second test film with different data.",
        "genres_ids": [genre_id],
        "country": "Another Country",
        "release_year": 2024,
    }

    response = requests.post(create_film_url, json=film_data, headers=auth_headers)

    assert response.status_code == 201, f"Failed to create second film, status: {response.status_code}"

    film = response.json()
    return film


@pytest.fixture(scope="session")
def watchlists(auth_headers):
    result = {}

    
    liked_url = f"{BASE_URL}/me/watchlists/liked"
    liked_response = requests.get(liked_url, headers=auth_headers)
    assert liked_response.status_code == 200, f"Failed to get liked watchlist, status: {liked_response.status_code}"
    result["liked"] = liked_response.json()

    
    watched_url = f"{BASE_URL}/me/watchlists/watched"
    watched_response = requests.get(watched_url, headers=auth_headers)
    assert watched_response.status_code == 200, (
        f"Failed to get watched watchlist, status: {watched_response.status_code}"
    )
    result["watched"] = watched_response.json()

    
    wish_url = f"{BASE_URL}/me/watchlists/wish"
    wish_response = requests.get(wish_url, headers=auth_headers)
    assert wish_response.status_code == 200, f"Failed to get wish watchlist, status: {wish_response.status_code}"
    result["wish"] = wish_response.json()

    return result


@pytest.fixture(scope="session")
def custom_watchlist(auth_headers):
    create_url = f"{BASE_URL}/me/watchlists"

    watchlist_data = {"title": f"My Test Watchlist {datetime.now().strftime('%Y%m%d%H%M%S')}"}

    response = requests.post(create_url, json=watchlist_data, headers=auth_headers)

    assert response.status_code == 201, f"Failed to create custom watchlist, status: {response.status_code}"

    return response.json()



@pytest.fixture(scope="session")
def mix_id(auth_headers):
    mixes_url = f"{BASE_URL}/mix"

    response = requests.get(mixes_url, headers=auth_headers)

    if response.status_code != 200 or not response.json():
        pytest.skip("Failed to get mixes or no mixes available")

    return response.json()[0]["id"]
