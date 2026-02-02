import json
from datetime import datetime

from product_reviews.models import ProviderReviewList, Review


def test_review_to_dict():
    """Test Review model to_dict serialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    d = review.to_dict()

    assert "text" in d
    assert d["rating"] == 5


def test_review_to_json():
    """Test Review model to_json serialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    data = review.to_json()
    assert isinstance(data, str)
    review2 = json.loads(data)
    assert review2["created_at"] == "2020-01-01T00:00:00"


def test_review_to_representation():
    """Test Review model to_representation serialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    review2 = review.to_representation()
    assert review2["text"] == "This is a dummy review for testing."
    assert review2["created_at"] == "2020-01-01T00:00:00"


def test_review_from_representation():
    """Test Review model from_representation deserialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    restored_review = Review.from_representation(review.to_representation())
    assert restored_review.created_at == datetime(2020, 1, 1)
    assert restored_review.text == "This is a dummy review for testing."
    assert restored_review.rating == 5.0
    assert restored_review.pros is None
    assert restored_review.cons is None
    assert restored_review.summary is None


def test_provider_review_list():
    """Test ProviderReviewList count method and reviews property."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    provider_review_list = ProviderReviewList(provider="test", reviews=[review])
    assert provider_review_list.count() == 1
    assert len(provider_review_list.reviews) == 1
