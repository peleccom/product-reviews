"""Test command for product-reviews CLI."""

from __future__ import annotations

import argparse
import sys

import responses
from rich.console import Console
from rich.table import Table

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import ReviewsParseException
from product_reviews.providers.registry import Registry
from product_reviews.providers.testing import (
    capture_http_requests,
    clear_provider_mocks,
    get_mock_storage,
    load_mock_data,
    register_mock_responses,
    save_mock_response,
    validate_reviews,
)

from .base import BaseCommand

console = Console()


def _test_test_url(
    provider_class: type[BaseReviewsProvider],
    provider: BaseReviewsProvider,
    url: str,
    url_index: int,
    re_record: bool,
) -> tuple[bool, list[str]]:
    """Test a single test URL.

    Args:
        provider_class: The provider class.
        provider: The provider instance.
        url: The test URL.
        url_index: The index of the URL in test_urls list.
        re_record: Whether to force re-recording.

    Returns:
        Tuple of (success, messages).
    """
    provider_name = provider_class.name
    storage = get_mock_storage()

    # Try to load cached mock data
    mock_data = None if re_record else load_mock_data(provider_class, url_index, url_type="valid", storage=storage)
    mock_captured_data = mock_data.get("captured_data", []) if mock_data else []

    if mock_data and mock_captured_data:
        # Use cached mock response
        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            register_mock_responses(rsps, mock_captured_data)
            console.print("  [cyan]Using cached mock response[/cyan]")

            try:
                reviews = provider.get_reviews(url)
            except Exception as e:
                return False, [f"[red]FAIL: Provider '{provider_name}' failed to fetch reviews from {url}: {e}[/red]"]
    else:
        # Make real API call and capture HTTP requests
        console.print("  [yellow]Making real API call (re-recording)[/yellow]")

        try:
            with capture_http_requests() as captured_data:
                reviews = provider.get_reviews(url)
        except Exception as e:
            console.print(f"  [red]Exception during re-recording: {e}[/red]")
            return False, [f"[red]FAIL: Provider '{provider_name}' failed to fetch reviews from {url}: {e}[/red]"]

        if captured_data:
            console.print(f"  [cyan]Captured {len(captured_data)} request(s)[/cyan]")

        # Save mock response
        mock_file = save_mock_response(
            provider_class, url_index, url, reviews, captured_data or [], url_type="valid", storage=storage
        )
        console.print(f"[green]Saved mock response to {mock_file}[/green]")

    is_valid, error_msg = validate_reviews(reviews)
    if not is_valid:
        return False, [f"[red]FAIL: Provider '{provider_name}' review validation failed: {error_msg}[/red]"]

    return True, [f"[green]PASS: Provider '{provider_name}' passed for {url} ({len(reviews)} reviews)[/green]"]


def _test_invalid_url(
    provider_class: type[BaseReviewsProvider],
    provider: BaseReviewsProvider,
    url: str,
    url_index: int,
    re_record: bool,
) -> tuple[bool, list[str]]:
    """Test a single invalid URL.

    Args:
        provider_class: The provider class.
        provider: The provider instance.
        url: The invalid URL.
        url_index: The index of the URL in invalid_urls list.
        re_record: Whether to force re-recording.

    Returns:
        Tuple of (success, messages).
    """
    provider_name = provider_class.name
    storage = get_mock_storage()

    # Try to load cached mock data
    mock_data = None if re_record else load_mock_data(provider_class, url_index, url_type="invalid", storage=storage)
    mock_captured_data = mock_data.get("captured_data", []) if mock_data else []

    if mock_data and mock_captured_data:
        # Use cached mock response
        with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
            register_mock_responses(rsps, mock_captured_data)
            console.print("  [cyan]Using cached mock response[/cyan]")

            try:
                provider.get_reviews(url)
            except ReviewsParseException:
                return True, [f"[green]PASS: Provider '{provider_name}' correctly raised exception for {url}[/green]"]
            except Exception as e:
                return False, [f"[red]FAIL: Provider '{provider_name}' raised wrong exception for {url}: {e}[/red]"]
            else:
                return False, [
                    f"[red]FAIL: Provider '{provider_name}' should raise exception for invalid URL {url}[/red]"
                ]
    else:
        # Make real API call and capture HTTP requests
        console.print("  [yellow]Making real API call (re-recording)[/yellow]")

        exception_raised = None
        try:
            with capture_http_requests() as captured_data:
                provider.get_reviews(url)
        except ReviewsParseException as e:
            exception_raised = e
        except Exception as e:
            console.print(f"  [red]Exception during re-recording: {e}[/red]")
            return False, [f"[red]FAIL: Provider '{provider_name}' raised wrong exception for {url}: {e}[/red]"]

        if captured_data:
            console.print(f"  [cyan]Captured {len(captured_data)} request(s)[/cyan]")

        # Save mock response even for invalid URLs
        # For invalid URLs, we save empty reviews list but still capture HTTP data
        mock_file = save_mock_response(
            provider_class, url_index, url, [], captured_data or [], url_type="invalid", storage=storage
        )
        console.print(f"[green]Saved mock response to {mock_file}[/green]")

        # Check if exception was raised
        if exception_raised:
            return True, [f"[green]PASS: Provider '{provider_name}' correctly raised exception for {url}[/green]"]
        else:
            return False, [f"[red]FAIL: Provider '{provider_name}' should raise exception for invalid URL {url}[/red]"]


