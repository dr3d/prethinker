#!/usr/bin/env python3
"""Create small A/B semantic probe fixtures from mutation-lab edge labels."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT_DIR = REPO_ROOT / "tmp" / "public_benchmark" / "mutation_lab" / "semantic_probes"
DEFAULT_PLAN_JSON = DEFAULT_OUT_DIR / "semantic_ab_probe_plan.json"
DEFAULT_PLAN_MD = DEFAULT_OUT_DIR / "semantic_ab_probe_plan.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_PLAN_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_PLAN_MD)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out_dir = _resolve(args.out_dir)
    plan = build_plan(out_dir)
    write_probe_files(plan)
    out_json = _resolve(args.out_json)
    out_md = _resolve(args.out_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(plan, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    out_md.write_text(render_markdown(plan), encoding="utf-8")
    print(json.dumps({"fixtures": len(plan["fixtures"]), "rows": plan["total_rows"], "json": str(out_json), "markdown": str(out_md)}, indent=2))
    return 0


def build_plan(out_dir: Path) -> dict[str, Any]:
    probes = _probe_definitions()
    fixtures: list[dict[str, Any]] = []
    for probe in probes:
        for variant in probe["variants"]:
            fixture = f"{probe['probe_id']}__{variant['variant_id']}"
            fixture_dir = out_dir / probe["probe_id"] / variant["variant_id"]
            fixtures.append(
                {
                    "fixture": fixture,
                    "bucket": "semantic_ab_probe",
                    "probe_id": probe["probe_id"],
                    "variant_id": variant["variant_id"],
                    "dataset_path": str(fixture_dir),
                    "source_file": "source.md",
                    "question_file": "qa_questions.jsonl",
                    "oracle_file": "oracle.jsonl",
                    "planned_rows": len(variant["questions"]),
                }
            )
    return {
        "schema_version": "semantic_ab_probe_plan_v1",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "run_settings": {"runs_per_model": 1},
        "total_rows": sum(int(item["planned_rows"]) for item in fixtures),
        "fixtures": fixtures,
        "probes": probes,
    }


def write_probe_files(plan: dict[str, Any]) -> None:
    by_fixture = {item["fixture"]: item for item in plan["fixtures"]}
    for probe in plan["probes"]:
        manifest_variants = []
        for variant in probe["variants"]:
            fixture_name = f"{probe['probe_id']}__{variant['variant_id']}"
            fixture = by_fixture[fixture_name]
            fixture_dir = Path(str(fixture["dataset_path"]))
            fixture_dir.mkdir(parents=True, exist_ok=True)
            (fixture_dir / "source.md").write_text(variant["source"].strip() + "\n", encoding="utf-8")
            _write_jsonl(fixture_dir / "qa_questions.jsonl", variant["questions"])
            _write_jsonl(fixture_dir / "oracle.jsonl", variant["oracle"])
            manifest_variants.append(
                {
                    "variant_id": variant["variant_id"],
                    "fixture": fixture_name,
                    "expected_distinction": variant["expected_distinction"],
                }
            )
        manifest = {
            "schema_version": "semantic_probe_manifest_v1",
            "probe_id": probe["probe_id"],
            "distinction": probe["distinction"],
            "variants": manifest_variants,
        }
        probe_dir = Path(str(by_fixture[f"{probe['probe_id']}__{probe['variants'][0]['variant_id']}"]["dataset_path"])).parent
        (probe_dir / "probe_manifest.json").write_text(json.dumps(manifest, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Semantic A/B Probe Plan",
        "",
        f"- Generated UTC: `{plan.get('generated_utc', '')}`",
        f"- Fixtures: `{len(plan.get('fixtures', []))}`",
        f"- Rows: `{plan.get('total_rows', 0)}`",
        "",
        "| Fixture | Probe | Variant | Rows |",
        "| --- | --- | --- | ---: |",
    ]
    for fixture in plan.get("fixtures", []):
        lines.append(
            f"| `{fixture['fixture']}` | `{fixture['probe_id']}` | `{fixture['variant_id']}` | {fixture['planned_rows']} |"
        )
    lines.append("")
    return "\n".join(lines)


def _probe_definitions() -> list[dict[str, Any]]:
    return [
        _absence_probe(),
        _milestone_probe(),
    ]


def _absence_probe() -> dict[str, Any]:
    base_questions = [
        ("q001", "Is North Pier Glass eligible for the relocation-history exception?", "negative_existential"),
        ("q002", "What condition must be documented before the relocation-history exception can apply?", "lookup"),
        ("q003", "Does the packet establish a prior-county operating date for North Pier Glass?", "negative_existential"),
        ("q004", "Is absence of relocation documentation treated as unresolved or disqualifying in this packet?", "composition"),
        ("q005", "What is the disposition of North Pier Glass under the exception?", "lookup"),
        ("q006", "Which rule controls the relocation-history exception?", "authority"),
        ("q007", "Does the packet leave the relocation-file question open after packet close?", "composition"),
        ("q008", "What meaning-bearing distinction is tested by this packet?", "composition"),
    ]
    unresolved_source = """
