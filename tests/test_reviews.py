from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from requests import HTTPError

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import NoMatchedProvidersException, ReviewsParseException
from product_reviews.providers.registry import Registry
from product_reviews.reviews import ProductReviewsService, _parse_reviews


def test_reviews_list_empty():
    """Test empty reviews list."""
    reviews = []
    assert len(reviews) == 0


def test_reviews_list_multiple():
    """Test reviews list with multiple reviews."""
    review1 = Review(rating=5.0, created_at=datetime(2020, 1, 1))
    review2 = Review(rating=3.0, created_at=datetime(2020, 1, 2))
    reviews = [review1, review2]
    assert len(reviews) == 2


@patch("product_reviews.reviews._check_matched_provider")
def test_parse_reviews_success(mock_check):
    """Test parse_reviews returns reviews when provider matches."""
    mock_provider_class = Mock(spec=BaseReviewsProvider)
    mock_provider_class.check_url.return_value = True
    mock_provider_class.name = "TestProvider"
    mock_provider_instance = Mock(spec=BaseReviewsProvider)
    mock_provider_instance.get_reviews.return_value = [
        Review(rating=5.0, created_at=datetime(2020, 1, 2)),
        Review(rating=3.0, created_at=datetime(2020, 1, 1)),
    ]
    mock_provider_instance.name = "TestProvider"
    mock_provider_class.return_value = mock_provider_instance
    mock_check.return_value = mock_provider_class

    result = _parse_reviews("https://test.com/product")

    assert result.provider == "TestProvider"
    assert result.count() == 2
    assert result.reviews[0].rating == 5.0
    assert result.reviews[1].rating == 3.0


@patch("product_reviews.reviews._check_matched_provider")
def test_parse_reviews_http_error(mock_check):
    """Test parse_reviews raises ReviewsParseException on HTTP error."""
    mock_provider_class = Mock(spec=BaseReviewsProvider)
    mock_provider_class.check_url.return_value = True
    mock_provider_instance = Mock(spec=BaseReviewsProvider)
    mock_provider_instance.get_reviews.side_effect = HTTPError("Network error")
    mock_provider_class.return_value = mock_provider_instance
    mock_check.return_value = mock_provider_class

    with pytest.raises(ReviewsParseException):
        _parse_reviews("https://test.com/product")


@patch("product_reviews.reviews._check_matched_provider")
def test_parse_reviews_no_provider(mock_check):
    """Test parse_reviews raises NoMatchedProvidersException when no provider matches."""
    mock_check.return_value = None

    with pytest.raises(NoMatchedProvidersException):
        _parse_reviews("https://unknown.com/product")


def test_parse_reviews_sorts_by_created_at_desc(mock_providers):
    """Test parse_reviews sorts reviews by created_at descending."""
    review1 = Review(rating=5.0, created_at=datetime(2020, 1, 1))
    review2 = Review(rating=3.0, created_at=datetime(2020, 1, 2))
    review3 = Review(rating=4.0, created_at=datetime(2020, 1, 3))

    class MockProvider(BaseReviewsProvider):
        name = "TestProvider"

        @classmethod
        def check_url(cls, url: str) -> bool:
            return True

        def get_reviews(self, url: str) -> list[Review]:
            return [review2, review1, review3]

    mock_providers([MockProvider])

    result = _parse_reviews("https://test.com/product")

    assert result.reviews[0].created_at == datetime(2020, 1, 3)
    assert result.reviews[1].created_at == datetime(2020, 1, 2)
    assert result.reviews[2].created_at == datetime(2020, 1, 1)


def test_product_reviews_service_parse_reviews_instance_method(mock_providers):
    """Test ProductReviewsService.parse_reviews instance method delegation."""
    mock_provider_class = Mock(spec=BaseReviewsProvider)
    mock_provider_class.check_url.return_value = True
    mock_provider_class.name = "TestProvider"
    mock_provider_instance = Mock(spec=BaseReviewsProvider)
    mock_provider_instance.get_reviews.return_value = []
    mock_provider_instance.name = "TestProvider"
    mock_provider_class.return_value = mock_provider_instance

    mock_providers([mock_provider_class])

    service = ProductReviewsService()
    result = service.parse_reviews("https://test.com")

    assert result.provider == "TestProvider"


def test_product_reviews_service_list_providers_instance_method(mock_providers):
    """Test ProductReviewsService.list_providers instance method."""

    class P1(BaseReviewsProvider):
        name = "provider1"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    class P2(BaseReviewsProvider):
        name = "provider2"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([P1, P2])

    service = ProductReviewsService()
    result = service.list_providers()

    assert len(result) == 2
    assert P1 in result
    assert P2 in result


def test_product_reviews_service_get_provider_for_url():
    """Test ProductReviewsService.get_provider_for_url returns matched provider."""
    mock_registry = Mock(spec=Registry)
    mock_registry.get_provider_for_url.return_value = "test_provider"

    service = ProductReviewsService(registry=mock_registry)
    result = service.get_provider_for_url("https://test.com")

    mock_registry.get_provider_for_url.assert_called_once_with("https://test.com")
    assert result == "test_provider"


def test_product_reviews_service_get_provider_for_url_none():
    """Test ProductReviewsService.get_provider_for_url returns None when no match."""
    mock_registry = Mock(spec=Registry)
    mock_registry.get_provider_for_url.side_effect = Exception("No provider")

    service = ProductReviewsService(registry=mock_registry)
    result = service.get_provider_for_url("https://unknown.com")

    assert result is None


def test_product_reviews_service_get_provider_names(mock_providers):
    """Test ProductReviewsService.get_provider_names returns provider names."""

    class Provider1(BaseReviewsProvider):
        name = "provider1"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    class Provider2(BaseReviewsProvider):
        name = "provider2"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([Provider1, Provider2])

    service = ProductReviewsService()
    result = service.get_provider_names()

    assert set(result) == {"provider1", "provider2"}


def test_product_reviews_service_get_provider_class(mock_providers):
    """Test ProductReviewsService.get_provider_class returns correct class."""

    class P:
        name = "test_provider"

    mock_providers([P])

    service = ProductReviewsService()
    result = service.get_provider_class("test_provider")

    assert result == P


def test_product_reviews_service_get_provider_class_not_found(mock_providers):
    """Test ProductReviewsService.get_provider_class raises KeyError for unknown provider."""
    mock_providers([])

    service = ProductReviewsService()

    with pytest.raises(KeyError):
        service.get_provider_class("nonexistent_provider")


def test_product_reviews_service_get_provider(mock_providers):
    """Test ProductReviewsService.get_provider returns provider instance."""

    class TestProvider(BaseReviewsProvider):
        name = "test_provider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([TestProvider])

    service = ProductReviewsService()
    result = service.get_provider("test_provider")

    assert isinstance(result, TestProvider)
