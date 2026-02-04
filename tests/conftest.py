from unittest.mock import patch

import pytest
import responses

from product_reviews.testing.cache import ResponseCache


@pytest.fixture
def mock_providers():
    with patch("product_reviews.providers.loaders.iter_all_providers") as mock:

        def factory(values=None):
            if not values:
                values = []
            mock.return_value = (x for x in values)
            return mock

        yield factory


@pytest.fixture
def response_cache():
    """Provide a ResponseCache instance."""
    return ResponseCache()


@pytest.fixture
def mock_http_responses(response_cache):
    """
    Mock HTTP responses using cached data.
    Pytest should ALWAYS use cached data. If no cache exists, fail the test.
    """
    # Check if any cached responses exist
    providers_with_cache = response_cache.list_providers()

    if not providers_with_cache:
        pytest.fail(
            "No cached responses found. Run: product-reviews test --provider <provider_name> to record responses"
        )

    # Setup responses mock with cached data
    with responses.RequestsMock() as rsps:
        for provider in providers_with_cache:
            for test_case in response_cache.list_test_cases(provider):
                cached = response_cache.load_response(provider, test_case)
                if cached:
                    # Determine method from URL or default to GET
                    method = responses.GET

                    # Add the mock response
                    rsps.add(
                        method,
                        cached.url,
                        body=cached.body,
                        status=cached.status_code,
                        content_type=cached.headers.get("Content-Type", "application/json"),
                    )

        yield rsps


@pytest.fixture(autouse=True)
def auto_mock_http(request, response_cache):
    """
    Automatically mock HTTP requests for all tests.
    Tests should use cached data only.
    """
    # Skip auto-mock for specific tests that mark no_mock
    if request.node.get_closest_marker("no_auto_mock"):
        yield
        return

    # Check if we have cached responses
    providers_with_cache = response_cache.list_providers()

    if not providers_with_cache:
        # No cache - skip auto-mock but warn
        yield
        return

    # Mock HTTP responses for tests that need it
    with responses.RequestsMock() as rsps:
        for provider in providers_with_cache:
            for test_case in response_cache.list_test_cases(provider):
                cached = response_cache.load_response(provider, test_case)
                if cached:
                    rsps.add(
                        responses.GET,
                        cached.url,
                        body=cached.body,
                        status=cached.status_code,
                        content_type=cached.headers.get("Content-Type", "application/json"),
                    )
        yield rsps


def pytest_generate_tests(metafunc):
    """
    Dynamically generate test cases from cached responses.
    This creates tests for each cached response.
    """
    if "provider_test_case" in metafunc.fixturenames:
        cache = ResponseCache()
        test_cases = []

        for provider in cache.list_providers():
            for test_case in cache.list_test_cases(provider):
                cached = cache.load_response(provider, test_case)
                if cached:
                    test_cases.append((provider, test_case, cached))

        if not test_cases:
            pytest.skip("No cached responses found. Run: product-reviews test --provider <name>")

        metafunc.parametrize("provider_test_case", test_cases, ids=[f"{p}_{t}" for p, t, _ in test_cases])
