"""HTTP request capture and replay utilities for provider testing."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import requests
import responses


@contextmanager
def capture_http_requests() -> Generator[list[dict[str, Any]], None, None]:
    """Context manager that captures HTTP requests made via requests library.

    Patches requests.get and requests.post to capture all request/response data.
    Automatically restores original functions when done.

    Yields:
        List that will be populated with captured request/response data.

    Example:
        with capture_http_requests() as captured_data:
            response = requests.get("https://example.com")
            # captured_data now contains the request/response info
    """
    captured_data: list[dict[str, Any]] = []

    original_get = requests.get
    original_post = requests.post

    def capturing_get(url: str, **kwargs: Any) -> Any:
        response = original_get(url, **kwargs)
        headers = dict(response.headers)
        # Remove encoding headers that can cause issues during replay
        for key in ["Content-Encoding", "Transfer-Encoding"]:
            headers.pop(key, None)
        captured_data.append({
            "method": "GET",
            "url": url,
            "headers": headers,
            "status_code": response.status_code,
            "text": response.text,
        })
        return response

    def capturing_post(url: str, **kwargs: Any) -> Any:
        response = original_post(url, **kwargs)
        headers = dict(response.headers)
        # Remove encoding headers that can cause issues during replay
        for key in ["Content-Encoding", "Transfer-Encoding"]:
            headers.pop(key, None)
        captured_data.append({
            "method": "POST",
            "url": url,
            "headers": headers,
            "status_code": response.status_code,
            "text": response.text,
            "json": kwargs.get("json"),
        })
        return response

    # Patch the functions
    requests.get = capturing_get  # type: ignore[assignment]
    requests.post = capturing_post  # type: ignore[assignment]

    try:
        yield captured_data
    finally:
        # Always restore original functions
        requests.get = original_get
        requests.post = original_post


def register_mock_responses(rsps: responses.RequestsMock, captured_data: list[dict[str, Any]]) -> None:
    """Register captured HTTP data as mock responses.

    Args:
        rsps: The responses mock instance to register with.
        captured_data: List of captured request/response data dicts.
    """
    for captured in captured_data:
        method = captured.get("method", "GET")
        mock_url = captured.get("url")
        status_code = captured.get("status_code", 200)
        body = captured.get("text", "")

        if method == "POST":
            rsps.add(responses.POST, mock_url, body=body, status=status_code)
        else:
            rsps.add(responses.GET, mock_url, body=body, status=status_code)
