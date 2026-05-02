import unittest
import json
from pathlib import Path

from kb_pipeline import _compute_effective_clarification_eagerness


ROOT = Path(__file__).resolve().parents[1]
CE_TRAP = ROOT / "datasets" / "clarification_eagerness" / "clarification_eagerness_trap"


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


if __name__ == "__main__":
    unittest.main()
