from __future__ import annotations

from dataclasses import asdict, dataclass

from app.models import Citation


@dataclass(frozen=True)
class VerificationResult:
    source_path: str
    quote: str
    verified: bool
    start_char: int | None
    end_char: int | None
    start_line: int | None
    end_line: int | None
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _normalize_newlines(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def verify_citation(source_text: str, citation: Citation) -> VerificationResult:
    """Verify that the cited quote appears exactly in the source text."""
    normalized_source = _normalize_newlines(source_text)
    normalized_quote = _normalize_newlines(citation.quote)

    if not normalized_quote:
        return VerificationResult(
            source_path=citation.source_path,
            quote=citation.quote,
            verified=False,
            start_char=None,
            end_char=None,
            start_line=None,
            end_line=None,
            reason="Quote is empty.",
        )

    start = normalized_source.find(normalized_quote)
    if start == -1:
        return VerificationResult(
            source_path=citation.source_path,
            quote=citation.quote,
            verified=False,
            start_char=None,
            end_char=None,
            start_line=None,
            end_line=None,
            reason="Quoted passage was not found in the source document.",
        )

    end = start + len(normalized_quote)
    start_line = normalized_source.count("\n", 0, start) + 1
    end_line = normalized_source.count("\n", 0, end) + 1

    return VerificationResult(
        source_path=citation.source_path,
        quote=citation.quote,
        verified=True,
        start_char=start,
        end_char=end,
        start_line=start_line,
        end_line=end_line,
        reason="Quoted passage exists in the source document.",
    )
