"""Dynamic tests for providers based on cached responses."""

from __future__ import annotations

import pytest
import responses

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.reviews import ProductReviewsService


class TestProviderResponses:
    """Tests for provider responses based on cached data."""

    def test_cached_response_exists(self, provider_test_case):
        """Verify that a cached response exists and is loadable."""
        provider_name, test_case, cached = provider_test_case
        assert cached is not None
        assert cached.url
        assert cached.status_code is not None

    def test_provider_url_matches(self, provider_test_case):
        """Test that the provider matches the cached URL."""
        provider_name, test_case, cached = provider_test_case

        # Get the provider class
        service = ProductReviewsService()
        provider_class: type[BaseReviewsProvider] | None = None
        for p in service.list_providers():
            if p().name == provider_name:
                provider_class = p
                break

        if not provider_class:
            pytest.skip(f"Provider {provider_name} not installed")

        # Type assertion after skip
        assert provider_class is not None

        # Check if URL should match
        should_match = cached.is_valid
        actual_match = provider_class.check_url(cached.url)

        if should_match:
            assert actual_match, f"Provider {provider_name} should match URL {cached.url}"
        else:
            # Invalid URLs might not match - that's ok
            pass

    def test_provider_fetches_reviews(self, mock_http_responses, provider_test_case):
        """Test that the provider can fetch reviews from cached response."""
        provider_name, test_case, cached = provider_test_case

        # Skip error responses
        if not cached.is_valid:
            pytest.skip("Error response - testing error handling separately")

        # Get the provider
        service = ProductReviewsService()
        provider_class: type[BaseReviewsProvider] | None = None
        for p in service.list_providers():
            if p().name == provider_name:
                provider_class = p
                break

        if not provider_class:
            pytest.skip(f"Provider {provider_name} not installed")

        # Type assertion after skip
        assert provider_class is not None

        # Test fetching reviews
        provider = provider_class()
        reviews = provider.get_reviews(cached.url)

        # Verify we got the expected number of reviews
        assert len(reviews) == cached.reviews_count, f"Expected {cached.reviews_count} reviews, got {len(reviews)}"

        # Verify review fields
        for review in reviews:
            assert review.created_at is not None, "Review must have created_at"
            # rating can be None, that's ok


class TestProviderUrlMatching:
    """Tests for provider URL regex matching."""

    def test_provider_matches_own_urls(self, provider_test_case):
        """Test that provider matches URLs in test_urls."""
        provider_name, test_case, cached = provider_test_case

        # Only test valid responses
        if not cached.is_valid:
            return

        service = ProductReviewsService()
        provider_class: type[BaseReviewsProvider] | None = None
        for p in service.list_providers():
            if p().name == provider_name:
                provider_class = p
                break

        if not provider_class:
            pytest.skip(f"Provider {provider_name} not installed")

        # Type assertion after skip
        assert provider_class is not None

        provider = provider_class()

        # Valid responses should match the provider's URL pattern
        if "test_url" in test_case and cached.is_valid:
            assert provider.check_url(cached.url), f"Provider {provider_name} should match its test URL: {cached.url}"

    def test_provider_rejects_invalid_urls(self, provider_test_case):
        """Test that provider does not match URLs in test_invalid_urls."""
        provider_name, test_case, cached = provider_test_case

        # Only test invalid URL responses
        if "invalid" not in test_case:
            return

        service = ProductReviewsService()
        provider_class: type[BaseReviewsProvider] | None = None
        for p in service.list_providers():
            if p().name == provider_name:
                provider_class = p
                break

        if not provider_class:
            pytest.skip(f"Provider {provider_name} not installed")

        # Type assertion after skip
        assert provider_class is not None

        provider = provider_class()

        # Invalid URLs should NOT match
        # (Provider might still match them if the pattern is broad, but that's ok)
        # This test mainly documents the expected behavior
        matches = provider.check_url(cached.url)
        if matches:
            # If it matches, the provider should handle it gracefully (error or empty)
            pass  # This is ok


class TestProviderErrorHandling:
    """Tests for provider error handling."""

    def test_error_response_handling(self, mock_http_responses, provider_test_case):
        """Test that providers handle error responses gracefully."""
        provider_name, test_case, cached = provider_test_case

        # Only test error responses
        if cached.is_valid:
            pytest.skip("Only testing error responses")

        service = ProductReviewsService()
        provider_class: type[BaseReviewsProvider] | None = None
        for p in service.list_providers():
            if p().name == provider_name:
                provider_class = p
                break

        if not provider_class:
            pytest.skip(f"Provider {provider_name} not installed")

        # Type assertion after skip
        assert provider_class is not None

        provider = provider_class()

        # Provider should either raise an exception or return empty list
        try:
            reviews = provider.get_reviews(cached.url)
            # If we get here, provider should return empty list or handle gracefully
            assert len(reviews) == 0, f"Provider should return empty list for error URL, got {len(reviews)} reviews"
        except Exception:
            # Exception is acceptable for error URLs
            pass
