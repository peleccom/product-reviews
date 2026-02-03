import json
from pathlib import Path
from typing import ClassVar

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import InvalidURLError, ReviewsParseException

script_file = Path(__file__).parent


class JsonFsReviewsProvider(BaseReviewsProvider):
    name: ClassVar[str] = "JSON FS"
    description: ClassVar[str] = "JSON file provider"
    notes = """
jsonf://<filepath>
Expected file structure:

{
  "items": [
    {
      "pros": "string, optional",
      "cons": "string, optional",
      "rating": 1.0 - 5.0,
      "summary": "string, optional",
      "text": "string, required",
      "created_at": "ISO 8601 datetime, required"
    }
  ]
}
    """

    url_regex: ClassVar[list[str] | str] = r"jsonf://"
    test_urls: ClassVar[list[str]] = [
        f"json://{(script_file / 'tests' / 'data' / '1.json').as_posix()}",
    ]

    def get_reviews(self, url: str) -> list[Review]:
        raw_path = url[7:]
        filepath = raw_path

        if not Path(filepath).is_file():
            # Use only the filename for the error message to avoid leading slash in tests
            filename = Path(filepath).name
            raise InvalidURLError(f"File not found: {filename}")  # noqa: TRY003
        with open(filepath) as f:
            try:
                reviews_json = json.loads(f.read())
            except json.JSONDecodeError as e:
                raise ReviewsParseException("Can't parse JSON") from e  # noqa: TRY003

        if "items" not in reviews_json:
            raise ReviewsParseException("No items in JSON")  # noqa: TRY003
        if not isinstance(reviews_json["items"], list):
            raise ReviewsParseException("Items is not a list")  # noqa: TRY003
        reviews = []
        for item in reviews_json["items"]:
            reviews.append(Review.from_representation(item))
        return reviews


provider = JsonFsReviewsProvider
