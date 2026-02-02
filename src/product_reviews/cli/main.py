import argparse
import logging
import sys

from product_reviews.cli.health_check import run_health_checks
from product_reviews.providers.exceptions import ReviewsParseException
from product_reviews.providers.registry import list_providers
from product_reviews.reviews import ProductReviewsService

logger = logging.getLogger("product-reviews")


def command_list(args: argparse.Namespace):
    for provider in list_providers():
        p = provider()
        print("*" * 50)
        print(f"Name: {p.name}")
        print(f"Description: {p.description}")
        if hasattr(p, "notes") and p.notes:
            print(f"Notes: {p.notes.strip()}")
        print(f"Pattern: {provider().url_regex}")
        print("-" * 50 + "\n")


def command_scrape(args: argparse.Namespace):
    service = ProductReviewsService()
    try:
        reviews = service.parse_reviews(args.url)
    except ReviewsParseException as e:
        print(f"Can't parse reviews. Caused by {e.__cause__!r}")
        return sys.exit(1)
    except Exception as e:
        print(e)
        raise

    print(f"Provider: {reviews.provider}\n")
    for item in reviews.reviews:
        print(item.to_dict(), end="\n\n")
    print(f"Count: {reviews.count()}")
    logger.info(f"got {reviews.count()} reviews")


def command_health(args: argparse.Namespace):
    providers = None
    if args.provider:
        service = ProductReviewsService()
        providers = [p for p in service.list_providers() if p().name.lower() == args.provider.lower()]
        if not providers:
            print(f"Error: Provider '{args.provider}' not found")
            sys.exit(1)

    success = run_health_checks(providers)
    sys.exit(0 if success else 1)


def main() -> None:
    # Set up the argument parser
    parser = argparse.ArgumentParser(description="CLI app to scrape reviews and check providers health.")

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape reviews from a URL")
    scrape_parser.add_argument("url", type=str, help="URL of the site to scrape reviews from")

    # Health check command
    health_parser = subparsers.add_parser("health", help="Check health of review providers")
    health_parser.add_argument("--provider", type=str, help="Check specific provider (by name)")

    # List providers command
    subparsers.add_parser("list", help="List providers")

    # Parse the arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)
    if args.command == "scrape":
        return command_scrape(args)
    elif args.command == "health":
        return command_health(args)
    elif args.command == "list":
        return command_list(args)


if __name__ == "__main__":
    main()
