"""Mock storage abstraction for provider testing.

Provides an extensible system for storing and loading mock data in different formats.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml


class MockStorage(ABC):
    """Abstract base class for mock data storage implementations."""

    @abstractmethod
    def save_mock(self, path: Path, data: dict[str, Any]) -> None:
        """Save mock data to a file.

        Args:
            path: Path to save the mock file (without extension).
            data: Mock data dictionary to save.
        """

    @abstractmethod
    def load_mock(self, path: Path) -> dict[str, Any] | None:
        """Load mock data from a file.

        Args:
            path: Path to the mock file (without extension).

        Returns:
            Mock data dictionary, or None if file doesn't exist.
        """

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get the file extension for this storage format.

        Returns:
            File extension including the dot (e.g., '.yaml', '.json').
        """


class YamlMockStorage(MockStorage):
    """YAML-based mock storage implementation.

    Provides human-readable mock files with clean formatting.
    This is the default storage format.
    """

    def save_mock(self, path: Path, data: dict[str, Any]) -> None:
        """Save mock data to a YAML file."""
        file_path = path.with_suffix(self.get_file_extension())
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                width=120,
            )

    def load_mock(self, path: Path) -> dict[str, Any] | None:
        """Load mock data from a YAML file."""
        file_path = path.with_suffix(self.get_file_extension())
        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get_file_extension(self) -> str:
        """Get the file extension for YAML format."""
        return ".yaml"


class JsonMockStorage(MockStorage):
    """JSON-based mock storage implementation.

    Provides backward compatibility with the original JSON format.
    Can be used if JSON format is preferred over YAML.
    """

    def save_mock(self, path: Path, data: dict[str, Any]) -> None:
        """Save mock data to a JSON file."""
        file_path = path.with_suffix(self.get_file_extension())
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_mock(self, path: Path) -> dict[str, Any] | None:
        """Load mock data from a JSON file."""
        file_path = path.with_suffix(self.get_file_extension())
        if not file_path.exists():
            return None

        with open(file_path, encoding="utf-8") as f:
            return json.load(f)

    def get_file_extension(self) -> str:
        """Get the file extension for JSON format."""
        return ".json"


def get_mock_storage(format_type: str = "yaml") -> MockStorage:
    """Get a mock storage implementation by format name.

    Args:
        format_type: Storage format name ('yaml' or 'json'). Defaults to 'yaml'.

    Returns:
        MockStorage implementation for the requested format.

    Raises:
        ValueError: If format is not supported.
    """
    if format_type == "yaml":
        return YamlMockStorage()
    elif format_type == "json":
        return JsonMockStorage()
    else:
        msg = f"Unsupported mock storage format: {format_type}. Use 'yaml' or 'json'."
        raise ValueError(msg)
