import json
import tempfile
import unittest
from pathlib import Path

from scripts.summarize_semantic_ir_model_matrix import format_markdown, summarize_run


class SemanticIRModelMatrixSummaryTests(unittest.TestCase):
    def test_summarize_run_groups_scores_by_semantic_model(self) -> None:
        rows = [
            {
                "scenario_id": "weak_case_one",
                "semantic_model": "google/gemma-4-26b-a4b",
                "legacy": {"score": {"decision_ok": False, "safe_outcome_ok": True, "rough_score": 0.25}},
                "semantic_ir": {
                    "score": {"decision_ok": True, "safe_outcome_ok": True, "rough_score": 1.0},
                    "non_mapper_parse_rescue_count": 0,
                },
            },
            {
                "scenario_id": "weak_case_two",
                "semantic_model": "google/gemma-4-26b-a4b",
                "legacy": {"score": {"decision_ok": True, "safe_outcome_ok": False, "rough_score": 0.75}},
                "semantic_ir": {
                    "score": {"decision_ok": False, "safe_outcome_ok": True, "rough_score": 0.5},
                    "non_mapper_parse_rescue_count": 1,
                },
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "run.jsonl"
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            summary = summarize_run(path)
        self.assertEqual(summary["model"], "google/gemma-4-26b-a4b")
        self.assertEqual(summary["scenario_group"], "weak_edges")
        self.assertEqual(summary["runs"], 2)
        self.assertEqual(summary["semantic_decision_ok"], 1)
        self.assertEqual(summary["semantic_safe_outcome_ok"], 2)
        self.assertEqual(summary["semantic_avg_score"], 0.75)
        self.assertEqual(summary["legacy_decision_ok"], 1)
        self.assertEqual(summary["legacy_safe_outcome_ok"], 1)
        self.assertEqual(summary["legacy_avg_score"], 0.5)
        self.assertEqual(summary["semantic_non_mapper_rescues"], 1)

    def test_format_markdown_renders_matrix_row(self) -> None:
        markdown = format_markdown(
            [
                {
                    "scenario_group": "rule_mutation",
                    "model": "qwen/qwen3.5-9b",
                    "runs": 10,
                    "semantic_decision_ok": 10,
                    "semantic_safe_outcome_ok": 10,
                    "semantic_avg_score": 0.917,
                    "legacy_decision_ok": 6,
                    "legacy_safe_outcome_ok": 8,
                    "legacy_avg_score": 0.758,
                    "semantic_non_mapper_rescues": 0,
                    "file": "run.jsonl",
                }
            ]
        )
        self.assertIn("| rule_mutation | `qwen/qwen3.5-9b` | 10 | 10/10 | 10/10 | 0.917 | 6/10 | 8/10 | 0.758 |", markdown)
        self.assertIn("`run.jsonl`", markdown)


if __name__ == "__main__":
    unittest.main()
