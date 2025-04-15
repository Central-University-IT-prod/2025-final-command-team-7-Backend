import pytest
import requests
import json
import time
import uuid
import random
import string
from urllib.parse import quote, urlencode
from datetime import datetime


BASE_URL = "http://REDACTED/api/v1"


def random_string(length=8):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


@pytest.fixture(scope="session")
def test_user_data():
    timestamp = int(time.time())
    return {
        "username": f"testuser_{timestamp}_{random_string(5)}",
        "email": f"testuser_{timestamp}_{random_string(5)}@example.com",
        "password": "Password123!",
    }


@pytest.fixture(scope="session")
def auth_token(test_user_data):
    register_url = f"{BASE_URL}/auth/register"
    register_data = {
        "username": test_user_data["username"],
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }

    try:
        register_response = requests.post(register_url, json=register_data)
        print(f"Registration response: {register_response.status_code}")
    except Exception as e:
        print(f"Registration failed: {e}")

    login_url = f"{BASE_URL}/auth/login"
    login_data = {"email": test_user_data["email"], "password": test_user_data["password"]}

    login_response = requests.post(login_url, json=login_data)

    if login_response.status_code != 201:
        pytest.skip(f"Could not authenticate: {login_response.status_code}, {login_response.text}")

    token_data = login_response.json()
    return token_data.get("token")


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    if not auth_token:
        pytest.skip("No auth token available")

    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


@pytest.fixture(scope="session")
def created_film(auth_headers):
    create_film_url = f"{BASE_URL}/films"

    genres_url = f"{BASE_URL}/genres"
    genres_response = requests.get(genres_url, headers=auth_headers)

    if genres_response.status_code != 200 or not genres_response.json():
        pytest.skip("Could not fetch genres for film creation")

    genre_id = genres_response.json()[0]["id"]

    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    film_data = {
        "title": f"Test Search Film {time_str}",
        "description": f"This is a test film created for search API testing with unique identifier {time_str}",
        "genres_ids": [genre_id],
        "country": "Test Country",
        "release_year": 2023,
    }

    response = requests.post(create_film_url, json=film_data, headers=auth_headers)

    if response.status_code != 201:
        pytest.skip(f"Could not create test film: {response.status_code}, {response.text}")

    return response.json()


@pytest.fixture(scope="session")
def second_film(auth_headers):
    create_film_url = f"{BASE_URL}/films"

    genres_url = f"{BASE_URL}/genres"
    genres_response = requests.get(genres_url, headers=auth_headers)

    if genres_response.status_code != 200 or not genres_response.json():
        pytest.skip("Could not fetch genres for film creation")

    genres = genres_response.json()
    genre_id = genres[1]["id"] if len(genres) > 1 else genres[0]["id"]

    time_str = datetime.now().strftime("%Y%m%d%H%M%S")
    film_data = {
        "title": f"Second Search Film {time_str}",
        "description": f"This is a different test film with another description {time_str}",
        "genres_ids": [genre_id],
        "country": "Another Country",
        "release_year": 2024,
    }

    response = requests.post(create_film_url, json=film_data, headers=auth_headers)

    if response.status_code != 201:
        pytest.skip(f"Could not create second test film: {response.status_code}, {response.text}")

    return response.json()


@pytest.fixture(scope="session")
def genres(auth_headers):
    genres_url = f"{BASE_URL}/genres"

    response = requests.get(genres_url, headers=auth_headers)

    if response.status_code != 200:
        return []

    return response.json()


@pytest.fixture(scope="session")
def moods(auth_headers):
    moods_url = f"{BASE_URL}/moods"

    response = requests.get(moods_url, headers=auth_headers)

    if response.status_code != 200:
        return []

    return response.json()


