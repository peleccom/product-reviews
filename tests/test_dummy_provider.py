from datetime import datetime
from unittest.mock import patch

from product_reviews.models import ReviewList
from product_reviews.providers.providers.dummy import provider
from product_reviews.providers.providers.dummy.provider import DummyReviewsProvider


def test_dummy_provider_properties():
    """Test dummy provider properties and URL matching."""
    provider_instance = DummyReviewsProvider()

    assert provider_instance.name == "dummy"
    assert provider_instance.check_url("https://example.com/reviews/product-1")
    assert provider_instance.check_url("http://example.com/reviews/product-2")
    assert not provider_instance.check_url("https://other.com/reviews/product")


@patch("product_reviews.providers.providers.dummy.provider.datetime")
def test_dummy_provider_get_reviews_returns_mock_data(mock_datetime):
    """Test dummy provider returns mock review data with current timestamp."""
    mock_now = datetime(2020, 1, 1, 12, 0, 0)
    mock_datetime.now.return_value = mock_now

    provider_instance = DummyReviewsProvider()
    result = provider_instance.get_reviews("https://example.com/reviews/product")

    assert isinstance(result, ReviewList)
    assert result.count() == 2
    assert len(result.reviews) == 2

    first_review = result.reviews[0]
    assert first_review.rating == 5.0
    assert first_review.text == "This is a dummy review for testing."
    assert first_review.created_at == mock_now

    second_review = result.reviews[1]
    assert second_review.rating == 4.0
    assert second_review.text == "Another dummy review."
    assert second_review.created_at == mock_now


def test_dummy_provider_module_variable():
    """Test dummy provider module variable exposes correct class."""
    assert provider is DummyReviewsProvider
