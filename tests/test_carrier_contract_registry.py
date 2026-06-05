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
    cgmp_item = carrier_contract("fda_cgmp_violation_item/5")
    citation = carrier_contract("fda_violation_citation/4")
    detail = carrier_contract("fda_violation_detail/5")
    detail_slot = carrier_contract("fda_violation_detail_slot/4")
    response_assessment = carrier_contract("fda_response_assessment/5")
    response_assessment_item = carrier_contract("fda_response_assessment_item/6")
    response_documentation_gap = carrier_contract("fda_response_documentation_gap/5")
    response_investigation_gap = carrier_contract("fda_response_investigation_gap/5")
    insanitary_condition = carrier_contract("fda_insanitary_condition/5")
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
    assert "501(a)(2)(B) CGMP violations" in violation_text
    assert "501(a)(2)(A) insanitary-condition observations" in violation_text
    assert "same local violation_N atom in violation_id and violation_number" in violation_text
    assert "Do not use the warning-letter id" in violation_text
    assert "Do not create an fda_violation/5 row from an FDCA 501(a)(2)(A)" in violation_text
    assert "do not renumber the modeled subset" in violation_text
    assert "Do not merge several numbered CGMP bullets" in violation_text
    assert "paragraph_summary_as_category" in violation_text
    assert "insanitary_condition_duplicate" in violation_text

    assert cgmp_item is not None
    assert cgmp_item["args"] == [
        "violation_id",
        "letter_id",
        "violation_number",
        "cgmps_citation",
        "source_or_scope",
    ]
    cgmp_item_text = " ".join(cgmp_item["contract"] + cgmp_item["forbidden_uses"])
    assert "Use this bundle before category population" in cgmp_item_text
    assert "same local violation_N atom" in cgmp_item_text
    assert "only CGMP requirement citations" in cgmp_item_text
    assert "adulteration_authority" in cgmp_item_text

    assert citation is not None
    citation_text = " ".join(citation["contract"] + citation["forbidden_uses"])
    assert "specific numbered fda_violation/5 subject" in citation_text
    assert "same violation_N atom used as both violation_id and violation_number" in citation_text
    assert "Do not reuse the same cgmps_requirement citation" in citation_text
    assert "adulteration-authority citations" in citation_text
    assert "Do not collect citations from several numbered violations" in citation_text

    assert detail is not None
    detail_text = " ".join(detail["contract"] + detail["forbidden_uses"])
    assert "one atomic detail" in detail_text
    assert "observation_subject" in detail["value_domains"]["detail_kind"]
    assert "facility/equipment/control-style violation" in detail_text
    assert "Do not use observation_subject for investigation_failure" in detail_text
    assert "mini-paragraph" in detail_text
    assert "multi_detail_summary" in detail_text

    assert detail_slot is not None
    assert detail_slot["args"] == ["violation_id", "detail_kind", "role_or_purpose", "source_or_scope"]
    detail_slot_text = " ".join(detail_slot["contract"] + detail_slot["forbidden_uses"])
    assert "intentionally does not claim the open detail_value" in detail_slot_text
    assert "answer substitute" in detail_slot_text
    assert "detail_value_claim" in detail_slot_text

    assert response_assessment is not None
    assert response_assessment["args"] == [
        "assessment_id",
        "violation_id",
        "assessment_kind",
        "assessment_scope",
        "source_or_scope",
    ]
    response_assessment_text = " ".join(
        response_assessment["contract"] + response_assessment["forbidden_uses"]
    )
    assert "corrective action" in response_assessment_text
    assert "same local violation_N atom" in response_assessment_text
    assert "attach by the source-stated critique topic and citation family" in response_assessment_text
    assert "did not provide sufficient supporting documentation" in response_assessment_text
    assert "documentation_not_provided has priority" in response_assessment_text
    assert "failed to investigate" in response_assessment_text
    assert "failing to implement an interim corrective action" in response_assessment_text
    assert "unable to assess" in response_assessment_text
    assert "response_inadequate" in response_assessment["value_domains"]["assessment_kind"]
    assert "corrective_action_evaluation" in response_assessment["value_domains"]["assessment_scope"]
    assert "full_response_paragraph" in response_assessment_text

    assert response_assessment_item is not None
    assert response_assessment_item["args"] == [
        "assessment_id",
        "violation_id",
        "cgmps_citation",
        "assessment_kind",
        "assessment_scope",
        "source_or_scope",
    ]
    response_assessment_item_text = " ".join(
        response_assessment_item["contract"] + response_assessment_item["forbidden_uses"]
    )
    assert "Use this bundle before response-assessment projection" in response_assessment_item_text
    assert "citation agrees with the existing fda_cgmp_violation_item/5 bundle" in response_assessment_item_text
    assert "not by paragraph order" in response_assessment_item_text
    assert "environmental-monitoring/action-limit" in response_assessment_item_text
    assert "documentation_not_provided has priority" in response_assessment_item_text
    assert "cfr_21_211_113_b" in response_assessment_item["value_domains"]["cgmps_citation"]
    assert "documentation_not_provided" in response_assessment_item["value_domains"]["assessment_kind"]
    assert "corrective_action_evaluation" in response_assessment_item["value_domains"]["assessment_scope"]
    assert "citation_not_in_numbered_item_map" in response_assessment_item_text

    assert response_documentation_gap is not None
    assert response_documentation_gap["args"] == [
        "gap_id",
        "violation_id",
        "cgmps_citation",
        "gap_kind",
        "source_or_scope",
    ]
    response_documentation_gap_text = " ".join(
        response_documentation_gap["contract"] + response_documentation_gap["forbidden_uses"]
    )
    assert "missing submitted material" in response_documentation_gap_text
    assert "documentation_not_provided" in response_documentation_gap_text
    assert "citation will be dropped before projection" in response_documentation_gap_text
    assert "supporting_documentation" in response_documentation_gap["value_domains"]["gap_kind"]
    assert "cfr_21_211_113_b" in response_documentation_gap["value_domains"]["cgmps_citation"]
    assert "missing_document_title" in response_documentation_gap_text

    assert response_investigation_gap is not None
    assert response_investigation_gap["args"] == [
        "gap_id",
        "violation_id",
        "cgmps_citation",
        "investigation_gap_kind",
        "source_or_scope",
    ]
    response_investigation_gap_text = " ".join(
        response_investigation_gap["contract"] + response_investigation_gap["forbidden_uses"]
    )
    assert "failed to investigate" in response_investigation_gap_text
    assert "not_investigated" in response_investigation_gap_text
    assert "only for the investigation-failure citation family cfr_21_211_192" in response_investigation_gap_text
    assert "thorough_investigation_not_ensured" in response_investigation_gap["value_domains"]["investigation_gap_kind"]
    assert "cfr_21_211_192" in response_investigation_gap["value_domains"]["cgmps_citation"]
    assert "organism_name" in response_investigation_gap_text

    assert insanitary_condition is not None
    assert insanitary_condition["args"] == [
        "condition_id",
        "letter_id",
        "condition_number",
        "condition_category",
        "source_or_scope",
    ]
    condition_text = " ".join(insanitary_condition["contract"] + insanitary_condition["forbidden_uses"])
    assert "501(a)(2)(A)" in condition_text
    assert "separate CGMP violation list" in condition_text
    assert "contact with a critical surface" in condition_text
    assert "first-air disruption" in condition_text
    assert "full_observation_sentence" in condition_text

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


