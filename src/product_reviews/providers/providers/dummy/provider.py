from datetime import datetime
from re import Pattern
from typing import ClassVar

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider


class DummyReviewsProvider(BaseReviewsProvider):
    name: ClassVar[str] = "dummy"
    description: ClassVar[str] = "A dummy provider for testing."
    url_regex: ClassVar[str | Pattern[str]] = r"https?://example\.com/reviews/.*"
    test_urls: ClassVar[list[str]] = [
        "https://example.com/reviews/product-1",
        "https://example.com/reviews/product-2",
    ]

    def get_reviews(self, url: str) -> list[Review]:
        return [
            Review(
                rating=5.0,
                text="This is a dummy review for testing.",
                created_at=datetime.now(),
            ),
            Review(
                rating=4.0,
                text="Another dummy review.",
                created_at=datetime.now(),
            ),
        ]


provider = DummyReviewsProvider
