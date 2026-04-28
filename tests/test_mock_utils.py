"""Tests for mock_utils module - simplified tests."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.testing.mock_utils import (
    MOCKS_DIR,
    MockFileNotFoundError,
    clear_provider_mocks,
    get_mock_file,
    load_mock_data,
    load_mock_response,
    validate_reviews,
)


class TestProvider(BaseReviewsProvider):
    """Test provider for testing utilities."""

    name = "test_provider"

    def get_reviews(self, url: str) -> list[Review]:
        return []


class TestGetMocksDir:
    """Tests for get_mocks_dir function."""

    def test_mocks_dir_constant(self):
        """Test that MOCKS_DIR constant is 'mocks'."""
        assert MOCKS_DIR == "mocks"


class TestGetMockFile:
    """Tests for get_mock_file function."""

    def test_raises_when_mocks_dir_unknown(self):
        """Test raising MockFileNotFoundError when mocks directory cannot be determined."""
        with patch("product_reviews.providers.testing.mock_utils.get_mocks_dir") as mock:
            mock.return_value = None
            with pytest.raises(MockFileNotFoundError):
                get_mock_file(TestProvider, 0, "valid", 0)

    def test_returns_path_for_valid_provider(self):
        """Test getting mock file path returns correct path structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mocks_dir = Path(tmpdir)
            with patch("product_reviews.providers.testing.mock_utils.get_mocks_dir") as mock:
                mock.return_value = mocks_dir
                result = get_mock_file(TestProvider, 0, "valid", 0)
                assert str(result).startswith(str(mocks_dir))
                assert "test_provider" in str(result)


class TestClearProviderMocks:
    """Tests for clear_provider_mocks function."""

    def test_returns_zero_when_no_mocks_dir(self):
        """Test returning 0 when mocks directory doesn't exist."""
        with patch("product_reviews.providers.testing.mock_utils.get_mocks_dir") as mock:
            mock.return_value = None
            result = clear_provider_mocks(TestProvider)
            assert result == 0


class TestLoadMockData:
    """Tests for load_mock_data function."""

    def test_load_mock_data_function_exists(self):
        """Test that load_mock_data function exists and is callable."""
        assert callable(load_mock_data)

    def test_load_mock_data_raises_on_nonexistent(self):
        """Test load_mock_data raises when mocks directory cannot be determined."""
        with patch("product_reviews.providers.testing.mock_utils.get_mocks_dir") as mock:
            mock.return_value = None
            with pytest.raises(MockFileNotFoundError):
                load_mock_data(TestProvider, 0, "valid")


class TestLoadMockResponse:
    """Tests for load_mock_response function."""

    def test_load_mock_response_function_exists(self):
        """Test that load_mock_response function exists and is callable."""
        assert callable(load_mock_response)

    def test_load_mock_response_raises_on_nonexistent(self):
        """Test load_mock_response raises when mocks directory cannot be determined."""
        with patch("product_reviews.providers.testing.mock_utils.get_mocks_dir") as mock:
            mock.return_value = None
            with pytest.raises(MockFileNotFoundError):
                load_mock_response(TestProvider, 0, "valid")


class TestValidateReviews:
    """Tests for validate_reviews function."""

    def test_validates_valid_reviews(self):
        """Test that valid reviews pass validation."""
        reviews = [
            Review(rating=5.0, text="Great!", created_at=datetime.now()),
            Review(rating=4.0, created_at=datetime.now()),
        ]

        is_valid, error_msg = validate_reviews(reviews)
        assert is_valid is True
        assert error_msg == ""

    def test_returns_false_for_empty_reviews(self):
        """Test that empty reviews list is invalid."""
        is_valid, _ = validate_reviews([])
        assert is_valid is False

    def test_validates_reviews_with_rating(self):
        """Test validation with different rating values."""
        reviews = [Review(rating=5.0, created_at=datetime.now())]
        is_valid, _ = validate_reviews(reviews)
        assert is_valid is True

    def test_validates_reviews_with_all_fields(self):
        """Test validation with all optional fields."""
        reviews = [
            Review(
                rating=4.5,
                text="Excellent",
                pros="Good quality",
                cons="Pricey",
                summary="Great product",
                created_at=datetime.now(),
            )
        ]
        is_valid, _ = validate_reviews(reviews)
        assert is_valid is True
