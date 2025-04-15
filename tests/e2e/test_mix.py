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
    email = f"mixtest_{timestamp}@example.com"
    username = f"mixtest_{timestamp}"
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
def mix_id(auth_headers):
    mixes_url = f"{BASE_URL}/mix"

    response = requests.get(mixes_url, headers=auth_headers)

    if response.status_code != 200 or not response.json():
        pytest.skip("Failed to get mixes or no mixes available")

    return response.json()[0]["id"]


class TestMixAPI:

    def test_list_mixes(self, auth_headers):
        mixes_url = f"{BASE_URL}/mix"

        response = requests.get(mixes_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to list mixes: {response.status_code}, {response.text}"

        mixes = response.json()
        assert isinstance(mixes, list), "Mixes response should be a list"

        if mixes:
            first_mix = mixes[0]
            assert "id" in first_mix, "Mix is missing 'id' field"
            assert "title" in first_mix, "Mix is missing 'title' field"
            assert "color1" in first_mix, "Mix is missing 'color1' field"
            assert "color2" in first_mix, "Mix is missing 'color2' field"
            assert "color3" in first_mix, "Mix is missing 'color3' field"

    def test_get_mix_by_id(self, auth_headers, mix_id):
        mix_url = f"{BASE_URL}/mix/{mix_id}"

        response = requests.get(mix_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get mix by ID: {response.status_code}, {response.text}"

        mix_data = response.json()
        assert mix_data["id"] == mix_id, "Mix ID doesn't match"
        assert "title" in mix_data, "Mix is missing 'title' field"
        assert "color1" in mix_data, "Mix is missing 'color1' field"
        assert "color2" in mix_data, "Mix is missing 'color2' field"
        assert "color3" in mix_data, "Mix is missing 'color3' field"

    def test_get_nonexistent_mix(self, auth_headers):
        
        nonexistent_id = str(uuid.uuid4())
        mix_url = f"{BASE_URL}/mix/{nonexistent_id}"

        response = requests.get(mix_url, headers=auth_headers)

        assert response.status_code == 404, f"Expected 404 for nonexistent mix, got {response.status_code}"

    def test_get_mix_items(self, auth_headers, mix_id):
        items_url = f"{BASE_URL}/mix/{mix_id}/items"

        response = requests.get(items_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get mix items: {response.status_code}, {response.text}"

        items = response.json()
        assert isinstance(items, list), "Mix items response should be a list"

        
        if items:
            first_item = items[0]
            assert "id" in first_item, "Film item is missing 'id' field"
            assert "title" in first_item, "Film item is missing 'title' field"
            assert "description" in first_item, "Film item is missing 'description' field"

    def test_list_mixes_no_auth(self):
        mixes_url = f"{BASE_URL}/mix"

        response = requests.get(mixes_url)

        
        assert response.status_code in [200, 401, 403], f"Unexpected status code: {response.status_code}"

        if response.status_code == 200:
            mixes = response.json()
            assert isinstance(mixes, list), "Mixes response should be a list"

    def test_get_mix_items_no_auth(self, mix_id):
        items_url = f"{BASE_URL}/mix/{mix_id}/items"

        response = requests.get(items_url)

        
        assert response.status_code in [200, 401, 403], f"Unexpected status code: {response.status_code}"

        if response.status_code == 200:
            items = response.json()
            assert isinstance(items, list), "Mix items response should be a list"

    def test_mix_response_structure_complete(self, auth_headers, mix_id):
        mix_url = f"{BASE_URL}/mix/{mix_id}"

        response = requests.get(mix_url, headers=auth_headers)

        assert response.status_code == 200, f"Failed to get mix: {response.status_code}, {response.text}"

        mix_data = response.json()

        required_fields = ["id", "title", "color1", "color2", "color3"]
        for field in required_fields:
            assert field in mix_data, f"Mix is missing required field '{field}'"
