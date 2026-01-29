import json
from datetime import datetime

import pytest

from product_reviews.models import ReviewList
from product_reviews.providers.exceptions import InvalidURLError, ReviewsParseException
from product_reviews.providers.providers.jsonfs import provider
from product_reviews.providers.providers.jsonfs.provider import JsonFsReviewsProvider


def test_jsonfs_provider_properties():
    """Test JSON FS provider properties and URL matching."""
    provider_instance = JsonFsReviewsProvider()

    assert provider_instance.name == "JSON FS"
    assert provider_instance.description == "JSON file provider"
    # notes may be Optional[str], guard against None
    notes = provider_instance.notes or ""
    assert "jsonf://" in notes
    assert provider_instance.check_url("jsonf://test.json")
    assert not provider_instance.check_url("http://example.com")


def test_jsonfs_provider_get_reviews_success(tmp_path):
    """Test JSON FS provider successfully parses valid JSON file."""
    test_data = {
        "items": [
            {"text": "Great product", "rating": 5.0, "created_at": "2020-01-01T10:00:00"},
            {"text": "Average product", "rating": 3.0, "created_at": "2020-01-02T10:00:00"},
        ]
    }

    test_file = tmp_path / "test.json"
    test_file.write_text(json.dumps(test_data))

    provider_instance = JsonFsReviewsProvider()
    result = provider_instance.get_reviews(f"jsonf://{test_file}")

    assert isinstance(result, ReviewList)
    assert result.count() == 2
    assert len(result.reviews) == 2

    first_review = result.reviews[0]
    assert first_review.text == "Great product"
    assert first_review.rating == 5.0
    assert first_review.created_at == datetime(2020, 1, 1, 10, 0, 0)


def test_jsonfs_provider_get_reviews_file_not_found():
    """Test JSON FS provider raises error for non-existent file."""
    provider_instance = JsonFsReviewsProvider()

    # Escape the dot to avoid regex interpretation in match
    with pytest.raises(InvalidURLError, match=r"File not found: nonexistent\.json"):
        provider_instance.get_reviews("jsonf://nonexistent.json")


def test_jsonfs_provider_get_reviews_invalid_json(tmp_path):
    """Test JSON FS provider raises error for invalid JSON syntax."""
    test_file = tmp_path / "invalid.json"
    test_file.write_text("{invalid json")

    provider_instance = JsonFsReviewsProvider()

    with pytest.raises(ReviewsParseException, match="Can't parse JSON"):
        provider_instance.get_reviews(f"jsonf://{test_file}")


def test_jsonfs_provider_get_reviews_no_items_key(tmp_path):
    """Test JSON FS provider raises error when items key is missing."""
    test_data = {"no_items": []}
    test_file = tmp_path / "no_items.json"
    test_file.write_text(json.dumps(test_data))

    provider_instance = JsonFsReviewsProvider()

    with pytest.raises(ReviewsParseException, match="No items in JSON"):
        provider_instance.get_reviews(f"jsonf://{test_file}")


def test_jsonfs_provider_get_reviews_items_not_list(tmp_path):
    """Test JSON FS provider raises error when items is not a list."""
    test_data = {"items": "not a list"}
    test_file = tmp_path / "not_list.json"
    test_file.write_text(json.dumps(test_data))

    provider_instance = JsonFsReviewsProvider()

    with pytest.raises(ReviewsParseException, match="Items is not a list"):
        provider_instance.get_reviews(f"jsonf://{test_file}")


def test_jsonfs_provider_get_reviews_with_optional_fields(tmp_path):
    """Test JSON FS provider parses optional review fields correctly."""
    test_data = {
        "items": [
            {
                "text": "Complete review",
                "rating": 4.5,
                "created_at": "2020-01-01T10:00:00",
                "pros": "Good quality",
                "cons": "Expensive",
                "summary": "Good overall",
            }
        ]
    }

    test_file = tmp_path / "complete.json"
    test_file.write_text(json.dumps(test_data))

    provider_instance = JsonFsReviewsProvider()
    result = provider_instance.get_reviews(f"jsonf://{test_file}")

    review = result.reviews[0]
    assert review.pros == "Good quality"
    assert review.cons == "Expensive"
    assert review.summary == "Good overall"


def test_jsonfs_provider_module_variable():
    """Test JSON FS provider module variable exposes correct class."""
    assert provider is JsonFsReviewsProvider
