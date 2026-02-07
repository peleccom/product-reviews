from datetime import datetime
from typing import ClassVar
from unittest.mock import MagicMock, patch

from product_reviews.cli.commands.command_health import get_all_providers, main, run_health_checks
from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider


class MockHealthyProvider(BaseReviewsProvider):
    name = "HealthyProvider"
    test_urls: ClassVar[list[str]] = ["https://healthy.example/test"]

    def get_reviews(self, url: str) -> list[Review]:
        # Return a valid non-empty list to simulate healthy results
        return [Review(rating=5.0, text="ok", created_at=datetime.now())]


class MockUnhealthyProvider(BaseReviewsProvider):
    name = "UnhealthyProvider"
    test_urls: ClassVar[list[str]] = ["https://unhealthy.example/test"]

    def get_reviews(self, url: str) -> list[Review]:
        # Return a list with a single invalid review (missing rating)
        return [Review(rating=None, created_at=datetime.now())]


def test_get_all_providers_filters_ozon_by(mock_providers):
    """Test get_all_providers filters out ozon_by provider."""

    class OzonProvider(BaseReviewsProvider):
        name = "ozon_by"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    class OtherProvider(BaseReviewsProvider):
        name = "OtherProvider"

        def get_reviews(self, url: str) -> list[Review]:
            return []

    mock_providers([OzonProvider, OtherProvider])

    result = get_all_providers()

    assert len(result) == 1
    assert result[0].name == "OtherProvider"


@patch("product_reviews.cli.commands.command_health.get_all_providers")
@patch("product_reviews.cli.commands.command_health.console")
def test_run_health_checks_all_healthy(mock_console, mock_providers):
    """Test run_health_checks returns True when all providers are healthy."""
    mock_providers.return_value = [MockHealthyProvider]
    mock_console.status.return_value.__enter__ = MagicMock()
    mock_console.status.return_value.__exit__ = MagicMock()

    result = run_health_checks()

    assert result is True
    mock_console.print.assert_called_once()


@patch("product_reviews.cli.commands.command_health.get_all_providers")
@patch("product_reviews.cli.commands.command_health.console")
def test_run_health_checks_some_unhealthy(mock_console, mock_providers):
    """Test run_health_checks returns False when some providers are unhealthy."""
    mock_providers.return_value = [MockHealthyProvider, MockUnhealthyProvider]
    mock_console.status.return_value.__enter__ = MagicMock()
    mock_console.status.return_value.__exit__ = MagicMock()

    result = run_health_checks()

    assert result is False
    mock_console.print.assert_called_once()


@patch("product_reviews.cli.commands.command_health.get_all_providers")
@patch("product_reviews.cli.commands.command_health.console")
def test_run_health_checks_with_custom_providers(mock_console, mock_providers):
    """Test run_health_checks with custom provider list."""
    providers = [MockHealthyProvider]

    result = run_health_checks(providers)

    assert result is True
    mock_providers.assert_not_called()


@patch("product_reviews.cli.commands.command_health.run_health_checks")
def test_health_check_main_all_healthy(mock_health_checks):
    """Test health check main function returns 0 when all healthy."""
    mock_health_checks.return_value = True

    result = main()

    assert result == 0
    mock_health_checks.assert_called_once()


@patch("product_reviews.cli.commands.command_health.run_health_checks")
def test_health_check_main_some_unhealthy(mock_health_checks):
    """Test health check main function returns 1 when some unhealthy."""
    mock_health_checks.return_value = False

    result = main()

    assert result == 1
    mock_health_checks.assert_called_once()


@patch("product_reviews.cli.commands.command_health.run_health_checks")
@patch("product_reviews.cli.commands.command_health.console")
def test_health_check_main_exception(mock_console, mock_health_checks):
    """Test health check main function handles exceptions gracefully."""
    mock_health_checks.side_effect = Exception("Test error")

    result = main()

    assert result == 2
    mock_console.print.assert_called_once()
    assert "Error running health checks" in mock_console.print.call_args[0][0]