def test_ntsb_investigation_contracts_keep_skeleton_and_prose_separate() -> None:
    report = carrier_contract("ntsb_report/5")
    occurrence = carrier_contract("ntsb_occurrence/6")
    occurrence_time = carrier_contract("ntsb_occurrence_time/5")
    vehicle = carrier_contract("ntsb_vehicle/6")
    party = carrier_contract("ntsb_party/5")
    injuries = carrier_contract("ntsb_injury_count/6")
    timeline = carrier_contract("ntsb_timeline_event/6")
    condition = carrier_contract("ntsb_condition/5")
    safety_action = carrier_contract("ntsb_safety_action/6")
    finding = carrier_contract("ntsb_finding/5")

    assert report is not None
    assert report["args"] == ["report_id", "report_kind", "report_status", "issue_date", "source_or_scope"]
    report_text = " ".join(report["contract"] + report["forbidden_uses"])
    assert "Use companion NTSB carriers" in report_text
    assert "full_report_title" in report_text
    assert "aviation_accident" in report["value_domains"]["report_kind"]

    assert occurrence is not None
    assert occurrence["args"] == [
        "occurrence_id",
        "report_id",
        "occurrence_kind",
        "occurrence_date",
        "location_id",
        "source_or_scope",
    ]
    occurrence_text = " ".join(occurrence["contract"] + occurrence["forbidden_uses"])
    assert "Do not use this row for every timeline event" in occurrence_text
    assert "occurrence_<report_id>" in occurrence_text
    assert "event_kind=occurrence_time" in occurrence_text
    assert "location_prefix_atom" in occurrence_text
    assert "full_event_summary" in occurrence_text

    assert occurrence_time is not None
    assert occurrence_time["args"] == [
        "occurrence_id",
        "time_value",
        "time_basis",
        "time_role",
        "source_or_scope",
    ]
    occurrence_time_text = " ".join(occurrence_time["contract"] + occurrence_time["forbidden_uses"])
    assert "Occurrence-time relation" in occurrence_time_text
    assert "t_1713_30_est" in occurrence_time_text
    assert "t_2025_11_05_1713_30_est" in occurrence_time_text
    assert "bare_numeric_time_atom" in occurrence_time_text
    assert "eastern_standard_time" in occurrence_time["value_domains"]["time_basis"]

    assert vehicle is not None
    assert vehicle["args"] == [
        "vehicle_id",
        "occurrence_id",
        "vehicle_role",
        "vehicle_type",
        "identifier_value",
        "source_or_scope",
    ]
    vehicle_text = " ".join(vehicle["contract"] + vehicle["forbidden_uses"])
    assert "document_id_as_identifier" in vehicle_text
    assert "identifier_value=not_stated" in vehicle_text
    assert "crowd out the accident_vehicle" in vehicle_text
    assert "vehicle_type=combination_vehicle" in vehicle_text
    assert "Passing or oncoming vehicles" in vehicle_text
    assert "Parked struck objects" in vehicle_text
    assert "tow_vessel" in vehicle["value_domains"]["vehicle_role"]

    assert party is not None
    assert party["args"] == ["occurrence_id", "party_id", "party_role", "party_name", "source_or_scope"]
    party_text = " ".join(party["contract"] + party["forbidden_uses"])
    assert "does not itself assert fault" in party_text
    assert "generic_role_as_name" in party_text

    assert injuries is not None
    assert injuries["args"] == [
        "occurrence_id",
        "subject_scope",
        "fatal_count",
        "serious_count",
        "minor_count",
        "source_or_scope",
    ]
    injuries_text = " ".join(injuries["contract"] + injuries["forbidden_uses"])
    assert "one source-stated casualty table row" in injuries_text
    assert "full six-slot shape" in injuries_text
    assert "5_8_3" in injuries_text
    assert "driver, 0, 1, 0" in injuries_text
    assert "duplicate not_stated partition" in injuries_text
    assert "victim_narrative" in injuries_text

    assert timeline is not None
    assert timeline["args"] == [
        "occurrence_id",
        "event_id",
        "event_kind",
        "event_time_or_date",
        "sequence_role",
        "source_or_scope",
    ]
    timeline_text = " ".join(timeline["contract"] + timeline["forbidden_uses"])
    assert "full_event_sentence" in timeline_text
    assert "warning_issued" in timeline["value_domains"]["event_kind"]
    assert "mutual_aid_request" in timeline["value_domains"]["event_kind"]
    assert "hazmat_entry" in timeline["value_domains"]["event_kind"]
    assert "road_closure_ordered" in timeline["value_domains"]["event_kind"]
    assert "road_closure_completed" in timeline["value_domains"]["event_kind"]
    assert "response_sequence" in timeline_text
    assert "do not encode postcrash reviews" in timeline_text

    assert condition is not None
    condition_text = " ".join(condition["contract"] + condition["forbidden_uses"])
    assert "one atomic source-stated value" in condition_text
    assert "condition_kind=visibility" in condition_text
    assert "degrees_310_knots_4" in condition_text
    assert "condition_kind=speed_limit" in condition_text
    assert "rural_unlit_undivided_highway" in condition_text
    assert "cvr_not_recovered" in condition_text
    assert "bare_recorder_state" in condition_text
    assert "probable_cause_text" in condition_text
    assert "hazmat_classification" in condition["value_domains"]["condition_kind"]
    assert "hazmat_material" in condition["value_domains"]["condition_kind"]
    assert "hazmat_un_number" in condition["value_domains"]["condition_kind"]
    assert "speed_limit" in condition["value_domains"]["condition_kind"]

    assert safety_action is not None
    safety_text = " ".join(safety_action["contract"] + safety_action["forbidden_uses"])
    assert "one source-stated safety action" in safety_text
    assert "unexplained initials-only atom" in safety_text
    assert "first-class safety-action rows" in safety_text
    assert "full_directive_text" in safety_text
    assert "after_action_review" in safety_action["value_domains"]["action_kind"]
    assert "hazmat_training" in safety_action["value_domains"]["action_kind"]
    assert "roadway_improvement" in safety_action["value_domains"]["action_kind"]

    assert finding is not None
    finding_text = " ".join(finding["contract"] + finding["forbidden_uses"])
    assert "abstain with domain_omission/5" in finding_text
    assert "no final probable cause" in finding_text
    assert "not_stated is not a valid finding_kind" in finding_text
    assert "not_stated" not in finding["value_domains"]["finding_kind"]
    assert "no impairment" in finding_text
    assert "full_probable_cause_paragraph" in finding_text


