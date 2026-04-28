import types
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
    get_registry,
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


def test_registry_raises_key_error_for_unknown_provider(mock_providers):
    """Test Registry.get_provider_class raises KeyError for unknown provider."""
    mock_providers([])
    registry = Registry()

    with pytest.raises(KeyError):
        registry.get_provider_class("nonexistent")


def test_registry_clear_cache_multiple_times(mock_providers):
    """Test Registry.clear_cache can be called multiple times safely."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock = mock_providers([TestProvider])
    registry = Registry()
    registry.list_providers()
    registry.list_providers()
    assert mock.call_count == 1

    registry.clear_cache()
    registry.clear_cache()
    registry.clear_cache()
    mock.reset_mock()

    # Cache starts as None, first access loads, subsequent clears don't reload
    registry.list_providers()
    # After initial load, multiple clears don't reload until next access
    assert mock.call_count == 1


def test_registry_with_empty_plugins_dir(mock_providers):
    """Test Registry initialization with empty plugins directory."""
    registry = Registry(plugins_dir=Path(""))
    assert registry._plugins_dir == Path("")


class TestRegistryPrivateMethods:
    """Test Registry private methods."""

    def test_registry_load_providers_caches_correctly(self):
        """Test _load_providers correctly caches providers."""

        class TestProvider(BaseReviewsProvider):
            name = "TestProvider"

            def get_reviews(self, url: str) -> list[Review]:
                return []

        with patch("product_reviews.providers.loaders.iter_all_providers") as mock_iter:
            mock_iter.return_value = iter([TestProvider])
            registry = Registry()

            providers1 = registry._load_providers()
            providers2 = registry._load_providers()

            assert providers1 is providers2


class TestRegistryEdgeCases:
    """Edge case tests for Registry."""

    def test_registry_get_provider_raises_key_error_for_unknown(self):
        """Test Registry.get_provider raises KeyError for unknown provider."""
        with patch("product_reviews.providers.loaders.iter_all_providers") as mock_iter:
            mock_iter.return_value = iter([])
            registry = Registry()

            with pytest.raises(KeyError):
                registry.get_provider("nonexistent")

    def test_registry_clear_cache_when_already_cleared(self):
        """Test Registry.clear_cache when providers were never loaded."""

        class TestProvider(BaseReviewsProvider):
            name = "TestProvider"

            def get_reviews(self, url: str) -> list[Review]:
                return []

        with patch("product_reviews.providers.loaders.iter_all_providers") as mock_iter:
            mock_iter.return_value = iter([TestProvider])
            registry = Registry()

            registry.clear_cache()
            registry.clear_cache()
            registry.clear_cache()

            assert registry._providers is None


class TestDeprecatedFunctions:
    """Test deprecated module-level functions."""

    def test_get_registry_creates_new_instance(self):
        """Test get_registry creates a new Registry instance."""

        registry = get_registry()
        assert isinstance(registry, Registry)
        assert registry._plugins_dir is None

    def test_get_registry_with_plugins_dir(self):
        """Test get_registry with custom plugins directory."""

        custom_dir = Path("/custom/plugins")
        registry = get_registry(plugins_dir=custom_dir)
        assert isinstance(registry, Registry)
        assert registry._plugins_dir == custom_dir

    def test_iter_providers_with_empty_providers(self):
        """Test iter_providers with empty providers dict."""

        result = list(iter_providers(providers={}))
        assert len(result) == 0

    def test_iter_providers_with_multiple_providers(self):
        """Test iter_providers with multiple providers."""

        class ProviderA(BaseReviewsProvider):
            name = "AProvider"

            def get_reviews(self, url: str) -> list[Review]:
                return []

        class ProviderB(BaseReviewsProvider):
            name = "BProvider"

            def get_reviews(self, url: str) -> list[Review]:
                return []

        providers = {"AProvider": ProviderA, "BProvider": ProviderB}

        result = list(iter_providers(providers=providers))

        assert len(result) == 2
        assert result[0] == ("AProvider", ProviderA)
        assert result[1] == ("BProvider", ProviderB)

    def test_list_providers_with_empty_providers(self):
        """Test list_providers with empty providers dict."""

        with patch("product_reviews.providers.loaders.iter_all_providers") as mock_iter:
            mock_iter.return_value = iter([])
            result = list_providers()
            assert isinstance(result, list)

    def test_get_provider_for_url_with_multiple_providers(self):
        """Test get_provider_for_url with multiple providers."""

        class ProviderA(BaseReviewsProvider):
            name = "AProvider"
            url_regex = r"https?://a\.com/.*"

            def get_reviews(self, url: str) -> list[Review]:
                return []

        class ProviderB(BaseReviewsProvider):
            name = "BProvider"
            url_regex = r"https?://b\.com/.*"

            def get_reviews(self, url: str) -> list[Review]:
                return []

        providers = {"AProvider": ProviderA, "BProvider": ProviderB}

        result_a = get_provider_for_url("https://a.com/product", providers=providers)
        result_b = get_provider_for_url("https://b.com/product", providers=providers)

        assert result_a == ProviderA
        assert result_b == ProviderB

    def test_get_provider_for_url_raises_correctly_with_empty(self):
        """Test get_provider_for_url raises ProviderLoadError when empty providers."""
        with pytest.raises(ProviderLoadError):
            get_provider_for_url("https://test.com/product", providers={})

    def test_iter_providers_returns_generator(self):
        """Test iter_providers returns a generator."""

        class TestProvider(BaseReviewsProvider):
            name = "TestProvider"

            def get_reviews(self, url: str) -> list[Review]:
                return []

        result = iter_providers(providers={"TestProvider": TestProvider})

        assert isinstance(result, types.GeneratorType)
