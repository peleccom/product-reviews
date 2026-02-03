import json
from unittest.mock import Mock, patch

import pytest

from product_reviews.providers.exceptions import NoMatchedProvidersException
from product_reviews.providers.providers.dummy.provider import DummyReviewsProvider
from product_reviews.providers.registry import Registry
from product_reviews.reviews import ProductReviewsService


def test_end_to_end_dummy_provider_workflow(tmp_path):
    """Test end-to-end workflow with dummy provider."""
    test_data = {"items": [{"text": "Excellent product", "rating": 5.0, "created_at": "2020-01-01T10:00:00"}]}

    test_file = tmp_path / "test_reviews.json"
    test_file.write_text(json.dumps(test_data))

    service = ProductReviewsService()

    reviews = service.parse_reviews(f"jsonf://{test_file}")

    assert reviews.provider == "JSON FS"
    assert reviews.count() == 1
    assert reviews.reviews[0].text == "Excellent product"
    assert reviews.reviews[0].rating == 5.0


def test_end_to_end_provider_listing():
    """Test end-to-end provider listing functionality."""
    service = ProductReviewsService()

    providers = service.list_providers()
    # Ensure providers are actually loaded
    assert len(providers) > 0

    provider_names = service.get_provider_names()

    assert len(provider_names) > 0
    assert "dummy" in provider_names
    assert "JSON FS" in provider_names


@patch("product_reviews.reviews._check_matched_provider")
def test_end_to_end_error_handling(mock_check):
    """Test end-to-end error handling for unmatched providers."""
    mock_check.return_value = None

    service = ProductReviewsService()

    with pytest.raises(NoMatchedProvidersException):
        service.parse_reviews("https://unknown-provider.com/product")


def test_end_to_end_provider_selection():
    """Test end-to-end provider selection functionality."""

    mock_registry = Mock(spec=Registry)
    mock_registry.get_provider_for_url.return_value = DummyReviewsProvider
    mock_registry.get_provider.return_value = DummyReviewsProvider()

    service = ProductReviewsService(registry=mock_registry)

    url = "https://example.com/reviews/test"
    provider_class = service.get_provider_for_url(url)
    assert provider_class == DummyReviewsProvider

    provider_instance = service.get_provider("dummy")
    assert provider_instance.__class__.__name__ == "DummyReviewsProvider"


def test_multiple_provider_types_loaded():
    """Test multiple provider types are loaded correctly."""
    service = ProductReviewsService()

    all_providers = service.list_providers()

    assert len(all_providers) >= 2
    provider_names = [p.name for p in all_providers]

    assert "dummy" in provider_names
    assert "JSON FS" in provider_names


def test_default_plugins_available_with_custom_plugins_dir(tmp_path, monkeypatch):
    """Test that default plugins (dummy and JSON FS) are available when CUSTOM_PLUGINS_DIR is set."""
    custom_plugins_dir = tmp_path / "custom_plugins"
    custom_plugins_dir.mkdir()

    monkeypatch.setenv("PRODUCT_REVIEWS_PLUGINS_DIR", str(custom_plugins_dir))

    service = ProductReviewsService()

    provider_names = service.get_provider_names()

    assert "dummy" in provider_names, "dummy provider should be available"
    assert "JSON FS" in provider_names, "JSON FS provider should be available"
