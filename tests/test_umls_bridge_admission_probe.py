from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "run_umls_bridge_admission_probe.py"
SPEC = importlib.util.spec_from_file_location("run_umls_bridge_admission_probe", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_bridge_admission_probe_scores_expected_actions(tmp_path):
    bridge_path = tmp_path / "umls_bridge_facts.pl"
    bridge_path.write_text(
        "\n".join(
            [
                "umls_concept(metformin, 'C0025598').",
                "umls_semantic_group(metformin, medication).",
                "umls_alias_norm(metformin, glucophage).",
                "umls_concept(blood_pressure_measurement, 'C0005824').",
                "umls_semantic_group(blood_pressure_measurement, lab_or_procedure).",
                "umls_alias_norm(blood_pressure_measurement, blood_pressure_reading).",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    battery_path = tmp_path / "battery.json"
    battery_path.write_text(
        """
{
  "cases": [
    {
      "case_id": "brand_admit",
      "utterance": "Mara takes Glucophage.",
      "logic_string": "taking(mara, metformin).",
      "facts": ["taking(mara, metformin)."],
      "expected_action": "admit",
      "expected_mentions": ["metformin"]
    },
    {
      "case_id": "mismatch_clarify",
      "utterance": "Mara's blood pressure reading was high.",
      "logic_string": "has_condition(mara, blood_pressure_measurement).",
      "facts": ["has_condition(mara, blood_pressure_measurement)."],
      "expected_action": "clarify",
      "expected_mentions": ["blood_pressure_measurement"]
    }
  ]
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    summary = MODULE.run_probe(bridge_path, battery_path, tmp_path / "out")
    assert summary["counts"] == {"cases": 2, "pass": 2, "fail": 0}


def test_bridge_admission_probe_summary_mentions_cases():
    text = MODULE._render_summary_md(
        {
            "generated_at_utc": "2026-04-24T00:00:00+00:00",
            "bridge_loaded": True,
            "bridge_concepts": 2,
            "counts": {"cases": 1, "pass": 1, "fail": 0},
            "cases": [
                {
                    "case_id": "brand_admit",
                    "verdict": "pass",
                    "actual_action": "admit",
                    "expected_action": "admit",
                    "found_mentions": ["metformin"],
                    "found_vague_surfaces": [],
                    "blocking_vague_surfaces": [],
                }
            ],
        }
    )
    assert "UMLS Bridge Admission Probe" in text
    assert "brand_admit" in text
    assert "metformin" in text
