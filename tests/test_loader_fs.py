"""Tests for loader_fs module."""

import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.loader_fs import (
    _find_provider_in_module,
    get_local_providers_dir,
    load_fs_provider,
    load_fs_providers,
)


class MockProvider(BaseReviewsProvider):
    """Test provider class."""

    name = "mock"

    def get_reviews(self, url: str):
        return []


class AnotherMockProvider(BaseReviewsProvider):
    """Another test provider class."""

    name = "another_mock"

    def get_reviews(self, url: str):
        return []


def test_get_local_providers_dir():
    """Test get_local_providers_dir returns correct path."""
    result = get_local_providers_dir()
    assert isinstance(result, Path)
    assert result.name == "providers"


def test_get_local_providers_dir_exists():
    """Test that local providers directory exists."""
    providers_dir = get_local_providers_dir()
    assert providers_dir.exists()
    assert providers_dir.is_dir()


def test_load_fs_provider_none_for_non_directory():
    """Test load_fs_provider returns None for non-directory paths."""
    non_dir = Path("/tmp/this_is_not_a_directory.txt")  # noqa: S108
    result = load_fs_provider(non_dir)
    assert result is None


def test_load_fs_provider_none_for_missing_provider_file():
    """Test load_fs_provider returns None when provider.py is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        empty_dir = Path(tmpdir) / "empty_provider"
        empty_dir.mkdir()
        result = load_fs_provider(empty_dir)
        assert result is None


def test_load_fs_provider_valid_provider():
    """Test load_fs_provider loads a valid provider."""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider_dir = Path(tmpdir) / "test_provider"
        provider_dir.mkdir()

        provider_file = provider_dir / "provider.py"
        provider_file.write_text(
            """
from product_reviews.providers.base import BaseReviewsProvider

class TestProvider(BaseReviewsProvider):
    name = "test_provider"

    def get_reviews(self, url):
        return []
"""
        )

        result = load_fs_provider(provider_dir)
        assert result is not None
        assert result.name == "test_provider"


def test_load_fs_provider_provider_attr():
    """Test load_fs_provider finds provider via 'provider' attr."""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider_dir = Path(tmpdir) / "test_provider"
        provider_dir.mkdir()

        provider_file = provider_dir / "provider.py"
        provider_file.write_text(
            """
from product_reviews.providers.base import BaseReviewsProvider

class SomeProvider(BaseReviewsProvider):
    name = "some_provider"

    def get_reviews(self, url):
        return []

provider = SomeProvider
"""
        )

        result = load_fs_provider(provider_dir)
        assert result is not None
        assert result.name == "some_provider"


def test_load_fs_provider_titled_provider():
    """Test load_fs_provider finds provider via TitleCaseProvider pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider_dir = Path(tmpdir) / "custom_name"
        provider_dir.mkdir()

        provider_file = provider_dir / "provider.py"
        provider_file.write_text(
            """
from product_reviews.providers.base import BaseReviewsProvider

class CustomNameProvider(BaseReviewsProvider):
    name = "custom_name"

    def get_reviews(self, url):
        return []
"""
        )

        result = load_fs_provider(provider_dir)
        assert result is not None
        assert result.name == "custom_name"


def test_load_fs_provider_does_not_subclass():
    """Test load_fs_provider returns None when class doesn't subclass BaseReviewsProvider."""

    with tempfile.TemporaryDirectory() as tmpdir:
        provider_dir = Path(tmpdir) / "bad_provider"
        provider_dir.mkdir()

        provider_file = provider_dir / "provider.py"
        provider_file.write_text(
            """
class NotAProvider:
    name = "not_a_provider"
"""
        )

        result = load_fs_provider(provider_dir)
        assert result is None


def test_load_fs_provider_exception_handling():
    """Test load_fs_provider handles exceptions gracefully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        provider_dir = Path(tmpdir) / "broken_provider"
        provider_dir.mkdir()

        provider_file = provider_dir / "provider.py"
        provider_file.write_text(
            """
raise RuntimeError("Intentional error")
"""
        )

        result = load_fs_provider(provider_dir)
        assert result is None


def test_find_provider_in_module_direct():
    """Test _find_provider_in_module finds provider directly."""
    module = MagicMock()
    module.provider = MockProvider
    result = _find_provider_in_module(module)
    assert result is MockProvider


def test_find_provider_in_module_title_case():
    """Test _find_provider_in_module finds via title case."""
    module = MagicMock()
    module.__name__ = "mymodule"
    module.MyModuleProvider = AnotherMockProvider
    module.provider = AnotherMockProvider
    result = _find_provider_in_module(module)
    assert result is AnotherMockProvider


def test_find_provider_in_module_dir_scan():
    """Test _find_provider_in_module scans dir as fallback."""
    module = MagicMock()
    module.__name__ = "unknownmodule"
    del module.provider
    del module.UnknownModuleProvider
    module.OtherProvider = MockProvider
    module.__dict__ = {"OtherProvider": MockProvider}

    def mock_dir(module):
        return ["OtherProvider"]

    with patch("product_reviews.providers.loader_fs.dir", mock_dir):
        result = _find_provider_in_module(module)
    assert result is MockProvider


def test_load_fs_providers_returns_generator():
    """Test load_fs_providers returns a generator."""
    result = load_fs_providers()

    assert isinstance(result, types.GeneratorType)


def test_load_fs_providers_filters_hidden():
    """Test load_fs_providers filters directories starting with underscore."""
    with tempfile.TemporaryDirectory() as tmpdir:
        providers_dir = Path(tmpdir)

        hidden_dir = providers_dir / "_hidden"
        hidden_dir.mkdir()

        visible_dir = providers_dir / "visible"
        visible_dir.mkdir()

        (hidden_dir / "provider.py").write_text("")
        (visible_dir / "provider.py").write_text(
            """
from product_reviews.providers.base import BaseReviewsProvider

class VisibleProvider(BaseReviewsProvider):
    name = "visible"
    def get_reviews(self, url):
        return []
"""
        )

        result = list(load_fs_providers(providers_dir))
        provider_names = [p.name for p in result]

        assert "visible" in provider_names
        assert "_hidden" not in provider_names


def test_load_fs_providers_handles_missing_directory():
    """Test load_fs_providers handles non-existent directory."""
    result = load_fs_providers(Path("/nonexistent/path"))

    assert isinstance(result, types.GeneratorType)
    result_list = list(result)
    assert result_list == []
