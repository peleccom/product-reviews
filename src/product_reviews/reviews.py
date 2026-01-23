import logging

from requests import HTTPError

from .models import ProviderReviewList
from .providers.base import BaseReviewsProvider
from .providers.exceptions import NoMatchedProvidersException, ReviewsParseException
from .providers.registry import list_providers

logger = logging.getLogger(__name__)


def parse_reviews(url: str) -> ProviderReviewList:
    providerClass = _check_matched_provider(url)
    if not providerClass:
        print("No providers matches url")
        raise NoMatchedProvidersException(f'No matcherd providers for "{url}"')  # noqa: TRY003
    provider = providerClass()
    try:
        review_list = provider.get_reviews(url)
        review_list.reviews.sort(
            key=lambda x: x.created_at,
            reverse=True,
        )
    except HTTPError as e:
        raise ReviewsParseException() from e

    logger.debug(f"got {review_list.count()} reviews")
    return ProviderReviewList(provider=provider.name, reviews=review_list.reviews)


def _check_matched_provider(url: str) -> type[BaseReviewsProvider] | None:
    for cls in list_providers():
        if cls.check_url(url):
            return cls
    return None


class ProductReviewsService:
    @staticmethod
    def parse_reviews(url: str) -> ProviderReviewList:
        return parse_reviews(url)

    @staticmethod
    def list_providers() -> list[type[BaseReviewsProvider]]:
        return list_providers()

    def get_provider_for_url(self, url: str) -> type[BaseReviewsProvider]:
        return _check_matched_provider(url)

    def get_provider_class(self, provider_name: str) -> type[BaseReviewsProvider]:
        return list_providers()[provider_name]

    def get_provider_names(self) -> list[str]:
        return list(list_providers().keys())

    def get_provider(self, provider_name: str) -> BaseReviewsProvider:
        return list_providers()[provider_name]()
