"""Mock file management utilities for provider testing."""

from __future__ import annotations

import sys
from pathlib import Path

from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider, ReviewListValidator
from product_reviews.providers.loader_fs import get_local_providers_dir
from product_reviews.providers.testing.mock_storage import MockStorage, get_mock_storage

MOCKS_DIR = "mocks"


class MockFileNotFoundError(Exception):
    """Raised when mock file is not found."""


def get_provider_module_path(provider_class: type[BaseReviewsProvider]) -> Path | None:
    """Get the file path where the provider class is defined.

    Args:
        provider_class: The provider class to locate.

    Returns:
        Path to the provider's module file, or None if not found.
    """
    module = sys.modules.get(provider_class.__module__)
    if module is not None:
        module_file = getattr(module, "__file__", None)
        if module_file is not None:
            return Path(module_file).resolve()

    module_name = provider_class.__module__.split(".")[-1]
    module = sys.modules.get(module_name)
    if module is not None:
        module_file = getattr(module, "__file__", None)
        if module_file is not None:
            return Path(module_file).resolve()

    providers_dir = get_local_providers_dir()
    provider_path = providers_dir / module_name
    provider_file = provider_path / "provider.py"
    if provider_file.exists():
        return provider_file.resolve()

    return None


def get_mocks_dir(provider_class: type[BaseReviewsProvider]) -> Path | None:
    """Get the mocks directory for a provider.

    For local providers (in the product-reviews package), mocks are stored
    near the provider implementation. For external providers (via entry points),
    mocks are stored in a central location.

    Args:
        provider_class: The provider class.

    Returns:
        Path to the mocks directory.
    """
    module_path = get_provider_module_path(provider_class)
    if module_path is not None:
        mocks_dir = module_path.parent / MOCKS_DIR
        return mocks_dir.resolve()


def get_mock_file(
    provider_class: type[BaseReviewsProvider],
    url_index: int,
    url_type: str = "valid",
    mock_index: int = 0,
    storage: MockStorage | None = None,
) -> Path:
    """Get the mock file path for a specific URL index.

    Args:
        provider_class: The provider class.
        url_index: The index of the URL in test_urls or invalid_urls list.
        url_type: Type of URL - 'valid' or 'invalid'. Defaults to 'valid'.
        mock_index: The index of the mock for this URL (for paginated results).
        storage: Mock storage implementation. If None, uses default YAML storage.

    Returns:
        Path to the mock file (without extension).

    Raises:
        MockFileNotFoundError: If the mocks directory cannot be determined.
    """
    mocks_dir = get_mocks_dir(provider_class)
    if mocks_dir is None:
        msg = f"Cannot determine mocks directory for provider '{provider_class.name}'"
        raise MockFileNotFoundError(msg)

    mocks_dir.mkdir(parents=True, exist_ok=True)

    if storage is None:
        storage = get_mock_storage()

    # Build filename without extension (storage will add it)
    if url_type == "invalid":
        filename = f"{provider_class.name}_invalid_{url_index}_{mock_index}"
    else:
        filename = f"{provider_class.name}_{url_index}_{mock_index}"

    return mocks_dir / filename


def clear_provider_mocks(provider_class: type[BaseReviewsProvider]) -> int:
    """Clear all mock files for a provider.

    Args:
        provider_class: The provider class.

    Returns:
        Number of files deleted.
    """
    mocks_dir = get_mocks_dir(provider_class)
    if not mocks_dir or not mocks_dir.exists():
        return 0

    count = 0
    # Delete both .yaml and .json files for compatibility
    for pattern in [f"{provider_class.name}_*.yaml", f"{provider_class.name}_*.json"]:
        for mock_file in mocks_dir.glob(pattern):
            mock_file.unlink()
            count += 1

    return count


def save_mock_response(
    provider_class: type[BaseReviewsProvider],
    url_index: int,
    url: str,
    reviews: list[Review],
    captured_data: list[dict] | None = None,
    url_type: str = "valid",
    mock_index: int = 0,
    storage: MockStorage | None = None,
) -> Path:
    """Save mock response to a file.

    Args:
        provider_class: The provider class.
        url_index: The index of the URL in test_urls or invalid_urls list.
        url: The original URL.
        reviews: The list of reviews to save.
        captured_data: List of captured request/response data (for providers with pagination).
        url_type: Type of URL - 'valid' or 'invalid'. Defaults to 'valid'.
        mock_index: The index of the mock for this URL (for paginated results).
        storage: Mock storage implementation. If None, uses default YAML storage.

    Returns:
        Path to the saved mock file.
    """
    if storage is None:
        storage = get_mock_storage()

    mock_file = get_mock_file(provider_class, url_index, url_type, mock_index, storage)
    reviews_data = [r.to_representation() for r in reviews]
    mock_data = {"url": url, "reviews": reviews_data, "captured_data": captured_data}

    storage.save_mock(mock_file, mock_data)

    # Return the actual file path with extension
    return mock_file.with_suffix(storage.get_file_extension())


def load_mock_data(
    provider_class: type[BaseReviewsProvider],
    url_index: int,
    url_type: str = "valid",
    mock_index: int = 0,
    storage: MockStorage | None = None,
) -> dict | None:
    """Load mock data (including actual_url) from file.

    Args:
        provider_class: The provider class.
        url_index: The index of the URL in test_urls or invalid_urls list.
        url_type: Type of URL - 'valid' or 'invalid'. Defaults to 'valid'.
        mock_index: The index of the mock for this URL (for paginated results).
        storage: Mock storage implementation. If None, uses default YAML storage.

    Returns:
        Mock data dict or None if file doesn't exist.
    """
    if storage is None:
        storage = get_mock_storage()

    mock_file = get_mock_file(provider_class, url_index, url_type, mock_index, storage)
    return storage.load_mock(mock_file)


def load_mock_response(
    provider_class: type[BaseReviewsProvider],
    url_index: int,
    url_type: str = "valid",
    mock_index: int = 0,
    storage: MockStorage | None = None,
) -> list[Review] | None:
    """Load mock response from file.

    Args:
        provider_class: The provider class.
        url_index: The index of the URL in test_urls or invalid_urls list.
        url_type: Type of URL - 'valid' or 'invalid'. Defaults to 'valid'.
        mock_index: The index of the mock for this URL (for paginated results).
        storage: Mock storage implementation. If None, uses default YAML storage.

    Returns:
        List of reviews from mock, or None if file doesn't exist.
    """
    mock_data = load_mock_data(provider_class, url_index, url_type, mock_index, storage)
    if mock_data is None:
        return None

    return [Review.from_representation(r) for r in mock_data["reviews"]]


def validate_reviews(reviews: list[Review]) -> tuple[bool, str]:
    """Validate that reviews have required fields.

    Args:
        reviews: The reviews to validate.

    Returns:
        Tuple of (is_valid, error_message).
    """
    try:
        ReviewListValidator().check_reviews_count(reviews)
        for review in reviews:
            ReviewListValidator().check_review_fields(review)
    except Exception as e:
        return False, str(e)
    else:
        return True, ""
