from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from product_reviews.models import Review, ReviewList
from product_reviews.providers.base import BaseReviewsProvider


class ExampleReviewsProvider(BaseReviewsProvider):
    name: ClassVar[str] = "example"
    description: ClassVar[str] = "An example provider for testing."
    url_regex: ClassVar[str] = r"https?://example\.com/products/.*"
    test_urls: ClassVar[list[str]] = [
        "https://example.com/products/product-1",
        "https://example.com/products/product-2",
    ]

    def get_reviews(self, url: str) -> ReviewList:
        reviews = [
            Review(
                rating=5.0,
                text="This is an example review for testing purposes.",
                created_at=datetime.now(),
            ),
            Review(
                rating=3.0,
                text="Average quality, could be better.",
                created_at=datetime.now(),
            ),
        ]
        review_list = ReviewList(
            reviews=reviews,
        )
        return review_list
