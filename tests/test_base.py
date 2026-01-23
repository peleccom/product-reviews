import json
from datetime import datetime

from product_reviews.models import Review, ReviewList


def test_review_to_dict():
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    d = review.to_dict()

    assert "text" in d
    assert d["rating"] == 5


def test_review_to_json():
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    data = review.to_json()
    assert isinstance(data, str)
    review2 = json.loads(data)
    assert review2["created_at"] == "2020-01-01T00:00:00"


def test_review_list():
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    review_list = ReviewList(reviews=[review])
    assert review_list.count() == 1
