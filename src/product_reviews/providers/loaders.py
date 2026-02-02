import os
from itertools import chain
from pathlib import Path

from product_reviews.providers.base import BaseReviewsProvider
from product_reviews.providers.loader_entrypoint import load_entry_point_providers
from product_reviews.providers.loader_fs import load_fs_providers

ENV_PLUGINS_DIR = "PRODUCT_REVIEWS_PLUGINS_DIR"


def get_plugins_dir() -> Path | None:
    """Get the plugins directory from environment variable.

    Returns:
        Path to plugins directory if PRODUCT_REVIEWS_PLUGINS_DIR is set, otherwise None.
    """
    plugins_dir = os.environ.get(ENV_PLUGINS_DIR)
    if plugins_dir:
        return Path(plugins_dir)


def iter_all_providers(plugins_dir: Path | None = None):
    return chain(load_entry_point_providers(), load_fs_providers(plugins_dir))


def load_all_providers_map(
    plugins_dir: Path | None = None,
) -> dict[str, type[BaseReviewsProvider]]:
    providers: dict[str, type[BaseReviewsProvider]] = {}

    for provider_class in iter_all_providers(plugins_dir):
        providers[provider_class.name] = provider_class
    return providers
