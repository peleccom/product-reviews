import argparse
import sys

from product_reviews.cli.commands.command_health import CommandHealth
from product_reviews.cli.commands.command_list import CommandList
from product_reviews.cli.commands.command_scrape import CommandScrape
from product_reviews.cli.commands.command_test import CommandTest

subcommands = (
    CommandHealth(),
    CommandList(),
    CommandScrape(),
    CommandTest(),
)


def main() -> None:
    """Main entry point for product-reviews CLI."""
    parser = argparse.ArgumentParser(description="CLI app to scrape reviews and check providers health.")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    for command in subcommands:
        subparser = subparsers.add_parser(command.name, help=command.help)
        command.add_arguments(subparser)

    # Parse the arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    for command in subcommands:
        if command.name == args.command:
            result = command.run(args)
            if isinstance(result, int):
                return sys.exit(result)
            return


if __name__ == "__main__":
    main()
