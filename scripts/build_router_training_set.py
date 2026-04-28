from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_mixed_domain_agility import build_mixed_cases  # noqa: E402
from scripts.run_multilingual_semantic_ir_probe import MULTILINGUAL_CASES  # noqa: E402
from scripts.run_semantic_ir_lava_sweep import load_frontier_pack_cases  # noqa: E402


DEFAULT_OUT = REPO_ROOT / "docs" / "data" / "router_training" / "router_training_seed_v1.jsonl"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a labeled semantic_router_v1 seed corpus.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_router_training_rows()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"Wrote {len(rows)} router training rows to {out}")
    return 0


def build_router_training_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in load_frontier_pack_cases(REPO_ROOT / "docs" / "data" / "frontier_packs"):
        if not case.expected_profile:
            continue
        rows.append(
            _row(
                row_id=case.id,
                source=case.source,
                utterance=case.utterance,
                context=list(case.context),
                expected_profile=case.expected_profile,
                expected_decision=case.expected_decision,
                labels={"frontier_pack": case.source.split(":", 1)[-1]},
            )
        )
    for item in MULTILINGUAL_CASES:
        rows.append(
            _row(
                row_id=str(item.get("id") or f"multilingual_{len(rows) + 1:04d}"),
                source="multilingual_probe",
                utterance=str(item.get("utterance") or ""),
                context=[str(ctx) for ctx in item.get("context", []) if str(ctx).strip()],
                expected_profile=str(item.get("expected_profile") or ""),
                labels={"language": item.get("language")},
            )
        )
    for item in build_mixed_cases():
        rows.append(
            _row(
                row_id=str(item.get("id") or f"mixed_{len(rows) + 1:04d}"),
                source=str(item.get("source") or "mixed_domain_agility"),
                utterance=str(item.get("utterance") or ""),
                context=[str(ctx) for ctx in item.get("context", []) if str(ctx).strip()],
                expected_profile=str(item.get("expected_profile") or ""),
                labels={"mixed_domain_agility": True},
            )
        )
    return _dedupe_rows(rows)


def _row(
    *,
    row_id: str,
    source: str,
    utterance: str,
    context: list[str],
    expected_profile: str,
    expected_decision: str = "",
    labels: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "semantic_router_training_v1",
        "id": row_id,
        "source": source,
        "utterance": utterance,
        "context": context,
        "expected_profile": expected_profile,
        "expected_decision": expected_decision,
        "labels": labels or {},
    }


def _dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (
            str(row.get("utterance") or "").strip(),
            "\n".join(str(item) for item in row.get("context", [])),
            str(row.get("expected_profile") or "").strip(),
        )
        if not key[0] or not key[2] or key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


if __name__ == "__main__":
    raise SystemExit(main())
