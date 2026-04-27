from __future__ import annotations

from pathlib import Path

from scripts.run_mixed_domain_agility import build_mixed_cases
from src.domain_profiles import load_domain_profile_catalog, select_domain_profile


ROOT = Path(__file__).resolve().parents[1]


def test_mixed_domain_agility_case_builder_includes_frontier_sources():
    cases = build_mixed_cases()
    sources = {str(row.get("source")) for row in cases}
    assert "goldilocks" in sources
    assert "glitch" in sources
    assert "ledger" in sources
    assert "silverton" in sources
    assert "harbor" in sources
    assert "courtlistener" in sources
    assert "sec_contracts" in sources
    assert "medical" in sources


def test_mixed_domain_selector_handles_representative_sources():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    cases = {
        str(row.get("source")): row
        for row in build_mixed_cases()
        if str(row.get("source")) not in {"harbor"}
    }
    expected_by_source = {
        "goldilocks": "story_world@v0",
        "glitch": "story_world@v0",
        "ledger": "probate@v0",
        "silverton": "probate@v0",
        "courtlistener": "legal_courtlistener@v0",
        "sec_contracts": "sec_contracts@v0",
        "medical": "medical@v0",
    }
    for source, expected_profile in expected_by_source.items():
        row = cases[source]
        selected = select_domain_profile(
            str(row.get("utterance") or ""),
            context=[str(item) for item in row.get("context", [])],
            catalog=catalog,
        )
        assert selected.get("profile_id") == expected_profile