def test_osha_related_activity_contract_keeps_blank_flags_not_stated() -> None:
    related = carrier_contract("osha_related_activity/5")

    assert related is not None
    assert related["args"] == ["inspection_id", "activity_type", "activity_number", "safety_flag", "health_flag"]
    text = " ".join(related["contract"] + related["forbidden_uses"])
    assert "Blank Safety or Health cells mean not_stated" in text
    assert "use no only when the source explicitly states" in text
    assert "narrative_relationship" in text


def test_sec_form_8k_contracts_keep_skeleton_and_substance_separate() -> None:
    filing = carrier_contract("sec_filing/6")
    registrant = carrier_contract("sec_registrant/4")
    identifier = carrier_contract("sec_registrant_identifier/5")
    item = carrier_contract("sec_filing_item/5")
    exhibit = carrier_contract("sec_exhibit/5")
    signatory = carrier_contract("sec_signatory/5")

    assert filing is not None
    assert filing["args"] == [
        "filing_id",
        "form_type",
        "report_kind",
        "event_date",
        "filing_date",
        "source_or_scope",
    ]
    filing_text = " ".join(filing["contract"] + filing["forbidden_uses"])
    assert "companion SEC carriers" in filing_text
    assert "emit exactly one sec_filing/6 wrapper row" in filing_text
    assert "Do not omit sec_filing/6" in filing_text
    assert "cover-page Date of Report" in filing_text
    assert "do not substitute item-body event dates" in filing_text
    assert "Use not_stated when no separate filing date is stated" in filing_text
    assert "signature_date_as_filing_date" in filing_text
    assert "report_date_as_filing_date" in filing_text
    assert "agreement_terms" in filing_text
    assert "form_8_k" in filing["value_domains"]["form_type"]
    assert "form_8_k_a" in filing["value_domains"]["form_type"]

    assert registrant is not None
    assert registrant["args"] == ["filing_id", "registrant_id", "jurisdiction", "source_or_scope"]
    registrant_text = " ".join(registrant["contract"] + registrant["forbidden_uses"])
    assert "sec_registrant_identifier/5" in registrant_text
    assert "telephone values" in registrant_text
    assert "full source-stated legal registrant name" in registrant_text
    assert "not ticker symbols" in registrant_text
    assert "same registrant_id" in registrant_text
    assert "full_cover_table" in registrant_text

    assert identifier is not None
    assert identifier["args"] == [
        "filing_id",
        "registrant_id",
        "identifier_kind",
        "identifier_value",
        "source_or_scope",
    ]
    identifier_text = " ".join(identifier["contract"] + identifier["forbidden_uses"])
    assert "same full-legal-name-derived registrant_id" in identifier_text
    assert "do not substitute ticker symbols" in identifier_text
    assert "numeric-leading" in identifier_text
    assert "do not infer CIK" in identifier_text
    assert "unstated_cik" in identifier_text
    assert "exchange_nasdaq_stock_market_llc" in identifier_text
    assert "commission_file_number" in identifier["value_domains"]["identifier_kind"]

    assert item is not None
    assert item["args"] == ["filing_id", "item_code", "item_kind", "item_role", "source_or_scope"]
    item_text = " ".join(item["contract"] + item["forbidden_uses"])
    assert "heading, not the paragraph body" in item_text
    assert "Item 9.01" in item_text
    assert "item_role=exhibit" in item_text
    assert "not the registrant/company name" in item_text
    assert "numeric_leading_filing_id" in item_text
    assert "item_2_02" in item_text
    assert "item_4_02" in item_text
    assert "results_of_operations_financial_condition" in item["value_domains"]["item_kind"]
    assert "non_reliance" in item["value_domains"]["item_kind"]
    assert "officer_departure_appointment" in item["value_domains"]["item_kind"]
    assert "substantive" in item["value_domains"]["item_role"]

    treatment = carrier_contract("sec_filing_item_treatment/4")
    assert treatment is not None
    assert treatment["args"] == ["filing_id", "item_code", "item_treatment", "source_or_scope"]
    treatment_text = " ".join(treatment["contract"] + treatment["forbidden_uses"])
    assert "Item 2.02 or Item 7.01" in treatment_text
    assert "not to Item 9.01" in treatment_text
    assert "exhibit-row treatment belongs in sec_exhibit/5" in treatment_text
    assert "never an exhibit_table_row_* handle" in treatment_text
    assert "furnished" in treatment["value_domains"]["item_treatment"]

    assert exhibit is not None
    assert exhibit["args"] == ["filing_id", "exhibit_number", "exhibit_kind", "exhibit_role", "source_or_scope"]
    exhibit_text = " ".join(exhibit["contract"] + exhibit["forbidden_uses"])
    assert "full exhibit description" in exhibit_text
    assert "one row for each exhibit table row" in exhibit_text
    assert "exhibit_table_row_10_1" in exhibit_text
    assert "policy/plan exhibits use exhibit_kind=other_exhibit" in exhibit_text
    assert "Item-body language" in exhibit_text
    assert "sec_filing_item_treatment/4" in exhibit_text
    assert "filed as Exhibit N and incorporated by reference" in exhibit_text
    assert "exhibit_role=filed" in exhibit_text
    assert "never infer legal treatment from cover_page_ixbrl format alone" in exhibit_text
    assert "cover_page_ixbrl" in exhibit["value_domains"]["exhibit_kind"]

    assert signatory is not None
    assert signatory["args"] == [
        "filing_id",
        "signatory_id",
        "signatory_title",
        "signature_date",
        "source_or_scope",
    ]
    signatory_text = " ".join(signatory["contract"] + signatory["forbidden_uses"])
    assert "full_signature_block" in signatory_text

    event = carrier_contract("sec_material_event/6")
    assert event is not None
    assert event["args"] == [
        "filing_id",
        "event_id",
        "event_kind",
        "event_subject",
        "event_date",
        "source_or_scope",
    ]
    event_text = " ".join(event["contract"] + event["forbidden_uses"])
    assert "fenced SEC event lens" in event_text
    assert "must not be the event paragraph" in event_text
    assert "Do not add this carrier to the promoted SEC skeleton profile" in event_text
    assert "body_summary" in event_text
    assert "material_definitive_agreement" in event["value_domains"]["event_kind"]


