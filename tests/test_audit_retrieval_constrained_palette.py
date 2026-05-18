import json
import tempfile
import unittest
from pathlib import Path

from scripts.audit_retrieval_constrained_palette import run_audit


class RetrievalConstrainedPaletteAuditTests(unittest.TestCase):
    def test_recalls_matching_schema_at_top_k(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compile_dir = root / "compile" / "fixture_a"
            compile_dir.mkdir(parents=True)
            compile_json = compile_dir / "domain_bootstrap_file_fixture_a.json"
            compile_json.write_text(
                json.dumps(
                    {
                        "parsed": {
                            "candidate_predicates": [
                                {
                                    "signature": "source_authority/3",
                                    "args": ["subject", "authority", "scope"],
                                    "description": "Authority or rule governing a source-stated action",
                                    "why": "Captures authorized action and scope",
                                },
                                {
                                    "signature": "unrelated_measure/2",
                                    "args": ["thing", "value"],
                                    "description": "Numeric measurement",
                                },
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            boundary = root / "boundary.json"
            boundary.write_text(
                json.dumps(
                    {
                        "coordinates": [
                            {
                                "fixture": "fixture_a",
                                "id": "q001",
                                "failure_surface": "compile_surface_gap",
                                "question": "Which rule authorized the access scope?",
                                "rationale": "The answer needs the authority source and governed action.",
                                "predicate_hints": ["source_authority"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = run_audit(
                compile_paths=[root / "compile"],
                boundary_plan=boundary,
                source_gap_audit=None,
                fixtures={"fixture_a"},
                failure_surfaces={"compile_surface_gap"},
                k_values=[1],
                registry_scope="global",
            )

        self.assertEqual(report["summary_by_k"]["1"]["verdict_counts"], {"schema_recalled": 1})

    def test_reports_missed_schema_when_correct_signature_not_retrieved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compile_dir = root / "compile" / "fixture_a"
            compile_dir.mkdir(parents=True)
            compile_json = compile_dir / "domain_bootstrap_file_fixture_a.json"
            compile_json.write_text(
                json.dumps(
                    {
                        "parsed": {
                            "candidate_predicates": [
                                {
                                    "signature": "source_authority/3",
                                    "args": ["subject", "authority", "scope"],
                                    "description": "Authority and governing scope",
                                },
                                {
                                    "signature": "event_date/2",
                                    "args": ["event", "date"],
                                    "description": "Current date and deadline timing",
                                },
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            boundary = root / "boundary.json"
            boundary.write_text(
                json.dumps(
                    {
                        "coordinates": [
                            {
                                "fixture": "fixture_a",
                                "id": "q001",
                                "failure_surface": "compile_surface_gap",
                                "question": "What date was current?",
                                "rationale": "The answer is a date.",
                                "predicate_hints": ["source_authority"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = run_audit(
                compile_paths=[root / "compile"],
                boundary_plan=boundary,
                source_gap_audit=None,
                fixtures={"fixture_a"},
                failure_surfaces={"compile_surface_gap"},
                k_values=[1],
                registry_scope="global",
            )

        self.assertEqual(report["summary_by_k"]["1"]["verdict_counts"], {"missed_schema": 1})

    def test_reports_family_recall_when_sibling_schema_is_retrieved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compile_dir = root / "compile" / "fixture_a"
            compile_dir.mkdir(parents=True)
            compile_json = compile_dir / "domain_bootstrap_file_fixture_a.json"
            compile_json.write_text(
                json.dumps(
                    {
                        "parsed": {
                            "candidate_predicates": [
                                {
                                    "signature": "person_role/3",
                                    "args": ["person", "role", "context"],
                                    "description": "Person role in a named context",
                                },
                                {
                                    "signature": "role/2",
                                    "args": ["person", "role"],
                                    "description": "Role held by a person",
                                },
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )
            boundary = root / "boundary.json"
            boundary.write_text(
                json.dumps(
                    {
                        "coordinates": [
                            {
                                "fixture": "fixture_a",
                                "id": "q001",
                                "failure_surface": "compile_surface_gap",
                                "question": "Who held the role?",
                                "rationale": "The answer needs a role holder.",
                                "predicate_hints": ["person_role"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            report = run_audit(
                compile_paths=[root / "compile"],
                boundary_plan=boundary,
                source_gap_audit=None,
                fixtures={"fixture_a"},
                failure_surfaces={"compile_surface_gap"},
                k_values=[1],
                registry_scope="global",
            )

        self.assertEqual(
            report["summary_by_k"]["1"]["verdict_counts"],
            {"family_recalled_schema_missed": 1},
        )


if __name__ == "__main__":
    unittest.main()
