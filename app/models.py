from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


ReviewDecision = Literal["approved", "rejected"]


@dataclass(frozen=True)
class Citation:
    source_path: str
    quote: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimCard:
    id: str
    text: str
    citation: Citation

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "text": self.text,
            "citation": self.citation.to_dict(),
        }
