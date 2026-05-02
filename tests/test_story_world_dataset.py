import json
import re
from pathlib import Path

from scripts.run_domain_bootstrap_qa import (
    parse_markdown_answer_key,
    parse_numbered_markdown_questions,
)
from scripts.run_rule_acquisition_pass import (
    _derived_head_rules,
    _probe_queries,
    _rule_lifecycle_counts,
    _rule_body_goal_support,
    _runtime_trial,
    _rule_trial_item_lifecycle,
    _rule_trial_item_promotion_ready,
    _unsupported_body_fragments,
)


ROOT = Path(__file__).resolve().parents[1]
OTTERS = ROOT / "datasets" / "story_worlds" / "otters_clockwork_pie"
IRON_HARBOR = ROOT / "datasets" / "story_worlds" / "iron_harbor_water_crisis"
BLACKTHORN = ROOT / "datasets" / "story_worlds" / "blackthorn_misconduct_case"
KESTREL = ROOT / "datasets" / "story_worlds" / "kestrel_claim"
GLASS_TIDE = ROOT / "datasets" / "story_worlds" / "glass_tide_charter"


def test_otters_story_world_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "qa_support_map.jsonl",
        "intake_plan.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
    }

    assert expected.issubset({path.name for path in OTTERS.iterdir()})


