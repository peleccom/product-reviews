from typing import cast

import pytest

from product_reviews.models import ReviewList
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import ProviderLoadError
from product_reviews.providers.registry import get_provider_for_url, iter_providers, list_providers


def test_list_providers_sorts_by_name(mock_providers):
    """Test list_providers returns providers sorted alphabetically by name."""

    class ProviderA(BaseReviewsProvider):
        name = "ZProvider"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    class ProviderB(BaseReviewsProvider):
        name = "AProvider"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([ProviderA, ProviderB])

    result = list_providers()

    assert len(result) == 2
    assert result[0].name == "AProvider"
    assert result[1].name == "ZProvider"


def test_iter_providers_yields_pairs(mock_providers):
    """Test iter_providers yields (name, class) tuples for each provider."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([TestProvider])

    result = list(iter_providers())

    assert len(result) == 1
    assert result[0] == ("TestProvider", TestProvider)


def test_get_provider_for_url_success(mock_providers):
    """Test get_provider_for_url returns correct provider when URL matches regex."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([TestProvider])

    result = get_provider_for_url("https://test.com/product")

    assert result == TestProvider


def test_get_provider_for_url_no_match(mock_providers):
    """Test get_provider_for_url raises ProviderLoadError when no provider matches URL."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([TestProvider])

    with pytest.raises(ProviderLoadError, match=r"No provider found for URL: https://other\.com/product"):
        get_provider_for_url("https://other.com/product")


def test_get_provider_for_url_with_custom_providers():
    """Test get_provider_for_url works with custom provider dictionary."""

    class CustomProvider(BaseReviewsProvider):
        name = "CustomProvider"
        url_regex = r"https?://custom\.com/.*"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    providers = cast(dict[str, type[BaseReviewsProvider]], {"custom": CustomProvider})

    result = get_provider_for_url("https://custom.com/product", providers)

    assert result == CustomProvider


def test_get_provider_for_url_with_none_providers_uses_load_all(mock_providers):
    """Test get_provider_for_url uses load_all when providers parameter is None."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mocked_providers = mock_providers([TestProvider])

    result = get_provider_for_url("https://test.com/product", providers=None)

    mocked_providers.assert_called_once()
    assert result == TestProvider
