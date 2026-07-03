from __future__ import annotations

import os
from typing import Protocol

from app.models import Citation, ClaimCard


class ClaimProvider(Protocol):
    name: str

    def generate_claims(self, source_text: str, source_path: str) -> list[ClaimCard]:
        """Return candidate claim cards for the source document."""


class DemoProvider:
    name = "demo"

    def generate_claims(self, source_text: str, source_path: str) -> list[ClaimCard]:
        return [
            ClaimCard(
                id="claim-001",
                text=(
                    "The Aurora Memory Pilot began in March 2026 to evaluate "
                    "provenance-aware claim review."
                ),
                citation=Citation(
                    source_path=source_path,
                    quote=(
                        "The Aurora Memory Pilot began in March 2026 to evaluate "
                        "provenance-aware claim review for internal research summaries."
                    ),
                ),
            ),
            ClaimCard(
                id="claim-002",
                text="The pilot uses synthetic examples instead of customer records.",
                citation=Citation(
                    source_path=source_path,
                    quote=(
                        "All review examples in the pilot use synthetic operational notes, "
                        "fictional team names, and generated metrics rather than customer records."
                    ),
                ),
            ),
            ClaimCard(
                id="claim-003",
                text="A reviewer must approve or reject every generated claim before export.",
                citation=Citation(
                    source_path=source_path,
                    quote=(
                        "The pilot requires reviewers to approve or reject each generated claim "
                        "before the claim can appear in a decision packet."
                    ),
                ),
            ),
            ClaimCard(
                id="claim-004",
                text="Citation verification is an exact passage match against the fixture.",
                citation=Citation(
                    source_path=source_path,
                    quote=(
                        "A source passage passes citation verification only when the quoted text "
                        "appears exactly in the loaded Markdown fixture."
                    ),
                ),
            ),
        ]


class FireworksProvider:
    name = "fireworks"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("FIREWORKS_API_KEY")

    def generate_claims(self, source_text: str, source_path: str) -> list[ClaimCard]:
        if not self.api_key:
            raise RuntimeError(
                "FIREWORKS_API_KEY is required when PROVIDER=fireworks and DEMO_MODE=false."
            )
        raise NotImplementedError(
            "FireworksProvider is a public integration boundary only. Add the real "
            "request once credentials, supported model names, and official API details "
            "are available."
        )


def demo_mode_enabled() -> bool:
    raw = os.environ.get("DEMO_MODE", "true").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def get_provider() -> ClaimProvider:
    provider_name = os.environ.get("PROVIDER", "demo").strip().lower()

    if demo_mode_enabled() or provider_name == "demo":
        return DemoProvider()

    if provider_name == "fireworks":
        return FireworksProvider()

    raise ValueError(f"Unknown provider: {provider_name}")
