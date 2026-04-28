"""Tests for mock_storage module."""

import tempfile
from abc import ABC
from pathlib import Path

import pytest

from product_reviews.providers.testing.mock_storage import (
    JsonMockStorage,
    MockStorage,
    YamlMockStorage,
    get_mock_storage,
)


class TestMockStorage:
    """Tests for MockStorage abstract base class."""

    def test_is_abc(self):
        """Test MockStorage is an abstract base class."""
        assert issubclass(MockStorage, ABC)


class TestYamlMockStorage:
    """Tests for YamlMockStorage class."""

    @pytest.fixture
    def storage(self):
        """Create a YamlMockStorage instance."""
        return YamlMockStorage()

    def test_get_file_extension(self, storage):
        """Test YAML storage returns .yaml extension."""
        assert storage.get_file_extension() == ".yaml"

    def test_save_and_load_mock(self, storage):
        """Test saving and loading mock data with YAML storage."""
        data = {
            "url": "https://example.com",
            "reviews": [{"rating": 5.0, "text": "Great!", "created_at": "2024-01-01T00:00:00"}],
            "captured_data": [],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_mock"
            storage.save_mock(path, data)
            loaded = storage.load_mock(path)

            assert loaded["url"] == "https://example.com"
            assert len(loaded["reviews"]) == 1
            assert loaded["reviews"][0]["rating"] == 5.0

    def test_load_mock_nonexistent(self, storage):
        """Test loading nonexistent file returns None."""
        path = Path("/nonexistent/path/mock.yaml")
        result = storage.load_mock(path)
        assert result is None

    def test_save_creates_parents(self, storage):
        """Test save creates parent directories."""
        data = {"test": "data"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "deep" / "mock"
            storage.save_mock(path, data)
            assert path.with_suffix(".yaml").exists()


class TestJsonMockStorage:
    """Tests for JsonMockStorage class."""

    @pytest.fixture
    def storage(self):
        """Create a JsonMockStorage instance."""
        return JsonMockStorage()

    def test_get_file_extension(self, storage):
        """Test JSON storage returns .json extension."""
        assert storage.get_file_extension() == ".json"

    def test_save_and_load_mock(self, storage):
        """Test saving and loading mock data with JSON storage."""
        data = {
            "url": "https://example.com",
            "reviews": [{"rating": 4.5, "text": "Good product", "created_at": "2024-01-02T00:00:00"}],
            "captured_data": [],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_mock"
            storage.save_mock(path, data)
            loaded = storage.load_mock(path)

            assert loaded["url"] == "https://example.com"
            assert len(loaded["reviews"]) == 1
            assert loaded["reviews"][0]["rating"] == 4.5

    def test_load_mock_nonexistent(self, storage):
        """Test loading nonexistent file returns None."""
        path = Path("/nonexistent/path/mock.json")
        result = storage.load_mock(path)
        assert result is None


class TestGetMockStorage:
    """Tests for get_mock_storage function."""

    def test_get_yaml_storage(self):
        """Test getting YAML storage."""
        storage = get_mock_storage("yaml")
        assert isinstance(storage, YamlMockStorage)

    def test_get_json_storage(self):
        """Test getting JSON storage."""
        storage = get_mock_storage("json")
        assert isinstance(storage, JsonMockStorage)

    def test_get_yaml_default(self):
        """Test that default storage is YAML."""
        storage = get_mock_storage()
        assert isinstance(storage, YamlMockStorage)

    def test_invalid_format_raises(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported mock storage format"):
            get_mock_storage("invalid")

    def test_error_message_format(self):
        """Test error message includes the invalid format."""
        with pytest.raises(ValueError) as exc_info:
            get_mock_storage("xml")
        assert "xml" in str(exc_info.value)