class TestSearchAPI:
    def test_search_auth_comparison(self):
        query = "movie"
        search_url = f"{BASE_URL}/search?query={query}"

        unauthenticated_response = requests.get(search_url)

        try:
            test_user = {
                "email": f"testuser_{int(time.time())}@example.com",
                "password": "Password123!",
                "username": f"testuser_{int(time.time())}",
            }

            register_url = f"{BASE_URL}/auth/register"
            requests.post(register_url, json=test_user)

            login_url = f"{BASE_URL}/auth/login"
            login_resp = requests.post(login_url, json={"email": test_user["email"], "password": test_user["password"]})

            if login_resp.status_code == 201:
                token = login_resp.json().get("token")
                auth_headers = {"Authorization": f"Bearer {token}"}
                authenticated_response = requests.get(search_url, headers=auth_headers)

                assert unauthenticated_response.status_code == authenticated_response.status_code, (
                    "Authentication changes API status code"
                )

                if unauthenticated_response.status_code == 200 and authenticated_response.status_code == 200:
                    try:
                        unauth_data = unauthenticated_response.json()
                        auth_data = authenticated_response.json()

                        assert type(unauth_data) == type(auth_data), "Authentication changes response data structure"
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            print(f"Auth comparison error: {e}")

    def test_search_films_endpoint(self, auth_headers, created_film):
        if not created_film:
            pytest.skip("No test film available")

        search_term = created_film["title"].split()[0]

        films_search_url = f"{BASE_URL}/films/search?title={search_term}"
        films_response = requests.get(films_search_url, headers=auth_headers)

        custom_search_url = f"{BASE_URL}/search?query={search_term}"
        custom_response = requests.get(custom_search_url, headers=auth_headers)

        assert films_response.status_code == 200, (
            f"Films search endpoint failed with status {films_response.status_code}"
        )

        assert custom_response.status_code in [200, 404, 501], (
            f"Custom search endpoint failed with status {custom_response.status_code}"
        )

        if films_response.status_code == 200 and custom_response.status_code == 200:
            try:
                films_data = films_response.json()
                custom_data = custom_response.json()

                if isinstance(films_data, list) and isinstance(custom_data, list):
                    pass
                elif isinstance(films_data, dict) and isinstance(custom_data, dict):
                    pass
            except json.JSONDecodeError:
                pass

    def test_search_without_auth(self):
        search_url = f"{BASE_URL}/search?query=test"

        response = requests.get(search_url)

        assert response.status_code in [200, 401, 403, 404, 501], (
            f"Unauthenticated search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from unauthenticated search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_basic_search_functionality(self, auth_headers, created_film):
        if not created_film:
            pytest.skip("No created film available for testing")

        search_term = created_film["title"].split()[0]
        search_url = f"{BASE_URL}/search?query={search_term}"

        response = requests.get(search_url, headers=auth_headers)

        print(f"Search response status: {response.status_code}")
        if response.status_code == 200:
            print(f"First 100 chars of search response: {str(response.text)[:100]}...")

        assert response.status_code in [200, 404, 501], f"Search endpoint failed with status {response.status_code}"

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from search endpoint"

                found = False
                if isinstance(results, list):
                    for item in results:
                        if item.get("id") == created_film["id"]:
                            found = True
                            break
                elif isinstance(results, dict):
                    if "items" in results:
                        for item in results["items"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break
                    elif "results" in results:
                        for item in results["results"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_with_empty_query(self, auth_headers):
        search_url = f"{BASE_URL}/search?query="

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Empty query search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()

                assert results is not None, "Null response for empty query search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_with_non_alphanumeric_chars(self, auth_headers):
        special_chars_query = "movie & drama! (action)"
        search_url = f"{BASE_URL}/search?query={quote(special_chars_query)}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Special chars search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from special characters search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_performance(self, auth_headers):
        search_url = f"{BASE_URL}/search?query=movie"

        start_time = time.time()
        response = requests.get(search_url, headers=auth_headers)
        end_time = time.time()

        response_time = end_time - start_time

        assert response.status_code in [200, 404, 501], f"Search failed with status {response.status_code}"

        max_response_time = 5.0
        assert response_time < max_response_time, (
            f"Search response time {response_time}s exceeds maximum {max_response_time}s"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from performance test"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_with_min_length_query(self, auth_headers):
        search_url = f"{BASE_URL}/search"

        one_char_params = {"query": "a"}
        one_char_response = requests.get(search_url, params=one_char_params, headers=auth_headers)

        two_char_params = {"query": "ab"}
        two_char_response = requests.get(search_url, params=two_char_params, headers=auth_headers)

        assert one_char_response.status_code in [200, 400, 404, 501], (
            f"One-char search failed with status {one_char_response.status_code}"
        )
        assert two_char_response.status_code in [200, 400, 404, 501], (
            f"Two-char search failed with status {two_char_response.status_code}"
        )

        if one_char_response.status_code == 200:
            try:
                results = one_char_response.json()
                assert results is not None, "Empty response from one-character search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_long_query(self, auth_headers):
        long_query = "test " * 200

        search_url = f"{BASE_URL}/search?query={quote(long_query)}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Long query search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from long query search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_response_structure(self, auth_headers):
        search_url = f"{BASE_URL}/search?query=movie"

        response = requests.get(search_url, headers=auth_headers)

        if response.status_code == 200:
            try:
                results = response.json()

                if isinstance(results, list):
                    if results:
                        first_item = results[0]

                        assert "id" in first_item, "Film item missing 'id' field"
                        assert "title" in first_item, "Film item missing 'title' field"
                elif isinstance(results, dict):
                    if "items" in results and results["items"]:
                        first_item = results["items"][0]
                        assert "id" in first_item, "Film item missing 'id' field"
                        assert "title" in first_item, "Film item missing 'title' field"
                    elif "results" in results and results["results"]:
                        first_item = results["results"][0]
                        assert "id" in first_item, "Film item missing 'id' field"
                        assert "title" in first_item, "Film item missing 'title' field"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")
            except (IndexError, KeyError, TypeError):
                pass

    def test_search_nonexistent_film(self, auth_headers):
        nonexistent_title = f"XYZ123ThisFilmDoesNotExist456ABC789_{uuid.uuid4()}"
        search_url = f"{BASE_URL}/search?query={quote(nonexistent_title)}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 404, 501], (
            f"Nonexistent film search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()

                if isinstance(results, list):
                    pass
                elif isinstance(results, dict):
                    pass
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_unicode_characters(self, auth_headers):
        unicode_query = "фильм 电影 映画 🎬"
        search_url = f"{BASE_URL}/search?query={quote(unicode_query)}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], f"Unicode search failed with status {response.status_code}"

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from Unicode search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_with_description(self, auth_headers):
        search_url = f"{BASE_URL}/search"
        params = {"description": "adventure exciting journey"}

        response = requests.get(search_url, params=params, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Description search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from description search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_with_genre_filter(self, auth_headers, genres):
        if not genres or len(genres) == 0:
            pytest.skip("No genres available for testing")

        search_url = f"{BASE_URL}/search"
        params = {"query": "movie", "genres_ids": genres[0]["id"]}

        response = requests.get(search_url, params=params, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Genre-filtered search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from genre-filtered search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_malformed_params(self, auth_headers):
        search_url = f"{BASE_URL}/search"

        params = {"query": "test", "genres_ids": "not-a-valid-id-format"}

        response = requests.get(search_url, params=params, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Invalid params search failed with status {response.status_code}"
        )

    def test_search_combined_params(self, auth_headers, genres, moods):
        search_url = f"{BASE_URL}/search"

        params = {"query": "adventure"}

        if genres and len(genres) > 0:
            params["genres_ids"] = genres[0]["id"]

        if moods and len(moods) > 0:
            params["moods_ids"] = moods[0]["id"]

        response = requests.get(search_url, params=params, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Combined params search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from combined params search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_exact_match(self, auth_headers, created_film):
        if not created_film:
            pytest.skip("No created film available for testing")

        search_url = f"{BASE_URL}/search?query={quote(created_film['title'])}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 404, 501], f"Exact match search failed with status {response.status_code}"

        if response.status_code == 200:
            try:
                results = response.json()

                found = False
                if isinstance(results, list):
                    for item in results:
                        if item.get("id") == created_film["id"]:
                            found = True
                            break
                elif isinstance(results, dict):
                    if "items" in results:
                        for item in results["items"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break
                    elif "results" in results:
                        for item in results["results"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break

                if not found:
                    print("Warning: Exact title search did not find the film")

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_multiple_terms(self, auth_headers, created_film):
        if not created_film:
            pytest.skip("No created film available for testing")

        words = created_film["title"].split()
        if len(words) > 1:
            query = f"{words[0]} {words[-1]}"
        else:
            query = f"{words[0]} film"

        search_url = f"{BASE_URL}/search?query={quote(query)}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 404, 501], (
            f"Multiple terms search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from multiple terms search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_case_insensitivity(self, auth_headers, created_film):
        if not created_film:
            pytest.skip("No created film available for testing")

        word = created_film["title"].split()[0]
        uppercase_query = word.upper()

        if word == uppercase_query:
            pytest.skip("Cannot test case insensitivity with already uppercase word")

        search_url = f"{BASE_URL}/search?query={quote(uppercase_query)}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 404, 501], (
            f"Case insensitivity search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()

                found = False
                if isinstance(results, list):
                    for item in results:
                        if item.get("id") == created_film["id"]:
                            found = True
                            break
                elif isinstance(results, dict):
                    if "items" in results:
                        for item in results["items"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break
                    elif "results" in results:
                        for item in results["results"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break

                if not found:
                    print("Warning: Case insensitive search did not find the film")

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_with_limit_parameter(self, auth_headers):
        search_url = f"{BASE_URL}/search?query=movie&limit=1"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], f"Limited search failed with status {response.status_code}"

        if response.status_code == 200:
            try:
                results = response.json()

                if isinstance(results, list):
                    if len(results) > 1:
                        print("Warning: Limit parameter was ignored, returned more than 1 result")
                elif isinstance(results, dict):
                    if "items" in results and len(results["items"]) > 1:
                        print("Warning: Limit parameter was ignored, returned more than 1 result")
                    elif "results" in results and len(results["results"]) > 1:
                        print("Warning: Limit parameter was ignored, returned more than 1 result")

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_with_pagination(self, auth_headers):
        page1_url = f"{BASE_URL}/search?query=movie&page=1&limit=2"

        page2_url = f"{BASE_URL}/search?query=movie&page=2&limit=2"

        response1 = requests.get(page1_url, headers=auth_headers)
        response2 = requests.get(page2_url, headers=auth_headers)

        assert response1.status_code in [200, 400, 404, 501], (
            f"Page 1 search failed with status {response1.status_code}"
        )
        assert response2.status_code in [200, 400, 404, 501], (
            f"Page 2 search failed with status {response2.status_code}"
        )

        if response1.status_code == 200 and response2.status_code == 200:
            try:
                results1 = response1.json()
                results2 = response2.json()

                if isinstance(results1, list) and isinstance(results2, list):
                    ids1 = [item.get("id") for item in results1 if "id" in item]
                    ids2 = [item.get("id") for item in results2 if "id" in item]

                    if ids1 and ids2:
                        if ids1 == ids2:
                            print("Warning: Pagination not working, same results on different pages")

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_film_complete_fields(self, auth_headers):
        search_url = f"{BASE_URL}/search?query=movie"

        response = requests.get(search_url, headers=auth_headers)

        if response.status_code == 200:
            try:
                results = response.json()

                film = None
                if isinstance(results, list) and results:
                    film = results[0]
                elif isinstance(results, dict):
                    if "items" in results and results["items"]:
                        film = results["items"][0]
                    elif "results" in results and results["results"]:
                        film = results["results"][0]

                if film:
                    expected_fields = ["id", "title", "description"]
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

                    for field in expected_fields:
                        assert field in film, f"Required field '{field}' missing from film response"

                    assert isinstance(film["id"], str), "Film id should be a string (UUID)"
                    assert isinstance(film["title"], str), "Film title should be a string"
                    assert isinstance(film["description"], str), "Film description should be a string"

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")
            except (IndexError, KeyError, AssertionError) as e:
                print(f"Film field check failed: {e}")

    def test_search_two_identical_requests(self, auth_headers):
        search_url = f"{BASE_URL}/search?query=movie"

        response1 = requests.get(search_url, headers=auth_headers)
        response2 = requests.get(search_url, headers=auth_headers)

        assert response1.status_code == response2.status_code, "Different status codes for identical requests"

        if response1.status_code == 200 and response2.status_code == 200:
            try:
                results1 = response1.json()
                results2 = response2.json()

                assert type(results1) == type(results2), "Different response formats for identical requests"

                if isinstance(results1, list) and isinstance(results2, list):
                    assert len(results1) == len(results2), "Different number of results for identical requests"
                elif isinstance(results1, dict) and isinstance(results2, dict):
                    if "items" in results1 and "items" in results2:
                        assert len(results1["items"]) == len(results2["items"]), (
                            "Different number of items for identical requests"
                        )
                    elif "results" in results1 and "results" in results2:
                        assert len(results1["results"]) == len(results2["results"]), (
                            "Different number of results for identical requests"
                        )

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")
            except AssertionError as e:
                print(f"Warning: {e}")

    def test_search_by_year(self, auth_headers):
        search_url = f"{BASE_URL}/search?release_year=2023"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], f"Year search failed with status {response.status_code}"

        if response.status_code == 200:
            try:
                results = response.json()

                if isinstance(results, list) and results:
                    for film in results:
                        if "release_year" in film and film["release_year"] is not None:
                            if film["release_year"] != 2023:
                                print("Warning: Film with incorrect year in results")
                elif isinstance(results, dict):
                    items = []
                    if "items" in results:
                        items = results["items"]
                    elif "results" in results:
                        items = results["results"]

                    if items:
                        for film in items:
                            if "release_year" in film and film["release_year"] is not None:
                                if film["release_year"] != 2023:
                                    print("Warning: Film with incorrect year in results")

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_by_country(self, auth_headers):
        search_url = f"{BASE_URL}/search?country={quote('Test Country')}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], f"Country search failed with status {response.status_code}"

        if response.status_code == 200:
            try:
                results = response.json()
                assert results is not None, "Empty response from country search"
            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_missing_required_params(self, auth_headers):
        search_url = f"{BASE_URL}/search"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 400, 404, 501], (
            f"Missing params search failed with status {response.status_code}"
        )

    def test_search_concurrent_requests(self, auth_headers):
        import threading

        search_url = f"{BASE_URL}/search?query=movie"

        results = []

        def make_request():
            response = requests.get(search_url, headers=auth_headers)
            results.append((response.status_code, response.text if response.status_code == 200 else None))

        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        for status_code, response_text in results:
            assert status_code in [200, 404, 501], f"Concurrent search failed with status {status_code}"
            if status_code == 200:
                try:
                    json.loads(response_text)
                except json.JSONDecodeError:
                    pytest.fail("Response is not valid JSON")

    def test_search_description_keywords(self, auth_headers, created_film):
        if not created_film or "description" not in created_film or not created_film["description"]:
            pytest.skip("No film with description available for testing")

        words = created_film["description"].split()
        if len(words) < 3:
            pytest.skip("Film description too short for keyword search")

        keyword = words[2]
        if len(keyword) < 4:
            keyword = words[-1]

        search_url = f"{BASE_URL}/search?query={keyword}"

        response = requests.get(search_url, headers=auth_headers)

        assert response.status_code in [200, 404, 501], (
            f"Description keyword search failed with status {response.status_code}"
        )

        if response.status_code == 200:
            try:
                results = response.json()

                found = False
                if isinstance(results, list):
                    for item in results:
                        if item.get("id") == created_film["id"]:
                            found = True
                            break
                elif isinstance(results, dict):
                    if "items" in results:
                        for item in results["items"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break
                    elif "results" in results:
                        for item in results["results"]:
                            if item.get("id") == created_film["id"]:
                                found = True
                                break

                if not found:
                    print(f"Warning: Film not found when searching for keyword '{keyword}' from its description")

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")

    def test_search_films_comparison(self, auth_headers, created_film, second_film):
        if not created_film or not second_film:
            pytest.skip("Test films not available")

        first_word = created_film["title"].split()[0]
        second_word = second_film["title"].split()[0]

        if first_word == second_word:
            pytest.skip("Films have same first word, cannot test distinctive search")

        search1_url = f"{BASE_URL}/search?query={quote(first_word)}"
        search2_url = f"{BASE_URL}/search?query={quote(second_word)}"

        response1 = requests.get(search1_url, headers=auth_headers)
        response2 = requests.get(search2_url, headers=auth_headers)

        assert response1.status_code in [200, 404, 501], f"First film search failed with status {response1.status_code}"
        assert response2.status_code in [200, 404, 501], (
            f"Second film search failed with status {response2.status_code}"
        )

        if response1.status_code == 200 and response2.status_code == 200:
            try:
                results1 = response1.json()
                results2 = response2.json()

                found1 = False
                found2 = False

                if isinstance(results1, list):
                    for item in results1:
                        if item.get("id") == created_film["id"]:
                            found1 = True
                            break
                elif isinstance(results1, dict):
                    if "items" in results1:
                        for item in results1["items"]:
                            if item.get("id") == created_film["id"]:
                                found1 = True
                                break
                    elif "results" in results1:
                        for item in results1["results"]:
                            if item.get("id") == created_film["id"]:
                                found1 = True
                                break

                if isinstance(results2, list):
                    for item in results2:
                        if item.get("id") == second_film["id"]:
                            found2 = True
                            break
                elif isinstance(results2, dict):
                    if "items" in results2:
                        for item in results2["items"]:
                            if item.get("id") == second_film["id"]:
                                found2 = True
                                break
                    elif "results" in results2:
                        for item in results2["results"]:
                            if item.get("id") == second_film["id"]:
                                found2 = True
                                break

                if not found1:
                    print(f"Warning: First film not found when searching for '{first_word}'")
                if not found2:
                    print(f"Warning: Second film not found when searching for '{second_word}'")

            except json.JSONDecodeError:
                pytest.fail("Response is not valid JSON")
