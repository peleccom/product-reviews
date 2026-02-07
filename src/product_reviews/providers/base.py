from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import ClassVar

from product_reviews.models import HealthCheckResult, Review

logger = logging.getLogger(__name__)


class ReviewValidationError(Exception):
    pass


class ReviewListValidator:
    def check_review_fields(self, review: Review):
        if not review.created_at:
            raise ReviewValidationError("Review created_at is required")  # noqa: TRY003
        if not review.rating:
            raise ReviewValidationError("Review rating is required")  # noqa: TRY003
        if review.text and not isinstance(review.text, str):
            raise ReviewValidationError("Review text must be a string")  # noqa: TRY003
        if review.pros and not isinstance(review.pros, str):
            raise ReviewValidationError("Review pros must be a string")  # noqa: TRY003
        if review.cons and not isinstance(review.cons, str):
            raise ReviewValidationError("Review cons must be a string")  # noqa: TRY003
        if review.summary and not isinstance(review.summary, str):
            raise ReviewValidationError("Review summary must be a string")  # noqa: TRY003

    def check_reviews_count(self, reviews: list[Review]):
        if not reviews or len(reviews) == 0:
            raise ReviewValidationError("No reviews found")  # noqa: TRY003


def _get_health_for_url(provider: BaseReviewsProvider, url: str) -> HealthCheckResult:
    try:
        reviews = provider.get_reviews(url)
    except Exception as e:
        return HealthCheckResult(
            is_healthy=False,
            message=f"Error fetching reviews: {e!s}",
            url=url,
            reviews_count=0,
        )

    try:
        ReviewListValidator().check_reviews_count(reviews)
    except ReviewValidationError:
        return HealthCheckResult(
            is_healthy=False,
            message="No reviews found",
            url=url,
            reviews_count=0,
        )

    try:
        for review in reviews:
            ReviewListValidator().check_review_fields(review)
    except ReviewValidationError:
        return HealthCheckResult(
            is_healthy=False,
            message="Review validation failed",
            url=url,
            reviews_count=0,
        )

    return HealthCheckResult(
        is_healthy=True,
        message="Successfully fetched reviews",
        url=url,
        reviews_count=len(reviews),
    )


class BaseReviewsProvider(ABC):
    """
    Base class for all review providers.
    """

    name: ClassVar[str]
    description: ClassVar[str]
    notes: ClassVar[str | None]
    url_regex: ClassVar[list[str] | str]
    test_urls: ClassVar[list[str]] = []
    invalid_urls: ClassVar[list[str]] = []

    @classmethod
    def check_url(cls, url: str) -> bool:
        if isinstance(cls.url_regex, (list, tuple)):
            for url_regex in cls.url_regex:
                if re.match(url_regex, url):
                    logger.debug(f"Url match with `{cls.name}`")
                    return True
        else:
            if re.match(cls.url_regex, url):
                logger.debug(f"Url match with `{cls.name}`")
                return True
        return False

    @abstractmethod
    def get_reviews(self, url: str) -> list[Review]:
        raise NotImplementedError

    def check_health(self, url: str | None = None) -> list[HealthCheckResult]:
        """
        Check health of the provider by testing all test URLs.
        If a specific URL is provided, only health-check that URL is evaluated.
        Returns a list of HealthCheckResult objects, one for each tested URL.
        """
        if url is not None:
            return [_get_health_for_url(self, url)]
        if not self.test_urls:
            return [
                HealthCheckResult(
                    is_healthy=False,
                    message="No test URLs configured",
                )
            ]

        results = []
        for url in self.test_urls:
            results.append(_get_health_for_url(self, url))
        return results

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name!r})>"