# Relocation Exception Packet A - Pending Documentation

## Rule R-4.1 - Relocation-History Exception

An applicant may substitute a prior-county operating date for the local
operating-history rule if it relocated from an adjacent county. If the packet
does not yet include relocation documentation, the exception is not decided.
The case remains pending until the Records Office confirms whether the
relocation file exists.

## Applicant Record

Applicant: North Pier Glass.
Application date: 2026-04-12.
Local incorporation date: 2025-08-20.
Claim: the applicant says it relocated from Marden County in 2025.
Records Office status: no relocation file has been transmitted as of packet
close, but the office has until 2026-05-20 to confirm or deny the file.

## Determination

Base operating history by local date alone is too short. The R-4.1 exception is
pending because the record has not yet confirmed whether qualifying relocation
documentation exists.
"""
    negative_source = """
# Relocation Exception Packet B - Required Condition Missing

## Rule R-4.1 - Relocation-History Exception

An applicant may substitute a prior-county operating date for the local
operating-history rule only if the packet contains documented relocation from
an adjacent county. If the packet contains no relocation documentation by packet
close, the exception is unavailable for this round.

## Applicant Record

Applicant: North Pier Glass.
Application date: 2026-04-12.
Local incorporation date: 2025-08-20.
Claim: the applicant says it relocated from Marden County in 2025.
Records Office status: final search complete. The office found no relocation
file, no prior-county certificate, and no approved transfer record.

## Determination

Base operating history by local date alone is too short. The R-4.1 exception is
not available because documented relocation is a required condition and the
final packet contains no such documentation.
"""
    variants = [
        {
            "variant_id": "unresolved_absence",
            "expected_distinction": "absence remains pending because later documentation is allowed",
            "source": unresolved_source,
            "questions": _questions(base_questions, "absence_negative_evidence_vs_unresolved__unresolved_absence"),
            "oracle": _oracle(
                "absence_negative_evidence_vs_unresolved__unresolved_absence",
                [
                    ("q001", "No final eligibility determination; the exception is pending until the Records Office confirms whether the relocation file exists.", "negative_existential"),
                    ("q002", "Documentation that North Pier Glass relocated from an adjacent county.", "lookup"),
                    ("q003", "No. The packet says no relocation file has been transmitted as of packet close.", "negative_existential"),
                    ("q004", "Unresolved. The rule allows later confirmation, so missing documentation is not yet disqualifying.", "composition"),
                    ("q005", "Pending under R-4.1.", "lookup"),
                    ("q006", "Rule R-4.1.", "authority"),
                    ("q007", "Yes. The Records Office has until 2026-05-20 to confirm or deny the file.", "composition"),
                    ("q008", "Whether absent documentation means unresolved status or negative evidence.", "composition"),
                ],
            ),
        },
        {
            "variant_id": "negative_absence",
            "expected_distinction": "absence is disqualifying because the required condition is missing at final packet close",
            "source": negative_source,
            "questions": _questions(base_questions, "absence_negative_evidence_vs_unresolved__negative_absence"),
            "oracle": _oracle(
                "absence_negative_evidence_vs_unresolved__negative_absence",
                [
                    ("q001", "No. The R-4.1 exception is unavailable because documented relocation is required and the final packet contains none.", "negative_existential"),
                    ("q002", "Documented relocation from an adjacent county in the packet.", "lookup"),
                    ("q003", "No. The final search found no relocation file, prior-county certificate, or approved transfer record.", "negative_existential"),
                    ("q004", "Disqualifying. Missing documentation is negative evidence because the rule requires it by packet close.", "composition"),
                    ("q005", "Not eligible under R-4.1.", "lookup"),
                    ("q006", "Rule R-4.1.", "authority"),
                    ("q007", "No. The final search is complete, and the exception is unavailable for this round.", "composition"),
                    ("q008", "Whether absent documentation means unresolved status or negative evidence.", "composition"),
                ],
            ),
        },
    ]
    variants.extend(
        [
            _clone_variant_with_suffix(
                variants[0],
                probe_id="absence_negative_evidence_vs_unresolved",
                suffix="distractor",
                source_suffix=_absence_distractor(),
                expected_suffix="with irrelevant eligible-applicant distractor",
            ),
            _clone_variant_with_suffix(
                variants[1],
                probe_id="absence_negative_evidence_vs_unresolved",
                suffix="distractor",
                source_suffix=_absence_distractor(),
                expected_suffix="with irrelevant eligible-applicant distractor",
            ),
            _clone_variant_with_suffix(
                variants[0],
                probe_id="absence_negative_evidence_vs_unresolved",
                suffix="hard",
                source_suffix=_absence_hard_distractor(),
                expected_suffix="with near-collision same-rule opposite-outcome pressure",
                extra_question=("q000", "Is North Pier Glazing eligible for the relocation-history exception?", "composition"),
                extra_oracle=("q000", "Yes. North Pier Glazing is a separate applicant whose relocation file was confirmed.", "composition"),
            ),
            _clone_variant_with_suffix(
                variants[1],
                probe_id="absence_negative_evidence_vs_unresolved",
                suffix="hard",
                source_suffix=_absence_hard_distractor(),
                expected_suffix="with near-collision same-rule opposite-outcome pressure",
                extra_question=("q000", "Is North Pier Glazing eligible for the relocation-history exception?", "composition"),
                extra_oracle=("q000", "Yes. North Pier Glazing is a separate applicant whose relocation file was confirmed.", "composition"),
            ),
        ]
    )
    return {
        "probe_id": "absence_negative_evidence_vs_unresolved",
        "distinction": "missing fact as pending unresolved status versus missing required condition as negative evidence",
        "variants": variants,
    }


def _milestone_probe() -> dict[str, Any]:
    base_questions = [
        ("q001", "At what time did the safety condition become true?", "temporal"),
        ("q002", "At what time did Officer Vale certify the safety condition?", "temporal"),
        ("q003", "At what time does the public-notice deadline clock begin?", "temporal"),
        ("q004", "Which timestamp controls the public-notice deadline?", "composition"),
        ("q005", "Are the condition time and certification time interchangeable for the deadline?", "negative_existential"),
        ("q006", "What rule controls the deadline start?", "authority"),
        ("q007", "If the deadline is 48 hours, when is the deadline before weekend adjustment?", "temporal"),
        ("q008", "What meaning-bearing distinction is tested by this packet?", "composition"),
    ]
    condition_source = """
