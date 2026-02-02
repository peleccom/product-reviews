from datetime import datetime

from freezegun import freeze_time

from product_reviews.providers.providers.dummy import provider
from product_reviews.providers.providers.dummy.provider import DummyReviewsProvider


def test_dummy_provider_properties():
    """Test dummy provider properties and URL matching."""
    provider_instance = DummyReviewsProvider()

    assert provider_instance.name == "dummy"
    assert provider_instance.check_url("https://example.com/reviews/product-1")
    assert provider_instance.check_url("http://example.com/reviews/product-2")
    assert not provider_instance.check_url("https://other.com/reviews/product")


@freeze_time("2020-01-01 12:00:00")
def test_dummy_provider_get_reviews_returns_mock_data():
    """Test dummy provider returns mock review data with current timestamp."""
    now = datetime(2020, 1, 1, 12, 0, 0)

    provider_instance = DummyReviewsProvider()
    result = provider_instance.get_reviews("https://example.com/reviews/product")

    assert isinstance(result, list)
    assert len(result) == 2

    first_review = result[0]
    assert first_review.rating == 5.0
    assert first_review.text == "This is a dummy review for testing."
    assert first_review.created_at == now

    second_review = result[1]
    assert second_review.rating == 4.0
    assert second_review.text == "Another dummy review."
    assert second_review.created_at == now


def test_dummy_provider_module_variable():
    """Test dummy provider module variable exposes correct class."""
    assert provider is DummyReviewsProvider
