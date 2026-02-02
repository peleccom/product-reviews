from __future__ import annotations

import logging
from collections.abc import Iterator
from pathlib import Path

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import ProviderLoadError
from product_reviews.providers.loaders import (
    get_plugins_dir,
    load_all_providers_map,
)

logger = logging.getLogger(__name__)


class Registry:
    """Registry for managing review provider plugins.

    This class handles loading, caching, and querying of provider plugins
    from entry points and file system directories.

    Args:
        plugins_dir: Optional path to a plugins directory. If not provided,
            uses the PRODUCT_REVIEWS_PLUGINS_DIR environment variable.
    """

    def __init__(self, plugins_dir: Path | None = None) -> None:
        self._plugins_dir = plugins_dir
        self._providers: dict[str, type[BaseReviewsProvider]] | None = None

    def _load_providers(self) -> dict[str, type[BaseReviewsProvider]]:
        """Load and cache all providers.

        Returns:
            Dictionary mapping provider names to provider classes.
        """
        if self._providers is None:
            self._providers = load_all_providers_map(self._plugins_dir)
        return self._providers

    def get_provider_for_url(self, url: str) -> type[BaseReviewsProvider]:
        """Find a provider that can handle the given URL.

        Args:
            url: The URL to find a provider for.

        Returns:
            The provider class that can handle the URL.

        Raises:
            ProviderLoadError: If no provider is found for the URL.
        """
        for provider_class in self._load_providers().values():
            if provider_class.check_url(url):
                return provider_class

        msg = f"No provider found for URL: {url}"
        raise ProviderLoadError(msg)

    def iter_providers(self) -> Iterator[tuple[str, type[BaseReviewsProvider]]]:
        """Iterate over all registered providers.

        Yields:
            Tuples of (provider_name, provider_class).
        """
        yield from self._load_providers().items()

    def list_providers(self) -> list[type[BaseReviewsProvider]]:
        """List all registered providers sorted by name.

        Returns:
            Sorted list of provider classes.
        """
        return sorted(self._load_providers().values(), key=lambda x: x.name)

    def get_provider_class(self, provider_name: str) -> type[BaseReviewsProvider]:
        """Get a provider class by name.

        Args:
            provider_name: The name of the provider.

        Returns:
            The provider class.

        Raises:
            KeyError: If provider is not found.
        """
        return self._load_providers()[provider_name]

    def get_provider_names(self) -> list[str]:
        """Get all registered provider names.

        Returns:
            Sorted list of provider names.
        """
        return sorted(self._load_providers().keys())

    def get_provider(self, provider_name: str) -> BaseReviewsProvider:
        """Get an instance of a provider by name.

        Args:
            provider_name: The name of the provider.

        Returns:
            An instance of the provider.

        Raises:
            KeyError: If provider is not found.
        """
        return self._load_providers()[provider_name]()

    def clear_cache(self) -> None:
        """Clear the provider cache.

        This forces providers to be reloaded on next access.
        """
        self._providers = None


def get_registry(plugins_dir: Path | None = None) -> Registry:
    """Create a new Registry instance.

    Args:
        plugins_dir: Optional path to a plugins directory.

    Returns:
        A new Registry instance.
    """
    return Registry(plugins_dir=plugins_dir)


def get_default_registry() -> Registry:
    """Get the default registry using environment variable.

    Returns:
        Registry configured with PRODUCT_REVIEWS_PLUGINS_DIR.
    """
    return Registry(plugins_dir=get_plugins_dir())


def get_provider_for_url(
    url: str,
    providers: dict[str, type[BaseReviewsProvider]] | None = None,
) -> type[BaseReviewsProvider]:
    """Find a provider that can handle the given URL.

    Note: This function is deprecated. Use Registry.get_provider_for_url instead.

    Args:
        url: The URL to find a provider for.
        providers: Optional pre-loaded providers dictionary.

    Returns:
        The provider class that can handle the URL.

    Raises:
        ProviderLoadError: If no provider is found for the URL.
    """
    if providers is None:
        registry = get_default_registry()
        return registry.get_provider_for_url(url)

    for provider_class in providers.values():
        if provider_class.check_url(url):
            return provider_class

    msg = f"No provider found for URL: {url}"
    raise ProviderLoadError(msg)


def iter_providers(
    providers: dict[str, type[BaseReviewsProvider]] | None = None,
) -> Iterator[tuple[str, type[BaseReviewsProvider]]]:
    """Iterate over all registered providers.

    Note: This function is deprecated. Use Registry.iter_providers instead.

    Args:
        providers: Optional pre-loaded providers dictionary.

    Yields:
        Tuples of (provider_name, provider_class).
    """
    if providers is None:
        registry = get_default_registry()
        yield from registry.iter_providers()
        return

    yield from providers.items()


def list_providers() -> list[type[BaseReviewsProvider]]:
    """List all registered providers sorted by name.

    Note: This function is deprecated. Use Registry.list_providers instead.

    Returns:
        Sorted list of provider classes.
    """
    return get_default_registry().list_providers()
