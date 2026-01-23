import importlib
import logging
from collections.abc import Generator

from .base import BaseReviewsProvider

ENTRY_POINT_GROUP = "product_reviews.providers"


logger = logging.getLogger(__name__)


def load_entry_point_providers() -> Generator[type[BaseReviewsProvider], None, None]:
    eps = importlib.metadata.entry_points(group=ENTRY_POINT_GROUP)

    for ep in eps:
        try:
            provider_class = ep.load()
            if not isinstance(provider_class, type) or not issubclass(provider_class, BaseReviewsProvider):
                logger.warning(f"Provider {ep.name!r} does not subclass BaseReviewsProvider")
                continue
            logger.debug(f"Loaded provider {ep.name!r} from entry point")
            yield provider_class
        except Exception as e:
            logger.warning(f"Failed to load provider {ep.name!r}: {e}")
