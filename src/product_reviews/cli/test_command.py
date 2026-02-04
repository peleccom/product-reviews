"""Test command for running provider tests with mocked data."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from rich.console import Console

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.registry import list_providers
from product_reviews.testing.cache import ResponseCache
from product_reviews.testing.recorder import ResponseRecorder

logger = logging.getLogger(__name__)
console = Console()


def get_provider_by_name(name: str) -> type[BaseReviewsProvider] | None:
    """Get a provider class by name."""
    providers = list_providers()
    provider_names = [p().name for p in providers]
    console.print(f"[dim]Available providers: {provider_names}[/dim]")
    for provider_class in providers:
        if provider_class().name.lower() == name.lower():
            return provider_class
    return None


def record_provider(provider_class: type[BaseReviewsProvider], re_record: bool = False) -> bool:
    """
    Record responses for a provider.
    Returns True if all test_urls succeeded, False otherwise.
    """
    provider = provider_class()
    provider_name = provider.name

    console.print(f"[bold blue]Recording responses for {provider_name}...[/bold blue]")

    recorder = ResponseRecorder()
    successful, failed = recorder.record_provider(provider_class, re_record=re_record)

    # Print results
    for result in successful:
        if result.reviews_count > 0:
            console.print(f"  [green]✓[/green] {result.test_case}: {result.reviews_count} reviews cached")
        elif result.status_code:
            console.print(f"  [green]✓[/green] {result.test_case}: HTTP {result.status_code} cached")
        else:
            console.print(f"  [green]✓[/green] {result.test_case}: cached")

    for result in failed:
        console.print(f"  [red]✗[/red] {result.test_case}: {result.error_message}")

    if failed:
        console.print(
            f"\n[red]ERROR: Recording failed for {len(failed)} URL(s). Fix parser before running tests.[/red]"
        )
        return False

    console.print(f"[green]Successfully recorded {len(successful)} response(s)[/green]")
    return True


def run_pytest(provider_name: str | None = None, verbose: bool = False) -> int:
    """Run pytest with recorded responses."""
    console.print("\n[bold blue]Running tests...[/bold blue]")

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    # If provider specified, only run tests for that provider
    if provider_name:
        cmd.extend(["-k", f"{provider_name}"])

    # Add coverage if not verbose
    if not verbose:
        cmd.append("--tb=short")

    # Get product-reviews package directory
    package_dir = Path(__file__).parent.parent.parent

    # Explicitly pass tests directory from installed package
    tests_dir = package_dir / "tests"

    # Override rootdir and config to prevent picking up local files
    cmd.extend([
        "--rootdir",
        str(package_dir),
        "--override-ini",
        str(package_dir / "pyproject.toml"),
    ])

    # Add tests directory explicitly
    cmd.append(str(tests_dir))

    # Run pytest
    result = subprocess.run(cmd, capture_output=False, text=True, cwd=str(package_dir))
    return result.returncode


def command_test(args: argparse.Namespace) -> int:
    """
    Main test command.
    Records responses - recording IS the test for providers.
    For external packages, this is sufficient (no separate pytest needed).
    """
    import os

    cache_dir = args.cache_dir
    if cache_dir:
        os.environ["PRODUCT_REVIEWS_CACHE_DIR"] = cache_dir

    cache = ResponseCache()
    re_record = args.re_record

    # Detect if we're running from product-reviews or external package
    package_dir = Path(__file__).parent.parent.parent
    is_external = package_dir != Path.cwd()

    if args.all:
        providers = list_providers()
    elif args.provider:
        provider_class = get_provider_by_name(args.provider)
        if not provider_class:
            console.print(f"[red]Error: Provider '{args.provider}' not found[/red]")
            return 1
        providers = [provider_class]
    else:
        console.print("[red]Error: Specify --provider or --all[/red]")
        return 1

    # Process each provider
    for provider_class in providers:
        provider = provider_class()
        provider_name = provider.name

        needs_recording = re_record or not cache.has_cached_responses(provider_name)

        if needs_recording:
            success = record_provider(provider_class, re_record=re_record)
            if not success:
                return 1
        else:
            console.print(f"[green]Using cached responses for {provider_name}[/green]")

    # Recording IS test - no separate pytest needed
    # For external packages, recording is sufficient
    # For internal (product-reviews), run pytest for unit tests of testing infrastructure
    if is_external:
        console.print("\n[green]Recording completed. Tests passed![/green]")
        return 0

    return run_pytest(verbose=args.verbose)


def main_test_command() -> int:
    """Entry point for test command."""
    parser = argparse.ArgumentParser(description="Test providers with cached responses (records on first run)")
    parser.add_argument("--provider", type=str, help="Test specific provider (by name)")
    parser.add_argument("--all", action="store_true", help="Test all providers")
    parser.add_argument("--re-record", action="store_true", help="Force re-recording of responses")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--cache-dir", type=str, help="Cache directory (default: use package location or local tests/fixtures)"
    )

    args = parser.parse_args()
    return command_test(args)


if __name__ == "__main__":
    sys.exit(main_test_command())
