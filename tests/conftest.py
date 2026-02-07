"""Pytest configuration for product-reviews."""

from unittest.mock import patch

import pytest


@pytest.fixture
def mock_providers():
    """Fixture to mock provider iteration for testing."""
    with patch("product_reviews.providers.loaders.iter_all_providers") as mock:

        def factory(values=None):
            if not values:
                values = []
            mock.return_value = (x for x in values)
            return mock

        yield factory
