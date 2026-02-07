"""Health check command for product-reviews CLI."""

import argparse
import sys
from typing import Union

from rich.console import Console
from rich.table import Table

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.reviews import ProductReviewsService, _list_providers

from .base import BaseCommand

console = Console()


def add_health_parser(subparsers):
    health_parser = subparsers.add_parser("health", help="Check health of review providers")
    health_parser.add_argument("--provider", type=str, help="Check specific provider (by name)")


def get_all_providers() -> list[type[BaseReviewsProvider]]:
    """Get all available review providers."""
    providers = _list_providers()
    # Temporarily filter out ozon_by provider due to browser automation issues
    return [p for p in providers if p.name != "ozon_by"]


def _select_provider(providers: Union[list[type[BaseReviewsProvider]], None] = None) -> list[type[BaseReviewsProvider]]:
    if providers is None:
        providers = get_all_providers()

    return providers


def run_health_checks(providers: Union[list[type[BaseReviewsProvider]], None] = None) -> bool:
    """Run health checks for all providers or specified providers.

    Args:
        providers: Optional list of providers to check. If None, checks all providers.

    Returns:
        True if all providers are healthy, False otherwise.
    """
    providers = _select_provider(providers)

    table = Table(title="Review Providers Health Check")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Reviews Count", justify="right", style="magenta")
    table.add_column("Message", style="yellow")

    all_healthy = True
    total_providers = len(providers)
    last_provider_name = None

    with console.status("[bold green]Running health checks...") as status:
        for idx, provider_class in enumerate(providers, 1):
            provider = provider_class()
            status.update(f"[bold blue]Checking {provider.name} ({idx}/{total_providers})")

            results = provider.check_health()

            for result_idx, result in enumerate(results):
                check_mark = "✓" if result.is_healthy else "✗"
                status_style = "green" if result.is_healthy else "red"

                provider_cell = "" if result_idx > 0 and provider.name == last_provider_name else provider.name
                last_provider_name = provider.name

                table.add_row(
                    provider_cell,
                    check_mark,
                    str(result.reviews_count),
                    result.message,
                    style=status_style if not result.is_healthy else None,
                )

                if not result.is_healthy:
                    all_healthy = False

            if idx < len(providers):
                table.add_section()

    console.print(table)
    return all_healthy


class CommandHealth(BaseCommand):
    name = "health"
    help = "Check health of review providers"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--provider", type=str, help="Check specific provider (by name)")

    def run(self, args):
        """Execute the health command.

        Args:
            args: Command line arguments.
        """
        providers = None
        if args.provider:
            service = ProductReviewsService()
            providers = [p for p in service.list_providers() if p().name.lower() == args.provider.lower()]
            if not providers:
                print(f"Error: Provider '{args.provider}' not found")
                sys.exit(1)

        success = run_health_checks(providers)
        sys.exit(0 if success else 1)


def main() -> int:
    """Main entry point for health check CLI."""
    try:
        all_healthy = run_health_checks()
    except Exception as e:
        console.print(f"[red]Error running health checks: {e!s}[/red]")
        return 2
    else:
        return 0 if all_healthy else 1


if __name__ == "__main__":
    sys.exit(main())
