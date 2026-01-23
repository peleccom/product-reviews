class ProductReviewsError(Exception):
    """Base exception for product reviews errors."""


class NoMatchedProvidersException(ProductReviewsError):
    """Raised when no provider matches the given URL."""


class ProviderLoadError(ProductReviewsError):
    """Raised when a provider fails to load."""


class ProviderNotReadyError(ProductReviewsError):
    """Raised when a provider is not ready (e.g., missing dependencies)."""


class InvalidURLError(ProductReviewsError):
    """Raised when an invalid URL is provided."""


class ReviewsParseException(Exception):
    """Raised when an error occurs while parsing reviews."""

    pass
