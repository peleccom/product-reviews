"""Testing utilities for product-reviews providers.

This module provides shared testing infrastructure for both CLI commands
and pytest plugin, including mock storage, HTTP capture, and validation utilities.
"""

from product_reviews.providers.testing.http_capture import (
    capture_http_requests,
    register_mock_responses,
)
from product_reviews.providers.testing.mock_storage import (
    JsonMockStorage,
    MockStorage,
    YamlMockStorage,
    get_mock_storage,
)
from product_reviews.providers.testing.mock_utils import (
    MockFileNotFoundError,
    clear_provider_mocks,
    get_mock_file,
    get_mocks_dir,
    get_provider_module_path,
    load_mock_data,
    load_mock_response,
    save_mock_response,
    validate_reviews,
)

__all__ = [
    "JsonMockStorage",
    "MockFileNotFoundError",
    "MockStorage",
    "YamlMockStorage",
    "capture_http_requests",
    "clear_provider_mocks",
    "get_mock_file",
    "get_mock_storage",
    "get_mocks_dir",
    "get_provider_module_path",
    "load_mock_data",
    "load_mock_response",
    "register_mock_responses",
    "save_mock_response",
    "validate_reviews",
]
