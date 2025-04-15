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
    email = f"watchtest_{timestamp}@example.com"
    username = f"watchtest_{timestamp}"
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
def test_film_id(auth_headers):

    genres_url = f"{BASE_URL}/genres"
    genres_response = requests.get(genres_url, headers=auth_headers)

    if genres_response.status_code != 200 or not genres_response.json():
        pytest.skip("Failed to get genres for film creation")

    genre_id = genres_response.json()[0]["id"]

    
    timestamp = int(time.time())
    film_data = {
        "title": f"Watchlist Test Film {timestamp}",
        "description": f"Test film for watchlist tests {timestamp}",
        "genres_ids": [genre_id],
        "country": "Test Country",
        "release_year": 2023,
    }

    create_url = f"{BASE_URL}/films"
    response = requests.post(create_url, json=film_data, headers=auth_headers)

    if response.status_code != 201:
        pytest.skip(f"Failed to create test film: {response.status_code}, {response.text}")

    return response.json()["id"]


@pytest.fixture(scope="session")
def custom_watchlist_id(auth_headers):
    timestamp = int(time.time())
    watchlist_data = {"title": f"Test Watchlist {timestamp}"}

    create_url = f"{BASE_URL}/me/watchlists"
    response = requests.post(create_url, json=watchlist_data, headers=auth_headers)

    if response.status_code != 201:
        pytest.skip(f"Failed to create custom watchlist: {response.status_code}, {response.text}")

    return response.json()["id"]


