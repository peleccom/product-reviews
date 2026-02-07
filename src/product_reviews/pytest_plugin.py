"""Pytest plugin for product-reviews testing infrastructure.

This plugin is automatically loaded when product-reviews is installed
(via the ``pytest11`` entry point). It auto-generates tests for every
registered provider based on their ``test_urls`` and ``invalid_urls``.

No test files are required — just install product-reviews and run pytest.
Mock data must be pre-recorded using ``product-reviews test --re-record``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
import requests
import responses

from product_reviews.providers.exceptions import ReviewsParseException
from product_reviews.providers.registry import Registry
from product_reviews.providers.testing import (
    get_mock_storage,
    load_mock_data,
    register_mock_responses,
    validate_reviews,
)

if TYPE_CHECKING:
    from product_reviews.providers.base import BaseReviewsProvider


class ProviderTestError(Exception):
    """Raised when a provider test assertion fails."""


class ProviderTestItem(pytest.Item):
    """A single auto-generated test for a provider URL.

    Runs the provider's ``get_reviews()`` against a URL with mocked HTTP
    responses and validates the returned reviews.
    """

    def __init__(
        self,
        name: str,
        parent: pytest.Collector,
        provider_class: type[BaseReviewsProvider],
        url: str,
        url_index: int,
        expect_error: bool,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, parent, **kwargs)
        self.provider_class = provider_class
        self.url = url
        self.url_index = url_index
        self.expect_error = expect_error

    def runtest(self) -> None:
        """Execute the provider test."""
        provider = self.provider_class()

        if self.expect_error:
            self._run_invalid_url_test(provider)
            return

        self._run_valid_url_test(provider)

    def _run_invalid_url_test(self, provider: BaseReviewsProvider) -> None:
        """Test that an invalid URL raises ReviewsParseException using recorded mock data."""
        storage = get_mock_storage()
        mock_data = load_mock_data(self.provider_class, self.url_index, url_type="invalid", storage=storage)
        captured_data = mock_data.get("captured_data", []) if mock_data else []

        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            register_mock_responses(rsps, captured_data)

            try:
                provider.get_reviews(self.url)
            except ReviewsParseException:
                return
            except requests.exceptions.ConnectionError as e:
                if "Connection refused by Responses" in str(e):
                    msg = (
                        f"No mock data for invalid URL in provider '{self.provider_class.name}'. "
                        "Run 'product-reviews test --re-record' to generate mocks."
                    )
                    raise ProviderTestError(msg) from e
                raise

        msg = f"Expected ReviewsParseException for URL: {self.url}"
        raise ProviderTestError(msg)

    def _run_valid_url_test(self, provider: BaseReviewsProvider) -> None:
        """Test a valid URL using recorded mock data."""
        storage = get_mock_storage()
        mock_data = load_mock_data(self.provider_class, self.url_index, url_type="valid", storage=storage)
        captured_data = mock_data.get("captured_data", []) if mock_data else []

        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            register_mock_responses(rsps, captured_data)

            try:
                reviews = provider.get_reviews(self.url)
            except requests.exceptions.ConnectionError as e:
                if "Connection refused by Responses" in str(e):
                    msg = (
                        f"No mock data for provider '{self.provider_class.name}'. "
                        "Run 'product-reviews test --re-record' to generate mocks."
                    )
                    raise ProviderTestError(msg) from e
                raise

        is_valid, error_msg = validate_reviews(reviews)
        if not is_valid:
            msg = f"Review validation failed for '{self.provider_class.name}': {error_msg}"
            raise ProviderTestError(msg)

    def repr_failure(self, excinfo: pytest.ExceptionInfo[BaseException], style: Any = None) -> str:
        """Provide a concise failure representation."""
        return str(excinfo.value)

    def reportinfo(self) -> tuple[str, None, str]:
        """Provide test location and description for reports."""
        error_suffix = " (expect error)" if self.expect_error else ""
        return "product-reviews", None, f"{self.provider_class.name}: {self.url}{error_suffix}"


class ProviderTestCollector(pytest.Collector):
    """Collector that auto-generates test items for all registered providers."""

    def collect(self) -> list[ProviderTestItem]:
        """Discover providers and yield test items for each URL."""
        items: list[ProviderTestItem] = []
        registry = Registry()

        for _name, provider_class in registry.iter_providers():
            if not provider_class.test_urls and not provider_class.invalid_urls:
                continue
            items.extend(self._collect_provider(provider_class))

        return items

    def _collect_provider(
        self,
        provider_class: type[BaseReviewsProvider],
    ) -> list[ProviderTestItem]:
        """Generate test items for a single provider."""
        items: list[ProviderTestItem] = []
        name = provider_class.name

        for url_index, url in enumerate(provider_class.test_urls):
            items.append(
                ProviderTestItem.from_parent(
                    self,
                    name=f"{name}[valid-{url}]",
                    provider_class=provider_class,
                    url=url,
                    url_index=url_index,
                    expect_error=False,
                )
            )

        for url_index, url in enumerate(provider_class.invalid_urls):
            items.append(
                ProviderTestItem.from_parent(
                    self,
                    name=f"{name}[invalid-{url}]",
                    provider_class=provider_class,
                    url=url,
                    url_index=url_index,
                    expect_error=True,
                )
            )

        return items


def pytest_collection_modifyitems(
    session: pytest.Session,
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Inject auto-generated provider tests into the test suite."""
    collector = ProviderTestCollector.from_parent(session, name="product-reviews", nodeid="product-reviews")
    items.extend(collector.collect())
