from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from requests import HTTPError

from product_reviews.models import ProviderReviewList, Review, ReviewList
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import NoMatchedProvidersException, ReviewsParseException
from product_reviews.reviews import ProductReviewsService, parse_reviews


def test_review_list_count_empty():
    """Test review list count returns zero for empty list."""
    review_list = ReviewList(reviews=[])
    assert review_list.count() == 0


def test_review_list_count_multiple():
    """Test review list count returns correct number for multiple reviews."""
    review1 = Review(rating=5.0, created_at=datetime(2020, 1, 1))
    review2 = Review(rating=3.0, created_at=datetime(2020, 1, 2))
    review_list = ReviewList(reviews=[review1, review2])
    assert review_list.count() == 2


@patch("product_reviews.reviews._check_matched_provider")
def test_parse_reviews_success(mock_check):
    """Test parse_reviews returns reviews when provider matches."""
    mock_provider_class = Mock(spec=BaseReviewsProvider)
    mock_provider_class.check_url.return_value = True
    mock_provider_class.name = "TestProvider"
    mock_provider_instance = Mock(spec=BaseReviewsProvider)
    mock_provider_instance.get_reviews.return_value = ReviewList(
        reviews=[
            Review(rating=5.0, created_at=datetime(2020, 1, 2)),
            Review(rating=3.0, created_at=datetime(2020, 1, 1)),
        ]
    )
    mock_provider_instance.name = "TestProvider"
    mock_provider_class.return_value = mock_provider_instance
    mock_check.return_value = mock_provider_class

    result = parse_reviews("https://test.com/product")

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
        parse_reviews("https://test.com/product")


@patch("product_reviews.reviews._check_matched_provider")
def test_parse_reviews_no_provider(mock_check):
    """Test parse_reviews raises NoMatchedProvidersException when no provider matches."""
    mock_check.return_value = None

    with pytest.raises(NoMatchedProvidersException):
        parse_reviews("https://unknown.com/product")


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

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[review2, review1, review3])

    mock_providers([MockProvider])

    result = parse_reviews("https://test.com/product")

    assert result.reviews[0].created_at == datetime(2020, 1, 3)
    assert result.reviews[1].created_at == datetime(2020, 1, 2)
    assert result.reviews[2].created_at == datetime(2020, 1, 1)


def test_product_reviews_service_parse_reviews_static_method():
    """Test ProductReviewsService.parse_reviews static method delegation."""
    with patch("product_reviews.reviews.parse_reviews") as mock_parse:
        mock_parse.return_value = ProviderReviewList(provider="test", reviews=[])

        result = ProductReviewsService.parse_reviews("https://test.com")

        mock_parse.assert_called_once_with("https://test.com")
        assert result.provider == "test"


def test_product_reviews_service_list_providers_static_method(mock_providers):
    """Test ProductReviewsService.list_providers static method."""

    class P1:
        name = "provider1"

    class P2:
        name = "provider2"

    mocked_providers = mock_providers([P1, P2])

    result = ProductReviewsService.list_providers()

    mocked_providers.assert_called_once()
    assert result == [P1, P2]


@patch("product_reviews.reviews._check_matched_provider")
def test_product_reviews_service_get_provider_for_url(mock_check):
    """Test ProductReviewsService.get_provider_for_url returns matched provider."""
    mock_check.return_value = "test_provider"

    service = ProductReviewsService()
    result = service.get_provider_for_url("https://test.com")

    mock_check.assert_called_once_with("https://test.com")
    assert result == "test_provider"


@patch("product_reviews.reviews._check_matched_provider")
def test_product_reviews_service_get_provider_for_url_none(mock_check):
    """Test ProductReviewsService.get_provider_for_url returns None when no match."""
    mock_check.return_value = None

    service = ProductReviewsService()
    result = service.get_provider_for_url("https://unknown.com")

    assert result is None


def test_product_reviews_service_get_provider_names(mock_providers):
    """Test ProductReviewsService.get_provider_names returns provider names."""

    class Provider1(BaseReviewsProvider):
        name = "provider1"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    class Provider2(BaseReviewsProvider):
        name = "provider2"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

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

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([TestProvider])

    service = ProductReviewsService()
    result = service.get_provider("test_provider")

    assert isinstance(result, TestProvider)
