import unittest

from kb_pipeline import _compute_effective_clarification_eagerness


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


if __name__ == "__main__":
    unittest.main()