# Safety Milestone Packet A - Condition Clock

## Rule T-6.3 - Public Notice Deadline

The Authority must issue public notice within forty-eight hours after the
underlying safety condition becomes true. Later staff certification confirms
the condition but does not start or reset the deadline clock.

## Event Log

2026-05-01 17:00 - Sensor sequence completed; the safety condition became true.
2026-05-01 17:30 - Officer Vale certified in the operations ledger that the
safety condition had been met.

## Determination

For Rule T-6.3, the public-notice clock begins at 2026-05-01 17:00. The
17:30 certification is evidence of the condition but is not the clock-start
event.
"""
    certification_source = """
# Safety Milestone Packet B - Certification Clock

## Rule T-6.3 - Public Notice Deadline

The Authority must issue public notice within forty-eight hours after an
authorized officer certifies that the underlying safety condition has been met.
The condition may become true earlier, but the deadline clock does not begin
until certification is logged.

## Event Log

2026-05-01 17:00 - Sensor sequence completed; the safety condition became true.
2026-05-01 17:30 - Officer Vale certified in the operations ledger that the
safety condition had been met.

## Determination

For Rule T-6.3, the public-notice clock begins at 2026-05-01 17:30. The
17:00 condition time is necessary background but is not the clock-start event.
"""
    variants = [
        {
            "variant_id": "condition_clock",
            "expected_distinction": "deadline starts at condition time",
            "source": condition_source,
            "questions": _questions(base_questions, "condition_time_vs_certification_time__condition_clock"),
            "oracle": _oracle(
                "condition_time_vs_certification_time__condition_clock",
                [
                    ("q001", "2026-05-01 17:00.", "temporal"),
                    ("q002", "2026-05-01 17:30.", "temporal"),
                    ("q003", "2026-05-01 17:00.", "temporal"),
                    ("q004", "The underlying condition time controls the deadline.", "composition"),
                    ("q005", "No. The 17:30 certification confirms the condition but does not start or reset the clock.", "negative_existential"),
                    ("q006", "Rule T-6.3.", "authority"),
                    ("q007", "2026-05-03 17:00 before any weekend adjustment.", "temporal"),
                    ("q008", "Whether the deadline attaches to condition time or certification time.", "composition"),
                ],
            ),
        },
        {
            "variant_id": "certification_clock",
            "expected_distinction": "deadline starts at certification time",
            "source": certification_source,
            "questions": _questions(base_questions, "condition_time_vs_certification_time__certification_clock"),
            "oracle": _oracle(
                "condition_time_vs_certification_time__certification_clock",
                [
                    ("q001", "2026-05-01 17:00.", "temporal"),
                    ("q002", "2026-05-01 17:30.", "temporal"),
                    ("q003", "2026-05-01 17:30.", "temporal"),
                    ("q004", "The officer certification time controls the deadline.", "composition"),
                    ("q005", "No. The 17:00 condition time is background; the 17:30 certification starts the deadline.", "negative_existential"),
                    ("q006", "Rule T-6.3.", "authority"),
                    ("q007", "2026-05-03 17:30 before any weekend adjustment.", "temporal"),
                    ("q008", "Whether the deadline attaches to condition time or certification time.", "composition"),
                ],
            ),
        },
    ]
    variants.extend(
        [
            _clone_variant_with_suffix(
                variants[0],
                probe_id="condition_time_vs_certification_time",
                suffix="distractor",
                source_suffix=_milestone_distractor(),
                expected_suffix="with irrelevant drill-timeline distractor",
            ),
            _clone_variant_with_suffix(
                variants[1],
                probe_id="condition_time_vs_certification_time",
                suffix="distractor",
                source_suffix=_milestone_distractor(),
                expected_suffix="with irrelevant drill-timeline distractor",
            ),
        ]
    )
    return {
        "probe_id": "condition_time_vs_certification_time",
        "distinction": "underlying condition timestamp versus later certification timestamp",
        "variants": variants,
    }


def _questions(items: list[tuple[str, str, str]], source_id: str) -> list[dict[str, str]]:
    return [{"id": qid, "question": question, "category": category, "source_id": source_id} for qid, question, category in items]


def _oracle(source_id: str, items: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    return [{"id": qid, "reference_answer": answer, "category": category, "source_id": source_id} for qid, answer, category in items]


def _clone_variant_with_suffix(
    variant: dict[str, Any],
    *,
    probe_id: str,
    suffix: str,
    source_suffix: str,
    expected_suffix: str,
    extra_question: tuple[str, str, str] | None = None,
    extra_oracle: tuple[str, str, str] | None = None,
) -> dict[str, Any]:
    variant_id = f"{variant['variant_id']}_{suffix}"
    source_id = f"{probe_id}__{variant_id}"
    questions = [{**row, "source_id": source_id} for row in variant["questions"]]
    oracle = [{**row, "source_id": source_id} for row in variant["oracle"]]
    if extra_question:
        questions = _questions([extra_question], source_id) + questions
    if extra_oracle:
        oracle = _oracle(source_id, [extra_oracle]) + oracle
    return {
        "variant_id": variant_id,
        "expected_distinction": f"{variant['expected_distinction']}; {expected_suffix}",
        "source": f"{variant['source'].strip()}\n\n{source_suffix.strip()}\n",
        "questions": questions,
        "oracle": oracle,
    }


def _absence_distractor() -> str:
    return """
