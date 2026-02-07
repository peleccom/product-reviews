"""Scrape command for product-reviews CLI."""

import argparse
import logging
import sys

from product_reviews.providers.exceptions import ReviewsParseException
from product_reviews.reviews import ProductReviewsService

from .base import BaseCommand

logger = logging.getLogger("product-reviews")


class CommandScrape(BaseCommand):
    name = "scrape"
    help = "Scrape reviews from a URL"

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("url", type=str, help="URL of the site to scrape reviews from")

    def run(self, args: argparse.Namespace):
        """Execute the scrape command.

        Args:
            args: Command line arguments.
        """
        service = ProductReviewsService()
        try:
            reviews = service.parse_reviews(args.url)
        except ReviewsParseException as e:
            print(f"Can't parse reviews. Caused by {e.__cause__!r}")
            sys.exit(1)
        except Exception as e:
            print(e)
            raise

        print(f"Provider: {reviews.provider}\n")
        for item in reviews.reviews:
            print(item.to_dict(), end="\n\n")
        print(f"Count: {reviews.count()}")
        logger.info(f"got {reviews.count()} reviews")
