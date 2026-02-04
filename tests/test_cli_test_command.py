"""Tests for test_command module."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from product_reviews.cli.test_command import command_test, get_provider_by_name, record_provider
from product_reviews.providers.providers.dummy.provider import DummyReviewsProvider
from product_reviews.testing.cache import ResponseCache


class TestGetProviderByName:
    """Tests for get_provider_by_name function."""

    def test_get_provider_by_name_found(self):
        """Test getting a provider by name when it exists."""
        provider = get_provider_by_name("dummy")
        assert provider is not None
        assert provider().name == "dummy"

    def test_get_provider_by_name_not_found(self):
        """Test getting a provider by name when it doesn't exist."""
        provider = get_provider_by_name("nonexistent")
        assert provider is None


class TestRecordProvider:
    """Tests for record_provider function."""

    @patch("product_reviews.cli.test_command.ResponseRecorder")
    def test_record_provider_success(self, mock_recorder_class):
        """Test recording provider when successful."""
        mock_recorder = MagicMock()
        mock_recorder_class.return_value = mock_recorder

        # Mock successful recording
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.reviews_count = 5
        mock_result.test_case = "test_url_000"
        mock_recorder.record_provider.return_value = ([mock_result], [])

        result = record_provider(DummyReviewsProvider)

        assert result is True
        mock_recorder.record_provider.assert_called_once()

    @patch("product_reviews.cli.test_command.ResponseRecorder")
    def test_record_provider_failure(self, mock_recorder_class):
        """Test recording provider when it fails."""
        mock_recorder = MagicMock()
        mock_recorder_class.return_value = mock_recorder

        # Mock failed recording
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.test_case = "test_url_000"
        mock_result.error_message = "Failed to parse"
        mock_recorder.record_provider.return_value = ([], [mock_result])

        result = record_provider(DummyReviewsProvider)

        assert result is False


class TestCommandTest:
    """Tests for command_test function."""

    @patch("product_reviews.cli.test_command.record_provider")
    @patch("product_reviews.cli.test_command.ResponseCache")
    def test_command_test_with_provider_class(self, mock_cache_class, mock_record):
        """Test command_test with --provider-class for external provider."""
        mock_cache = MagicMock()
        mock_cache_class.return_value = mock_cache
        mock_cache.has_cached_responses.return_value = False
        mock_record.return_value = True

        args = MagicMock()
        args.provider_class = "product_reviews.providers.providers.dummy.provider.DummyReviewsProvider"
        args.all = False
        args.provider = None
        args.re_record = False
        args.cache_dir = None

        result = command_test(args)

        assert result == 0
        mock_record.assert_called_once()

    @patch("product_reviews.cli.test_command.record_provider")
    @patch("product_reviews.cli.test_command.ResponseCache")
    def test_command_test_with_internal_provider(self, mock_cache_class, mock_record):
        """Test command_test with --provider for internal provider."""
        mock_cache = MagicMock()
        mock_cache_class.return_value = mock_cache
        mock_cache.has_cached_responses.return_value = True
        mock_record.return_value = True

        args = MagicMock()
        args.provider_class = None
        args.all = False
        args.provider = "dummy"
        args.re_record = False
        args.cache_dir = None

        result = command_test(args)

        assert result == 0

    @patch("product_reviews.cli.test_command.ResponseCache")
    def test_command_test_provider_not_found(self, mock_cache_class):
        """Test command_test when provider is not found."""
        mock_cache = MagicMock()
        mock_cache_class.return_value = mock_cache

        args = MagicMock()
        args.provider_class = None
        args.all = False
        args.provider = "nonexistent_provider"
        args.re_record = False
        args.cache_dir = None

        result = command_test(args)

        assert result == 1

    @patch("product_reviews.cli.test_command.ResponseCache")
    def test_command_test_no_provider_specified(self, mock_cache_class):
        """Test command_test when no provider is specified."""
        mock_cache = MagicMock()
        mock_cache_class.return_value = mock_cache

        args = MagicMock()
        args.provider_class = None
        args.all = False
        args.provider = None
        args.re_record = False
        args.cache_dir = None

        result = command_test(args)

        assert result == 1

    @patch("product_reviews.cli.test_command.record_provider")
    @patch("product_reviews.cli.test_command.ResponseCache")
    def test_command_test_recording_failure(self, mock_cache_class, mock_record):
        """Test command_test when recording fails."""
        mock_cache = MagicMock()
        mock_cache_class.return_value = mock_cache
        mock_cache.has_cached_responses.return_value = False
        mock_record.return_value = False

        args = MagicMock()
        args.provider_class = "product_reviews.providers.providers.dummy.provider.DummyReviewsProvider"
        args.all = False
        args.provider = None
        args.re_record = False
        args.cache_dir = None

        result = command_test(args)

        assert result == 1