def test_sec_material_event_probe_is_not_offered_by_promoted_sec_profile() -> None:
    registry_path = REPO_ROOT / "datasets" / "domain_profiles" / "sec_form_8k_v1" / "ontology_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    predicate_signatures = {item["signature"] for item in registry["predicates"]}
    offered_signatures = {
        signature
        for lens in registry["lenses"]
        for signature in lens.get("allowed_signatures", [])
    }

    assert carrier_contract("sec_material_event/6") is not None
    assert "sec_material_event/6" not in predicate_signatures
    assert "sec_material_event/6" not in offered_signatures


def test_sec_profile_registry_registrant_notes_keep_ids_legal_name_derived() -> None:
    registry_path = REPO_ROOT / "datasets" / "domain_profiles" / "sec_form_8k_v1" / "ontology_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    by_signature = {item["signature"]: item for item in registry["predicates"]}

    registrant_notes = by_signature["sec_registrant/4"]["notes"]
    identifier_notes = by_signature["sec_registrant_identifier/5"]["notes"]

    assert "full source-stated legal registrant name" in registrant_notes
    assert "not ticker symbols" in registrant_notes
    assert "used consistently by companion identifier rows" in registrant_notes
    assert "same full-legal-name-derived registrant_id" in identifier_notes


def test_puc_and_gao_wrapper_contracts_keep_substance_out_of_slots() -> None:
    puc = carrier_contract("puc_order/7")
    gao = carrier_contract("gao_bid_protest_decision/7")

    assert puc is not None
    assert puc["args"] == [
        "order_id",
        "agency_id",
        "docket_id",
        "order_kind",
        "issued_date",
        "decision_status",
        "source_or_scope",
    ]
    puc_text = " ".join(puc["contract"] + puc["forbidden_uses"])
    assert "settlement terms" in puc_text
    assert "certificate-of-service" in puc_text
    assert "doc_control_number_as_docket" in puc_text
    assert "resolution" in puc["value_domains"]["order_kind"]
    assert "memorializes_decision" in puc["value_domains"]["decision_status"]

    assert gao is not None
    assert gao["args"] == [
        "decision_id",
        "forum_id",
        "docket_id",
        "procurement_id",
        "decision_date",
        "decision_status",
        "source_or_scope",
    ]
    gao_text = " ".join(gao["contract"] + gao["forbidden_uses"])
    assert "current GAO file or B-number" in gao_text
    assert "recommendations" in gao_text
    assert "cited_precedent_as_current_docket" in gao_text
    assert "gao" in gao["value_domains"]["forum_id"]
    assert "sustained" in gao["value_domains"]["decision_status"]


