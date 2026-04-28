from __future__ import annotations

from pathlib import Path

from src.domain_profiles import (
    load_domain_profile_catalog,
    load_profile_package,
    profile_package_context,
    profile_package_contracts,
    select_domain_profile,
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
    assert "legal_courtlistener@v0" in profile_ids
    assert "sec_contracts@v0" in profile_ids
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
    assert "has_trait/2" in story_signatures
    assert "returned_from/2" in story_signatures
    probate_contracts = profile_package_contracts(probate)
    probate_signatures = {row["signature"] for row in probate_contracts}
    assert "claimed/3" in probate_signatures
    assert "candidate_identity/2" in probate_signatures
    assert "guardianship_of/2" in probate_signatures
    legal = load_profile_package("legal_courtlistener@v0", catalog)
    legal_signatures = {row["signature"] for row in profile_package_contracts(legal)}
    assert "access_log_entry/4" in legal_signatures
    assert "document_states/3" in legal_signatures
    assert "relative_date_resolves_to/3" in legal_signatures
    assert "interval_start/2" in legal_signatures
    assert "outside_district_interval/3" in legal_signatures
    legal_contracts = profile_package_contracts(legal)
    finding_contract = next(row for row in legal_contracts if row["signature"] == "finding/4")
    assert finding_contract["validators"][0]["reason"] == "allegation_not_court_finding"
    sec = load_profile_package("sec_contracts@v0", catalog)
    sec_signatures = {row["signature"] for row in profile_package_contracts(sec)}
    assert "clearance_event/4" in sec_signatures
    sec_contracts = profile_package_contracts(sec)
    breach_contract = next(row for row in sec_contracts if row["signature"] == "breach_event/2")
    assert breach_contract["validators"][0]["reason"] == "obligation_language_not_breach_event"
    assert any("unknown_agent" in line for line in profile_package_context(story))
    assert any("source_fidelity_policy" in line for line in profile_package_context(story))
    assert any("Little Wee Bear" in line and "Baby Bear" in line for line in profile_package_context(story))
    assert any("claim" in line for line in profile_package_context(probate))


def test_profile_selector_can_switch_across_medical_legal_and_contract_turns():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    turns = [
        ("Priya is taking Coumadin and her serum creatinine was repeated.", "medical@v0"),
        ("In Doe v. Acme, the complaint alleged breach but the court found only timeliness.", "legal_courtlistener@v0"),
        ("The borrower shall repay the loan after the maturity date unless default is waived.", "sec_contracts@v0"),
        ("Mara's blood pressure reading was high.", "medical@v0"),
    ]
    selected = [
        select_domain_profile(utterance, catalog=catalog, context=[]).get("profile_id")
        for utterance, _expected in turns
    ]
    assert selected == [expected for _utterance, expected in turns]


def test_profile_selector_does_not_stick_to_previous_domain_context():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    sec_context = [
        "obligation(borrower, repay_loan_after_maturity, loan_agreement).",
        "subject_to(repay_loan_after_maturity, default_not_waived).",
    ]
    selected = select_domain_profile(
        "Mara's blood pressure reading was high.",
        catalog=catalog,
        context=sec_context,
    )
    assert selected.get("profile_id") == "medical@v0"


def test_profile_selector_uses_profile_owned_keywords_and_context():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    selected = select_domain_profile(
        "Nia wrote 'last Friday' in the flood note.",
        catalog=catalog,
        context=["Existing note anchor: flood_note dated May 13, 2024."],
    )
    assert selected.get("profile_id") == "legal_courtlistener@v0"
    selected = select_domain_profile(
        "Artur: papa me dijo en el taller, solo nosotros dos, 'all mine now' -- no Beatrice.",
        catalog=catalog,
        context=["Rule: verbal changes require two non-beneficiary witnesses."],
    )
    assert selected.get("profile_id") == "probate@v0"


def test_profile_selector_uses_context_for_anaphoric_medical_followup():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    selected = select_domain_profile(
        "It came back high after the repeat this afternoon.",
        catalog=catalog,
        context=[
            "Active patient: Priya.",
            "Previous event: serum creatinine was repeated this afternoon.",
        ],
    )
    assert selected.get("profile_id") == "medical@v0"


def test_profile_selector_uses_profile_owned_noisy_probate_keywords():
    catalog = load_domain_profile_catalog(ROOT / "modelfiles" / "domain_profile_catalog.v0.json")
    selected = select_domain_profile(
        "Btrice txtd: i was in Londn ONT, pas Londres UK, jamais outta country > a wknd.",
        catalog=catalog,
        context=[
            "Beatrice is a Silverton beneficiary.",
            "The forfeiture condition requires more than five consecutive years outside the country.",
        ],
    )
    assert selected.get("profile_id") == "probate@v0"
