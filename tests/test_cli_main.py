import argparse
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from product_reviews.cli.main import main
from product_reviews.models import ProviderReviewList, Review, ReviewList
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import ReviewsParseException


@patch("product_reviews.cli.main.logger")
def test_command_list(mock_logger, mock_providers, monkeypatch, capsys):
    """Test CLI list command displays provider information correctly."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"
        description = "Test provider description"
        notes = "Test notes"
        url_regex = r"https?://test\.com/.*"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([TestProvider])

    monkeypatch.setattr(sys, "argv", ["product-reviews", "list"])
    main()
    captured = capsys.readouterr()

    assert "*" * 50 in captured.out
    assert "Name: TestProvider" in captured.out
    assert "Description: Test provider description" in captured.out
    assert "Notes: Test notes" in captured.out


@patch("product_reviews.cli.main.ProductReviewsService.parse_reviews")
@patch("product_reviews.cli.main.logger")
def test_command_scrape_success(mock_logger, mock_parse, monkeypatch, capsys):
    """Test CLI scrape command successfully extracts and displays reviews."""
    mock_reviews = [Review(rating=5.0, text="Great", created_at=datetime(2020, 1, 1))]
    mock_parse.return_value = ProviderReviewList(provider="TestProvider", reviews=mock_reviews)

    monkeypatch.setattr(sys, "argv", ["product-reviews", "scrape", "https://test.com"])
    main()
    captured = capsys.readouterr()

    assert "Provider: TestProvider" in captured.out
    assert "Count: 1" in captured.out
    mock_parse.assert_called_once_with("https://test.com")


@patch("product_reviews.cli.main.ProductReviewsService.parse_reviews")
@patch("product_reviews.cli.main.logger")
def test_command_scrape_parse_exception(mock_logger, mock_parse, monkeypatch, capsys):
    """Test CLI scrape command handles ReviewsParseException and exits with error code 1."""
    exception = ReviewsParseException("Parse failed")
    cause_exception = Exception("Mock cause")
    exception.__cause__ = cause_exception
    mock_parse.side_effect = exception

    monkeypatch.setattr(sys, "argv", ["product-reviews", "scrape", "https://test.com"])
    with pytest.raises(SystemExit) as excinfo:
        main()

    captured = capsys.readouterr()
    assert "Can't parse reviews. Caused by Exception('Mock cause')" in captured.out
    assert excinfo.value.code == 1
    mock_parse.assert_called_once_with("https://test.com")


@patch("product_reviews.cli.main.ProductReviewsService.parse_reviews")
@patch("product_reviews.cli.main.logger")
def test_command_scrape_general_exception(mock_logger, mock_parse, monkeypatch, capsys):
    """Test CLI scrape command raises general exceptions without handling them."""
    mock_parse.side_effect = Exception("General error")

    monkeypatch.setattr(sys, "argv", ["product-reviews", "scrape", "https://test.com"])
    with pytest.raises(Exception, match="General error"):
        main()

    captured = capsys.readouterr()
    assert captured.out is not None
    mock_parse.assert_called_once_with("https://test.com")


@patch("product_reviews.cli.main.run_health_checks")
@patch("product_reviews.cli.main.logger")
def test_command_health_success(mock_logger, mock_health, mock_providers, monkeypatch):
    """Test CLI health command exits with code 0 when health checks pass."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([TestProvider])
    mock_health.return_value = True

    monkeypatch.setattr(sys, "argv", ["product-reviews", "health", "--provider", "TestProvider"])
    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 0
    mock_health.assert_called_once()


@patch("product_reviews.cli.main.run_health_checks")
@patch("product_reviews.cli.main.logger")
def test_command_health_provider_not_found(mock_logger, mock_health, mock_providers, monkeypatch, capsys):
    """Test CLI health command displays error and exits with code 1 when provider not found."""

    class TestProvider(BaseReviewsProvider):
        name = "TestProvider"

        def get_reviews(self, url: str) -> ReviewList:
            return ReviewList(reviews=[])

    mock_providers([TestProvider])

    monkeypatch.setattr(sys, "argv", ["product-reviews", "health", "--provider", "NonExistent"])
    with pytest.raises(SystemExit) as excinfo:
        main()

    captured = capsys.readouterr()
    assert "Error: Provider 'NonExistent' not found" in captured.out
    assert excinfo.value.code == 1
    mock_health.assert_not_called()


@patch("product_reviews.cli.main.argparse.ArgumentParser")
@patch("product_reviews.cli.main.logger")
def test_main_no_command(mock_logger, mock_parser):
    """Test CLI main function prints help and exits when no command provided."""
    mock_instance = Mock()
    mock_parser.return_value = mock_instance
    mock_instance.parse_args.return_value = argparse.Namespace(command=None)
    mock_instance.print_help.return_value = None

    with patch("sys.exit") as mock_exit:
        main()

        mock_instance.print_help.assert_called_once()
        mock_exit.assert_called_once_with(1)
        mock_parser.assert_called_once()
        mock_instance.parse_args.assert_called_once()


@patch("product_reviews.cli.main.argparse.ArgumentParser")
@patch("product_reviews.cli.main.logger")
def test_main_scrape_command(mock_logger, mock_parser):
    """Test CLI main function calls command_scrape when scrape command provided."""
    mock_instance = Mock()
    mock_parser.return_value = mock_instance
    mock_instance.parse_args.return_value = argparse.Namespace(command="scrape", url="https://test.com")

    with patch("product_reviews.cli.main.command_scrape") as mock_scrape:
        main()

        mock_scrape.assert_called_once_with(argparse.Namespace(command="scrape", url="https://test.com"))
        mock_parser.assert_called_once()
        mock_instance.parse_args.assert_called_once()


@patch("product_reviews.cli.main.argparse.ArgumentParser")
@patch("product_reviews.cli.main.logger")
def test_main_health_command(mock_logger, mock_parser):
    """Test CLI main function calls command_health when health command provided."""
    mock_instance = Mock()
    mock_parser.return_value = mock_instance
    mock_instance.parse_args.return_value = argparse.Namespace(command="health", provider=None)

    with patch("product_reviews.cli.main.command_health") as mock_health:
        main()

        mock_health.assert_called_once_with(argparse.Namespace(command="health", provider=None))
        mock_parser.assert_called_once()
        mock_instance.parse_args.assert_called_once()


@patch("product_reviews.cli.main.argparse.ArgumentParser")
@patch("product_reviews.cli.main.logger")
def test_main_list_command(mock_logger, mock_parser):
    """Test CLI main function calls command_list when list command provided."""
    mock_instance = Mock()
    mock_parser.return_value = mock_instance
    mock_instance.parse_args.return_value = argparse.Namespace(command="list")

    with patch("product_reviews.cli.main.command_list") as mock_list:
        main()

        mock_list.assert_called_once_with(argparse.Namespace(command="list"))
        mock_parser.assert_called_once()
        mock_instance.parse_args.assert_called_once()