def test_puc_and_gao_domain_profiles_match_registered_contracts() -> None:
    for registry_path in [
        REPO_ROOT / "datasets" / "domain_profiles" / "puc_order_v1" / "ontology_registry.json",
        REPO_ROOT / "datasets" / "domain_profiles" / "procurement_gao_decision_v1" / "ontology_registry.json",
    ]:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        for item in registry["predicates"]:
            contract = carrier_contract(item["signature"])
            assert contract is not None
            assert item["args"] == contract["args"]


def test_ntsb_domain_profile_registry_matches_registered_contracts() -> None:
    registry_path = REPO_ROOT / "datasets" / "domain_profiles" / "ntsb_investigation_v1" / "ontology_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    predicates = registry["predicates"]

    assert len(predicates) == 11
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


def test_osha_violation_status_contract_includes_formal_settlement_event() -> None:
    status = carrier_contract("osha_violation_status/5")

    assert status is not None
    assert "formal_settlement" in status["value_domains"]["latest_event"]


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
    assert "each distinct explicit adulteration-authority statement" in text
    assert "authority_or_scope" in text
    assert "fdca_501_a_2_a" in text
    assert "fdca_501_a_2_b" in text
    assert "explicitly states adulteration under section 501(a)(2)(A)" in text
    assert "Do not infer it from sterile-drug observations" in text
    assert "FDCA 801(a)(3)" in text


