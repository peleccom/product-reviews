from pathlib import Path
from unittest.mock import patch

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.loaders import (
    ENV_PLUGINS_DIR,
    get_plugins_dir,
    load_all_providers_map,
)


@patch("product_reviews.providers.loaders.load_entry_point_providers")
@patch("product_reviews.providers.loaders.load_fs_providers")
def test_load_all_providers(mock_fs, mock_entry):
    """Test load_all_providers_map loads providers from all sources."""

    class EntryProvider(BaseReviewsProvider):
        name = "EntryProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    class FsProvider(BaseReviewsProvider):
        name = "FsProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_entry.return_value = [EntryProvider]
    mock_fs.return_value = [FsProvider]

    result = load_all_providers_map()

    assert len(result) == 2
    assert result["EntryProvider"] == EntryProvider
    assert result["FsProvider"] == FsProvider
    mock_entry.assert_called_once()
    mock_fs.assert_called_once()


@patch("product_reviews.providers.loaders.load_entry_point_providers")
@patch("product_reviews.providers.loaders.load_fs_providers")
def test_load_all_providers_with_custom_dir(mock_fs, mock_entry):
    """Test load_all_providers_map with custom directory."""

    class CustomFsProvider(BaseReviewsProvider):
        name = "CustomFsProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    custom_dir = Path("/custom/path")
    mock_entry.return_value = []
    mock_fs.return_value = [CustomFsProvider]

    result = load_all_providers_map(plugins_dir=custom_dir)

    assert len(result) == 1
    assert result["CustomFsProvider"] == CustomFsProvider
    mock_entry.assert_called_once()
    mock_fs.assert_called_once_with(custom_dir)


@patch("product_reviews.providers.loaders.load_entry_point_providers")
@patch("product_reviews.providers.loaders.load_fs_providers")
def test_load_all_providers_no_providers(mock_fs, mock_entry):
    """Test load_all_providers_map handles no available providers."""
    mock_entry.return_value = []
    mock_fs.return_value = []

    result = load_all_providers_map()

    assert len(result) == 0
    mock_entry.assert_called_once()
    mock_fs.assert_called_once()


def test_get_plugins_dir_from_env():
    """Test get_plugins_dir returns path from environment variable."""
    custom_path = "/custom/plugins"
    with patch.dict("os.environ", {ENV_PLUGINS_DIR: custom_path}, clear=False):
        result = get_plugins_dir()
        assert result == Path(custom_path)


def test_get_plugins_dir_not_set():
    """Test get_plugins_dir returns None when env var not set."""
    with patch.dict("os.environ", {}, clear=True):
        result = get_plugins_dir()
        assert result is None


def test_env_plugins_dir_constant():
    """Test ENV_PLUGINS_DIR constant is correct."""
    assert ENV_PLUGINS_DIR == "PRODUCT_REVIEWS_PLUGINS_DIR"
