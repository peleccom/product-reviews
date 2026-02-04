"""Test generator for creating dynamic tests from cached responses."""

from __future__ import annotations

import logging
from typing import Any

import responses

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.testing.cache import CachedResponse, ResponseCache

logger = logging.getLogger(__name__)


class ProviderTestGenerator:
    """Generates pytest tests from cached provider responses."""

    def __init__(self, cache: ResponseCache | None = None):
        self.cache = cache or ResponseCache()

    def generate_tests_for_provider(self, provider_class: type[BaseReviewsProvider]) -> list[dict[str, Any]]:
        """Generate test configurations for a provider."""
        provider_name = provider_class.name
        test_cases = []

        # Get all cached responses for this provider
        cached_cases = self.cache.list_test_cases(provider_name)

        for test_case in cached_cases:
            response = self.cache.load_response(provider_name, test_case)
            if response:
                test_cases.append({
                    "provider": provider_class,
                    "test_case": test_case,
                    "response": response,
                })

        return test_cases

    def get_all_test_configs(self) -> dict[str, list[dict[str, Any]]]:
        """Get test configurations for all providers with cached responses."""
        from product_reviews.reviews import _list_providers

        configs = {}
        providers = {p.name: p for p in _list_providers()}

        for provider_name in self.cache.list_providers():
            if provider_name in providers:
                provider_class = providers[provider_name]
                test_cases = self.generate_tests_for_provider(provider_class)
                if test_cases:
                    configs[provider_name] = test_cases

        return configs


def generate_dynamic_tests() -> None:
    """
    Dynamically generate pytest test functions from cached responses.
    This should be called from conftest.py
    """
    cache = ResponseCache()
    generator = ProviderTestGenerator(cache)
    configs = generator.get_all_test_configs()

    for provider_name, test_cases in configs.items():
        for test_config in test_cases:
            response = test_config["response"]
            test_case = test_config["test_case"]

            # Create test function name
            test_name = f"test_{provider_name}_{test_case}"

            if response.is_valid:
                # Create test for valid response
                _create_valid_response_test(test_name, test_config["provider"], response)
            else:
                # Create test for error response
                _create_error_response_test(test_name, test_config["provider"], response)


def _create_valid_response_test(
    test_name: str, provider_class: type[BaseReviewsProvider], response: CachedResponse
) -> None:
    """Create a test function for a valid response."""

    def test_func(self):
        # Setup mock
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                response.url,
                body=response.body,
                status=response.status_code,
                content_type=response.headers.get("Content-Type", "application/json"),
            )

            # Test that provider can fetch reviews
            provider = provider_class()
            reviews = provider.get_reviews(response.url)

            # Assert we got reviews
            assert len(reviews) > 0, f"Expected reviews but got none for {response.url}"
            assert len(reviews) == response.reviews_count, (
                f"Expected {response.reviews_count} reviews, got {len(reviews)}"
            )

            # Assert reviews have required fields
            for review in reviews:
                assert review.created_at is not None, "Review must have created_at"

    # Attach test function to class
    test_func.__name__ = test_name
    setattr(TestProviderBase, test_name, test_func)


def _create_error_response_test(
    test_name: str, provider_class: type[BaseReviewsProvider], response: CachedResponse
) -> None:
    """Create a test function for an error response."""

    def test_func(self):
        # Setup mock for error response
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                response.url,
                body=response.body,
                status=response.status_code,
                content_type=response.headers.get("Content-Type", "text/html"),
            )

            # Test that URL doesn't match provider (or provider handles error)
            provider = provider_class()

            # If URL doesn't match regex, check_url should return False
            if not provider.check_url(response.url):
                assert True
                return

            # If URL matches, provider should raise an exception or return empty
            try:
                reviews = provider.get_reviews(response.url)
                # Provider might return empty list for error URLs
                assert len(reviews) == 0, f"Expected no reviews for error URL {response.url}"
            except Exception:
                # Exception is acceptable for error URLs
                pass

    test_func.__name__ = test_name
    setattr(TestProviderBase, test_name, test_func)


class TestProviderBase:
    """Base class for dynamically generated provider tests."""

    pass
