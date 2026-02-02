from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import ProviderLoadError
from product_reviews.providers.registry import (
    Registry,
    get_default_registry,
    get_provider_for_url,
    iter_providers,
    list_providers,
)


def test_registry_initialization():
    """Test Registry can be initialized with a custom plugins directory."""
    custom_path = Path("/custom/plugins")
    registry = Registry(plugins_dir=custom_path)

    assert registry._plugins_dir == custom_path


def test_registry_default_initialization():
    """Test Registry can be initialized without arguments."""
    registry = Registry()

    assert registry._plugins_dir is None
    assert registry._providers is None


def test_registry_get_provider_for_url(mock_providers):
    """Test Registry.get_provider_for_url returns correct provider."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])
    registry = Registry()

    result = registry.get_provider_for_url("https://test.com/product")

    assert result == TestProvider


def test_registry_get_provider_for_url_no_match(mock_providers):
    """Test Registry.get_provider_for_url raises error when no provider matches."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])
    registry = Registry()

    with pytest.raises(ProviderLoadError, match=r"No provider found for URL: https://other\.com/product"):
        registry.get_provider_for_url("https://other.com/product")


def test_registry_iter_providers(mock_providers):
    """Test Registry.iter_providers yields (name, class) tuples."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])
    registry = Registry()

    result = list(registry.iter_providers())

    assert len(result) == 1
    assert result[0] == ("TestProvider", TestProvider)


def test_registry_list_providers(mock_providers):
    """Test Registry.list_providers returns sorted providers."""

    class ProviderA(BaseReviewsProvider):
        name = "ZProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    class ProviderB(BaseReviewsProvider):
        name = "AProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([ProviderA, ProviderB])
    registry = Registry()

    result = registry.list_providers()

    assert len(result) == 2
    assert result[0].name == "AProvider"
    assert result[1].name == "ZProvider"


def test_registry_get_provider_class(mock_providers):
    """Test Registry.get_provider_class returns provider class by name."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])
    registry = Registry()

    result = registry.get_provider_class("TestProvider")

    assert result == TestProvider


def test_registry_get_provider_names(mock_providers):
    """Test Registry.get_provider_names returns sorted names."""

    class ProviderA(BaseReviewsProvider):
        name = "ZProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    class ProviderB(BaseReviewsProvider):
        name = "AProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([ProviderA, ProviderB])
    registry = Registry()

    result = registry.get_provider_names()

    assert result == ["AProvider", "ZProvider"]


def test_registry_get_provider(mock_providers):
    """Test Registry.get_provider returns provider instance."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])
    registry = Registry()

    result = registry.get_provider("TestProvider")

    assert isinstance(result, TestProvider)


def test_registry_caches_providers(mock_providers):
    """Test Registry caches loaded providers."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock = mock_providers([TestProvider])
    registry = Registry()

    registry.list_providers()
    assert mock.call_count == 1

    registry.list_providers()
    assert mock.call_count == 1


def test_registry_clear_cache(mock_providers):
    """Test Registry.clear_cache forces reload."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock = mock_providers([TestProvider])
    registry = Registry()

    registry.list_providers()
    assert mock.call_count == 1

    registry.clear_cache()

    registry.list_providers()
    assert mock.call_count == 2


def test_get_default_registry():
    """Test get_default_registry creates registry with plugins dir from env."""
    with patch("product_reviews.providers.registry.get_plugins_dir") as mock:
        mock.return_value = Path("/test/plugins")
        registry = get_default_registry()

        assert isinstance(registry, Registry)
        assert registry._plugins_dir == Path("/test/plugins")


def test_list_providers_sorts_by_name(mock_providers):
    """Test list_providers returns providers sorted alphabetically by name."""

    class ProviderA(BaseReviewsProvider):
        name = "ZProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    class ProviderB(BaseReviewsProvider):
        name = "AProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([ProviderA, ProviderB])

    result = list_providers()

    assert len(result) == 2
    assert result[0].name == "AProvider"
    assert result[1].name == "ZProvider"


def test_iter_providers_yields_pairs(mock_providers):
    """Test iter_providers yields (name, class) tuples for each provider."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])

    result = list(iter_providers())

    assert len(result) == 1
    assert result[0] == ("TestProvider", TestProvider)


def test_get_provider_for_url_success(mock_providers):
    """Test get_provider_for_url returns correct provider when URL matches regex."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])

    result = get_provider_for_url("https://test.com/product")

    assert result == TestProvider


def test_get_provider_for_url_no_match(mock_providers):
    """Test get_provider_for_url raises ProviderLoadError when no provider matches URL."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])

    with pytest.raises(ProviderLoadError, match=r"No provider found for URL: https://other\.com/product"):
        get_provider_for_url("https://other.com/product")


def test_get_provider_for_url_with_custom_providers():
    """Test get_provider_for_url works with custom provider dictionary."""

    class CustomProvider(BaseReviewsProvider):
        name = "CustomProvider"
        url_regex = r"https?://custom\.com/.*"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    providers = cast(dict[str, type[BaseReviewsProvider]], {"custom": CustomProvider})

    result = get_provider_for_url("https://custom.com/product", providers)

    assert result == CustomProvider


def test_get_provider_for_url_with_none_providers_uses_load_all(mock_providers):
    """Test get_provider_for_url uses load_all when providers parameter is None."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mocked_providers = mock_providers([TestProvider])

    result = get_provider_for_url("https://test.com/product", providers=None)

    mocked_providers.assert_called_once()
    assert result == TestProvider
