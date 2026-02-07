"""List command for product-reviews CLI."""

import argparse
from argparse import ArgumentParser

from rich.console import Console
from rich.table import Table

from product_reviews.providers.registry import list_providers

from .base import BaseCommand

console = Console()


class CommandList(BaseCommand):
    name = "list"
    help = "List available review providers"

    def add_arguments(self, parser: ArgumentParser):
        pass

    def run(self, args: argparse.Namespace) -> None:
        """Execute the list command.

        Args:
            args: Command line arguments.
        """
        providers = list_providers()

        table = Table(title="Review Providers")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Pattern", style="magenta")
        table.add_column("Notes", style="yellow")

        for idx, provider in enumerate(providers):
            p = provider()
            notes = p.notes.strip() if hasattr(p, "notes") and p.notes else "-"
            pattern = str(p.url_regex) if isinstance(p.url_regex, str) else "\n".join(map(str, p.url_regex))
            table.add_row(
                p.name,
                p.description,
                pattern,
                notes,
            )

            if idx < len(providers) - 1:
                table.add_section()

        console.print(table)
