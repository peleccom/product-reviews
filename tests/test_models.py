import json
from datetime import datetime

from product_reviews.models import HealthCheckResult, ProviderReviewList, Review


def test_review_to_dict():
    """Test Review model to_dict serialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    d = review.to_dict()

    assert "text" in d
    assert d["rating"] == 5


def test_review_to_json():
    """Test Review model to_json serialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    data = review.to_json()
    assert isinstance(data, str)
    review2 = json.loads(data)
    assert review2["created_at"] == "2020-01-01T00:00:00"


def test_review_to_representation():
    """Test Review model to_representation serialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    review2 = review.to_representation()
    assert review2["text"] == "This is a dummy review for testing."
    assert review2["created_at"] == "2020-01-01T00:00:00"


def test_review_from_representation():
    """Test Review model from_representation deserialization method."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    restored_review = Review.from_representation(review.to_representation())
    assert restored_review.created_at == datetime(2020, 1, 1)
    assert restored_review.text == "This is a dummy review for testing."
    assert restored_review.rating == 5.0
    assert restored_review.pros is None
    assert restored_review.cons is None
    assert restored_review.summary is None


def test_provider_review_list():
    """Test ProviderReviewList count method and reviews property."""
    review = Review(
        rating=5.0,
        text="This is a dummy review for testing.",
        created_at=datetime(2020, 1, 1),
    )
    provider_review_list = ProviderReviewList(provider="test", reviews=[review])
    assert provider_review_list.count() == 1
    assert len(provider_review_list.reviews) == 1


def test_provider_review_list_empty():
    """Test ProviderReviewList with empty reviews list."""
    provider_review_list = ProviderReviewList(provider="test", reviews=[])
    assert provider_review_list.count() == 0
    assert len(provider_review_list.reviews) == 0


def test_provider_review_list_multiple_reviews():
    """Test ProviderReviewList with multiple reviews."""
    reviews = [
        Review(rating=5.0, created_at=datetime(2020, 1, 1)),
        Review(rating=4.0, created_at=datetime(2020, 1, 2)),
        Review(rating=3.0, created_at=datetime(2020, 1, 3)),
    ]
    provider_review_list = ProviderReviewList(provider="multi", reviews=reviews)
    assert provider_review_list.count() == 3


def test_review_with_all_fields():
    """Test Review model with all optional fields."""
    review = Review(
        rating=4.5,
        text="Excellent product",
        pros="Good quality, fast shipping",
        cons="Slightly expensive",
        summary="Great buy",
        created_at=datetime(2020, 1, 1),
    )
    d = review.to_dict()
    assert d["pros"] == "Good quality, fast shipping"
    assert d["cons"] == "Slightly expensive"
    assert d["summary"] == "Great buy"


def test_review_with_none_fields():
    """Test Review model with None optional fields."""
    review = Review(rating=3.0, created_at=datetime(2020, 1, 1))
    d = review.to_dict()
    assert d["text"] is None
    assert d["pros"] is None
    assert d["cons"] is None
    assert d["summary"] is None


def test_review_rating_types():
    """Test Review model handles different rating types."""
    review_float = Review(rating=4.5, created_at=datetime(2020, 1, 1))
    review_int = Review(rating=5, created_at=datetime(2020, 1, 1))

    assert review_float.rating == 4.5
    assert review_int.rating == 5


def test_health_check_result_default_values():
    """Test HealthCheckResult has correct default values."""
    result = HealthCheckResult(is_healthy=True, message="OK")
    assert result.url == ""
    assert result.reviews_count == 0


def test_health_check_result_with_values():
    """Test HealthCheckResult with all values."""
    result = HealthCheckResult(
        is_healthy=True,
        message="Provider is working",
        url="https://example.com",
        reviews_count=10,
    )
    assert result.is_healthy is True
    assert result.message == "Provider is working"
    assert result.url == "https://example.com"
    assert result.reviews_count == 10


def test_health_check_result_unhealthy():
    """Test HealthCheckResult for unhealthy provider."""
    result = HealthCheckResult(
        is_healthy=False,
        message="Connection timeout",
        url="https://example.com",
        reviews_count=0,
    )
    assert result.is_healthy is False
    assert result.message == "Connection timeout"


def test_review_to_json_format():
    """Test Review.to_json returns valid JSON string."""
    review = Review(
        rating=5.0,
        text="Perfect!",
        created_at=datetime(2020, 1, 1),
    )
    json_str = review.to_json()

    parsed = json.loads(json_str)
    assert parsed["rating"] == 5.0
    assert parsed["text"] == "Perfect!"
    assert "created_at" in parsed


