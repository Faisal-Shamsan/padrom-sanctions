"""Unit tests for the screening matcher (no DB required)."""

from src.ingestion.models import SanctionEntry
from src.screening.matcher import find_top_match, normalise


def _make_entry(
    primary_name: str,
    aliases: list[str] | None = None,
) -> SanctionEntry:
    return SanctionEntry(
        source_list="EU",
        external_id="TEST-001",
        entity_type="P",
        primary_name=primary_name,
        aliases=aliases or [],
        raw_xml="",
    )


class TestNormalise:
    def test_lowercases(self) -> None:
        assert normalise("JOHN DOE") == "john doe"

    def test_strips_punctuation(self) -> None:
        # Punctuation is replaced with spaces, then whitespace is collapsed + stripped
        assert normalise("O'Brien, Jr.") == "o brien jr"

    def test_collapses_whitespace(self) -> None:
        assert normalise("  John   Doe  ") == "john doe"


class TestFindTopMatch:
    def test_exact_match_on_primary_name(self) -> None:
        entry = _make_entry("Viktor Bout")
        candidates = [entry]
        result_entry, score = find_top_match("viktor bout", candidates)
        assert result_entry is entry
        assert score == 1.0

    def test_exact_match_on_alias(self) -> None:
        entry = _make_entry(
            "Viktor Anatolyevich Bout", aliases=["Viktor Bout", "Victor Bout"]
        )
        candidates = [entry]
        result_entry, score = find_top_match("victor bout", candidates)
        assert result_entry is entry
        assert score == 1.0

    def test_fuzzy_hit_above_threshold(self) -> None:
        entry = _make_entry("Viktor Bout")
        candidates = [entry]
        # Minor misspelling — should still score above 0.85
        result_entry, score = find_top_match("viktor baut", candidates)
        assert result_entry is entry
        assert score >= 0.85

    def test_score_below_threshold_returns_none(self) -> None:
        entry = _make_entry("Viktor Bout")
        candidates = [entry]
        # Completely unrelated name
        result_entry, score = find_top_match("john smith", candidates)
        assert result_entry is None
        assert score == 0.0

    def test_empty_candidates_returns_none(self) -> None:
        result_entry, score = find_top_match("viktor bout", [])
        assert result_entry is None
        assert score == 0.0

    def test_selects_best_among_multiple_candidates(self) -> None:
        close = _make_entry("Viktor Bout")
        far = _make_entry("John Smith")
        candidates = [far, close]
        result_entry, score = find_top_match("viktor bout", candidates)
        assert result_entry is close
        assert score == 1.0

    def test_normalisation_applied_before_comparison(self) -> None:
        entry = _make_entry("Viktor Bout")
        candidates = [entry]
        # The service normalises before calling find_top_match; test the same path
        result_entry, score = find_top_match(normalise("viktor  bout!"), candidates)
        assert result_entry is entry
        assert score == 1.0