def test_otters_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (OTTERS / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 100
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q100"
    assert "Goldilocks" in records[0]["likely_mistake"]

    qa_text = (OTTERS / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 100
    assert len(answers) == 100
    assert questions[0]["id"] == "q001"
    assert "Little Slip of an Otter" in answers["q001"]


def test_otters_qa_support_map_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (OTTERS / "qa_support_map.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 20
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q020"
    assert all(row.get("required_support_any") for row in records)
    assert all(row.get("failure_classes") for row in records)
    assert any(
        "query_planner_missed_available_support" in row["failure_classes"]
        for row in records
    )


def test_otters_gold_kb_exercises_story_world_edges() -> None:
    kb = (OTTERS / "gold_kb.pl").read_text(encoding="utf-8")
    assert kb.count("event(") >= 100
    assert kb.count("story_time(") >= 100
    assert "judged(tilly_tumbletop" in kb
    assert "said(" in kb
    assert "final_state(" in kb
    assert "before(E1, E2)" in kb
    assert "location_after_event(clockwork_pie, e005, windowsill)." in kb
    for forbidden in ["goldilocks", "bear", "bears", "porridge", "chair", "chairs", "bed", "beds"]:
        assert re.search(rf"(?<![a-z0-9_]){forbidden}(?![a-z0-9_])", kb.casefold()) is None


def test_otters_metadata_is_graph_ready() -> None:
    buckets = json.loads((OTTERS / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((OTTERS / "ontology_registry.json").read_text(encoding="utf-8"))
    metrics = [
        json.loads(line)
        for line in (OTTERS / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(buckets["buckets"]) >= 10
    assert any(item["id"] == "template_contamination" for item in buckets["buckets"])
    assert registry["source"] == "gold_kb.pl"
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in ["event/5", "story_time/2", "before/2", "judged/4", "final_state/1"]:
        assert signature in signatures
    assert [row["timestamp"] for row in metrics] == sorted(row["timestamp"] for row in metrics)


def test_otters_fixture_text_is_ascii_stable() -> None:
    for path in OTTERS.iterdir():
        if path.suffix.lower() not in {".md", ".pl", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(ord(char) < 128 for char in text), path.name


def test_iron_harbor_story_world_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "qa_support_map.jsonl",
        "intake_plan.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
    }

    assert expected.issubset({path.name for path in IRON_HARBOR.iterdir()})


def test_iron_harbor_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (IRON_HARBOR / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 100
    assert records[0]["id"] == "q001"
    assert records[0]["source_id"] == "IH-001"
    assert records[-1]["id"] == "q100"
    assert records[-1]["source_id"] == "IH-100"
    assert records[23]["expected_answer"].startswith("No -- his last inspection was February 1")

    qa_text = (IRON_HARBOR / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 100
    assert len(answers) == 100
    assert questions[0]["id"] == "q001"
    assert "85 CFU/100mL" in answers["q001"]


def test_iron_harbor_qa_support_map_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (IRON_HARBOR / "qa_support_map.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 20
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q020"
    assert all(row.get("required_support_any") for row in records)
    assert all(row.get("failure_classes") for row in records)
    assert any("temporal_duration_gap" in row["failure_classes"] for row in records)
    assert any("set_difference_reasoning_gap" in row["failure_classes"] for row in records)


def test_iron_harbor_metadata_is_graph_ready() -> None:
    buckets = json.loads((IRON_HARBOR / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((IRON_HARBOR / "ontology_registry.json").read_text(encoding="utf-8"))
    metrics = [
        json.loads(line)
        for line in (IRON_HARBOR / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(buckets["buckets"]) >= 10
    assert any(item["id"] == "false_positive_violation" for item in buckets["buckets"])
    assert registry["source"] == "gold_kb.pl"
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in [
        "coliform_reading/4",
        "bypass_authorization/3",
        "notification/5",
        "before/2",
        "source_claim/4",
        "correction_record/4",
        "disclosure/4",
    ]:
        assert signature in signatures
    assert [row["timestamp"] for row in metrics] == sorted(row["timestamp"] for row in metrics)


def test_iron_harbor_fixture_text_is_ascii_stable() -> None:
    for path in IRON_HARBOR.iterdir():
        if path.suffix.lower() not in {".md", ".pl", ".json", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(ord(char) < 128 for char in text), path.name


def test_iron_harbor_traps_do_not_import_obvious_false_priors() -> None:
    story = (IRON_HARBOR / "story.md").read_text(encoding="utf-8").casefold()
    kb = (IRON_HARBOR / "gold_kb.pl").read_text(encoding="utf-8").casefold()

    assert "old harbor is not included in the notice" in story
    assert "non_residential_zone(foundry_row)" in kb
    assert re.search(r"(?<![a-z0-9_])residential_zone\(foundry_row\)", kb) is None
    assert "boil_water_notice(old_harbor" not in kb
    assert "inspection(pier_7_chlorination_unit, luis_ferreira, '2026-02-01')" in kb
    assert "inspection(pier_7_chlorination_unit, luis_ferreira, '2026-01-28')" not in kb
    assert "source_claim(luis_ferreira, pier_7_inspection_date, '2026-01-28', retracted)." in kb
    assert "disclosure(diane_cheng, aware_of_pump_deterioration_feb_20" in kb


def test_blackthorn_story_world_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "qa_support_map.jsonl",
        "intake_plan.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
    }

    assert expected.issubset({path.name for path in BLACKTHORN.iterdir()})


def test_blackthorn_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (BLACKTHORN / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 100
    assert records[0]["id"] == "q001"
    assert records[0]["source_id"] == "BT-001"
    assert records[-1]["id"] == "q100"
    assert records[-1]["source_id"] == "BT-100"
    assert records[41]["expected_answer"].startswith("Yes")

    qa_text = (BLACKTHORN / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 100
    assert len(answers) == 100
    assert questions[0]["id"] == "q001"
    assert "Elena Voss" in answers["q001"]


def test_blackthorn_qa_support_map_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (BLACKTHORN / "qa_support_map.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 20
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q020"
    assert all(row.get("required_support_any") for row in records)
    assert all(row.get("failure_classes") for row in records)
    assert any("deadline_anchor_error" in row["failure_classes"] for row in records)
    assert any("extension_authority_confusion" in row["failure_classes"] for row in records)


def test_blackthorn_metadata_is_graph_ready() -> None:
    buckets = json.loads((BLACKTHORN / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((BLACKTHORN / "ontology_registry.json").read_text(encoding="utf-8"))
    metrics = [
        json.loads(line)
        for line in (BLACKTHORN / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(buckets["buckets"]) >= 10
    assert any(item["id"] == "finding_sanction_collapse" for item in buckets["buckets"])
    assert registry["source"] == "gold_kb.pl"
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in [
        "person_role/2",
        "committee_member/3",
        "deadline_requirement/4",
        "deadline_met/4",
        "finding/4",
        "sanction_modified/4",
        "witness_claim/4",
        "advisory_opinion/4",
        "unresolved_question/2",
        "before/2",
    ]:
        assert signature in signatures
    assert [row["timestamp"] for row in metrics] == sorted(row["timestamp"] for row in metrics)


def test_blackthorn_preserves_multilingual_and_epistemic_traps() -> None:
    story = (BLACKTHORN / "story.md").read_text(encoding="utf-8")
    kb = (BLACKTHORN / "gold_kb.pl").read_text(encoding="utf-8").casefold()

    assert "Профессор Восс" in story
    assert "Ich war an der Datenanalyse" in story
    assert "両委員会の委員長として" in story
    assert "finding(fsrb, misconduct_upheld, '2027-02-03', final)." in kb
    assert "sanction_modified(fsrb, pi_suspension, 18_months, '2027-02-03')." in kb
    assert "advisory_status(patricia_moynihan, not_university_position)." in kb
    assert "unresolved_question(tanaka_reporting_obligation, rip_2024)." in kb
    assert "correction(correction_1, inquiry_committee_membership, henrik_larsson, kenji_hayashi)." in kb


def test_kestrel_story_world_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "qa_support_map.jsonl",
        "intake_plan.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
    }

    assert expected.issubset({path.name for path in KESTREL.iterdir()})


def test_kestrel_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (KESTREL / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 100
    assert records[0]["id"] == "q001"
    assert records[0]["source_id"] == "KS-001"
    assert records[-1]["id"] == "q100"
    assert records[-1]["source_id"] == "KS-100"
    assert records[8]["expected_answer"].startswith("As an H&M following underwriter")

    qa_text = (KESTREL / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 100
    assert len(answers) == 100
    assert questions[0]["id"] == "q001"
    assert "82,000 DWT bulk carrier" in answers["q001"]


def test_kestrel_qa_support_map_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (KESTREL / "qa_support_map.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 20
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q020"
    assert all(row.get("required_support_any") for row in records)
    assert all(row.get("failure_classes") for row in records)
    assert any("dual_role_collapse" in row["failure_classes"] for row in records)
    assert any("competing_accounts_collapse" in row["failure_classes"] for row in records)


def test_kestrel_metadata_is_oracle_safe_and_profile_ready() -> None:
    buckets = json.loads((KESTREL / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((KESTREL / "ontology_registry.json").read_text(encoding="utf-8"))

    assert len(buckets["buckets"]) >= 10
    assert any(item["id"] == "dual_role_collapse" for item in buckets["buckets"])
    assert any(item["id"] == "security_payment_confusion" for item in buckets["buckets"])
    assert registry["source"] == "starter_profile_not_gold_kb"
    assert "Do not derive cold-run context from gold_kb.pl" in registry["oracle_policy"]
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in [
        "vessel/2",
        "underwriter_line/4",
        "dual_role/3",
        "survey_finding/5",
        "cover_suspension/4",
        "reinsurance_layer/5",
        "security_posted/4",
        "witness_statement/5",
    ]:
        assert signature in signatures


def test_kestrel_preserves_maritime_insurance_traps() -> None:
    story = (KESTREL / "story.md").read_text(encoding="utf-8")
    kb = (KESTREL / "gold_kb.pl").read_text(encoding="utf-8").casefold()

    assert "Harbour Mutual" in story
    assert "Pinnacle Re" in story
    assert "The Bamburi" in story
    assert "The Star Sea" in story
    assert "dual_role(harbour_mutual" in kb
    assert "salvage_security" in kb
    assert "classification" in kb
    assert "pinnacle_re" in kb


def test_glass_tide_rule_ingestion_bundle_is_complete() -> None:
    expected = {
        "README.md",
        "story.md",
        "gold_kb.pl",
        "gold_kb_notes.md",
        "ontology_registry.json",
        "failure_buckets.json",
        "qa_source.md",
        "qa.md",
        "qa_battery.jsonl",
        "qa_support_map.jsonl",
        "intake_plan.md",
        "progress_journal.md",
        "progress_metrics.jsonl",
    }

    assert expected.issubset({path.name for path in GLASS_TIDE.iterdir()})


def test_glass_tide_qa_battery_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (GLASS_TIDE / "qa_battery.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 100
    assert records[0]["id"] == "q001"
    assert records[0]["source_id"] == "GT-001"
    assert records[-1]["id"] == "q100"
    assert records[-1]["source_id"] == "GT-100"
    assert records[17]["likely_mistake"] == "permission_event_or_claim_finding_collapse"

    qa_text = (GLASS_TIDE / "qa.md").read_text(encoding="utf-8")
    questions = parse_numbered_markdown_questions(qa_text)
    answers = parse_markdown_answer_key(qa_text)
    assert len(questions) == 100
    assert len(answers) == 100
    assert questions[0]["id"] == "q001"
    assert "Mara Vale" in answers["q001"]
    assert "unsupported claims do not become findings" in answers["q100"]


def test_glass_tide_qa_support_map_is_harness_ready() -> None:
    records = [
        json.loads(line)
        for line in (GLASS_TIDE / "qa_support_map.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(records) == 20
    assert records[0]["id"] == "q001"
    assert records[-1]["id"] == "q020"
    assert all(row.get("required_support_any") for row in records)
    assert all(row.get("failure_classes") for row in records)
    assert any("executable_rule_missing" in row["failure_classes"] for row in records)
    assert any("permission_event_collapse" in row["failure_classes"] for row in records)


def test_glass_tide_metadata_is_rule_frontier_ready() -> None:
    buckets = json.loads((GLASS_TIDE / "failure_buckets.json").read_text(encoding="utf-8"))
    registry = json.loads((GLASS_TIDE / "ontology_registry.json").read_text(encoding="utf-8"))
    metrics = [
        json.loads(line)
        for line in (GLASS_TIDE / "progress_metrics.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(buckets["buckets"]) >= 10
    assert any(item["id"] == "executable_rule_missing" for item in buckets["buckets"])
    assert any(item["id"] == "claim_finding_collapse" for item in buckets["buckets"])
    assert registry["source"] == "starter_profile_not_gold_kb"
    assert "Do not derive cold-run context from gold_kb.pl" in registry["oracle_policy"]
    signatures = {item["signature"] for item in registry["predicates"]}
    for signature in [
        "source_rule/2",
        "rule_text/2",
        "claim/3",
        "permission_at/4",
        "requirement/3",
        "exception/3",
        "override/3",
        "rule_candidate/4",
    ]:
        assert signature in signatures
    assert [row["timestamp"] for row in metrics] == sorted(row["timestamp"] for row in metrics)


def test_glass_tide_gold_kb_exercises_executable_rules() -> None:
    story = (GLASS_TIDE / "story.md").read_text(encoding="utf-8")
    kb = (GLASS_TIDE / "gold_kb.pl").read_text(encoding="utf-8").casefold()

    assert "testing Prethinker rule acquisition" in story
    assert kb.count(":-") >= 25
    assert "owes_harbor_tax(owner, cargo) :-" in kb
    assert "proposal_passes(proposal) :-" in kb
    assert "requires_quarantine_pier(vessel) :-" in kb
    assert "claim_only(p) :- claim(_, p, _), \\+ supports_finding(p)." in kb
    assert "may_dock_at_west_sluice(vessel) :-" in kb
    assert "docked_at(sunless_heron, west_sluice, t1825)." in kb
    assert "unauthorized_entry(person, archive_vault, t) :-" in kb
    assert "cleared_from_quarantine(patient) :-" in kb


def test_glass_tide_fixture_text_is_ascii_stable() -> None:
    for path in GLASS_TIDE.iterdir():
        if path.suffix.lower() not in {".md", ".pl", ".json", ".jsonl"}:
            continue
        text = path.read_text(encoding="utf-8")
        assert all(ord(char) < 128 for char in text), path.name


def test_rule_body_goal_support_requires_argument_pattern_match() -> None:
    facts = [
        "entity_property(bell_of_saint_loam, sacred_status, sacred).",
        "entity_property(blue_salt_crate_c17, sacred_status, not_sacred).",
        "charter_rule(salvage_rule, person_recovers_abandoned_cargo, earns_salvage_reward).",
    ]
    rule = (
        "derived_reward_status(Cargo, no_reward, salvage) :- "
        "charter_rule(salvage_rule, person_recovers_abandoned_cargo, earns_salvage_reward), "
        "entity_property(Cargo, type, sacred_cargo)."
    )

    support = _rule_body_goal_support(rule, facts)

    assert support[0]["matching_fact_count"] == 1
    assert support[1]["goal"] == "entity_property(Cargo, type, sacred_cargo)"
    assert support[1]["matching_fact_count"] == 0


def test_rule_body_goal_support_treats_uppercase_as_variable() -> None:
    facts = ["entity_property(repair_order_71, authorized_by, mara_vale_and_juno_vale)."]
    firing_rule = (
        "derived_authorization(RepairOrder, valid, glass_tide_repair) :- "
        "entity_property(RepairOrder, authorized_by, mara_vale_and_juno_vale)."
    )
    dormant_rule = (
        "derived_authorization(repair_order, valid, glass_tide_repair) :- "
        "entity_property(repair_order, authorized_by, mara_vale_and_juno_vale)."
    )

    firing_support = _rule_body_goal_support(firing_rule, facts)
    dormant_support = _rule_body_goal_support(dormant_rule, facts)

    assert firing_support[0]["matching_fact_count"] == 1
    assert dormant_support[0]["matching_fact_count"] == 0


def test_rule_body_goal_support_catches_lowercase_role_placeholders() -> None:
    facts = [
        "holds_role(mara_vale, harbor_warden, active).",
        "holds_role(juno_vale, chief_tide_engineer, active).",
        "authorized_action(repair_order_71, mara_vale, valid).",
        "authorized_action(repair_order_71, juno_vale, valid).",
    ]
    rule = (
        "derived_authorization(repair_order, valid, glass_tide_window) :- "
        "holds_role(warden, harbor_warden, active), "
        "holds_role(engineer, chief_tide_engineer, active), "
        "authorized_action(repair_order, warden, valid), "
        "authorized_action(repair_order, engineer, valid)."
    )

    support = _rule_body_goal_support(rule, facts)

    assert [item["matching_fact_count"] for item in support] == [0, 0, 0, 0]
    assert support[0]["goal"] == "holds_role(warden, harbor_warden, active)"


def test_rule_body_fragment_diagnostics_report_unsupported_constructs() -> None:
    rule = (
        "derived_reward_status(Actor, salvage_reward, Cargo) :- "
        "charter_rule(salvage_rule, person_recovers_abandoned_cargo, earns_salvage_reward), "
        "entity_property(Cargo, type, abandoned_cargo), "
        "Actor = person_recovers_abandoned_cargo."
    )

    assert _unsupported_body_fragments(rule) == ["Actor = person_recovers_abandoned_cargo"]


def test_rule_body_fragment_diagnostics_report_numeric_helper_value_variable_misuse() -> None:
    rule = (
        "derived_tax_status(Cargo, taxable, harbor) :- "
        "entity_property(Cargo, value, Value), "
        "value_greater_than(Value, 100), "
        "entity_property(Cargo, relief_status, not_relief)."
    )

    assert _unsupported_body_fragments(rule) == [
        "value_greater_than(Value, 100) uses value variable where entity argument is required"
    ]


def test_rule_trial_promotion_ready_requires_clean_firing_rule() -> None:
    assert _rule_trial_item_promotion_ready(
        {
            "status": "success",
            "num_rows": 1,
            "unsupported_body_signatures": [],
            "unsupported_body_goals": [],
            "unsupported_body_fragments": [],
        }
    )
    assert not _rule_trial_item_promotion_ready(
        {
            "status": "success",
            "num_rows": 1,
            "unsupported_body_signatures": [],
            "unsupported_body_goals": ["entity_property(Cargo, type, sacred_cargo)"],
            "unsupported_body_fragments": [],
        }
    )
    assert not _rule_trial_item_promotion_ready(
        {
            "status": "success",
            "num_rows": 6,
            "unsupported_body_signatures": [],
            "unsupported_body_goals": [],
            "unsupported_body_fragments": [],
        }
    )


def test_rule_trial_lifecycle_distinguishes_loaded_firing_and_promotion_ready() -> None:
    dormant = {
        "status": "success",
        "num_rows": 0,
        "unsupported_body_signatures": [],
        "unsupported_body_goals": [],
        "unsupported_body_fragments": [],
    }
    firing_dirty = {
        "status": "success",
        "num_rows": 1,
        "unsupported_body_signatures": [],
        "unsupported_body_goals": ["entity_property(Cargo, type, sacred_cargo)"],
        "unsupported_body_fragments": [],
    }
    promotion_ready = {
        "status": "success",
        "num_rows": 1,
        "unsupported_body_signatures": [],
        "unsupported_body_goals": [],
        "unsupported_body_fragments": [],
    }

    assert _rule_trial_item_lifecycle(dormant) == "runtime_loadable_rule"
    assert _rule_trial_item_lifecycle(firing_dirty) == "firing_rule"
    assert _rule_trial_item_lifecycle(promotion_ready) == "promotion_ready_rule"

    counts = _rule_lifecycle_counts([dormant, firing_dirty, promotion_ready], ["bad_rule: parse_error"])
    assert counts["candidate_rule"] == 4
    assert counts["mapper_admitted_rule"] == 4
    assert counts["runtime_loadable_rule"] == 3
    assert counts["firing_rule"] == 2
    assert counts["promotion_ready_rule"] == 1
    assert counts["durable_rule"] == 0


def test_rule_lens_keeps_only_derived_rule_heads() -> None:
    rules = [
        "derived_reward_status(Actor, salvage_reward, Cargo) :- recovered_from_water(Actor, Cargo, Time).",
        "rule_exception(salvage_rule, sacred_cargo_no_reward) :- sacred(Cargo).",
    ]

    assert _derived_head_rules(rules) == [
        "derived_reward_status(Actor, salvage_reward, Cargo) :- recovered_from_water(Actor, Cargo, Time)."
    ]


def test_rule_body_goal_support_can_use_runtime_virtual_helpers() -> None:
    from kb_pipeline import CorePrologRuntime

    runtime = CorePrologRuntime()
    assert runtime.assert_fact("entity_property(glass_eels, value, 300).")["status"] == "success"
    rule = "derived_tax_status(Cargo, taxable, harbor) :- value_greater_than(Cargo, 100)."

    support = _rule_body_goal_support(rule, ["entity_property(glass_eels, value, 300)."], runtime=runtime)

    assert support[0]["goal"] == "value_greater_than(Cargo, 100)"
    assert support[0]["matching_fact_count"] == 1
    assert support[0]["virtual_row_examples"] == [{"Cargo": "glass_eels"}]


def test_temporal_hour_spacing_helper_accepts_clock_atoms() -> None:
    from kb_pipeline import CorePrologRuntime

    runtime = CorePrologRuntime()

    assert runtime.query_rows("hours_at_least(10_00, 17_00, 6).")["status"] == "success"
    assert runtime.query_rows("hours_at_least(12_00, 17_00, 6).")["status"] == "no_results"
    assert runtime.query_rows("hours_at_least(t1000, t1700, 6).")["status"] == "success"


def test_support_count_helper_counts_distinct_supporters() -> None:
    from kb_pipeline import CorePrologRuntime

    runtime = CorePrologRuntime()
    for fact in [
        "supported(copper_rails_proposal, mara_vale).",
        "supported(copper_rails_proposal, juno_vale).",
        "supported(copper_rails_proposal, ilya_sen).",
        "supported(copper_rails_proposal, tomas_reed).",
    ]:
        assert runtime.assert_fact(fact)["status"] == "success"

    assert runtime.query_rows("support_count_at_least(copper_rails_proposal, 3).")["status"] == "success"
    assert runtime.query_rows("support_count_at_least(copper_rails_proposal, 5).")["status"] == "no_results"
    rows = runtime.query_rows("support_count_at_least(Proposal, 3).")
    assert rows["rows"] == [{"Proposal": "copper_rails_proposal"}]


def test_rule_probe_queries_score_positive_and_negative_expectations() -> None:
    from kb_pipeline import CorePrologRuntime

    runtime = CorePrologRuntime()
    assert runtime.assert_fact("entity_property(glass_eels, value, 300).")["status"] == "success"
    assert runtime.assert_rule(
        "derived_tax_status(Cargo, taxable, harbor) :- value_greater_than(Cargo, 100)."
    )["status"] == "success"

    positive = _probe_queries(
        runtime,
        ["derived_tax_status(glass_eels, taxable, harbor)."],
        expect_rows=True,
    )
    negative = _probe_queries(
        runtime,
        ["derived_tax_status(seed_crystals, taxable, harbor)."],
        expect_rows=False,
    )

    assert positive[0]["passed"]
    assert positive[0]["num_rows"] == 1
    assert negative[0]["passed"]
    assert negative[0]["num_rows"] == 0


def test_rule_runtime_trial_scores_promotion_in_isolated_rule_scope() -> None:
    trial = _runtime_trial(
        facts=[
            "p(a).",
            "q(b).",
        ],
        backbone_rules=[],
        rule_lens_rules=[
            "derived_status(X, ok, scope) :- p(X).",
            "derived_status(X, ok, scope) :- p(X), q(X).",
        ],
    )

    assert trial["trial_scope"] == "isolated_rule_for_promotion_combined_rules_for_probes"
    assert trial["promotion_ready_rule_count"] == 1
    assert trial["firing_rule_count"] == 1
    assert trial["combined_head_queries"][1]["num_rows"] == 1
    assert trial["derived_head_queries"][1]["trial_scope"] == "isolated_rule"
    assert trial["derived_head_queries"][1]["num_rows"] == 0
    assert trial["derived_head_queries"][1]["lifecycle_status"] == "runtime_loadable_rule"


def test_rule_runtime_trial_allows_context_dependent_temporal_helper_when_rule_fires() -> None:
    trial = _runtime_trial(
        facts=[
            "quarantine_patient(dax_orr).",
            "no_fever(dax_orr, 10_00).",
            "negative_test(dax_orr, 10_00).",
            "negative_test(dax_orr, 17_00).",
        ],
        backbone_rules=[],
        rule_lens_rules=[
            "derived_clearance_status(dax_orr, cleared, quarantine) :- "
            "quarantine_patient(dax_orr), no_fever(dax_orr, _), "
            "negative_test(dax_orr, T1), negative_test(dax_orr, T2), "
            "hours_at_least(T1, T2, 6).",
        ],
    )

    assert trial["promotion_ready_rule_count"] == 1
    assert trial["derived_head_queries"][0]["unsupported_body_goals"] == []
