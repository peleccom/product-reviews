import logging

from requests import HTTPError

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import NoMatchedProvidersException, ReviewsParseException
from product_reviews.providers.registry import Registry, get_default_registry

from .models import ProviderReviewList

logger = logging.getLogger(__name__)


def _parse_reviews(url: str, registry: Registry | None = None) -> ProviderReviewList:
    """Parse reviews from a given URL.

    Args:
        url: The URL to parse reviews from.
        registry: Optional registry instance. Uses default registry if not provided.

    Returns:
        ProviderReviewList containing the parsed reviews.

    Raises:
        NoMatchedProvidersException: If no provider matches the URL.
        ReviewsParseException: If there's an error fetching reviews.
    """
    if registry is None:
        registry = get_default_registry()

    provider_class = _check_matched_provider(url, registry)
    if not provider_class:
        print("No providers matches url")
        raise NoMatchedProvidersException(f'No matched providers for "{url}"')  # noqa: TRY003
    provider = provider_class()
    try:
        reviews = provider.get_reviews(url)
        reviews.sort(
            key=lambda x: x.created_at,
            reverse=True,
        )
    except HTTPError as e:
        raise ReviewsParseException() from e

    logger.debug(f"got {len(reviews)} reviews")
    return ProviderReviewList(provider=provider.name, reviews=reviews)


def _check_matched_provider(url: str, registry: Registry | None = None) -> type[BaseReviewsProvider] | None:
    """Check if any provider matches the given URL.

    Args:
        url: The URL to check.
        registry: Optional registry instance. Uses default registry if not provided.

    Returns:
        The matching provider class or None.
    """
    if registry is None:
        registry = get_default_registry()

    for cls in registry.list_providers():
        if cls.check_url(url):
            return cls


def _list_providers() -> list[type[BaseReviewsProvider]]:
    """List all registered providers sorted by name.

    Note: This function is deprecated. Use ProductReviewsService.list_providers instead.

    Returns:
        Sorted list of provider classes.
    """
    return get_default_registry().list_providers()


class ProductReviewsService:
    """Class that provides the main interface to the `product-reviews` plugin system.

    It allows to parse reviews from a given URL, list available providers,
    and get a provider for a given URL.

    Args:
        registry: Optional registry instance. Uses default registry if not provided.
    """

    def __init__(self, registry: Registry | None = None) -> None:
        self._registry = registry

    @property
    def registry(self) -> Registry:
        """Get the registry instance.

        Returns:
            The registry instance, creating default if needed.
        """
        if self._registry is None:
            self._registry = get_default_registry()
        return self._registry

    def parse_reviews(self, url: str) -> ProviderReviewList:
        """Parse reviews from a given URL.

        Args:
            url: The URL to parse reviews from.

        Returns:
            ProviderReviewList containing the parsed reviews.
        """
        return _parse_reviews(url, self.registry)

    def list_providers(self) -> list[type[BaseReviewsProvider]]:
        """List all registered providers.

        Returns:
            Sorted list of provider classes.
        """
        return self.registry.list_providers()

    def get_provider_for_url(self, url: str) -> type[BaseReviewsProvider] | None:
        """Find a provider that can handle the given URL.

        Args:
            url: The URL to find a provider for.

        Returns:
            The provider class that can handle the URL, or None.
        """
        try:
            return self.registry.get_provider_for_url(url)
        except Exception:
            return None

    def get_provider_class(self, provider_name: str) -> type[BaseReviewsProvider]:
        """Get a provider class by name.

        Args:
            provider_name: The name of the provider.

        Returns:
            The provider class.
        """
        return self.registry.get_provider_class(provider_name)

    def get_provider_names(self) -> list[str]:
        """Get all registered provider names.

        Returns:
            Sorted list of provider names.
        """
        return self.registry.get_provider_names()

    def get_provider(self, provider_name: str) -> BaseReviewsProvider:
        """Get an instance of a provider by name.

        Args:
            provider_name: The name of the provider.

        Returns:
            An instance of the provider.
        """
        return self.registry.get_provider(provider_name)
