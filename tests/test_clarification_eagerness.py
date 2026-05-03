import unittest
import json
import importlib.util
from pathlib import Path

from kb_pipeline import _compute_effective_clarification_eagerness


ROOT = Path(__file__).resolve().parents[1]
CE_TRAP = ROOT / "datasets" / "clarification_eagerness" / "clarification_eagerness_trap"

RUNNER_SPEC = importlib.util.spec_from_file_location(
    "run_clarification_eagerness_fixture",
    ROOT / "scripts" / "run_clarification_eagerness_fixture.py",
)
assert RUNNER_SPEC is not None
RUNNER_MODULE = importlib.util.module_from_spec(RUNNER_SPEC)
assert RUNNER_SPEC.loader is not None
RUNNER_SPEC.loader.exec_module(RUNNER_MODULE)


class ClarificationEagernessTests(unittest.TestCase):
    def test_static_mode_keeps_base_eagerness(self) -> None:
        row = _compute_effective_clarification_eagerness(
            base_eagerness=0.2,
            mode="static",
            turn_index=1,
            kb_clause_count_at_start=0,
            kb_clause_count_current=0,
            is_brand_new_ontology=True,
            new_kb_boost=0.35,
            existing_kb_boost=0.12,
            decay_turns=24,
            decay_clauses=120,
        )
        self.assertEqual(row.get("mode"), "static")
        self.assertAlmostEqual(float(row.get("effective_eagerness", 0.0)), 0.2, places=6)

    def test_adaptive_mode_boosts_new_kb_early_turns(self) -> None:
        row = _compute_effective_clarification_eagerness(
            base_eagerness=0.35,
            mode="adaptive",
            turn_index=1,
            kb_clause_count_at_start=0,
            kb_clause_count_current=0,
            is_brand_new_ontology=True,
            new_kb_boost=0.35,
            existing_kb_boost=0.12,
            decay_turns=24,
            decay_clauses=120,
        )
        self.assertEqual(row.get("mode"), "adaptive")
        self.assertGreater(float(row.get("effective_eagerness", 0.0)), 0.35)
        self.assertEqual(str(row.get("phase", "")), "bootstrapping")

    def test_adaptive_mode_decays_toward_base(self) -> None:
        row = _compute_effective_clarification_eagerness(
            base_eagerness=0.35,
            mode="adaptive",
            turn_index=30,
            kb_clause_count_at_start=0,
            kb_clause_count_current=150,
            is_brand_new_ontology=True,
            new_kb_boost=0.35,
            existing_kb_boost=0.12,
            decay_turns=24,
            decay_clauses=120,
        )
        self.assertEqual(row.get("mode"), "adaptive")
        self.assertAlmostEqual(float(row.get("effective_eagerness", 0.0)), 0.35, places=6)
        self.assertEqual(str(row.get("phase", "")), "mature")

    def test_ce_trap_fixture_bundle_is_complete(self) -> None:
        expected = {
            "README.md",
            "source.md",
            "clear_answer_key.md",
            "ambiguity_cases.md",
            "qa.md",
            "expected_ce_behavior.md",
            "ingestion_cases.jsonl",
            "query_cases.jsonl",
            "baseline_qa.jsonl",
            "progress_journal.md",
            "progress_metrics.jsonl",
        }
        self.assertTrue(CE_TRAP.exists())
        self.assertTrue(expected.issubset({path.name for path in CE_TRAP.iterdir()}))

    def test_ce_trap_ingestion_cases_match_expected_distribution(self) -> None:
        rows = [
            json.loads(line)
            for line in (CE_TRAP / "ingestion_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[0]["id"], "ICT-001")
        self.assertEqual(rows[-1]["id"], "ICT-020")
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["expected_behavior"]] = counts.get(row["expected_behavior"], 0) + 1
            self.assertEqual(row["surface"], "ingestion")
            self.assertIsInstance(row["blocked_slots"], list)
            self.assertIsInstance(row["must_not_commit"], list)
        self.assertEqual(
            counts,
            {
                "clarify": 7,
                "commit_no_ask": 6,
                "commit_partial_clarify_blocked": 3,
                "commit_claim_no_ask": 2,
                "quarantine_no_ask": 2,
            },
        )
        safe_partial_rows = [row for row in rows if row["safe_partials_expected"]]
        self.assertEqual(len(safe_partial_rows), 13)

    def test_ce_trap_query_cases_match_expected_distribution(self) -> None:
        rows = [
            json.loads(line)
            for line in (CE_TRAP / "query_cases.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[0]["id"], "QCT-001")
        self.assertEqual(rows[-1]["id"], "QCT-020")
        counts: dict[str, int] = {}
        for row in rows:
            counts[row["expected_behavior"]] = counts.get(row["expected_behavior"], 0) + 1
            self.assertEqual(row["surface"], "query")
            self.assertTrue(row["question"])
        self.assertEqual(
            counts,
            {
                "clarify": 7,
                "answer": 11,
                "answer_multiple": 1,
                "answer_broad": 1,
            },
        )

    def test_ce_trap_baseline_and_text_are_stable(self) -> None:
        baseline = [
            json.loads(line)
            for line in (CE_TRAP / "baseline_qa.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(baseline), 10)
        self.assertEqual(baseline[0]["id"], "BASE-001")
        self.assertEqual(baseline[-1]["id"], "BASE-010")
        source = (CE_TRAP / "source.md").read_text(encoding="utf-8")
        self.assertIn("Charter Rule 7: Procurement release", source)
        self.assertIn("Claim SC-17 was disputed and not approved", source)
        for path in CE_TRAP.iterdir():
            if path.suffix.lower() not in {".md", ".jsonl"}:
                continue
            text = path.read_text(encoding="utf-8")
            self.assertTrue(all(ord(char) < 128 for char in text), path.name)

    def test_ce_runner_scores_blocked_slot_question_coverage(self) -> None:
        case = {
            "id": "SYN-001",
            "surface": "ingestion",
            "expected_behavior": "clarify",
            "blocked_slots": ["actor"],
            "safe_partials_expected": True,
            "must_not_commit": [],
        }
        ir = {
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "predicate": "logged_event",
                    "args": ["nadia_rao", "inspection"],
                    "safety": "safe",
                    "source": "direct",
                },
                {
                    "operation": "assert",
                    "predicate": "approved",
                    "args": ["unknown_actor", "repair_packet"],
                    "safety": "needs_clarification",
                    "source": "direct",
                },
            ],
            "clarification_questions": ["Who approved the repair packet?"],
        }
        scored = RUNNER_MODULE._score_case(case, ir, parsed_ok=True)
        self.assertEqual(scored["verdict"], "correct")
        self.assertTrue(scored["blocked_slot_question_required"])
        self.assertTrue(scored["blocked_slot_question_present"])
        self.assertFalse(scored["blocked_slot_question_missing"])

    def test_ce_runner_flags_missing_blocked_slot_question(self) -> None:
        case = {
            "id": "SYN-002",
            "surface": "ingestion",
            "expected_behavior": "clarify",
            "blocked_slots": ["approval_semantics"],
            "safe_partials_expected": True,
            "must_not_commit": [],
        }
        ir = {
            "decision": "commit",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "predicate": "release_event",
                    "args": ["payment"],
                    "safety": "safe",
                    "source": "direct",
                },
                {
                    "operation": "assert",
                    "predicate": "approved_payment",
                    "args": ["nadia_rao", "repair_funds"],
                    "safety": "unsafe",
                    "source": "direct",
                },
            ],
            "clarification_questions": [],
            "self_check": {},
        }
        scored = RUNNER_MODULE._score_case(case, ir, parsed_ok=True)
        summary = RUNNER_MODULE._summarize([scored])
        self.assertEqual(scored["verdict"], "undereager")
        self.assertTrue(scored["blocked_slot_question_required"])
        self.assertTrue(scored["blocked_slot_question_missing"])
        self.assertTrue(scored["blocked_slot_safe_write_violation"])
        self.assertEqual(summary["blocked_slot_question_required_count"], 1)
        self.assertEqual(summary["blocked_slot_question_present_count"], 0)
        self.assertEqual(summary["blocked_slot_question_missing_count"], 1)
        self.assertEqual(summary["blocked_slot_safe_write_violation_count"], 1)
        self.assertEqual(summary["blocked_slot_question_coverage"], 0.0)

    def test_ce_runner_does_not_treat_claim_content_as_fact_commit(self) -> None:
        case = {
            "id": "SYN-003",
            "surface": "ingestion",
            "expected_behavior": "clarify",
            "blocked_slots": ["actor"],
            "safe_partials_expected": True,
            "must_not_commit": ["`approved(_, repair_packet)`"],
        }
        ir = {
            "decision": "clarify",
            "candidate_operations": [
                {
                    "operation": "assert",
                    "predicate": "source_claim",
                    "args": ["nadia_rao", "claim_1"],
                    "safety": "safe",
                    "source": "direct",
                },
                {
                    "operation": "assert",
                    "predicate": "claim_content",
                    "args": ["claim_1", "approved_repair_packet"],
                    "safety": "safe",
                    "source": "direct",
                },
            ],
            "clarification_questions": ["Who does she refer to?"],
        }
        scored = RUNNER_MODULE._score_case(case, ir, parsed_ok=True)
        self.assertEqual(scored["verdict"], "correct")
        self.assertEqual(scored["forbidden_hits"], [])


if __name__ == "__main__":
    unittest.main()