class TestWatchlistsAPI:
    def test_get_liked_watchlist(self, auth_headers):
        liked_url = f"{BASE_URL}/me/watchlists/liked"

        response = requests.get(liked_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get liked watchlist: {response.status_code}, {response.text}"

        watchlist = response.json()
        assert "id" in watchlist, "Watchlist is missing 'id' field"
        assert "type" in watchlist, "Watchlist is missing 'type' field"
        assert watchlist["type"] == "liked", "Watchlist type should be 'liked'"

    def test_get_watched_watchlist(self, auth_headers):
        watched_url = f"{BASE_URL}/me/watchlists/watched"

        response = requests.get(watched_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get watched watchlist: {response.status_code}, {response.text}"

        watchlist = response.json()
        assert "id" in watchlist, "Watchlist is missing 'id' field"
        assert "type" in watchlist, "Watchlist is missing 'type' field"
        assert watchlist["type"] == "watched", "Watchlist type should be 'watched'"

    def test_get_wish_watchlist(self, auth_headers):
        wish_url = f"{BASE_URL}/me/watchlists/wish"

        response = requests.get(wish_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get wish watchlist: {response.status_code}, {response.text}"

        watchlist = response.json()
        assert "id" in watchlist, "Watchlist is missing 'id' field"
        assert "type" in watchlist, "Watchlist is missing 'type' field"
        assert watchlist["type"] == "wish", "Watchlist type should be 'wish'"

    def test_create_custom_watchlist(self, auth_headers):
        timestamp = int(time.time())
        watchlist_data = {"title": f"Test Custom Watchlist {timestamp}"}

        create_url = f"{BASE_URL}/me/watchlists"

        response = requests.post(create_url, json=watchlist_data, headers=auth_headers)

        assert response.status_code == 201, (
            f"Failed to create custom watchlist: {response.status_code}, {response.text}"
        )

        watchlist = response.json()
        assert "id" in watchlist, "Watchlist is missing 'id' field"
        assert "title" in watchlist, "Watchlist is missing 'title' field"
        assert "type" in watchlist, "Watchlist is missing 'type' field"

        assert "color1" in watchlist, "Watchlist is missing 'color1' field"
        assert "color2" in watchlist, "Watchlist is missing 'color2' field"
        assert "color3" in watchlist, "Watchlist is missing 'color3' field"

    def test_get_watchlist_by_id(self, auth_headers, custom_watchlist_id):
        watchlist_url = f"{BASE_URL}/me/watchlists/{custom_watchlist_id}"

        response = requests.get(watchlist_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get watchlist by ID: {response.status_code}, {response.text}"

        watchlist = response.json()
        assert watchlist["id"] == custom_watchlist_id, "Watchlist ID doesn't match"
        assert "title" in watchlist, "Watchlist is missing 'title' field"
        assert "type" in watchlist, "Watchlist is missing 'type' field"

        assert "color1" in watchlist, "Watchlist is missing 'color1' field"
        assert "color2" in watchlist, "Watchlist is missing 'color2' field"
        assert "color3" in watchlist, "Watchlist is missing 'color3' field"

    def test_get_nonexistent_watchlist(self, auth_headers):
        
        nonexistent_id = str(uuid.uuid4())
        watchlist_url = f"{BASE_URL}/me/watchlists/{nonexistent_id}"

        response = requests.get(watchlist_url, headers=auth_headers)

        assert response.status_code == 404, f"Expected 404 for nonexistent watchlist, got {response.status_code}"

    def test_add_film_to_liked_watchlist(self, auth_headers, test_film_id):
        add_url = f"{BASE_URL}/me/watchlists/liked/items/add"
        add_data = {"film_id": test_film_id}

        response = requests.put(add_url, json=add_data, headers=auth_headers)

        assert response.status_code == 204, (
            f"Failed to add film to liked watchlist: {response.status_code}, {response.text}"
        )

        
        items_url = f"{BASE_URL}/me/watchlists/liked/items"
        items_response = requests.get(items_url, headers=auth_headers)

        if items_response.status_code == 200:
            items = items_response.json()

            
            if "items" in items and items["items"]:
                film_ids = [item["id"] for item in items["items"]]
                assert test_film_id in film_ids, "Added film not found in liked watchlist items"

    def test_add_film_to_watched_watchlist(self, auth_headers, test_film_id):
        add_url = f"{BASE_URL}/me/watchlists/watched/items/add"
        add_data = {"film_id": test_film_id}

        response = requests.put(add_url, json=add_data, headers=auth_headers)

        assert response.status_code == 204, (
            f"Failed to add film to watched watchlist: {response.status_code}, {response.text}"
        )

        
        items_url = f"{BASE_URL}/me/watchlists/watched/items"
        items_response = requests.get(items_url, headers=auth_headers)

        if items_response.status_code == 200:
            items = items_response.json()

            
            if "items" in items and items["items"]:
                film_ids = [item["id"] for item in items["items"]]
                assert test_film_id in film_ids, "Added film not found in watched watchlist items"

    def test_add_film_to_wish_watchlist(self, auth_headers, test_film_id):
        add_url = f"{BASE_URL}/me/watchlists/wish/items/add"
        add_data = {"film_id": test_film_id}

        response = requests.put(add_url, json=add_data, headers=auth_headers)

        assert response.status_code == 204, (
            f"Failed to add film to wish watchlist: {response.status_code}, {response.text}"
        )

        
        items_url = f"{BASE_URL}/me/watchlists/wish/items"
        items_response = requests.get(items_url, headers=auth_headers)

        if items_response.status_code == 200:
            items = items_response.json()

            
            if "items" in items and items["items"]:
                film_ids = [item["id"] for item in items["items"]]
                assert test_film_id in film_ids, "Added film not found in wish watchlist items"

    def test_add_film_to_custom_watchlist(self, auth_headers, test_film_id, custom_watchlist_id):
        add_url = f"{BASE_URL}/me/watchlists/{custom_watchlist_id}/items/add"
        add_data = {"film_id": test_film_id}

        response = requests.put(add_url, json=add_data, headers=auth_headers)

        assert response.status_code == 204, (
            f"Failed to add film to custom watchlist: {response.status_code}, {response.text}"
        )

        
        items_url = f"{BASE_URL}/me/watchlists/{custom_watchlist_id}/items"
        items_response = requests.get(items_url, headers=auth_headers)

        if items_response.status_code == 200:
            items = items_response.json()

            
            if "items" in items and items["items"]:
                film_ids = [item["id"] for item in items["items"]]
                assert test_film_id in film_ids, "Added film not found in custom watchlist items"

    def test_remove_film_from_liked_watchlist(self, auth_headers, test_film_id):
        
        add_url = f"{BASE_URL}/me/watchlists/liked/items/add"
        add_data = {"film_id": test_film_id}
        requests.put(add_url, json=add_data, headers=auth_headers)

        
        remove_url = f"{BASE_URL}/me/watchlists/liked/items/{test_film_id}"

        response = requests.delete(remove_url, headers=auth_headers)

        assert response.status_code == 204, (
            f"Failed to remove film from liked watchlist: {response.status_code}, {response.text}"
        )

        
        items_url = f"{BASE_URL}/me/watchlists/liked/items"
        items_response = requests.get(items_url, headers=auth_headers)

        if items_response.status_code == 200:
            items = items_response.json()

            
            if "items" in items and items["items"]:
                film_ids = [item["id"] for item in items["items"]]
                assert test_film_id not in film_ids, "Removed film still found in liked watchlist items"

    def test_remove_film_from_custom_watchlist(self, auth_headers, test_film_id, custom_watchlist_id):
        
        add_url = f"{BASE_URL}/me/watchlists/{custom_watchlist_id}/items/add"
        add_data = {"film_id": test_film_id}
        requests.put(add_url, json=add_data, headers=auth_headers)

        
        remove_url = f"{BASE_URL}/me/watchlists/{custom_watchlist_id}/items/{test_film_id}"

        response = requests.delete(remove_url, headers=auth_headers)

        assert response.status_code == 204, (
            f"Failed to remove film from custom watchlist: {response.status_code}, {response.text}"
        )

        
        items_url = f"{BASE_URL}/me/watchlists/{custom_watchlist_id}/items"
        items_response = requests.get(items_url, headers=auth_headers)

        if items_response.status_code == 200:
            items = items_response.json()

            
            if "items" in items and items["items"]:
                film_ids = [item["id"] for item in items["items"]]
                assert test_film_id not in film_ids, "Removed film still found in custom watchlist items"

    def test_watchlist_response_structure(self, auth_headers, custom_watchlist_id):
        watchlist_url = f"{BASE_URL}/me/watchlists/{custom_watchlist_id}"

        response = requests.get(watchlist_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get watchlist: {response.status_code}, {response.text}"

        watchlist = response.json()

        required_fields = ["id", "user_id", "title", "type", "color1", "color2", "color3"]
        for field in required_fields:
            assert field in watchlist, f"Watchlist is missing required field '{field}'"