class TestReviewModel:
    """Additional tests for Review model coverage."""

    def test_review_to_dict_returns_dict(self):
        """Test Review.to_dict returns a dictionary."""
        review = Review(rating=4.0, created_at=datetime(2020, 1, 1))
        result = review.to_dict()
        assert isinstance(result, dict)

    def test_review_to_representation_with_datetime(self):
        """Test Review.to_representation formats datetime correctly."""
        review = Review(
            rating=5.0,
            text="Great!",
            created_at=datetime(2023, 6, 15, 10, 30, 45),
        )
        rep = review.to_representation()
        assert "created_at" in rep
        assert rep["created_at"] == "2023-06-15T10:30:45"
        assert isinstance(rep["created_at"], str)

    def test_review_to_json_valid_json(self):
        """Test Review.to_json returns valid JSON that can be parsed."""
        review = Review(
            rating=3.5,
            text="Average product",
            created_at=datetime(2021, 12, 25),
        )
        json_str = review.to_json()

        data = json.loads(json_str)
        assert data["rating"] == 3.5
        assert data["text"] == "Average product"

    def test_review_from_representation_datetime_parsing(self):
        """Test Review.from_representation parses datetime from ISO format."""
        review = Review(
            rating=4.5,
            text="Good!",
            created_at=datetime(2022, 3, 10),
        )
        rep = review.to_representation()
        restored = Review.from_representation(rep)
        assert restored.created_at.year == 2022
        assert restored.created_at.month == 3
        assert restored.created_at.day == 10
        assert restored.rating == 4.5

    def test_review_from_representation_with_all_fields(self):
        """Test Review.from_representation restores all fields."""
        original = Review(
            rating=4.0,
            text="Nice product",
            pros="Good quality",
            cons="Slightly expensive",
            summary="Recommended",
            created_at=datetime(2021, 5, 20),
        )
        rep = original.to_representation()
        restored = Review.from_representation(rep)
        assert restored.text == "Nice product"
        assert restored.pros == "Good quality"
        assert restored.cons == "Slightly expensive"
        assert restored.summary == "Recommended"


class TestProviderReviewList:
    """Tests for ProviderReviewList model."""

    def test_provider_review_list_with_reviews(self):
        """Test ProviderReviewList with multiple reviews."""
        reviews = [
            Review(rating=5.0, created_at=datetime(2020, 1, 1)),
            Review(rating=4.0, created_at=datetime(2020, 1, 2)),
        ]
        provider_list = ProviderReviewList(provider="TestProvider", reviews=reviews)
        assert provider_list.provider == "TestProvider"
        assert len(provider_list.reviews) == 2
        assert provider_list.count() == 2

    def test_provider_review_list_count_empty(self):
        """Test ProviderReviewList.count returns 0 for empty list."""
        provider_list = ProviderReviewList(provider="EmptyProvider", reviews=[])
        assert provider_list.count() == 0

    def test_provider_review_list_reviews_property(self):
        """Test ProviderReviewList.reviews property returns the list."""
        reviews = [Review(rating=5.0, created_at=datetime(2020, 1, 1))]
        provider_list = ProviderReviewList(provider="Test", reviews=reviews)
        assert provider_list.reviews is reviews


class TestHealthCheckResult:
    """Tests for HealthCheckResult model."""

    def test_health_check_result_minimal(self):
        """Test HealthCheckResult with minimal arguments."""
        result = HealthCheckResult(is_healthy=True, message="OK")
        assert result.is_healthy is True
        assert result.message == "OK"
        assert result.url == ""
        assert result.reviews_count == 0

    def test_health_check_result_full(self):
        """Test HealthCheckResult with all arguments."""
        result = HealthCheckResult(
            is_healthy=True,
            message="All good",
            url="https://example.com",
            reviews_count=42,
        )
        assert result.url == "https://example.com"
        assert result.reviews_count == 42

    def test_health_check_result_unhealthy(self):
        """Test HealthCheckResult for unhealthy provider."""
        result = HealthCheckResult(
            is_healthy=False,
            message="Provider failed",
            url="https://fail.com",
            reviews_count=0,
        )
        assert result.is_healthy is False
        assert result.message == "Provider failed"

    def test_health_check_result_zero_reviews(self):
        """Test HealthCheckResult with zero reviews count."""
        result = HealthCheckResult(
            is_healthy=True,
            message="No reviews yet",
            reviews_count=0,
        )
        assert result.reviews_count == 0

    def test_health_check_result_is_healthy_false(self):
        """Test HealthCheckResult with is_healthy=False."""
        result = HealthCheckResult(is_healthy=False, message="Error")
        assert result.is_healthy is False

    def test_health_check_result_message_types(self):
        """Test HealthCheckResult with different message types."""
        result_success = HealthCheckResult(is_healthy=True, message="Success")
        result_error = HealthCheckResult(is_healthy=False, message="Error: timeout")
        result_warning = HealthCheckResult(is_healthy=True, message="Warning: slow")

        assert result_success.message == "Success"
        assert "timeout" in result_error.message
        assert "slow" in result_warning.message
