import json
from pathlib import Path

from src.carrier_contract_registry import (
    carrier_contract,
    carrier_contract_prompt_lines,
    validate_carrier_contract_registry,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_carrier_contract_registry_is_structurally_valid() -> None:
    assert validate_carrier_contract_registry() == []


def test_list_member_contract_blocks_ground_smuggling() -> None:
    contract = carrier_contract("list_member/4")

    assert contract is not None
    text = " ".join(contract["contract"] + contract["forbidden_uses"])
    assert "must not encode the legal ground" in text
    assert "prior-art reference" in text
    assert "companion typed relation" in text
    assert "range carrier remains required" in text


def test_document_date_contract_keeps_date_role_structured() -> None:
    contract = carrier_contract("document_date/3")

    assert contract is not None
    assert contract["args"] == ["document_or_subject_id", "date_kind_or_role", "date_value"]
    text = " ".join(contract["contract"] + contract["forbidden_uses"])
    assert "date_kind_or_role is a structural role" in text
    assert "source excerpt" in text


def test_legal_citation_contract_preserves_future_amendment_scope() -> None:
    contract = carrier_contract("legal_citation_detail/4")

    assert contract is not None
    text = " ".join(contract["contract"] + contract["forbidden_uses"])
    assert "future amendments" in text
    assert "amendment_scope" in text
    assert "full_obligation_text" in text


def test_fda_warning_letter_contracts_keep_domain_slots_compact() -> None:
    warning_letter = carrier_contract("fda_warning_letter/5")
    violation = carrier_contract("fda_violation/5")
    detail = carrier_contract("fda_violation_detail/5")
    response = carrier_contract("fda_response_requirement/6")
    omission = carrier_contract("domain_omission/5")

    assert warning_letter is not None
    assert warning_letter["args"] == [
        "letter_id",
        "issuing_office",
        "recipient_entity",
        "issue_date",
        "source_or_scope",
    ]
    warning_text = " ".join(warning_letter["contract"] + warning_letter["forbidden_uses"])
    assert "Use companion FDA carriers" in warning_text
    assert "all_letter_details" in warning_text

    assert violation is not None
    assert violation["args"] == [
        "violation_id",
        "letter_id",
        "violation_number",
        "violation_category",
        "source_or_scope",
    ]
    violation_text = " ".join(violation["contract"] + violation["forbidden_uses"])
    assert "controlled FDA warning-letter category palette" in violation_text
    assert "paragraph_summary_as_category" in violation_text

    assert detail is not None
    detail_text = " ".join(detail["contract"] + detail["forbidden_uses"])
    assert "one atomic detail" in detail_text
    assert "mini-paragraph" in detail_text
    assert "multi_detail_summary" in detail_text

    assert response is not None
    response_text = " ".join(response["contract"] + response["forbidden_uses"])
    assert "fifteen_working_days" in response_text
    assert "full_response_instructions" in response_text

    assert omission is not None
    omission_text = " ".join(omission["contract"] + omission["forbidden_uses"])
    assert "makes gaps visible" in omission_text
    assert "do not normalize the slash to an underscore" in omission_text
    assert "answer_substitute" in omission_text


def test_fda_domain_profile_registry_matches_registered_contracts() -> None:
    registry_path = REPO_ROOT / "datasets" / "domain_profiles" / "fda_warning_letter_v1" / "ontology_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    predicates = registry["predicates"]

    assert len(predicates) >= 10
    for item in predicates:
        contract = carrier_contract(item["signature"])
        assert contract is not None
        assert item["args"] == contract["args"]


def test_monetary_payment_contract_keeps_amount_authority_and_purpose_typed() -> None:
    contract = carrier_contract("monetary_payment/5")

    assert contract is not None
    assert contract["args"] == ["subject_id", "amount", "authority_or_basis", "purpose_or_use", "source_or_scope"]
    text = " ".join(contract["contract"] + contract["forbidden_uses"])
    assert "usd_725000" in text
    assert "authority_or_basis" in text
    assert "purpose_or_use" in text
    assert "source_excerpt" in text


def test_obligation_detail_contract_keeps_obligation_terms_atomic() -> None:
    contract = carrier_contract("obligation_detail/5")

    assert contract is not None
    assert contract["args"] == ["obligation_id", "detail_kind", "detail_value", "role_or_purpose", "source_or_scope"]
    text = " ".join(contract["contract"] + contract["forbidden_uses"])
    assert "one atomic source-stated term" in text
    assert "schedule_9" in text
    assert "one_year" in text
    assert "full_obligation_text" in text


def test_procedural_rule_detail_contract_keeps_rule_consequences_atomic() -> None:
    contract = carrier_contract("procedural_rule_detail/5")

    assert contract is not None
    assert contract["args"] == ["rule_id", "detail_kind", "detail_value", "rule_context_or_action", "source_or_scope"]
    text = " ".join(contract["contract"] + contract["forbidden_uses"])
    assert "one atomic source-stated term" in text
    assert "deemed_denied" in text
    assert "basis_known_or_should_have_been_known" in text
    assert "full_rule_text" in text
    assert "computed_deadline" in text


def test_official_document_wrapper_contracts_preserve_typed_slots() -> None:
    identifier = carrier_contract("document_identifier_occurrence/5")
    registrant = carrier_contract("registrant_identity/2")
    registrant_name = carrier_contract("registrant_name/2")
    checkbox = carrier_contract("document_checkbox_provision/5")
    signatory = carrier_contract("document_signatory/3")
    signature = carrier_contract("document_signature/5")
    security_listing = carrier_contract("document_security_listing/5")

    assert identifier is not None
    assert identifier["args"] == [
        "document_id",
        "identifier_kind",
        "identifier_value",
        "occurrence_scope_or_label",
        "source_order",
    ]
    identifier_text = " ".join(identifier["contract"] + identifier["forbidden_uses"])
    assert "document_id_as_value" in identifier_text
    assert "Do not collapse distinct values" in identifier_text

    assert registrant is not None
    assert registrant["args"] == ["registrant_entity", "incorporation_or_organization_jurisdiction"]
    registrant_text = " ".join(registrant["contract"] + registrant["forbidden_uses"])
    assert "static charter/organization attribute" in registrant_text
    assert "status_state_at/4" in registrant_text
    assert "restatement_status" in registrant_text

    assert registrant_name is not None
    assert registrant_name["args"] == ["registrant_entity", "legal_name"]
    registrant_name_text = " ".join(registrant_name["contract"] + registrant_name["forbidden_uses"])
    assert "exact source-stated registrant" in registrant_name_text
    assert "ticker_symbol" in registrant_name_text
    assert "jurisdiction_carrier" in registrant_name_text

    assert checkbox is not None
    assert checkbox["args"] == ["document_id", "provision_label", "checkbox_state", "rule_label", "citation"]
    checkbox_text = " ".join(checkbox["contract"] + checkbox["forbidden_uses"])
    assert "one row per source-stated provision row" in checkbox_text
    assert "unstated_legal_consequence" in checkbox_text

    assert signatory is not None
    assert signatory["args"] == ["document_id", "signatory_name", "capacity_or_title"]
    signatory_text = " ".join(signatory["contract"] + signatory["forbidden_uses"])
    assert "source-stated signing capacity" in signatory_text
    assert "generic_named_person" in signatory_text

    assert signature is not None
    assert signature["args"] == [
        "document_id",
        "signatory_name",
        "capacity_or_title",
        "signature_date",
        "source_or_scope",
    ]
    signature_text = " ".join(signature["contract"] + signature["forbidden_uses"])
    assert "one source-stated signing act" in signature_text
    assert "filing_date_as_signature_date" in signature_text

    assert security_listing is not None
    assert security_listing["args"] == [
        "document_id",
        "security_class",
        "par_value",
        "trading_symbol",
        "exchange_or_market",
    ]
    listing_text = " ".join(security_listing["contract"] + security_listing["forbidden_uses"])
    assert "one source-stated listed-security table row" in listing_text
    assert "not_stated" in listing_text
    assert "ticker_only" in listing_text


def test_person_role_contracts_are_role_membership_only() -> None:
    role2 = carrier_contract("person_role/2")
    role3 = carrier_contract("person_role/3")
    party_context = carrier_contract("party_role_context/4")

    assert role2 is not None
    assert role2["args"] == ["person_id_or_name", "role_or_title"]
    role2_text = " ".join(role2["contract"] + role2["forbidden_uses"])
    assert "role membership only" in role2_text
    assert "role_label_as_person" in role2_text
    assert "unstated_authority" in role2_text

    assert role3 is not None
    assert role3["args"] == ["person_id_or_name", "role_or_title", "scope_or_context"]
    role3_text = " ".join(role3["contract"] + role3["forbidden_uses"])
    assert "source-stated context" in role3_text
    assert "Use a more specific carrier" in role3_text
    assert "action_performed" in role3_text

    assert party_context is not None
    assert party_context["args"] == ["scope_or_context", "party_or_person", "role_or_status", "source_or_scope"]
    party_text = " ".join(party_context["contract"] + party_context["forbidden_uses"])
    assert "Stable party-role relation" in party_text
    assert "party_role/3" in party_text
    assert "argument_order_guess" in party_text


def test_carrier_contract_prompt_lines_render_only_known_signatures() -> None:
    lines = carrier_contract_prompt_lines(["list_member/4", "not_registered/2", "claim_ground/4"])
    text = "\n".join(lines)

    assert "CARRIER CONTRACT list_member/4" in text
    assert "CARRIER CONTRACT claim_ground/4" in text
    assert "not_registered/2" not in text
    assert "forbidden uses" in text


def test_carrier_contract_prompt_lines_render_value_domains() -> None:
    lines = carrier_contract_prompt_lines(["fda_violation/5", "fda_conclusion_scope/4"])
    text = "\n".join(lines)

    assert "violation_category allowed values" in text
    assert "quality_unit_failure" in text
    assert "contamination_control" in text
    assert "investigation_failure" in text
    assert "scope_kind allowed values" in text
    assert "cited_violations_not_exhaustive" in text


def test_fda_violation_detail_contract_names_record_review_subject_trigger() -> None:
    lines = carrier_contract_prompt_lines(["fda_violation_detail/5"])
    text = "\n".join(lines)

    assert "record_review_subject" in text
    assert "If a violation states that required records were not reviewed" in text
    assert "OOS results" in text
    assert "environmental-monitoring results" in text
    assert "Do not encode those investigation subjects as affected_product" in text
    assert "Use procedure_scope for source-stated validation" in text
    assert "Do not encode a validation or qualification scope as missing_record_type" in text
    assert "affected_lot" in text


def test_fda_violation_contract_disambiguates_contamination_control_from_aseptic_processing() -> None:
    lines = carrier_contract_prompt_lines(["fda_violation/5"])
    text = "\n".join(lines)

    assert "violation_category=contamination_control" in text
    assert "prevent microbiological contamination" in text
    assert "violation_category=aseptic_processing only" in text
    assert "explicitly names aseptic processing" in text
    assert "clean, disinfect, maintain, or control rooms/equipment" in text
    assert "batch production/control records" in text
    assert "failing to thoroughly investigate unexplained discrepancies" in text


def test_fda_adulteration_basis_contract_includes_insanitary_conditions() -> None:
    lines = carrier_contract_prompt_lines(["fda_adulteration_basis/5"])
    text = "\n".join(lines)

    assert "adulteration_insanitary_conditions" in text


def test_fda_facility_identity_contract_blocks_document_ids_as_facility_ids() -> None:
    lines = carrier_contract_prompt_lines(["fda_facility_identity/5"])
    text = "\n".join(lines)

    assert "MARCS-CMS" in text
    assert "not_stated" in text


def test_fda_violation_citation_contract_allows_letter_level_consultant_citation() -> None:
    lines = carrier_contract_prompt_lines(["fda_violation_citation/4"])
    text = "\n".join(lines)

    assert "one violation or warning-letter subject" in text
    assert "use the warning-letter id as the first argument" in text
    assert "citation_role=consultant_qualification" in text


def test_fda_consultant_recommendation_contract_rejects_citation_as_provenance() -> None:
    lines = carrier_contract_prompt_lines(["fda_consultant_recommendation/4"])
    text = "\n".join(lines)

    assert "Do not put a citation atom such as cfr_21_211_34 in source_or_scope" in text
    assert "separate consultant qualification citation row" in text


def test_fda_inspection_event_contract_keeps_agency_separate_from_issuing_office() -> None:
    lines = carrier_contract_prompt_lines(["fda_inspection_event/6"])
    text = "\n".join(lines)

    assert "not the warning-letter issuing office header" in text
    assert "If the source says FDA inspected, use fda" in text


def test_fda_prior_warning_contract_prefers_source_stated_firm_scope() -> None:
    lines = carrier_contract_prompt_lines(["fda_prior_warning_letter/5"])
    text = "\n".join(lines)

    assert "only when the source explicitly states a prior warning letter" in text
    assert "prior inspection finding" in text
    assert "issued to the firm" in text
    assert "rather than the inspected facility" in text


def test_fda_conclusion_scope_contract_disambiguates_responsibility_recurrence() -> None:
    lines = carrier_contract_prompt_lines(["fda_conclusion_scope/4"])
    text = "\n".join(lines)

    assert "scope_kind=recurrence_prevention and scope_value=responsibility_to_correct" in text
    assert "Use scope_value=prevent_recurrence only" in text
    assert "ownership_change_context only when the source explicitly mentions ownership" in text
