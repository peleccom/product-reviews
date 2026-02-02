from datetime import datetime
from typing import ClassVar

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider


class MockReviewsProvider(BaseReviewsProvider):
    name = "MockProvider"
    description = "A mock provider for testing"
    url_regex = r"https?://mock\.example\.com/.*"
    test_urls: ClassVar[list[str]] = ["https://mock.example.com/test"]

    class TestProviderError(Exception):
        pass

    def get_reviews(self, url: str) -> list[Review]:
        if "error" in url:
            raise MockReviewsProvider.TestProviderError()
        if "empty" in url:
            return []

        return [
            Review(rating=5.0, text="Great product", created_at=datetime(2020, 1, 1)),
            Review(rating=3.0, text="Average product", created_at=datetime(2020, 1, 2)),
        ]


def test_base_provider_check_url_with_string_regex():
    """Test base provider URL matching with string regex pattern."""
    provider_instance = MockReviewsProvider()
    assert provider_instance.check_url("https://mock.example.com/product")
    assert provider_instance.check_url("http://mock.example.com/product")


def test_base_provider_check_url_no_match():
    """Test base provider URL matching returns False for non-matching URLs."""
    provider_instance = MockReviewsProvider()
    assert not provider_instance.check_url("https://other.com/product")


def test_base_provider_check_health_no_test_urls():
    """Test base provider health check when no test URLs configured."""

    class NoTestUrlsProvider(BaseReviewsProvider):
        name = "NoTestUrlsProvider"
        test_urls: ClassVar[list[str]] = []

        def get_reviews(self, url: str) -> list[Review]:
            return []

    provider_instance = NoTestUrlsProvider()
    results = provider_instance.check_health()

    assert len(results) == 1
    assert not results[0].is_healthy
    assert "No test URLs configured" in results[0].message


def test_base_provider_check_health_with_successful_fetch():
    """Test base provider health check with successful review fetch."""
    provider_instance = MockReviewsProvider()
    results = provider_instance.check_health()

    assert len(results) == 1
    assert results[0].is_healthy
    assert results[0].url == "https://mock.example.com/test"
    assert results[0].reviews_count == 2


def test_base_provider_check_health_with_empty_reviews():
    """Test base provider health check when no reviews are found."""
    provider_instance = MockReviewsProvider()
    results = provider_instance.check_health("https://mock.example.com/empty")

    assert len(results) == 1
    assert not results[0].is_healthy
    assert "No reviews found" in results[0].message


def test_base_provider_check_health_with_exception():
    """Test base provider health check when exception occurs during fetch."""
    provider_instance = MockReviewsProvider()
    results = provider_instance.check_health("https://mock.example.com/error")

    assert len(results) == 1
    assert not results[0].is_healthy
    assert "Error fetching reviews" in results[0].message


def test_base_provider_repr():
    """Test base provider string representation includes provider name."""
    provider_instance = MockReviewsProvider()
    repr_str = repr(provider_instance)

    assert "MockProvider" in repr_str
    assert "MockReviewsProvider" in repr_str
