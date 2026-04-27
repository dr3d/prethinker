from __future__ import annotations

from pathlib import Path

from src.domain_profiles import (
    load_domain_profile_catalog,
    load_profile_package,
    profile_package_context,
    profile_package_contracts,
    thin_profile_roster,
)


ROOT = Path(__file__).resolve().parents[1]


def test_domain_profile_catalog_loads_thin_roster():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    roster = thin_profile_roster(catalog)
    profile_ids = {row["profile_id"] for row in roster}
    assert "medical@v0" in profile_ids
    assert "story_world@v0" in profile_ids
    assert "probate@v0" in profile_ids
    medical = next(row for row in roster if row["profile_id"] == "medical@v0")
    assert "Bounded medical memory" in medical["description"]
    assert any("medication" in item for item in medical["use_when"])
    assert any("clinical advice" in item for item in medical["avoid_when"])
    assert "thick_context_source" not in medical


def test_mock_profile_packages_are_declarative_and_loadable():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    story = load_profile_package("story_world@v0", catalog)
    probate = load_profile_package("probate@v0", catalog)
    assert story["status"] == "proposal_mock"
    assert probate["status"] == "proposal_mock"
    story_contracts = profile_package_contracts(story)
    story_signatures = {row["signature"] for row in story_contracts}
    assert "tasted/2" in story_signatures
    assert "was_tasted/1" in story_signatures
    probate_contracts = profile_package_contracts(probate)
    probate_signatures = {row["signature"] for row in probate_contracts}
    assert "claimed/3" in probate_signatures
    assert "candidate_identity/2" in probate_signatures
    assert any("unknown_agent" in line for line in profile_package_context(story))
    assert any("claim" in line for line in profile_package_context(probate))
