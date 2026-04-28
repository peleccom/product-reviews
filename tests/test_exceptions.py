"""Tests for exception classes."""

import pytest

from product_reviews.providers.exceptions import (
    InvalidURLError,
    NoMatchedProvidersException,
    ProductReviewsError,
    ProviderLoadError,
    ProviderNotReadyError,
    ReviewsParseException,
)


class TestProductReviewsError:
    """Test the base exception class."""

    def test_product_reviews_error_is_exception(self):
        """Test ProductReviewsError can be instantiated."""
        error = ProductReviewsError("Test error message")
        assert isinstance(error, Exception)
        assert str(error) == "Test error message"

    def test_product_reviews_error_with_no_message(self):
        """Test ProductReviewsError with no message."""
        error = ProductReviewsError()
        assert isinstance(error, Exception)


class TestNoMatchedProvidersException:
    """Test NoMatchedProvidersException."""

    def test_no_matched_providers_exception(self):
        """Test NoMatchedProvidersException can be raised."""
        url = "https://unknown.com/product"
        with pytest.raises(NoMatchedProvidersException, match=f"No provider found for URL: {url}"):
            raise NoMatchedProvidersException(url)

    def test_no_matched_providers_inherits_from_base(self):
        """Test NoMatchedProvidersException inherits from ProductReviewsError."""
        assert issubclass(NoMatchedProvidersException, ProductReviewsError)

    def test_no_matched_providers_accepts_url(self):
        """Test NoMatchedProvidersException accepts URL parameter."""
        url = "https://unknown.com/product"
        exc = NoMatchedProvidersException(url)
        assert str(exc) == f"No provider found for URL: {url}"

    def test_no_matched_providers_match(self):
        """Test matching behavior for NoMatchedProvidersException."""
        url = "https://unknown.com/product"
        with pytest.raises(NoMatchedProvidersException, match="No provider found for URL"):
            raise NoMatchedProvidersException(url)


class TestProviderLoadError:
    """Test ProviderLoadError."""

    def test_provider_load_error_inherits_from_base(self):
        """Test ProviderLoadError inherits from ProductReviewsError."""
        assert issubclass(ProviderLoadError, ProductReviewsError)

    def test_provider_load_error_accepts_name(self):
        """Test ProviderLoadError accepts provider name."""
        provider_name = "TestProvider"
        exc = ProviderLoadError(provider_name)
        assert str(exc) == f"Failed to load provider: {provider_name}"

    def test_provider_load_error_match(self):
        """Test matching behavior for ProviderLoadError."""
        provider_name = "TestProvider"
        with pytest.raises(ProviderLoadError, match="Failed to load provider"):
            raise ProviderLoadError(provider_name)


class TestProviderNotReadyError:
    """Test ProviderNotReadyError."""

    def test_provider_not_ready_error_inherits_from_base(self):
        """Test ProviderNotReadyError inherits from ProductReviewsError."""
        assert issubclass(ProviderNotReadyError, ProductReviewsError)

    def test_provider_not_ready_error_accepts_name(self):
        """Test ProviderNotReadyError accepts provider name."""
        provider_name = "TestProvider"
        exc = ProviderNotReadyError(provider_name)
        assert str(exc) == f"Provider not ready: {provider_name}"

    def test_provider_not_ready_error_match(self):
        """Test matching behavior for ProviderNotReadyError."""
        provider_name = "TestProvider"
        with pytest.raises(ProviderNotReadyError, match="Provider not ready"):
            raise ProviderNotReadyError(provider_name)


class TestInvalidURLError:
    """Test InvalidURLError."""

    def test_invalid_url_error_inherits_from_base(self):
        """Test InvalidURLError inherits from ProductReviewsError."""
        assert issubclass(InvalidURLError, ProductReviewsError)

    def test_invalid_url_error_accepts_url(self):
        """Test InvalidURLError accepts URL."""
        url = "invalid-url"
        exc = InvalidURLError(url)
        assert str(exc) == f"Invalid URL: {url}"

    def test_invalid_url_error_match(self):
        """Test matching behavior for InvalidURLError."""
        url = "invalid-url"
        with pytest.raises(InvalidURLError, match="Invalid URL"):
            raise InvalidURLError(url)

    def test_invalid_url_error_is_product_reviews_error(self):
        """Test InvalidURLError inherits from ProductReviewsError."""
        error = InvalidURLError("Test")
        assert isinstance(error, ProductReviewsError)


class TestReviewsParseException:
    """Test ReviewsParseException."""

    def test_reviews_parse_exception(self):
        """Test ReviewsParseException can be raised."""
        message = "Failed to parse reviews"
        with pytest.raises(ReviewsParseException, match=message):
            raise ReviewsParseException(message)

    def test_reviews_parse_exception_inherits_from_exception(self):
        """Test ReviewsParseException inherits from Exception."""
        error = ReviewsParseException("Test")
        assert isinstance(error, Exception)

    def test_reviews_parse_exception_standalone(self):
        """Test ReviewsParseException does not inherit from ProductReviewsError."""
        error = ReviewsParseException("test")
        assert isinstance(error, Exception)
        assert not isinstance(error, ProductReviewsError)


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_product_reviews_error(self):
        """Test that most exceptions inherit from ProductReviewsError."""
        exceptions = [
            NoMatchedProvidersException("test"),
            ProviderLoadError("test"),
            ProviderNotReadyError("test"),
            InvalidURLError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, ProductReviewsError)

    def test_reviews_parse_exception_not_in_base(self):
        """Test ReviewsParseException does not inherit from ProductReviewsError."""
        error = ReviewsParseException("test")
        assert isinstance(error, Exception)
        assert not isinstance(error, ProductReviewsError)
