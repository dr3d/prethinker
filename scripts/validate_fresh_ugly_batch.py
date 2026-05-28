#!/usr/bin/env python3
"""Validate fresh ugly public fixture batches before compile/QA spending."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_FILES = (
    "source.md",
    "qa.md",
    "oracle.jsonl",
    "fixture_notes.md",
    "metadata.json",
)

EXTENDED_REQUIRED_FILES = (
    *REQUIRED_FILES,
    "source_original.txt",
    "qa_questions.jsonl",
    "provenance.md",
    "anti_leakage_manifest.md",
    "qa_authored_with_answers.md",
)

ACH_REQUIRED_FILES = (
    *EXTENDED_REQUIRED_FILES,
    "ach_payload.json",
)

OPTIONAL_ANSWER_KEY_FILES = (
    "qa_authored_with_answers.md",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir", type=Path)
    parser.add_argument("--expected-documents", type=int, default=12)
    parser.add_argument("--expected-questions", type=int, default=25)
    parser.add_argument(
        "--package-profile",
        choices=("legacy", "extended", "ach"),
        default="legacy",
        help="Validation profile. Use extended for current fresh ugly requests and ach for ACH heldout packages.",
    )
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = validate_batch(
        args.batch_dir,
        expected_documents=args.expected_documents,
        expected_questions=args.expected_questions,
        package_profile=args.package_profile,
    )
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(render_markdown(report), encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["summary"]["status"] == "pass" else 1


def validate_batch(
    batch_dir: Path,
    *,
    expected_documents: int = 12,
    expected_questions: int = 25,
    package_profile: str = "legacy",
) -> dict[str, Any]:
    root = batch_dir if batch_dir.is_absolute() else Path.cwd() / batch_dir
    rows: list[dict[str, Any]] = []
    batch_issues: list[str] = []
    if not root.exists():
        batch_issues.append(f"batch_dir_missing:{root}")
        fixture_dirs: list[Path] = []
    else:
        fixture_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    if package_profile == "ach":
        batch_manifest = root / "batch_manifest.json"
        if not batch_manifest.exists():
            batch_issues.append("missing_file:batch_manifest.json")
        else:
            manifest_error = _json_file_error(batch_manifest, expected_object=True)
            if manifest_error:
                batch_issues.append(f"batch_manifest_{manifest_error}")
    if len(fixture_dirs) != expected_documents:
        batch_issues.append(f"document_count:{len(fixture_dirs)} expected:{expected_documents}")
    for fixture_dir in fixture_dirs:
        rows.append(
            _validate_fixture(
                fixture_dir,
                expected_questions=expected_questions,
                package_profile=package_profile,
            )
        )
    if package_profile == "ach":
        batch_issues.extend(_ach_batch_issues(root, rows))
    issue_count = sum(len(row["issues"]) for row in rows) + len(batch_issues)
    warning_count = sum(len(row["warnings"]) for row in rows)
    return {
        "schema_version": "fresh_ugly_batch_validation_v1",
        "batch_dir": str(root),
        "summary": {
            "status": "pass" if issue_count == 0 else "fail",
            "fixture_count": len(rows),
            "expected_documents": expected_documents,
            "package_profile": package_profile,
            "issue_count": issue_count,
            "warning_count": warning_count,
            "batch_issues": batch_issues,
        },
        "fixtures": rows,
    }


def _validate_fixture(
    fixture_dir: Path,
    *,
    expected_questions: int,
    package_profile: str,
) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    required_files = _required_files_for_profile(package_profile)
    for name in required_files:
        if not (fixture_dir / name).exists():
            issues.append(f"missing_file:{name}")
    source_text = _read_text(fixture_dir / "source.md")
    qa_text = _read_text(fixture_dir / "qa.md")
    authored_text = _read_text(fixture_dir / "qa_authored_with_answers.md")
    notes_text = _read_text(fixture_dir / "fixture_notes.md")
    metadata_text = _read_text(fixture_dir / "metadata.json")
    provenance_text = _read_text(fixture_dir / "provenance.md")
    anti_leakage_text = _read_text(fixture_dir / "anti_leakage_manifest.md")
    metadata, metadata_error = _read_metadata(fixture_dir / "metadata.json")
    if metadata_error:
        issues.append(metadata_error)
    if not source_text.strip():
        issues.append("empty_source")
    if not notes_text.strip():
        issues.append("empty_fixture_notes")
    questions = _numbered_questions(qa_text)
    if len(questions) != expected_questions:
        issues.append(f"qa_question_count:{len(questions)} expected:{expected_questions}")
    if (fixture_dir / "qa_questions.jsonl").exists():
        qa_question_count, qa_question_issues = _question_jsonl_row_count(fixture_dir / "qa_questions.jsonl")
        issues.extend(qa_question_issues)
        if qa_question_count != expected_questions:
            issues.append(f"qa_questions_jsonl_row_count:{qa_question_count} expected:{expected_questions}")
    oracle_count, oracle_issues = _oracle_row_count(fixture_dir / "oracle.jsonl")
    oracle_complete = (fixture_dir / "oracle.jsonl").exists() and oracle_count == expected_questions and not oracle_issues
    qa_answers = _reference_answer_count(qa_text)
    authored_answers = _reference_answer_count(authored_text)
    answers = authored_answers or (qa_answers if not (fixture_dir / "qa_authored_with_answers.md").exists() else 0)
    for name in OPTIONAL_ANSWER_KEY_FILES:
        if not (fixture_dir / name).exists() and not oracle_complete and qa_answers != expected_questions:
            issues.append(f"missing_file:{name}")
    if answers != expected_questions and not oracle_complete:
        issues.append(f"reference_answer_count:{answers} expected:{expected_questions}")
    issues.extend(oracle_issues)
    if (fixture_dir / "oracle.jsonl").exists() and oracle_count != expected_questions:
        issues.append(f"oracle_row_count:{oracle_count} expected:{expected_questions}")
    if isinstance(metadata, dict):
        _validate_metadata(
            metadata,
            fixture_dir=fixture_dir,
            expected_questions=expected_questions,
            package_profile=package_profile,
            issues=issues,
            warnings=warnings,
        )
    if package_profile in {"extended", "ach"}:
        if not provenance_text.strip():
            issues.append("empty_provenance")
        if not anti_leakage_text.strip():
            issues.append("empty_anti_leakage_manifest")
        if not _declares_no_llm_source(anti_leakage_text):
            warnings.append("anti_leakage_manifest_no_llm_source_not_explicit")
    ach_payload_summary: dict[str, Any] | None = None
    if package_profile == "ach":
        ach_payload_summary = _validate_ach_payload(fixture_dir / "ach_payload.json", issues=issues)
    source_support = _reference_source_support_report(
        fixture_dir / "oracle.jsonl",
        source_text=source_text,
        notes_text=notes_text,
        metadata_text=metadata_text,
    )
    warnings.extend(source_support["warnings"])
    return {
        "fixture": fixture_dir.name,
        "status": "pass" if not issues else "fail",
        "question_count": len(questions),
        "reference_answer_count": answers,
        "oracle_row_count": oracle_count,
        "source_chars": len(source_text),
        "ach_payload": ach_payload_summary,
        "sensitivity_target": str(metadata.get("sensitivity_target") or "").strip().lower()
        if isinstance(metadata, dict)
        else "",
        "issues": issues,
        "warnings": warnings,
        "warning_details": source_support["details"],
    }


def _required_files_for_profile(package_profile: str) -> tuple[str, ...]:
    if package_profile == "ach":
        return ACH_REQUIRED_FILES
    if package_profile == "extended":
        return EXTENDED_REQUIRED_FILES
    return REQUIRED_FILES


def _validate_metadata(
    metadata: dict[str, Any],
    *,
    fixture_dir: Path,
    expected_questions: int,
    package_profile: str,
    issues: list[str],
    warnings: list[str],
) -> None:
    source_url = str(metadata.get("source_url") or "").strip()
    if not source_url.startswith(("http://", "https://")):
        issues.append("metadata_source_url_missing_or_non_http")
    if metadata.get("llm_authored_source") is True:
        issues.append("metadata_llm_authored_source_true")
    if metadata.get("llm_rewritten_source") is True:
        issues.append("metadata_llm_rewritten_source_true")
    if metadata.get("llm_authored_source") is not False:
        warnings.append("metadata_llm_authored_source_not_false")
    if metadata.get("llm_rewritten_source") is not False:
        warnings.append("metadata_llm_rewritten_source_not_false")
    question_count = metadata.get("question_count")
    if question_count is not None and int(question_count) != expected_questions:
        issues.append(f"metadata_question_count:{question_count} expected:{expected_questions}")
    document_id = str(metadata.get("document_id") or metadata.get("fixture_id") or "").strip()
    if document_id and document_id != fixture_dir.name:
        warnings.append(f"metadata_document_id_differs:{document_id}")
    if not isinstance(metadata.get("pressure_tags", []), list) or not metadata.get("pressure_tags", []):
        warnings.append("metadata_pressure_tags_missing")
    if package_profile == "ach":
        sensitivity = str(metadata.get("sensitivity_target") or "").strip().lower()
        if sensitivity not in {"high", "medium", "low"}:
            issues.append("metadata_sensitivity_target_missing_or_invalid")
    if package_profile in {"extended", "ach"}:
        if str(metadata.get("language") or "").strip().lower() != "en":
            warnings.append("metadata_language_not_en")
        if metadata.get("public_source") is not True:
            warnings.append("metadata_public_source_not_true")


def _numbered_questions(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*(?:q)?(\d{1,3})\.\s+(.+?)\s*$", line, flags=re.IGNORECASE)
        if match:
            out.append(match.group(2))
            continue
        match = re.match(r"^\s*\*\*Q\d{1,3}\b(?:\s*\[[^\]]+\])?\*\*\s+(.+?)\s*$", line, flags=re.IGNORECASE)
        if match:
            out.append(match.group(1))
            continue
        match = re.match(r"^\s*\*\*Q\d{1,3}\b(?:\s*\[[^\]]+\])?\s+(.+?)\*\*\s*$", line, flags=re.IGNORECASE)
        if match:
            out.append(match.group(1))
    return out


def _reference_answer_count(text: str) -> int:
    markers = re.findall(r"(?im)^\s*\*\*Reference answer\.\*\*", text)
    if markers:
        return len(markers)
    qa_markers = re.findall(r"(?im)^\s*\*\*A\s*:?\*\*", text)
    if qa_markers:
        return len(qa_markers)
    bold_numbered_questions = re.findall(r"(?m)^\s*\*\*\d{1,3}\.\s+.+?\*\*\s*$", text)
    if bold_numbered_questions:
        return len(bold_numbered_questions)
    bold_q_numbered_questions = re.findall(r"(?m)^\s*\*\*Q\d{1,3}\b.+?\*\*\s*$", text)
    if bold_q_numbered_questions:
        return len(bold_q_numbered_questions)
    localized_answers = re.findall(r"(?im)^\s*\*\*(?:answer|r[ée]ponse|antwort|respuesta)\s*:?\*\*", text)
    if localized_answers:
        return len(localized_answers)
    numbered_answers = re.findall(r"(?im)^(?:answer\s*)?\d{1,3}\.\s+\S", text)
    return len(numbered_answers)


def _read_metadata(path: Path) -> tuple[dict[str, Any] | None, str]:
    if not path.exists():
        return None, ""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, f"metadata_json_error:{exc}"
    if not isinstance(value, dict):
        return None, "metadata_not_object"
    return value, ""


def _json_file_error(path: Path, *, expected_object: bool = False) -> str:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"json_error:{exc}"
    if expected_object and not isinstance(value, dict):
        return "json_not_object"
    return ""


def _question_jsonl_row_count(path: Path) -> tuple[int, list[str]]:
    issues: list[str] = []
    ids: set[str] = set()
    count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        count += 1
        try:
            row = json.loads(line)
        except Exception as exc:
            issues.append(f"qa_questions_jsonl_error:line_{line_number}:{exc}")
            continue
        if not isinstance(row, dict):
            issues.append(f"qa_questions_jsonl_row_not_object:line_{line_number}")
            continue
        row_id = str(row.get("id") or "").strip()
        if not row_id:
            issues.append(f"qa_questions_jsonl_missing_id:line_{line_number}")
        elif row_id in ids:
            issues.append(f"qa_questions_jsonl_duplicate_id:{row_id}")
        else:
            ids.add(row_id)
        if not str(row.get("question") or "").strip():
            issues.append(f"qa_questions_jsonl_missing_question:{row_id or 'line_' + str(line_number)}")
    return count, issues


def _oracle_row_count(path: Path) -> tuple[int, list[str]]:
    if not path.exists():
        return 0, []
    issues: list[str] = []
    ids: set[str] = set()
    count = 0
    for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
        if not line.strip():
            continue
        count += 1
        try:
            row = json.loads(line)
        except Exception as exc:
            issues.append(f"oracle_jsonl_error:line_{line_number}:{exc}")
            continue
        if not isinstance(row, dict):
            issues.append(f"oracle_jsonl_row_not_object:line_{line_number}")
            continue
        row_id = str(row.get("id") or "").strip()
        if not row_id:
            issues.append(f"oracle_jsonl_missing_id:line_{line_number}")
        elif row_id in ids:
            issues.append(f"oracle_jsonl_duplicate_id:{row_id}")
        else:
            ids.add(row_id)
        if not str(row.get("reference_answer") or row.get("answer") or "").strip():
            issues.append(f"oracle_jsonl_missing_reference_answer:{row_id or 'line_' + str(line_number)}")
    return count, issues


def _declares_no_llm_source(text: str) -> bool:
    lowered = str(text or "").casefold()
    authored_declared = (
        "not llm-authored" in lowered
        or "not llm authored" in lowered
        or "llm_authored_source" in lowered and "false" in lowered
        or "no llm-authored" in lowered
        or "no llm authored" in lowered
    )
    rewritten_declared = (
        "not llm-rewritten" in lowered
        or "not llm rewritten" in lowered
        or "llm_rewritten_source" in lowered and "false" in lowered
        or "no llm-rewritten" in lowered
        or "no llm rewritten" in lowered
    )
    return authored_declared and rewritten_declared


def _validate_ach_payload(path: Path, *, issues: list[str]) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        issues.append(f"ach_payload_json_error:{exc}")
        return None
    if not isinstance(payload, dict):
        issues.append("ach_payload_not_object")
        return None
    hypotheses = payload.get("hypotheses")
    evidence_rows = payload.get("evidence_rows")
    expected_read = payload.get("expected_read")
    if not str(payload.get("fixture_id") or "").strip():
        issues.append("ach_payload_missing_fixture_id")
    if not str(payload.get("ach_question") or "").strip():
        issues.append("ach_payload_missing_ach_question")
    if not isinstance(hypotheses, list):
        issues.append("ach_payload_hypotheses_not_list")
        hypothesis_count = 0
    else:
        hypothesis_count = len(hypotheses)
        if not 3 <= hypothesis_count <= 5:
            issues.append(f"ach_payload_hypothesis_count:{hypothesis_count} expected:3-5")
        for index, item in enumerate(hypotheses, start=1):
            if not isinstance(item, dict):
                issues.append(f"ach_payload_hypothesis_not_object:{index}")
                continue
            for key in ("id", "label", "claim"):
                if not str(item.get(key) or "").strip():
                    issues.append(f"ach_payload_hypothesis_missing_{key}:{index}")
    if not isinstance(evidence_rows, list):
        issues.append("ach_payload_evidence_rows_not_list")
        evidence_count = 0
    else:
        evidence_count = len(evidence_rows)
        if not 6 <= evidence_count <= 10:
            issues.append(f"ach_payload_evidence_count:{evidence_count} expected:6-10")
        for index, item in enumerate(evidence_rows, start=1):
            if not isinstance(item, dict):
                issues.append(f"ach_payload_evidence_not_object:{index}")
                continue
            for key in ("id", "label", "source_coords", "text_anchor", "expected_relevance"):
                if not str(item.get(key) or "").strip():
                    issues.append(f"ach_payload_evidence_missing_{key}:{index}")
    if not isinstance(expected_read, dict):
        issues.append("ach_payload_expected_read_not_object")
        sensitivity = ""
    else:
        for key in ("best_hypothesis", "rationale", "sensitivity_expectation", "pivotal_evidence", "flip_note"):
            if not str(expected_read.get(key) or "").strip():
                issues.append(f"ach_payload_expected_read_missing_{key}")
        sensitivity = str(expected_read.get("sensitivity_expectation") or "").strip().lower()
        if sensitivity not in {"high", "medium", "low"}:
            issues.append("ach_payload_sensitivity_expectation_invalid")
    return {
        "hypothesis_count": hypothesis_count,
        "evidence_count": evidence_count,
        "sensitivity_expectation": sensitivity,
    }


def _ach_batch_issues(root: Path, rows: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    manifest_path = root / "batch_manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.exists():
        try:
            value = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                manifest = value
        except Exception:
            manifest = {}
    fixture_names = {str(row.get("fixture") or "") for row in rows}
    manifest_fixtures = manifest.get("fixtures")
    if isinstance(manifest_fixtures, list):
        manifest_ids = {
            str(item.get("fixture_id") or "").strip()
            for item in manifest_fixtures
            if isinstance(item, dict) and str(item.get("fixture_id") or "").strip()
        }
        missing_from_manifest = sorted(fixture_names - manifest_ids)
        missing_from_tree = sorted(manifest_ids - fixture_names)
        if missing_from_manifest:
            issues.append(f"batch_manifest_missing_fixture_ids:{','.join(missing_from_manifest)}")
        if missing_from_tree:
            issues.append(f"batch_manifest_fixture_ids_not_found:{','.join(missing_from_tree)}")
    distribution = {"high": 0, "medium": 0, "low": 0}
    for row in rows:
        sensitivity = str(row.get("sensitivity_target") or "").strip().lower()
        if sensitivity in distribution:
            distribution[sensitivity] += 1
    expected_distribution = manifest.get("expected_distribution")
    if isinstance(expected_distribution, dict):
        for key in ("high", "medium", "low"):
            try:
                expected = int(expected_distribution.get(key, 0))
            except (TypeError, ValueError):
                issues.append(f"batch_manifest_expected_distribution_invalid:{key}")
                continue
            if distribution[key] != expected:
                issues.append(f"sensitivity_distribution_{key}:{distribution[key]} expected:{expected}")
    elif rows:
        issues.append("batch_manifest_expected_distribution_missing")
    return issues


def _reference_source_support_report(
    oracle_path: Path,
    *,
    source_text: str,
    notes_text: str,
    metadata_text: str,
) -> dict[str, Any]:
    if not oracle_path.exists():
        return {"warnings": [], "details": []}
    source_norm = _search_text(source_text)
    notes_norm = _search_text(notes_text)
    metadata_norm = _search_text(metadata_text)
    notes_only_rows: list[str] = []
    metadata_only_rows: list[str] = []
    non_source_rows: list[str] = []
    absent_source_rows: list[str] = []
    declared_incomplete_source_rows: list[str] = []
    examples: list[str] = []
    absent_examples: list[str] = []
    incomplete_examples: list[str] = []
    details: list[dict[str, Any]] = []
    for row in _oracle_rows_for_support_check(oracle_path):
        row_id = str(row.get("id") or f"line_{len(non_source_rows) + 1}").strip()
        pressure_tags = row.get("pressure_tags")
        pressure_text = " ".join(str(tag).casefold() for tag in pressure_tags if isinstance(tag, str)) if isinstance(pressure_tags, list) else ""
        if "incomplete_in_source" in pressure_text or "external" in pressure_text:
            declared_incomplete_source_rows.append(row_id)
            if len(incomplete_examples) < 3:
                incomplete_examples.append(row_id)
            details.append(
                {
                    "kind": "oracle_declares_incomplete_source",
                    "row_id": row_id,
                    "pressure_tags": [str(tag) for tag in pressure_tags] if isinstance(pressure_tags, list) else [],
                }
            )
        answer = str(row.get("reference_answer") or row.get("answer") or "").strip()
        missing_terms = [term for term in _distinctive_reference_terms(answer) if term not in source_norm]
        if not missing_terms:
            continue
        absent_source_rows.append(row_id)
        if len(absent_examples) < 3:
            absent_examples.append(f"{row_id}:{','.join(missing_terms[:3])}")
        details.append(
            {
                "kind": "reference_terms_absent_from_source",
                "row_id": row_id,
                "missing_terms": missing_terms,
            }
        )
        notes_hit = any(term in notes_norm for term in missing_terms)
        metadata_hit = any(term in metadata_norm for term in missing_terms)
        if not notes_hit and not metadata_hit:
            continue
        non_source_rows.append(row_id)
        if notes_hit:
            notes_only_rows.append(row_id)
        if metadata_hit:
            metadata_only_rows.append(row_id)
        if len(examples) < 3:
            examples.append(f"{row_id}:{','.join(missing_terms[:3])}")
        details.append(
            {
                "kind": "reference_terms_absent_from_source_but_in_notes_or_metadata",
                "row_id": row_id,
                "missing_terms": missing_terms,
                "notes_hit": notes_hit,
                "metadata_hit": metadata_hit,
            }
        )
    warnings: list[str] = []
    if absent_source_rows:
        warnings.append(f"reference_terms_absent_from_source:{len(absent_source_rows)}")
        warnings.append(f"reference_absent_source_examples:{'|'.join(absent_examples)}")
    if non_source_rows:
        warnings.append(f"reference_terms_absent_from_source_but_in_notes_or_metadata:{len(non_source_rows)}")
        warnings.append(f"reference_non_source_examples:{'|'.join(examples)}")
    if notes_only_rows:
        warnings.append(f"reference_terms_found_in_fixture_notes:{len(notes_only_rows)}")
    if metadata_only_rows:
        warnings.append(f"reference_terms_found_in_metadata:{len(metadata_only_rows)}")
    if declared_incomplete_source_rows:
        warnings.append(f"oracle_declares_incomplete_source_rows:{len(declared_incomplete_source_rows)}")
        warnings.append(f"oracle_incomplete_source_examples:{'|'.join(incomplete_examples)}")
    return {"warnings": warnings, "details": details}


def _oracle_rows_for_support_check(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _search_text(text: str) -> str:
    return " ".join(_distinctive_reference_terms(text))


def _distinctive_reference_terms(text: str) -> list[str]:
    terms: list[str] = []
    for match in re.finditer(r"\b\d+(?:[.,]\d+)+(?:\s*%)?", str(text or ""), flags=re.UNICODE):
        raw_numeric = match.group(0).replace(" ", "").strip()
        if raw_numeric:
            terms.append(raw_numeric.casefold())
            terms.append(raw_numeric.rstrip("%").casefold())
    for match in re.finditer(r"[\w][\w./-]*", str(text or ""), flags=re.UNICODE):
        raw = match.group(0).strip("._-/")
        if not raw:
            continue
        term = raw.casefold()
        if len(term) >= 4 or any(char.isdigit() for char in term) or (len(raw) >= 2 and raw.isupper()):
            terms.append(term)
    return sorted(set(terms))


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Fresh Ugly Batch Validation",
        "",
        f"- Batch: `{report.get('batch_dir', '')}`",
        f"- Status: `{summary.get('status', '')}`",
        f"- Fixtures: `{summary.get('fixture_count', 0)}` / `{summary.get('expected_documents', 0)}`",
        f"- Issues: `{summary.get('issue_count', 0)}`",
        f"- Warnings: `{summary.get('warning_count', 0)}`",
        "",
        "| Fixture | Status | Questions | Answers | Oracle | Issues | Warnings |",
        "| --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in report.get("fixtures", []) or []:
        lines.append(
            "| `{fixture}` | `{status}` | {questions} | {answers} | {oracle} | {issues} | {warnings} |".format(
                fixture=row.get("fixture", ""),
                status=row.get("status", ""),
                questions=row.get("question_count", 0),
                answers=row.get("reference_answer_count", 0),
                oracle=row.get("oracle_row_count", 0),
                issues=", ".join(f"`{item}`" for item in row.get("issues", []) or []) or "-",
                warnings=", ".join(f"`{item}`" for item in row.get("warnings", []) or []) or "-",
            )
        )
    batch_issues = summary.get("batch_issues", [])
    if batch_issues:
        lines.extend(["", "## Batch Issues", ""])
        lines.extend(f"- `{item}`" for item in batch_issues)
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
