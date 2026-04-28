class ProductReviewsError(Exception):
    """Base exception for product reviews errors."""


class NoMatchedProvidersException(ProductReviewsError):
    """Raised when no provider matches the given URL."""

    def __init__(self, url: str) -> None:
        super().__init__(f"No provider found for URL: {url}")


class ProviderLoadError(ProductReviewsError):
    """Raised when a provider fails to load."""

    def __init__(self, provider_name: str) -> None:
        super().__init__(f"Failed to load provider: {provider_name}")


class ProviderNotReadyError(ProductReviewsError):
    """Raised when a provider is not ready (e.g., missing dependencies)."""

    def __init__(self, provider_name: str) -> None:
        super().__init__(f"Provider not ready: {provider_name}")


class InvalidURLError(ProductReviewsError):
    """Raised when an invalid URL is provided."""

    def __init__(self, url: str) -> None:
        super().__init__(f"Invalid URL: {url}")


class ReviewsParseException(Exception):
    """Raised when an error occurs while parsing reviews."""

    def __init__(self, message: str = "Parse error") -> None:
        super().__init__(message)
