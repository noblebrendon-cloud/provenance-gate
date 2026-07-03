from app.citation import verify_citation
from app.models import Citation


def test_verifies_exact_quote_with_line_numbers() -> None:
    source = "Heading\n\nThe quoted passage is present.\nFinal line."
    citation = Citation(source_path="fixtures/demo.md", quote="The quoted passage is present.")

    result = verify_citation(source, citation)

    assert result.verified is True
    assert result.start_line == 3
    assert result.end_line == 3
    assert result.start_char == source.index(citation.quote)


def test_fails_when_quote_is_not_in_source() -> None:
    source = "Only public synthetic text lives here."
    citation = Citation(source_path="fixtures/demo.md", quote="private customer record")

    result = verify_citation(source, citation)

    assert result.verified is False
    assert result.start_char is None
    assert "not found" in result.reason


def test_fails_empty_quote() -> None:
    result = verify_citation("Some source", Citation(source_path="fixtures/demo.md", quote=""))

    assert result.verified is False
    assert result.reason == "Quote is empty."
