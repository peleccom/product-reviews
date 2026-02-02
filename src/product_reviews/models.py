import dataclasses
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Review:
    """Review model."""

    rating: Optional[float]
    created_at: datetime
    text: Optional[str] = None
    pros: Optional[str] = None
    cons: Optional[str] = None
    summary: Optional[str] = None

    def to_dict(self):
        return dataclasses.asdict(self)

    def to_representation(self):
        d = self.to_dict()
        d["created_at"] = d["created_at"].isoformat()
        return d

    def to_json(self):
        r = self.to_representation()
        return json.dumps(r)

    @classmethod
    def from_representation(self, r):
        r["created_at"] = datetime.fromisoformat(r["created_at"])
        return Review(**r)


@dataclass
class ProviderReviewList:
    """Review list with provider name."""

    provider: str
    reviews: list[Review]

    def count(self) -> int:
        return len(self.reviews)


@dataclass
class HealthCheckResult:
    """
    Health check execution result.
    """

    is_healthy: bool
    message: str
    url: str = ""
    reviews_count: int = 0