def test_fda_facility_identity_contract_blocks_document_ids_as_facility_ids() -> None:
    lines = carrier_contract_prompt_lines(["fda_facility_identity/5"])
    text = "\n".join(lines)

    assert "MARCS-CMS" in text
    assert "not_stated" in text


def test_fda_correspondence_party_contract_prefers_mailbox_contact_when_no_person_stated() -> None:
    lines = carrier_contract_prompt_lines(["fda_correspondence_party/5"])
    text = "\n".join(lines)

    assert "party_role=contact" in text
    assert "correspondence email address or mailbox" in text
    assert "rather than a salutation" in text


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


def test_fda_response_requirement_contract_defines_electronic_channel_boundary() -> None:
    lines = carrier_contract_prompt_lines(["fda_response_requirement/6"])
    text = "\n".join(lines)

    assert "email address, mailbox, portal, or electronic submission destination" in text
    assert "use issuing_office only" in text
    assert "no electronic destination is stated" in text


def test_fda_response_assessment_contract_prioritizes_documentation_and_topic_attachment() -> None:
    lines = carrier_contract_prompt_lines(["fda_response_assessment/5"])
    text = "\n".join(lines)

    assert "attach by the source-stated critique topic and citation family" in text
    assert "cfr_21_211_113_b" in text
    assert "cfr_21_211_192" in text
    assert "documentation_not_provided has priority" in text
    assert "APS/media-fill documentation" in text


def test_fda_response_assessment_item_contract_renders_projection_cage() -> None:
    lines = carrier_contract_prompt_lines(["fda_response_assessment_item/6"])
    text = "\n".join(lines)

    assert "Use this bundle before response-assessment projection" in text
    assert "cgmps_citation allowed values" in text
    assert "cfr_21_211_42_c_10_iv" in text
    assert "assessment_kind allowed values" in text
    assert "documentation_not_provided" in text
    assert "citation_not_in_numbered_item_map" in text


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


def test_state_ag_obligation_contract_prefers_source_anchored_ids_and_local_dates() -> None:
    lines = carrier_contract_prompt_lines(["state_ag_obligation/7"])
    text = "\n".join(lines)

    assert "obligation_<paragraph_number>" in text
    assert "descriptive aliases such as obl_change_control" in text
    assert "Do not copy a document-wide effective date" in text
    assert "individual obligation paragraph states no specific deadline" in text
