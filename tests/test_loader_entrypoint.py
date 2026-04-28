"""Tests for loader_entrypoint module."""

import types
from unittest.mock import MagicMock, patch

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.loader_entrypoint import (
    ENTRY_POINT_GROUP,
    load_entry_point_providers,
)


class MockProvider1(BaseReviewsProvider):
    """Mock provider for testing."""

    name = "mock1"

    def get_reviews(self, url: str):
        return []


class MockProvider2(BaseReviewsProvider):
    """Mock provider for testing."""

    name = "mock2"

    def get_reviews(self, url: str):
        return []


class NotAProvider:
    """Class that is not a provider."""

    pass


def test_entry_point_group_constant():
    """Test ENTRY_POINT_GROUP constant is correct."""
    assert ENTRY_POINT_GROUP == "product_reviews.providers"


def test_load_entry_point_providers_returns_generator():
    """Test load_entry_point_providers returns a generator."""
    result = load_entry_point_providers()

    assert isinstance(result, types.GeneratorType)


@patch("product_reviews.providers.loader_entrypoint.metadata")
def test_load_entry_point_providers_empty(mock_metadata):
    """Test load_entry_point_providers handles empty entry points."""
    mock_eps = MagicMock()
    mock_eps.__iter__ = MagicMock(return_value=iter([]))
    mock_metadata.entry_points.return_value = mock_eps

    result = list(load_entry_point_providers())
    assert result == []


@patch("product_reviews.providers.loader_entrypoint.metadata")
def test_load_entry_point_providers_loads_valid_provider(mock_metadata):
    """Test load_entry_point_providers loads valid provider classes."""
    mock_ep = MagicMock()
    mock_ep.name = "test_provider"
    mock_ep.load.return_value = MockProvider1

    mock_eps = MagicMock()
    mock_eps.__iter__ = MagicMock(return_value=iter([mock_ep]))
    mock_metadata.entry_points.return_value = mock_eps

    result = list(load_entry_point_providers())
    assert len(result) == 1
    assert result[0] is MockProvider1


@patch("product_reviews.providers.loader_entrypoint.metadata")
def test_load_entry_point_providers_skips_non_subclass(mock_metadata):
    """Test load_entry_point_providers skips non-BaseReviewsProvider classes."""
    mock_ep = MagicMock()
    mock_ep.name = "not_a_provider"
    mock_ep.load.return_value = NotAProvider

    mock_eps = MagicMock()
    mock_eps.__iter__ = MagicMock(return_value=iter([mock_ep]))
    mock_metadata.entry_points.return_value = mock_eps

    result = list(load_entry_point_providers())
    assert result == []


@patch("product_reviews.providers.loader_entrypoint.metadata")
def test_load_entry_point_providers_skips_instance(mock_metadata):
    """Test load_entry_point_providers skips provider instances (not classes)."""
    mock_ep = MagicMock()
    mock_ep.name = "provider_instance"
    mock_ep.load.return_value = MockProvider1()

    mock_eps = MagicMock()
    mock_eps.__iter__ = MagicMock(return_value=iter([mock_ep]))
    mock_metadata.entry_points.return_value = mock_eps

    result = list(load_entry_point_providers())
    assert result == []


@patch("product_reviews.providers.loader_entrypoint.metadata")
def test_load_entry_point_providers_multiple_providers(mock_metadata):
    """Test load_entry_point_providers loads multiple providers."""
    mock_ep1 = MagicMock()
    mock_ep1.name = "provider1"
    mock_ep1.load.return_value = MockProvider1

    mock_ep2 = MagicMock()
    mock_ep2.name = "provider2"
    mock_ep2.load.return_value = MockProvider2

    mock_eps = MagicMock()
    mock_eps.__iter__ = MagicMock(return_value=iter([mock_ep1, mock_ep2]))
    mock_metadata.entry_points.return_value = mock_eps

    result = list(load_entry_point_providers())
    assert len(result) == 2
    assert MockProvider1 in result
    assert MockProvider2 in result


@patch("product_reviews.providers.loader_entrypoint.metadata")
def test_load_entry_point_providers_handles_load_error(mock_metadata):
    """Test load_entry_point_providers handles provider load errors gracefully."""
    mock_ep = MagicMock()
    mock_ep.name = "broken_provider"
    mock_ep.load.side_effect = ImportError("Cannot load module")

    mock_eps = MagicMock()
    mock_eps.__iter__ = MagicMock(return_value=iter([mock_ep]))
    mock_metadata.entry_points.return_value = mock_eps

    result = list(load_entry_point_providers())
    assert result == []


@patch("product_reviews.providers.loader_entrypoint.metadata")
def test_load_entry_point_providers_handles_exception(mock_metadata):
    """Test load_entry_point_providers catches exceptions during load."""
    mock_ep = MagicMock()
    mock_ep.name = "exception_provider"
    mock_ep.load.side_effect = RuntimeError("Unexpected error")

    mock_eps = MagicMock()
    mock_eps.__iter__ = MagicMock(return_value=iter([mock_ep]))
    mock_metadata.entry_points.return_value = mock_eps

    result = list(load_entry_point_providers())
    assert result == []
