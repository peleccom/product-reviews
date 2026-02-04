"""Recorder for capturing real API responses during testing."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import requests

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.testing.cache import ResponseCache

logger = logging.getLogger(__name__)


@dataclass
class RecordingResult:
    """Result of recording a single URL."""

    url: str
    test_case: str
    success: bool
    reviews_count: int = 0
    error_message: str | None = None
    status_code: int | None = None


class ResponseRecorder:
    """Records real API responses and caches them for testing."""

    def __init__(self, cache: ResponseCache | None = None):
        self.cache = cache or ResponseCache()
        self.session = requests.Session()

    def record_provider(
        self, provider_class: type[BaseReviewsProvider], re_record: bool = False
    ) -> tuple[list[RecordingResult], list[RecordingResult]]:
        """
        Record responses for all test URLs of a provider.

        Returns:
            Tuple of (successful_recordings, failed_recordings)
            If any test_url fails, failed_recordings will contain the failures.
        """
        provider = provider_class()
        provider_name = provider.name

        if re_record:
            self.cache.clear_provider(provider_name)

        successful = []
        failed = []

        # Record test_urls (must succeed)
        for i, url in enumerate(provider.test_urls):
            test_case = f"test_url_{i:03d}"
            result = self._record_test_url(provider, url, test_case)

            if result.success:
                successful.append(result)
            else:
                failed.append(result)
                logger.error(f"Failed to record {url}: {result.error_message}")

        # If any test_url failed, return early with failures
        if failed:
            return successful, failed

        # Record invalid_urls (errors expected, always cache)
        for i, url in enumerate(getattr(provider, "test_invalid_urls", [])):
            test_case = f"invalid_url_{i:03d}"
            result = self._record_invalid_url(url, test_case, provider_name)
            successful.append(result)

        return successful, failed

    def _record_test_url(self, provider: BaseReviewsProvider, url: str, test_case: str) -> RecordingResult:
        """Record a test URL. Must return valid reviews to be cached."""
        try:
            # Call the provider's get_reviews method (real API call)
            reviews = provider.get_reviews(url)

            # Validate reviews
            if not reviews:
                return RecordingResult(
                    url=url,
                    test_case=test_case,
                    success=False,
                    error_message="No reviews found",
                )

            if not self._validate_reviews(reviews):
                return RecordingResult(
                    url=url,
                    test_case=test_case,
                    success=False,
                    error_message="Reviews validation failed",
                )

            # Record the HTTP response
            # We need to re-fetch to get the raw response since get_reviews() doesn't return it
            http_response = self._fetch_response(url, provider)

            if http_response is None:
                return RecordingResult(
                    url=url,
                    test_case=test_case,
                    success=False,
                    error_message="Could not fetch raw response",
                )

            # Cache the successful response
            # Use local variable to help type checker
            status: int = http_response.status_code  # type: ignore[assignment]
            hdrs: dict[str, str] = dict(http_response.headers)
            body: str = http_response.text
            self.cache.save_response(
                provider=provider.name,
                test_case=test_case,
                url=url,
                status_code=status,
                headers=hdrs,
                body=body,
                is_valid=True,
                reviews=reviews,
            )

            return RecordingResult(
                url=url,
                test_case=test_case,
                success=True,
                reviews_count=len(reviews),
                status_code=http_response.status_code,
            )

        except Exception as e:
            return RecordingResult(
                url=url,
                test_case=test_case,
                success=False,
                error_message=str(e),
            )

    def _record_invalid_url(self, url: str, test_case: str, provider_name: str) -> RecordingResult:
        """Record an invalid URL. Always caches the error response."""
        try:
            response = self.session.get(url, timeout=30)

            self.cache.save_response(
                provider=provider_name,
                test_case=test_case,
                url=url,
                status_code=response.status_code,
                headers=dict(response.headers),
                body=response.text,
                is_valid=False,
                reviews=None,
                error_message=f"HTTP {response.status_code}",
            )

            return RecordingResult(
                url=url,
                test_case=test_case,
                success=True,
                status_code=response.status_code,
            )

        except Exception as e:
            # Cache the exception as an error
            self.cache.save_response(
                provider=provider_name,
                test_case=test_case,
                url=url,
                status_code=0,
                headers={},
                body=str(e),
                is_valid=False,
                reviews=None,
                error_message=str(e),
            )

            return RecordingResult(
                url=url,
                test_case=test_case,
                success=True,
                error_message=str(e),
            )

    def _validate_reviews(self, reviews: list[Review]) -> bool:
        """Validate that reviews have required fields."""
        if not reviews:
            return False

        for review in reviews:
            if review.created_at is None:
                return False
            # rating can be None, that's allowed

        return True

    def _fetch_response(self, url: str, provider: BaseReviewsProvider) -> requests.Response | None:
        """
        Fetch the raw HTTP response for a URL.
        This is a best-effort attempt to get the raw response.
        """
        try:
            # Try to determine the API URL from the provider
            # This is provider-specific, so we use a generic approach
            response = self.session.get(url, timeout=30, allow_redirects=True)
            return response
        except Exception as e:
            logger.warning(f"Could not fetch raw response for {url}: {e}")
            return None

    def record_custom_url(
        self,
        provider_class: type[BaseReviewsProvider],
        url: str,
        test_case: str,
    ) -> RecordingResult:
        """Record a custom URL for a provider."""
        provider = provider_class()
        return self._record_test_url(provider, url, test_case)