## Appendix - Unrelated Approved Relocation

South Quay Ceramics is a separate applicant. Its relocation file from Marden
County was confirmed, and its R-4.1 exception was approved. This appendix is
included only because the Records Office transmitted it in the same batch. It
does not describe North Pier Glass.
"""


def _absence_hard_distractor() -> str:
    return """
## Appendix - Same-Rule Near-Collision Records

This appendix contains separate applicants reviewed under the same R-4.1 rule.
The names are similar but identify different files.

### Applicant: North Pier Glazing

Local incorporation date: 2025-09-01.
Records Office status: final relocation file confirmed. North Pier Glazing
relocated from Marden County on 2025-08-15 and supplied prior-county operating
records dating to 2020-02-10.

Determination: R-4.1 applies to North Pier Glazing. The prior-county date may
be substituted for the local operating-history rule.

### Applicant: North Pine Glass

Local incorporation date: 2025-07-30.
Records Office status: wrong-file correction. A clerk initially attached North
Pier Glazing's relocation file to North Pine Glass, but the attachment was
withdrawn on 2026-05-02. North Pine Glass has no confirmed relocation file.

Determination: do not cite either appendix record as a determination for North
Pier Glass. North Pier Glass remains governed by its own Applicant Record and
Determination above.
"""


def _milestone_distractor() -> str:
    return """
## Appendix - Training Drill Timeline

A training drill on 2026-05-01 used a different rule, T-8.0. In that drill, a
practice safety condition became true at 16:45 and was certified at 17:00. The
drill did not involve Rule T-6.3 and does not control the public-notice deadline
in this packet.
"""


def _write_jsonl(path: Path, rows: list[dict[str, str]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows), encoding="utf-8")


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


if __name__ == "__main__":
    raise SystemExit(main())
