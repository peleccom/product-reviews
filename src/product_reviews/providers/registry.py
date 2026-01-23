from __future__ import annotations

import logging
from collections.abc import Iterator

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.exceptions import ProviderLoadError

from .loaders import load_all_providers

logger = logging.getLogger(__name__)


def get_provider_for_url(
    url: str,
    providers: dict[str, type[BaseReviewsProvider]] | None = None,
) -> type[BaseReviewsProvider]:
    if providers is None:
        providers = load_all_providers()

    for provider_class in providers.values():
        if provider_class.check_url(url):
            return provider_class

    msg = f"No provider found for URL: {url}"
    raise ProviderLoadError(msg)


def iter_providers(
    providers: dict[str, type[BaseReviewsProvider]] | None = None,
) -> Iterator[tuple[str, type[BaseReviewsProvider]]]:
    if providers is None:
        providers = load_all_providers()

    yield from providers.items()


def list_providers():
    return list(load_all_providers().values())
