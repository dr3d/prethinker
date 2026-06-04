#!/usr/bin/env python3
"""Validate candidate domain-predicate proposal files.

This is a pre-registry governance check. It validates whether a proposed
carrier family has enough recurring-anatomy, lens-scope, value-domain, example,
and promotion-gate structure to be reviewed without reopening prose smuggling
or row-specific predicate growth.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.carrier_contract_registry import carrier_contract  # noqa: E402
from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402


DEFAULT_ROOT = REPO_ROOT / "datasets" / "domain_predicate_proposals"
DEFAULT_PROFILE_ROOT = REPO_ROOT / "datasets" / "domain_profiles"

SIGNATURE_RE = re.compile(r"^[a-z][a-z0-9_]*/[1-9][0-9]*$")
ARG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
FACT_RE = re.compile(r"^\s*([a-z][a-z0-9_]*)\((.*)\)\.\s*$")
PROSE_SLOT_RE = re.compile(r"(text|excerpt|paragraph|sentence|summary|blob|narrative|rationale|explanation)")
REQUIRED_ANTI_LEAK_GUARDS = {
    "no_source_prose",
    "no_query_text_routing",
    "no_fixture_vocabulary",
    "no_answer_key_influence",
    "atom_shape_gate",
}
REQUIRED_PROMOTION_GATES = {
    "n_ge_3",
    "support_ge_2",
    "zero_forbidden",
    "atom_shape",
    "lens_scope",
    "value_domain",
    "unlike_transfer",
}
VALID_STATUSES = {"draft", "candidate", "rejected", "promoted"}


TEMPLATE: dict[str, Any] = {
    "schema": "domain_predicate_proposal_v1",
    "proposal_id": "example_document_family_carrier_v1",
    "status": "draft",
    "domain_profile": "example_domain_v1",
    "bounded_document_family": "One recurring official-document family.",
    "candidate_signature": "example_carrier/5",
    "lens_owner": "wrapper",
    "allowed_lenses": ["wrapper"],
    "recurring_anatomy": [
        "Repeated source anatomy item one.",
        "Repeated source anatomy item two.",
    ],
    "answer_classes": ["document_metadata"],
    "argument_roles": [
        {"name": "subject_id", "purpose": "Stable governed subject id.", "source_coordinate": False},
        {"name": "kind", "purpose": "Compact structural kind.", "source_coordinate": False},
        {"name": "value", "purpose": "Compact source-stated value.", "source_coordinate": False},
        {"name": "status", "purpose": "Compact status enum.", "source_coordinate": False},
        {"name": "source_or_scope", "purpose": "Source coordinate or scope atom.", "source_coordinate": True},
    ],
    "value_domains": {
        "kind": ["example_kind"],
        "status": ["stated", "not_stated"],
    },
    "positive_examples": [
        {
            "fixture_id": "example_seed_v1",
            "fact": "example_carrier(Subject, example_kind, example_value, stated, Src).",
        }
    ],
    "forbidden_examples": [
        {
            "fixture_id": "example_seed_v1",
            "fact": "example_carrier(Subject, full_source_sentence_blob, example_value, stated, Src).",
        }
    ],
    "unlike_transfer_plan": {
        "minimum_fixtures": 1,
        "n": 3,
        "support_threshold": 2,
        "heldout_policy": "unlike_same_family_document_not_used_to_shape_the_carrier",
    },
    "promotion_gates": [
        "n_ge_3",
        "support_ge_2",
        "zero_forbidden",
        "atom_shape",
        "lens_scope",
        "value_domain",
        "unlike_transfer",
    ],
    "anti_leak_guards": [
        "no_source_prose",
        "no_query_text_routing",
        "no_fixture_vocabulary",
        "no_answer_key_influence",
        "atom_shape_gate",
    ],
    "abstention_boundary": [
        "Do not emit when the value would require a prose-shaped atom.",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--profile-root", type=Path, default=DEFAULT_PROFILE_ROOT)
    parser.add_argument("--proposal", action="append", default=[], type=Path)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    parser.add_argument(
        "--expect-md",
        type=Path,
        default=None,
        help="Fail if this markdown file differs from the freshly rendered report.",
    )
    parser.add_argument("--print-template", action="store_true")
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.print_template:
        print(json.dumps(TEMPLATE, indent=2, sort_keys=True))
        return 0
    paths = _proposal_paths(root=args.root, explicit=args.proposal)
    report = build_report(paths, profile_root=args.profile_root)
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(
            report=report,
            expected_path=args.expect_md,
            rendered_md=rendered_md,
        )
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if args.exit_zero or report["summary"]["status"] == "pass" else 1


def build_report(paths: list[Path], *, profile_root: Path = DEFAULT_PROFILE_ROOT) -> dict[str, Any]:
    rows = [_validate_proposal(path, profile_root=profile_root) for path in paths]
    blocking_errors = sum(len(row["errors"]) for row in rows)
    warning_count = sum(len(row["warnings"]) for row in rows)
    return {
        "schema_version": "domain_predicate_proposal_validation_v1",
        "summary": {
            "proposal_count": len(rows),
            "blocking_errors": blocking_errors,
            "blocking_reasons": [],
            "warning_count": warning_count,
            "status": "fail" if blocking_errors else "pass",
        },
        "proposals": rows,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Domain Predicate Proposal Validation",
        "",
        "This report validates proposal shape only. A passing proposal is not a",
        "promoted domain-pack claim until its transfer plan succeeds under the",
        "claim-bearing gates.",
        "",
        f"- Proposals: `{summary['proposal_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Warnings: `{summary['warning_count']}`",
        f"- Status: `{summary['status']}`",
        "",
        "| Proposal | Signature | Status | Reviews | Errors | Warnings |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in report.get("proposals", []):
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                row.get("proposal_id") or row.get("path", ""),
                row.get("candidate_signature", ""),
                row.get("status", ""),
                _review_summary(row.get("review_results")),
                row.get("errors", []),
                row.get("warnings", []),
            )
        )
    return "\n".join(lines) + "\n"


def _proposal_paths(*, root: Path, explicit: list[Path]) -> list[Path]:
    paths = [path.resolve() for path in explicit]
    root_path = root.resolve()
    if root_path.exists():
        paths.extend(sorted(root_path.rglob("*.json")))
    unique: dict[str, Path] = {}
    for path in paths:
        unique[str(path)] = path
    return list(unique.values())


def _validate_proposal(path: Path, *, profile_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    data = _load_json(path)
    if not data:
        return _row(path=path, data={}, errors=["invalid_or_empty_json"], warnings=[])

    if str(data.get("schema") or "").strip() != "domain_predicate_proposal_v1":
        errors.append("unexpected_schema")
    status = str(data.get("status") or "").strip()
    if status not in VALID_STATUSES:
        errors.append("invalid_status")
    review_results = data.get("review_results") if isinstance(data.get("review_results"), list) else []
    if _has_blocked_review(review_results) and status != "rejected":
        errors.append("blocked_review_requires_rejected_status")

    proposal_id = str(data.get("proposal_id") or "").strip()
    if not proposal_id or not ARG_RE.match(proposal_id):
        errors.append("invalid_or_missing_proposal_id")

    signature = str(data.get("candidate_signature") or "").strip()
    arity = _signature_arity(signature)
    if arity < 1:
        errors.append("invalid_candidate_signature")

    domain_profile = str(data.get("domain_profile") or "").strip()
    profile = _load_profile(domain_profile, profile_root=profile_root)
    lens_owner = str(data.get("lens_owner") or "").strip()
    if not lens_owner or not ARG_RE.match(lens_owner):
        errors.append("invalid_or_missing_lens_owner")
    elif profile and lens_owner not in _profile_lenses(profile):
        errors.append("lens_owner_not_in_domain_profile")

    allowed_lenses = _string_list(data.get("allowed_lenses"))
    if lens_owner and lens_owner not in allowed_lenses:
        errors.append("lens_owner_not_in_allowed_lenses")
    if profile:
        known_lenses = _profile_lenses(profile)
        for lens in allowed_lenses:
            if lens not in known_lenses:
                errors.append(f"allowed_lens_not_in_domain_profile:{lens}")

    recurring_anatomy = _string_list(data.get("recurring_anatomy"))
    if len(recurring_anatomy) < 2:
        errors.append("recurring_anatomy_requires_at_least_two_items")
    if any(len(item) > 180 for item in recurring_anatomy):
        errors.append("recurring_anatomy_item_too_long")

    answer_classes = _string_list(data.get("answer_classes"))
    if not answer_classes:
        errors.append("missing_answer_classes")

    argument_roles = data.get("argument_roles")
    if not isinstance(argument_roles, list) or not argument_roles:
        errors.append("missing_argument_roles")
        argument_roles = []
    if arity > 0 and len(argument_roles) != arity:
        errors.append("argument_role_count_does_not_match_signature_arity")
    arg_names: set[str] = set()
    for index, role in enumerate(argument_roles):
        if not isinstance(role, dict):
            errors.append(f"argument_role_{index + 1}:not_object")
            continue
        name = str(role.get("name") or "").strip()
        purpose = str(role.get("purpose") or "").strip()
        if not ARG_RE.match(name):
            errors.append(f"argument_role_{index + 1}:invalid_name")
        if not purpose:
            errors.append(f"argument_role_{index + 1}:missing_purpose")
        if role.get("prose_allowed") is True:
            errors.append(f"argument_role_{name or index + 1}:prose_allowed_true")
        if PROSE_SLOT_RE.search(name):
            errors.append(f"argument_role_{name}:prose_shaped_slot_name")
        arg_names.add(name)

    value_domains = data.get("value_domains", {})
    if not isinstance(value_domains, dict):
        errors.append("value_domains_not_object")
        value_domains = {}
    for name, values in value_domains.items():
        if str(name) not in arg_names:
            errors.append(f"value_domain_arg_not_in_argument_roles:{name}")
        if not isinstance(values, list) or not values:
            errors.append(f"value_domain_empty:{name}")
            continue
        if len(values) > 40:
            errors.append(f"value_domain_too_large:{name}")
        for value in values:
            text = str(value).strip()
            if not ARG_RE.match(text):
                errors.append(f"value_domain_not_compact_atom:{name}:{text}")

    _validate_examples(data.get("positive_examples"), signature, "positive", errors)
    _validate_examples(data.get("forbidden_examples"), signature, "forbidden", errors)
    _validate_transfer_plan(data.get("unlike_transfer_plan"), errors)

    anti_leak_guards = set(_string_list(data.get("anti_leak_guards")))
    missing_anti_leak = sorted(REQUIRED_ANTI_LEAK_GUARDS - anti_leak_guards)
    if missing_anti_leak:
        errors.append(f"missing_anti_leak_guards:{','.join(missing_anti_leak)}")

    promotion_gates = set(_string_list(data.get("promotion_gates")))
    missing_gates = sorted(REQUIRED_PROMOTION_GATES - promotion_gates)
    if missing_gates:
        errors.append(f"missing_promotion_gates:{','.join(missing_gates)}")

    if not _string_list(data.get("abstention_boundary")):
        errors.append("missing_abstention_boundary")

    if status == "promoted":
        if carrier_contract(signature) is None:
            errors.append("promoted_signature_not_registered")
        if profile and signature not in _profile_signatures(profile):
            errors.append("promoted_signature_not_in_domain_profile")
        if profile and lens_owner and signature not in _lens_allowed_signatures(profile, lens_owner):
            errors.append("promoted_signature_not_in_lens_owner_allowlist")
    elif status in {"draft", "candidate"} and carrier_contract(signature) is None:
        warnings.append("candidate_signature_not_yet_registered")

    return _row(path=path, data=data, errors=errors, warnings=warnings)


def _validate_examples(value: Any, signature: str, kind: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"missing_{kind}_examples")
        return
    predicate, arity = signature.split("/", 1) if "/" in signature else ("", "0")
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            errors.append(f"{kind}_example_{index + 1}:not_object")
            continue
        fixture_id = str(item.get("fixture_id") or "").strip()
        fact = str(item.get("fact") or "").strip()
        if not fixture_id:
            errors.append(f"{kind}_example_{index + 1}:missing_fixture_id")
        parsed = FACT_RE.match(fact)
        if not parsed:
            errors.append(f"{kind}_example_{index + 1}:invalid_fact")
            continue
        if parsed.group(1) != predicate:
            errors.append(f"{kind}_example_{index + 1}:fact_signature_mismatch")
            continue
        arg_count = len(_split_args(parsed.group(2)))
        if str(arg_count) != str(arity):
            errors.append(f"{kind}_example_{index + 1}:fact_arity_mismatch")
        if len(fact) > 260:
            errors.append(f"{kind}_example_{index + 1}:fact_too_long")


def _validate_transfer_plan(value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append("missing_unlike_transfer_plan")
        return
    if _int_value(value.get("minimum_fixtures")) < 1:
        errors.append("unlike_transfer_plan_minimum_fixtures_lt_1")
    if _int_value(value.get("n")) < 3:
        errors.append("unlike_transfer_plan_n_lt_3")
    if _int_value(value.get("support_threshold")) < 2:
        errors.append("unlike_transfer_plan_support_threshold_lt_2")
    if not str(value.get("heldout_policy") or "").strip():
        errors.append("unlike_transfer_plan_missing_heldout_policy")


def _row(*, path: Path, data: dict[str, Any], errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "path": str(path),
        "proposal_id": str(data.get("proposal_id") or "").strip(),
        "status": str(data.get("status") or "").strip(),
        "domain_profile": str(data.get("domain_profile") or "").strip(),
        "candidate_signature": str(data.get("candidate_signature") or "").strip(),
        "lens_owner": str(data.get("lens_owner") or "").strip(),
        "review_results": data.get("review_results") if isinstance(data.get("review_results"), list) else [],
        "errors": errors,
        "warnings": warnings,
    }


def _has_blocked_review(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    for item in value:
        if not isinstance(item, dict):
            continue
        result = str(item.get("result") or "").strip()
        if result.startswith("blocked"):
            return True
    return False


def _review_summary(value: Any) -> str:
    if not isinstance(value, list) or not value:
        return ""
    parts: list[str] = []
    for item in value[:3]:
        if not isinstance(item, dict):
            continue
        fixture = str(item.get("fixture_id") or "").strip()
        result = str(item.get("result") or "").strip()
        if fixture or result:
            parts.append(f"{fixture}:{result}".strip(":"))
    return "; ".join(parts)


def _signature_arity(signature: str) -> int:
    if not SIGNATURE_RE.match(signature):
        return -1
    return int(signature.rsplit("/", 1)[1])


def _profile_lenses(profile: dict[str, Any]) -> set[str]:
    return {str(item.get("id") or "").strip() for item in profile.get("lenses", []) if isinstance(item, dict)}


def _profile_signatures(profile: dict[str, Any]) -> set[str]:
    return {str(item.get("signature") or "").strip() for item in profile.get("predicates", []) if isinstance(item, dict)}


def _lens_allowed_signatures(profile: dict[str, Any], lens_id: str) -> set[str]:
    for item in profile.get("lenses", []):
        if isinstance(item, dict) and str(item.get("id") or "").strip() == lens_id:
            return set(_string_list(item.get("allowed_signatures")))
    return set()


def _load_profile(domain_profile: str, *, profile_root: Path) -> dict[str, Any]:
    if not domain_profile:
        return {}
    path = Path(domain_profile)
    if not path.suffix:
        path = profile_root / domain_profile / "ontology_registry.json"
    elif not path.is_absolute():
        path = REPO_ROOT / path
    return _load_json(path)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _split_args(raw: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    escape = False
    for char in raw:
        if quote:
            current.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            continue
        if char == "(":
            depth += 1
            current.append(char)
            continue
        if char == ")":
            depth = max(0, depth - 1)
            current.append(char)
            continue
        if char == "," and depth == 0:
            args.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if current or raw.strip():
        args.append("".join(current).strip())
    return args


if __name__ == "__main__":
    raise SystemExit(main())
