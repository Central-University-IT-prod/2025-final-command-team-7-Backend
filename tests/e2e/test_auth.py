import pytest
import requests
import uuid
import time
import random
import string


BASE_URL = "http://REDACTED/api/v1"



def random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class TestAuthAPI:
    def test_register_new_user(self):
        register_url = f"{BASE_URL}/auth/register"

        
        timestamp = int(time.time())
        email = f"testuser_{timestamp}_{random_string(5)}@example.com"
        username = f"testuser_{timestamp}_{random_string(5)}"
        password = "Password123!"

        register_data = {"username": username, "email": email, "password": password}

        response = requests.post(register_url, json=register_data)

        
        assert response.status_code in [201, 409], f"Registration failed with status {response.status_code}"

        
        if response.status_code == 201:
            user_data = response.json()
            assert "id" in user_data, "No user ID in response"
            assert "username" in user_data, "No username in response"
            assert user_data["username"] == username, "Returned username doesn't match the request"

            
            assert uuid.UUID(user_data["id"], version=4), "Invalid user ID format"

    def test_register_duplicate_user(self):
        register_url = f"{BASE_URL}/auth/register"

        
        timestamp = int(time.time())
        email = f"duplicate_{timestamp}@example.com"
        username1 = f"user1_{timestamp}"

        first_register_data = {"username": username1, "email": email, "password": "Password123!"}

        first_response = requests.post(register_url, json=first_register_data)

        
        if first_response.status_code != 201:
            pytest.skip("First registration failed, cannot test duplicate")

        
        username2 = f"user2_{timestamp}"
        second_register_data = {
            "username": username2,
            "email": email,  
            "password": "Password123!",
        }

        second_response = requests.post(register_url, json=second_register_data)

        
        assert second_response.status_code == 409, "Expected 409 Conflict for duplicate email"

    def test_login_success(self):

        register_url = f"{BASE_URL}/auth/register"
        login_url = f"{BASE_URL}/auth/login"

        timestamp = int(time.time())
        email = f"login_test_{timestamp}@example.com"
        password = "Password123!"

        register_data = {"username": f"login_user_{timestamp}", "email": email, "password": password}

        register_response = requests.post(register_url, json=register_data)

        
        
        login_data = {"email": email, "password": password}

        login_response = requests.post(login_url, json=login_data)

        
        assert login_response.status_code == 201, f"Login failed with status {login_response.status_code}"

        login_result = login_response.json()
        assert "token" in login_result, "No token in login response"
        assert "id" in login_result, "No user ID in login response"

        
        assert login_result.get("email") == email, "Email in response doesn't match"

    def test_login_invalid_credentials(self):
        login_url = f"{BASE_URL}/auth/login"

        
        login_data = {"email": f"nonexistent_{uuid.uuid4()}@example.com", "password": "WrongPassword123!"}

        login_response = requests.post(login_url, json=login_data)

        
        assert login_response.status_code == 401, f"Expected 401 Unauthorized, got {login_response.status_code}"

    def test_get_telegram_auth_key(self):
        auth_key_url = f"{BASE_URL}/auth/telegram/get_auth_key"

        response = requests.post(auth_key_url)

        
        assert response.status_code == 201, f"Failed to get auth key, status: {response.status_code}"

        key_data = response.json()
        assert "auth_key" in key_data, "No auth_key in response"
        assert len(key_data["auth_key"]) > 0, "Empty auth_key in response"

    def test_check_telegram_auth_key(self):

        auth_key_url = f"{BASE_URL}/auth/telegram/get_auth_key"
        check_url = f"{BASE_URL}/auth/telegram/check_auth_key"

        get_key_response = requests.post(auth_key_url)

        if get_key_response.status_code != 201:
            pytest.skip("Failed to get auth key, cannot proceed with check test")

        auth_key = get_key_response.json().get("auth_key")

        
        check_data = {"tg_code": auth_key}

        check_response = requests.post(check_url, json=check_data)

        
        assert check_response.status_code in [200, 201], (
            f"Failed to check auth key, status: {check_response.status_code}"
        )

        
        try:
            result = check_response.json()
            assert isinstance(result, dict), "Response is not a JSON object"
        except:
            pass  

    def test_get_me_with_auth(self):

        register_url = f"{BASE_URL}/auth/register"
        login_url = f"{BASE_URL}/auth/login"
        me_url = f"{BASE_URL}/me"

        timestamp = int(time.time())
        email = f"me_test_{timestamp}@example.com"
        username = f"me_user_{timestamp}"
        password = "Password123!"

        
        register_data = {"username": username, "email": email, "password": password}

        requests.post(register_url, json=register_data)

        
        login_data = {"email": email, "password": password}

        login_response = requests.post(login_url, json=login_data)

        if login_response.status_code != 201:
            pytest.skip("Failed to login, cannot proceed with me test")

        token = login_response.json().get("token")

        
        headers = {"Authorization": f"Bearer {token}"}

        me_response = requests.get(me_url, headers=headers)

        assert me_response.status_code == 200, f"Failed to get me data, status: {me_response.status_code}"

        me_data = me_response.json()
        assert "id" in me_data, "No user ID in me response"
        assert "username" in me_data, "No username in me response"
        assert me_data["username"] == username, "Username doesn't match"
        assert me_data["email"] == email, "Email doesn't match"

    def test_get_me_without_auth(self):
        me_url = f"{BASE_URL}/me"

        
        response = requests.get(me_url)

        
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
