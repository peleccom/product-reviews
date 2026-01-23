from __future__ import annotations

from abc import ABC


class SearchFeature(ABC):  # noqa: B024
    """Marker interface for providers that support search functionality."""


class AsyncFeature(ABC):  # noqa: B024
    """Marker interface for providers that support async operations."""