def run_single_provider_test(
    provider_class: type[BaseReviewsProvider],
    re_record: bool = False,
) -> tuple[bool, list[str]]:
    """Test a single provider.

    Args:
        provider_class: The provider class to test.
        re_record: If True, force re-recording of mock responses.

    Returns:
        Tuple of (success, list of messages).
    """
    messages = []
    success = True

    provider = provider_class()
    provider_name = provider_class.name

    if not provider.test_urls and not provider.invalid_urls:
        messages.append(f"[yellow]Provider '{provider_name}' has no test_urls or invalid_urls defined[/yellow]")
        return True, messages

    if re_record:
        cleared = clear_provider_mocks(provider_class)
        if cleared > 0:
            console.print(f"[yellow]Cleared {cleared} mock files for '{provider_name}'[/yellow]")

    for url_index, url in enumerate(provider.test_urls):
        console.print(f"Testing provider '{provider_name}' with URL: {url}")
        url_success, url_messages = _test_test_url(provider_class, provider, url, url_index, re_record)
        success = success and url_success
        messages.extend(url_messages)

    for url_index, url in enumerate(provider.invalid_urls):
        console.print(f"Testing invalid URL: {url}")
        url_success, url_messages = _test_invalid_url(provider_class, provider, url, url_index, re_record)
        success = success and url_success
        messages.extend(url_messages)

    return success, messages


def run_provider_tests(
    providers: list[type[BaseReviewsProvider]] | None = None,
    re_record: bool = False,
) -> bool:
    """Run tests for all or specified providers.

    Args:
        providers: Optional list of providers to test. Tests all if None.
        re_record: If True, force re-recording of all mock responses.

    Returns:
        True if all tests passed, False otherwise.
    """
    if providers is None:
        registry = Registry()
        providers = registry.list_providers()

    all_success = True
    table = Table(title="Provider Test Results")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="magenta")

    for provider_class in providers:
        provider_name = provider_class.name
        success, messages = run_single_provider_test(provider_class, re_record)

        if not success:
            all_success = False

        status = "[green]PASS" if success else "[red]FAIL"
        details = "\n".join(messages) if messages else "No tests ran"

        table.add_row(provider_name, status, details)
        if provider_class != providers[-1]:
            table.add_section()

    console.print(table)
    return all_success


class CommandTest(BaseCommand):
    name = "test"
    help = "Test product review providers"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--provider", type=str, help="Test specific provider (by name)")
        parser.add_argument("--re-record", action="store_true", help="Force re-recording of mock responses")

    def run(self, args: argparse.Namespace):
        """Execute the test command.

        Args:
            args: Command line arguments.
        """
        re_record = args.re_record

        providers = None
        if args.provider:
            registry = Registry()
            try:
                provider_class = registry.get_provider_class(args.provider)
                providers = [provider_class]
            except KeyError:
                console.print(f"[red]Error: Provider '{args.provider}' not found[/red]")
                sys.exit(1)

        success = run_provider_tests(providers, re_record)
        return 0 if success else 1
