"""
Health check module for review providers.
"""

import sys
from typing import Union

from rich.console import Console
from rich.table import Table

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.reviews import list_providers

console = Console()


def get_all_providers() -> list[type[BaseReviewsProvider]]:
    """Get all available review providers."""
    providers = list_providers()
    # Temporarily filter out ozon_by provider due to browser automation issues
    return [p for p in providers if p.name != "ozon_by"]


def _select_provider(providers: Union[list[type[BaseReviewsProvider]], None] = None) -> list[type[BaseReviewsProvider]]:
    if providers is None:
        providers = get_all_providers()

    return providers


def run_health_checks(providers: Union[list[type[BaseReviewsProvider]], None] = None) -> bool:
    """
    Run health checks for all providers or specified providers.
    Returns True if all providers are healthy.
    """
    providers = _select_provider(providers)

    table = Table(title="Review Providers Health Check")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Reviews Count", justify="right", style="magenta")
    table.add_column("Message", style="yellow")

    all_healthy = True
    total_providers = len(providers)

    with console.status("[bold green]Running health checks...") as status:
        for idx, provider_class in enumerate(providers, 1):
            provider = provider_class()
            status.update(f"[bold blue]Checking {provider.name} ({idx}/{total_providers})")

            results = provider.check_health()

            for result in results:
                check_mark = "✓" if result.is_healthy else "✗"
                status_style = "green" if result.is_healthy else "red"

                table.add_row(
                    provider.name,
                    check_mark,
                    str(result.reviews_count),
                    result.message,
                    style=status_style if not result.is_healthy else None,
                )

                if not result.is_healthy:
                    all_healthy = False

    console.print(table)
    return all_healthy


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
