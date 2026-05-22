#!/usr/bin/env python3
"""Build a vocabulary-only profile registry from compile candidate palettes."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SIGNATURE_RE = re.compile(r"^([a-z][a-z0-9_]*)/([1-5])$")
TOKEN_RE = re.compile(r"[a-z0-9]+")


def build_registry(
    paths: list[Path],
    *,
    fixture: str = "",
    purpose: str = "",
    mode: str = "threshold",
    min_draw_share: float = 1.0,
    require_delivered: bool = False,
) -> dict[str, Any]:
    draws = [_load_compile(path) for path in _expand_paths(paths)]
    if not draws:
        return _registry(
            [],
            fixture=fixture,
            purpose=purpose,
            mode=mode,
            min_draw_share=min_draw_share,
            draw_count=0,
            require_delivered=require_delivered,
        )

    signatures_by_draw = [
        set(draw["delivered_predicates"] if require_delivered else draw["predicates"])
        for draw in draws
    ]
    counts: Counter[str] = Counter()
    for signature_set in signatures_by_draw:
        counts.update(signature_set)

    if mode == "first":
        selected = set(draws[0]["predicates"])
    elif mode == "union":
        selected = set().union(*signatures_by_draw)
    elif mode == "intersection":
        selected = set.intersection(*signatures_by_draw) if signatures_by_draw else set()
    elif mode == "threshold":
        threshold = max(1, int(math.ceil(len(draws) * max(0.0, min(1.0, min_draw_share)) - 0.000001)))
        selected = {signature for signature, count in counts.items() if count >= threshold}
    else:
        raise ValueError(f"Unknown mode: {mode}")

    rows = []
    for signature in sorted(selected):
        candidates = [row for draw in draws for row in draw["predicates"].get(signature, [])]
        rows.append(_registry_row(signature, candidates, draw_count=counts.get(signature, 0), total_draws=len(draws)))

    return _registry(
        rows,
        fixture=fixture or _common_fixture(draws),
        purpose=purpose,
        mode=mode,
        min_draw_share=min_draw_share,
        draw_count=len(draws),
        require_delivered=require_delivered,
    )


def _expand_paths(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for item in paths:
        path = item if item.is_absolute() else (REPO_ROOT / item).resolve()
        if path.is_file():
            out.append(path)
        elif path.is_dir():
            direct = sorted(path.glob("domain_bootstrap_file_*.json"))
            if direct:
                out.append(direct[-1])
            else:
                out.extend(sorted(path.glob("*/domain_bootstrap_file_*.json")))
    return sorted(dict.fromkeys(out))


def _load_compile(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    parsed = payload.get("parsed") if isinstance(payload.get("parsed"), dict) else {}
    delivered_signatures = _delivered_signatures(payload)
    rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in parsed.get("candidate_predicates", []) if isinstance(parsed.get("candidate_predicates"), list) else []:
        if not isinstance(item, dict):
            continue
        signature = _signature(item)
        if signature:
            rows[signature].append(item)
    return {
        "path": str(path),
        "fixture": path.parent.name,
        "predicates": dict(rows),
        "delivered_predicates": {signature: rows.get(signature, []) for signature in delivered_signatures if signature in rows},
    }


def _signature(item: dict[str, Any]) -> str:
    raw = str(item.get("signature", "")).strip().casefold()
    if SIGNATURE_RE.fullmatch(raw):
        return raw
    name = str(item.get("name") or item.get("predicate") or "").strip().casefold()
    args = item.get("args", [])
    if name and re.fullmatch(r"[a-z][a-z0-9_]*", name) and isinstance(args, list) and 1 <= len(args) <= 5:
        return f"{name}/{len(args)}"
    return ""


def _delivered_signatures(payload: dict[str, Any]) -> set[str]:
    source_compile = payload.get("source_compile") if isinstance(payload.get("source_compile"), dict) else {}
    facts = source_compile.get("facts", []) if isinstance(source_compile.get("facts"), list) else []
    out: set[str] = set()
    for fact in facts:
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\.\s*$", str(fact))
        if not match:
            continue
        predicate = match.group(1).strip().casefold()
        if predicate.startswith("source_record"):
            continue
        args = [part for part in match.group(2).split(",") if part.strip()]
        if 1 <= len(args) <= 5:
            out.add(f"{predicate}/{len(args)}")
    return out


def _registry_row(signature: str, candidates: list[dict[str, Any]], *, draw_count: int, total_draws: int) -> dict[str, Any]:
    arity = int(signature.rsplit("/", 1)[1])
    args = _best_args(candidates, arity)
    category = _category(signature)
    notes = (
        f"Palette candidate observed in {draw_count}/{total_draws} compile draw(s). "
        "Vocabulary scaffold only; direct source support and mapper admission are still required."
    )
    return {
        "signature": signature,
        "args": args,
        "category": category,
        "notes": notes,
        "draw_count": draw_count,
        "draw_share": round(draw_count / max(1, total_draws), 4),
    }


def _best_args(candidates: list[dict[str, Any]], arity: int) -> list[str]:
    counter: Counter[tuple[str, ...]] = Counter()
    for item in candidates:
        args = item.get("args", [])
        if not isinstance(args, list) or len(args) != arity:
            continue
        normalized = tuple(_safe_role_label(arg) for arg in args)
        if all(normalized):
            counter[normalized] += 1
    if counter:
        return list(counter.most_common(1)[0][0])
    return [f"arg_{index}" for index in range(1, arity + 1)]


def _safe_role_label(value: Any) -> str:
    text = str(value or "").strip().casefold()
    tokens = TOKEN_RE.findall(text.replace("-", "_"))
    if not tokens:
        return ""
    label = "_".join(tokens)[:40].strip("_")
    if not label or label[0].isdigit():
        return ""
    return label


def _category(signature: str) -> str:
    name = signature.split("/", 1)[0]
    tokens = set(name.split("_"))
    if tokens & {"status", "state", "phase", "result", "outcome"}:
        return "status_state"
    if tokens & {"date", "time", "timestamp", "deadline", "duration", "interval", "schedule"}:
        return "temporal"
    if tokens & {"amount", "count", "total", "value", "rate", "ratio", "threshold", "limit"}:
        return "quantity"
    if tokens & {"role", "actor", "authority", "issuer", "approver", "owner"}:
        return "role_authority"
    if tokens & {"source", "record", "document", "field", "note", "detail"}:
        return "source_record"
    if tokens & {"assignment", "assigned", "group", "member", "roster"}:
        return "membership_assignment"
    if tokens & {"rule", "policy", "requirement", "condition"}:
        return "rule_policy"
    if tokens & {"event", "change", "correction", "transition"}:
        return "event_change"
    return "domain_surface"


def _registry(
    rows: list[dict[str, Any]],
    *,
    fixture: str,
    purpose: str,
    mode: str,
    min_draw_share: float,
    draw_count: int,
    require_delivered: bool,
) -> dict[str, Any]:
    return {
        "schema": "candidate_profile_registry_v1",
        "fixture": str(fixture or "").strip(),
        "source": "compile_candidate_palette_v1 vocabulary only; not facts, not answers, not authority",
        "purpose": str(purpose or "Stabilize candidate predicate palette without injecting source facts.").strip(),
        "selection": {
            "mode": mode,
            "min_draw_share": min_draw_share,
            "draw_count": draw_count,
            "require_delivered": require_delivered,
        },
        "predicates": rows,
    }


def _common_fixture(draws: list[dict[str, Any]]) -> str:
    names = {str(draw.get("fixture", "")).strip() for draw in draws if str(draw.get("fixture", "")).strip()}
    return sorted(names)[0] if len(names) == 1 else ""


def render_markdown(registry: dict[str, Any]) -> str:
    selection = registry.get("selection") if isinstance(registry.get("selection"), dict) else {}
    lines = [
        "# Profile Palette Registry",
        "",
        f"- Fixture: `{registry.get('fixture', '')}`",
        f"- Predicate count: `{len(registry.get('predicates', [])) if isinstance(registry.get('predicates'), list) else 0}`",
        f"- Selection mode: `{selection.get('mode', '')}`",
        f"- Draw count: `{selection.get('draw_count', 0)}`",
        f"- Require delivered: `{selection.get('require_delivered', False)}`",
        "",
        "This registry is vocabulary-only. It does not contain facts, answers, expected rows, or source authority.",
        "",
        "| Signature | Args | Category | Draw share |",
        "| --- | --- | --- | ---: |",
    ]
    for row in registry.get("predicates", []) if isinstance(registry.get("predicates"), list) else []:
        lines.append(
            f"| `{row.get('signature', '')}` | `{row.get('args', [])}` | `{row.get('category', '')}` | {row.get('draw_share', '')} |"
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile-json", action="append", type=Path, default=[])
    parser.add_argument("--mode", choices=["first", "union", "intersection", "threshold"], default="threshold")
    parser.add_argument("--min-draw-share", type=float, default=1.0)
    parser.add_argument(
        "--require-delivered",
        action="store_true",
        help="Select only predicate signatures that were both offered by the profile and delivered as direct facts.",
    )
    parser.add_argument("--fixture", default="")
    parser.add_argument("--purpose", default="")
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-md", type=Path)
    args = parser.parse_args()

    registry = build_registry(
        args.compile_json,
        fixture=str(args.fixture or ""),
        purpose=str(args.purpose or ""),
        mode=str(args.mode),
        min_draw_share=float(args.min_draw_share),
        require_delivered=bool(args.require_delivered),
    )
    out_json = args.out_json if args.out_json.is_absolute() else (REPO_ROOT / args.out_json).resolve()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        out_md = args.out_md if args.out_md.is_absolute() else (REPO_ROOT / args.out_md).resolve()
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(render_markdown(registry), encoding="utf-8")
    print(json.dumps({"predicate_count": len(registry.get("predicates", [])), "out_json": str(out_json)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
