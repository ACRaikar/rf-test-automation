import pytest
import requests
from api_utils import report_result_core, get_post_titles_by_user_core

def fake_post_timeout(url, json, timeout):
    raise requests.exceptions.Timeout("simulated timeout")

def test_report_result_core_handles_timeout():
    result = report_result_core(fake_post_timeout, "https://test.com", "2024-06-01 12:00:00", 3.3, "FAIL")
    assert result == False


class FakeResponse:
    def __init__(self,json_data):
        self._json_data = json_data
    def raise_for_status(self):
        pass
    def json(self):
        return self._json_data

def fake_post_success(url, json, timeout):
    return FakeResponse({"json":json})

def test_report_result_core_success():
    payload = {"timestamp": "2024-06-01 12:00:00", "voltage": 3.3, "status": "FAIL"}
    result = report_result_core(fake_post_success, "https://jsonplaceholder.typicode.com/posts", payload["timestamp"], payload["voltage"], payload["status"])
    assert result == payload

class FakePostsResponse:
    def __init__(self, posts):
        self._posts = posts
    def raise_for_status(self):
        pass
    def json(self):
        return self._posts

def fake_get_success(url, timeout=10):
    return FakePostsResponse([
        {"userId": 1, "id": 1, "title": "first post"},
        {"userId": 1, "id": 2, "title": "second post"},
    ])

def fake_get_failure(url, timeout=10):
    raise requests.exceptions.ConnectionError("simulated connection failure")

def test_get_post_titles_by_user_core_success():
    result = get_post_titles_by_user_core(fake_get_success,1)
    assert result == ["first post", "second post"]

def test_get_post_titles_by_user_core_failure():
    result = get_post_titles_by_user_core(fake_get_failure,1)
    assert result is None