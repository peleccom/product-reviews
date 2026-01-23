from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import ClassVar

from product_reviews.models import HealthCheckResult, ReviewList

logger = logging.getLogger(__name__)


class BaseReviewsProvider(ABC):
    name: ClassVar[str]
    description: ClassVar[str]
    notes: ClassVar[str | None]
    url_regex: ClassVar[str | re.Pattern[str]]
    test_urls: ClassVar[list[str]] = []

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
    def get_reviews(self, url: str) -> ReviewList:
        raise NotImplementedError

    def check_health(self) -> list[HealthCheckResult]:
        """
        Check health of the provider by testing all test URLs.
        Returns a list of HealthCheckResult objects, one for each test URL.
        """
        if not self.test_urls:
            return [
                HealthCheckResult(
                    is_healthy=False,
                    message="No test URLs configured",
                )
            ]

        results = []
        for url in self.test_urls:
            try:
                review_list = self.get_reviews(url)
                if not review_list or not review_list.reviews:
                    results.append(
                        HealthCheckResult(
                            is_healthy=False,
                            message="No reviews found",
                            url=url,
                            reviews_count=0,
                        )
                    )
                else:
                    results.append(
                        HealthCheckResult(
                            is_healthy=True,
                            message="Successfully fetched reviews",
                            url=url,
                            reviews_count=review_list.count(),
                        )
                    )
            except Exception as e:
                results.append(
                    HealthCheckResult(
                        is_healthy=False,
                        message=f"Error fetching reviews: {e!s}",
                        url=url,
                        reviews_count=0,
                    )
                )
        return results

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name!r})>"
