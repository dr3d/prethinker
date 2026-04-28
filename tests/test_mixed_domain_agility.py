from __future__ import annotations

from scripts.run_mixed_domain_agility import build_mixed_cases


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
