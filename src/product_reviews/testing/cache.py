"""Cache manager for HTTP responses used in testing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from product_reviews.models import Review


@dataclass
class CachedResponse:
    """A cached HTTP response with metadata."""

    url: str
    status_code: int
    headers: dict[str, str]
    body: str | bytes
    is_valid: bool
    reviews_count: int = 0
    error_message: str | None = None

    @property
    def is_error(self) -> bool:
        return not self.is_valid


class ResponseCache:
    """Manages caching of HTTP responses for testing."""

    def __init__(self, base_path: str | Path | None = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "responses"
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_provider_dir(self, provider: str) -> Path:
        return self.base_path / provider

    def _get_test_case_dir(self, provider: str, test_case: str) -> Path:
        return self._get_provider_dir(provider) / test_case

    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use as a directory name."""
        return "".join(c if c.isalnum() or c in "_-" else "_" for c in name).lower()

    def save_response(
        self,
        provider: str,
        test_case: str,
        url: str,
        status_code: int,
        headers: dict[str, str],
        body: str | bytes,
        is_valid: bool,
        reviews: list[Review] | None = None,
        error_message: str | None = None,
    ) -> None:
        """Save a response to the cache."""
        test_case = self._sanitize_name(test_case)
        test_case_dir = self._get_test_case_dir(provider, test_case)
        test_case_dir.mkdir(parents=True, exist_ok=True)

        # Determine content type and file extension
        content_type = headers.get("Content-Type", "")
        if "json" in content_type:
            body_ext = "json"
        elif "html" in content_type:
            body_ext = "html"
        else:
            body_ext = "txt"

        # Save body
        body_file = test_case_dir / f"body.{body_ext}"
        if isinstance(body, str):
            body_file.write_text(body, encoding="utf-8")
        else:
            body_file.write_bytes(body)

        # Save metadata
        meta = {
            "url": url,
            "status_code": status_code,
            "headers": headers,
            "is_valid": is_valid,
            "reviews_count": len(reviews) if reviews else 0,
            "error_message": error_message,
            "body_file": f"body.{body_ext}",
        }
        meta_file = test_case_dir / "meta.json"
        meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    def load_response(self, provider: str, test_case: str) -> CachedResponse | None:
        """Load a cached response."""
        test_case = self._sanitize_name(test_case)
        test_case_dir = self._get_test_case_dir(provider, test_case)

        if not test_case_dir.exists():
            return None

        meta_file = test_case_dir / "meta.json"
        if not meta_file.exists():
            return None

        meta = json.loads(meta_file.read_text(encoding="utf-8"))

        # Load body
        body_file = test_case_dir / meta.get("body_file", "body.txt")
        if body_file.suffix == ".json":
            body = json.loads(body_file.read_text(encoding="utf-8"))
            body = json.dumps(body)
        else:
            body = body_file.read_text(encoding="utf-8")

        return CachedResponse(
            url=meta["url"],
            status_code=meta["status_code"],
            headers=meta["headers"],
            body=body,
            is_valid=meta["is_valid"],
            reviews_count=meta.get("reviews_count", 0),
            error_message=meta.get("error_message"),
        )

    def list_test_cases(self, provider: str) -> list[str]:
        """List all cached test cases for a provider."""
        provider_dir = self._get_provider_dir(provider)
        if not provider_dir.exists():
            return []

        test_cases = []
        for item in provider_dir.iterdir():
            if item.is_dir() and (item / "meta.json").exists():
                test_cases.append(item.name)
        return sorted(test_cases)

    def has_cached_responses(self, provider: str) -> bool:
        """Check if a provider has any cached responses."""
        return len(self.list_test_cases(provider)) > 0

    def list_providers(self) -> list[str]:
        """List all providers with cached responses."""
        if not self.base_path.exists():
            return []

        providers = []
        for item in self.base_path.iterdir():
            if item.is_dir():
                providers.append(item.name)
        return sorted(providers)

    def clear_provider(self, provider: str) -> None:
        """Clear all cached responses for a provider."""
        provider_dir = self._get_provider_dir(provider)
        if provider_dir.exists():
            import shutil

            shutil.rmtree(provider_dir)

    def get_all_responses(self, provider: str | None = None) -> dict[str, list[CachedResponse]]:
        """Get all cached responses, optionally filtered by provider."""
        result = {}
        providers = [provider] if provider else self.list_providers()

        for prov in providers:
            responses = []
            for test_case in self.list_test_cases(prov):
                response = self.load_response(prov, test_case)
                if response:
                    responses.append(response)
            if responses:
                result[prov] = responses

        return result

    def get_response_for_url(self, url: str) -> tuple[str, str, CachedResponse] | None:
        """Find a cached response by URL. Returns (provider, test_case, response) or None."""
        for provider in self.list_providers():
            for test_case in self.list_test_cases(provider):
                response = self.load_response(provider, test_case)
                if response and response.url == url:
                    return (provider, test_case, response)
        return None
