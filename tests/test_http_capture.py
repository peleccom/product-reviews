"""Tests for HTTP capture and replay utilities."""

import pytest
import requests
import responses

from product_reviews.providers.testing.http_capture import (
    capture_http_requests,
    register_mock_responses,
)


class TestCaptureHttpRequests:
    """Tests for capture_http_requests context manager."""

    @responses.activate
    def test_capture_get_request(self):
        """Test capturing GET requests."""
        responses.add(responses.GET, "https://example.com/test", body="test response")

        with capture_http_requests() as captured_data:
            response = requests.get("https://example.com/test", timeout=5)
            assert response.text == "test response"

        assert len(captured_data) == 1
        assert captured_data[0]["method"] == "GET"
        assert captured_data[0]["url"] == "https://example.com/test"
        assert captured_data[0]["status_code"] == 200
        assert captured_data[0]["text"] == "test response"

    @responses.activate
    def test_capture_post_request(self):
        """Test capturing POST requests."""
        responses.add(responses.POST, "https://example.com/test", body="post response")

        with capture_http_requests() as captured_data:
            response = requests.post("https://example.com/test", data={"key": "value"}, timeout=5)
            assert response.text == "post response"

        assert len(captured_data) == 1
        assert captured_data[0]["method"] == "POST"
        assert captured_data[0]["url"] == "https://example.com/test"
        assert captured_data[0]["status_code"] == 200

    @responses.activate
    def test_capture_multiple_requests(self):
        """Test capturing multiple requests."""
        responses.add(responses.GET, "https://example.com/test1", body="response 1")
        responses.add(responses.GET, "https://example.com/test2", body="response 2")

        with capture_http_requests() as captured_data:
            requests.get("https://example.com/test1", timeout=5)
            requests.get("https://example.com/test2", timeout=5)

        assert len(captured_data) == 2
        assert captured_data[0]["url"] == "https://example.com/test1"
        assert captured_data[1]["url"] == "https://example.com/test2"

    @responses.activate
    def test_capture_request_headers(self):
        """Test that request headers are captured."""
        responses.add(
            responses.GET,
            "https://example.com/test",
            body="ok",
            headers={"X-Custom": "value"},
        )

        with capture_http_requests() as captured_data:
            requests.get("https://example.com/test", headers={"X-Custom": "value"}, timeout=5)

        assert len(captured_data) == 1
        assert "X-Custom" in captured_data[0]["headers"]

    def test_capture_restores_original_functions(self):
        """Test that original requests functions are restored after context."""
        original_get = requests.get
        original_post = requests.post

        with capture_http_requests():
            pass

        assert requests.get is original_get
        assert requests.post is original_post

    def test_capture_restores_on_exception(self):
        """Test that original functions are restored even when exception occurs."""
        original_get = requests.get
        original_post = requests.post
        err = TestCaptureError()

        with pytest.raises(TestCaptureError), capture_http_requests():
            raise err

        assert requests.get is original_get
        assert requests.post is original_post


class TestCaptureError(Exception):
    """Test exception for testing."""

    pass

    def test_capture_empty_list_when_no_requests(self):
        """Test that captured_data is empty list when no requests made."""
        with capture_http_requests() as captured_data:
            pass

        assert captured_data == []

    @responses.activate
    def test_capture_with_status_code(self):
        """Test that status codes are captured correctly."""
        responses.add(responses.GET, "https://example.com/notfound", status=404)

        with capture_http_requests() as captured_data:
            response = requests.get("https://example.com/notfound", timeout=5)
            assert response.status_code == 404

        assert captured_data[0]["status_code"] == 404


class TestRegisterMockResponses:
    """Tests for register_mock_responses function."""

    def test_register_get_mock_response(self):
        """Test registering mock for GET request."""
        captured_data = [
            {
                "method": "GET",
                "url": "https://example.com/test",
                "status_code": 200,
                "text": "test response",
                "headers": {"Content-Type": "text/plain"},
            }
        ]

        with responses.RequestsMock() as rsps:
            register_mock_responses(rsps, captured_data)

            response = requests.get("https://example.com/test", timeout=5)
            assert response.status_code == 200
            assert response.text == "test response"

    def test_register_post_mock_response(self):
        """Test registering mock for POST request."""
        captured_data = [
            {
                "method": "POST",
                "url": "https://example.com/test",
                "status_code": 201,
                "text": "created",
                "headers": {"Content-Type": "application/json"},
            }
        ]

        with responses.RequestsMock() as rsps:
            register_mock_responses(rsps, captured_data)

            response = requests.post("https://example.com/test", json={"key": "value"}, timeout=5)
            assert response.status_code == 201
            assert response.text == "created"

    def test_register_multiple_mock_responses(self):
        """Test registering multiple mock responses."""
        captured_data = [
            {
                "method": "GET",
                "url": "https://example.com/test1",
                "status_code": 200,
                "text": "response 1",
                "headers": {},
            },
            {
                "method": "GET",
                "url": "https://example.com/test2",
                "status_code": 200,
                "text": "response 2",
                "headers": {},
            },
        ]

        with responses.RequestsMock() as rsps:
            register_mock_responses(rsps, captured_data)

            response1 = requests.get("https://example.com/test1", timeout=5)
            response2 = requests.get("https://example.com/test2", timeout=5)

            assert response1.text == "response 1"
            assert response2.text == "response 2"

    def test_register_with_missing_method_defaults_to_get(self):
        """Test that missing method defaults to GET."""
        captured_data = [
            {
                "url": "https://example.com/test",
                "status_code": 200,
                "text": "test",
                "headers": {},
            }
        ]

        with responses.RequestsMock() as rsps:
            register_mock_responses(rsps, captured_data)

            response = requests.get("https://example.com/test", timeout=5)
            assert response.status_code == 200

    def test_register_with_different_status_codes(self):
        """Test registering mock responses with various status codes."""
        captured_data = [
            {
                "method": "GET",
                "url": "https://example.com/ok",
                "status_code": 200,
                "text": "OK",
                "headers": {},
            },
            {
                "method": "GET",
                "url": "https://example.com/notfound",
                "status_code": 404,
                "text": "Not Found",
                "headers": {},
            },
        ]

        with responses.RequestsMock() as rsps:
            register_mock_responses(rsps, captured_data)

            assert requests.get("https://example.com/ok", timeout=5).status_code == 200
            assert requests.get("https://example.com/notfound", timeout=5).status_code == 404

    def test_register_with_empty_text(self):
        """Test registering mock response with empty body."""
        captured_data = [
            {
                "method": "GET",
                "url": "https://example.com/empty",
                "status_code": 204,
                "text": "",
                "headers": {},
            }
        ]

        with responses.RequestsMock() as rsps:
            register_mock_responses(rsps, captured_data)

            response = requests.get("https://example.com/empty", timeout=5)
            assert response.status_code == 204
            assert response.text == ""

    def test_register_with_no_captured_data(self):
        """Test registering with empty captured data list."""
        with responses.RequestsMock() as rsps:
            register_mock_responses(rsps, [])
            with pytest.raises(requests.exceptions.ConnectionError):
                requests.get("https://example.com/test", timeout=5)
