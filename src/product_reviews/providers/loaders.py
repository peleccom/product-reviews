from itertools import chain
from pathlib import Path

from .base import BaseReviewsProvider
from .loader_entrypoint import load_entry_point_providers
from .loader_fs import load_fs_providers


def iter_all_providers(local_providers_dir: Path | None = None):
    return chain(load_entry_point_providers(), load_fs_providers(local_providers_dir))


def load_all_providers_map(
    local_providers_dir: Path | None = None,
) -> dict[str, type[BaseReviewsProvider]]:
    providers: dict[str, type[BaseReviewsProvider]] = {}

    for provider_class in iter_all_providers(local_providers_dir):
        providers[provider_class.name] = provider_class
    return providers
