#!/usr/bin/env python3
"""
Blocksworld lane runner for Prethinker.

What this does:
1) Pull a small verified slice from Hugging Face Planetarium.
2) Import a STRIPS Blocksworld domain (Sys2Bench generated_domain.pddl).
3) Compile actions into a grounded transition system.
4) Solve/replay each sampled problem (BFS) to verify symbolic path viability.
5) Optionally run a small Prethinker NL ingestion pilot on the same cases.
6) Emit machine + markdown artifacts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import re
import subprocess
import sys
from collections import Counter, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from huggingface_hub import hf_hub_download

ROOT = Path(__file__).resolve().parents[1]
RUN_STORY_RAW = ROOT / "scripts" / "run_story_raw.py"

PRED_ALIASES = {
    "arm_empty": "handempty",
    "on_table": "ontable",
}


@dataclass(frozen=True)
class Literal:
    predicate: str
    args: tuple[str, ...]
    positive: bool = True


@dataclass(frozen=True)
class ActionSchema:
    name: str
    params: tuple[str, ...]
    pre_pos: tuple[tuple[str, tuple[str, ...]], ...]
    pre_neg: tuple[tuple[str, tuple[str, ...]], ...]
    add: tuple[tuple[str, tuple[str, ...]], ...]
    delete: tuple[tuple[str, tuple[str, ...]], ...]


def _utc_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S")


def _normalize_symbol(token: str) -> str:
    return str(token or "").strip().lower().replace("-", "_")


def _normalize_predicate(token: str) -> str:
    norm = _normalize_symbol(token)
    return PRED_ALIASES.get(norm, norm)


def _tokenize_sexpr(text: str) -> list[str]:
    tokens: list[str] = []
    current: list[str] = []
    for ch in text:
        if ch in ("(", ")"):
            if current:
                tokens.append("".join(current))
                current = []
            tokens.append(ch)
            continue
        if ch.isspace():
            if current:
                tokens.append("".join(current))
                current = []
            continue
        current.append(ch)
    if current:
        tokens.append("".join(current))
    return tokens


def _parse_sexpr_tokens(tokens: list[str], idx: int = 0) -> tuple[Any, int]:
    if idx >= len(tokens):
        raise ValueError("unexpected end of tokens")
    token = tokens[idx]
    if token == "(":
        out: list[Any] = []
        idx += 1
        while idx < len(tokens) and tokens[idx] != ")":
            node, idx = _parse_sexpr_tokens(tokens, idx)
            out.append(node)
        if idx >= len(tokens) or tokens[idx] != ")":
            raise ValueError("unbalanced parentheses")
        return out, idx + 1
    if token == ")":
        raise ValueError("unexpected ')'")
    return token, idx + 1


def _parse_sexpr(text: str) -> Any:
    tokens = _tokenize_sexpr(text)
    node, idx = _parse_sexpr_tokens(tokens, 0)
    if idx != len(tokens):
        raise ValueError("trailing tokens after parse")
    return node


def _iter_conj(expr: Any) -> list[Any]:
    if isinstance(expr, list) and expr:
        head = str(expr[0]).lower()
        if head == "and":
            return list(expr[1:])
    return [expr]


def _to_literal(expr: Any) -> Literal:
    if not isinstance(expr, list) or not expr:
        raise ValueError(f"invalid literal expression: {expr!r}")
    if str(expr[0]).lower() == "not":
        if len(expr) != 2:
            raise ValueError(f"invalid negated literal: {expr!r}")
        inner = _to_literal(expr[1])
        return Literal(predicate=inner.predicate, args=inner.args, positive=False)
    pred = _normalize_predicate(str(expr[0]))
    args = tuple(_normalize_symbol(str(x).lstrip("?")) for x in expr[1:])
    return Literal(predicate=pred, args=args, positive=True)


def _instantiate_term(
    pred: str,
    args: tuple[str, ...],
    env: dict[str, str],
) -> tuple[str, tuple[str, ...]]:
    out_args: list[str] = []
    for arg in args:
        key = arg.lstrip("?")
        out_args.append(env.get(key, env.get(arg, arg)))
    return pred, tuple(out_args)


def _parse_action_schema(action_expr: list[Any]) -> ActionSchema:
    if len(action_expr) < 2:
        raise ValueError(f"invalid action expr: {action_expr!r}")
    name = _normalize_symbol(str(action_expr[1]))
    fields: dict[str, Any] = {}
    idx = 2
    while idx + 1 < len(action_expr):
        key = str(action_expr[idx]).lower()
        value = action_expr[idx + 1]
        fields[key] = value
        idx += 2

    params_raw = fields.get(":parameters", [])
    params: list[str] = []
    if isinstance(params_raw, list):
        skip_type_next = False
        for tok in params_raw:
            token = str(tok)
            if skip_type_next:
                skip_type_next = False
                continue
            if token == "-":
                skip_type_next = True
                continue
            if token.startswith("?"):
                params.append(_normalize_symbol(token.lstrip("?")))

    pre_expr = fields.get(":precondition", ["and"])
    eff_expr = fields.get(":effect", ["and"])
    pre_literals = [_to_literal(x) for x in _iter_conj(pre_expr)]
    eff_literals = [_to_literal(x) for x in _iter_conj(eff_expr)]

    pre_pos: list[tuple[str, tuple[str, ...]]] = []
    pre_neg: list[tuple[str, tuple[str, ...]]] = []
    add: list[tuple[str, tuple[str, ...]]] = []
    delete: list[tuple[str, tuple[str, ...]]] = []

    for lit in pre_literals:
        target = pre_pos if lit.positive else pre_neg
        target.append((lit.predicate, lit.args))
    for lit in eff_literals:
        target = add if lit.positive else delete
        target.append((lit.predicate, lit.args))

    return ActionSchema(
        name=name,
        params=tuple(params),
        pre_pos=tuple(pre_pos),
        pre_neg=tuple(pre_neg),
        add=tuple(add),
        delete=tuple(delete),
    )


def _parse_domain_actions(domain_pddl: str) -> list[ActionSchema]:
    tree = _parse_sexpr(domain_pddl)
    if not isinstance(tree, list):
        raise ValueError("domain parse did not produce list tree")
    actions: list[ActionSchema] = []
    for node in tree:
        if not (isinstance(node, list) and node):
            continue
        if str(node[0]).lower() == ":action":
            actions.append(_parse_action_schema(node))
    return actions


def _parse_problem(problem_pddl: str) -> dict[str, Any]:
    tree = _parse_sexpr(problem_pddl)
    if not isinstance(tree, list):
        raise ValueError("problem parse did not produce list tree")

    objects: list[str] = []
    init_pos: set[tuple[str, tuple[str, ...]]] = set()
    goal_pos: set[tuple[str, tuple[str, ...]]] = set()
    goal_neg: set[tuple[str, tuple[str, ...]]] = set()

    for node in tree:
        if not (isinstance(node, list) and node):
            continue
        head = str(node[0]).lower()
        if head == ":objects":
            skip_type = False
            for tok in node[1:]:
                token = str(tok)
                if skip_type:
                    skip_type = False
                    continue
                if token == "-":
                    skip_type = True
                    continue
                objects.append(_normalize_symbol(token))
        elif head == ":init":
            for lit_expr in node[1:]:
                lit = _to_literal(lit_expr)
                if lit.positive:
                    init_pos.add((lit.predicate, lit.args))
        elif head == ":goal" and len(node) >= 2:
            for lit_expr in _iter_conj(node[1]):
                lit = _to_literal(lit_expr)
                target = goal_pos if lit.positive else goal_neg
                target.add((lit.predicate, lit.args))

    return {
        "objects": sorted(set(objects)),
        "init_pos": init_pos,
        "goal_pos": goal_pos,
        "goal_neg": goal_neg,
    }


def _state_satisfies(
    state: frozenset[tuple[str, tuple[str, ...]]],
    goal_pos: set[tuple[str, tuple[str, ...]]],
    goal_neg: set[tuple[str, tuple[str, ...]]],
) -> bool:
    if not goal_pos.issubset(state):
        return False
    if goal_neg.intersection(state):
        return False
    return True


def _ground_actions(
    schemas: list[ActionSchema],
    objects: list[str],
) -> list[tuple[str, tuple[str, ...], set[tuple[str, tuple[str, ...]]], set[tuple[str, tuple[str, ...]]], set[tuple[str, tuple[str, ...]]], set[tuple[str, tuple[str, ...]]]]]:
    grounded = []
    for schema in schemas:
        param_names = list(schema.params)
        if not param_names:
            env = {}
            name = schema.name
            pre_pos = {_instantiate_term(p, a, env) for p, a in schema.pre_pos}
            pre_neg = {_instantiate_term(p, a, env) for p, a in schema.pre_neg}
            add = {_instantiate_term(p, a, env) for p, a in schema.add}
            delete = {_instantiate_term(p, a, env) for p, a in schema.delete}
            grounded.append((name, tuple(), pre_pos, pre_neg, add, delete))
            continue

        for combo in itertools.product(objects, repeat=len(param_names)):
            env = {param_names[i]: combo[i] for i in range(len(param_names))}
            name = schema.name
            pre_pos = {_instantiate_term(p, a, env) for p, a in schema.pre_pos}
            pre_neg = {_instantiate_term(p, a, env) for p, a in schema.pre_neg}
            add = {_instantiate_term(p, a, env) for p, a in schema.add}
            delete = {_instantiate_term(p, a, env) for p, a in schema.delete}
            grounded.append((name, tuple(combo), pre_pos, pre_neg, add, delete))
    grounded.sort(key=lambda x: (x[0], x[1]))
    return grounded


def _bfs_plan(
    init_state: frozenset[tuple[str, tuple[str, ...]]],
    goal_pos: set[tuple[str, tuple[str, ...]]],
    goal_neg: set[tuple[str, tuple[str, ...]]],
    grounded_actions: list[tuple[str, tuple[str, ...], set[tuple[str, tuple[str, ...]]], set[tuple[str, tuple[str, ...]]], set[tuple[str, tuple[str, ...]]], set[tuple[str, tuple[str, ...]]]]],
    *,
    max_depth: int,
) -> tuple[list[str] | None, int]:
    if _state_satisfies(init_state, goal_pos, goal_neg):
        return [], 0

    visited = {init_state}
    queue: deque[tuple[frozenset[tuple[str, tuple[str, ...]]], list[str]]] = deque()
    queue.append((init_state, []))
    expansions = 0

    while queue:
        state, plan = queue.popleft()
        if len(plan) >= max_depth:
            continue
        expansions += 1
        for name, args, pre_pos, pre_neg, add, delete in grounded_actions:
            if not pre_pos.issubset(state):
                continue
            if pre_neg.intersection(state):
                continue
            next_state = frozenset((state - delete) | add)
            if next_state in visited:
                continue
            action_str = f"{name}({', '.join(args)})" if args else f"{name}()"
            next_plan = plan + [action_str]
            if _state_satisfies(next_state, goal_pos, goal_neg):
                return next_plan, expansions
            visited.add(next_state)
            queue.append((next_state, next_plan))
    return None, expansions


def _render_prolog_rules(schemas: list[ActionSchema]) -> str:
    lines: list[str] = []
    lines.append("% Auto-generated Blocksworld governor skeleton from PDDL actions")
    lines.append("% This file is a reference scaffold, not auto-loaded into runtime.")
    lines.append("")
    for schema in schemas:
        args = ", ".join(schema.params) if schema.params else ""
        head = f"{schema.name}({args})" if args else f"{schema.name}"

        pre_parts: list[str] = []
        for pred, pargs in schema.pre_pos:
            if pargs:
                pre_parts.append(f"{pred}({', '.join(pargs)})")
            else:
                pre_parts.append(pred)
        for pred, pargs in schema.pre_neg:
            atom = f"{pred}({', '.join(pargs)})" if pargs else pred
            pre_parts.append(f"\\+ {atom}")
        body = ", ".join(pre_parts) if pre_parts else "true"
        lines.append(f"governor_check({head}) :- {body}.")

        lines.append(f"% apply_effect({head}) should retract delete-literals then assert add-literals:")
        for pred, pargs in schema.delete:
            atom = f"{pred}({', '.join(pargs)})" if pargs else pred
            lines.append(f"%   retractall({atom}).")
        for pred, pargs in schema.add:
            atom = f"{pred}({', '.join(pargs)})" if pargs else pred
            lines.append(f"%   assertz({atom}).")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def _extract_predicates_from_parse(turns: list[dict[str, Any]]) -> set[str]:
    preds: set[str] = set()
    pattern = re.compile(r"([a-z_][a-z0-9_]*)\s*\(")
    for turn in turns:
        parsed = turn.get("parsed")
        if not isinstance(parsed, dict):
            continue
        pieces: list[str] = []
        logic = parsed.get("logic_string")
        if isinstance(logic, str):
            pieces.append(logic)
        facts = parsed.get("facts")
        if isinstance(facts, list):
            for f in facts:
                if isinstance(f, str):
                    pieces.append(f)
        for piece in pieces:
            for m in re.finditer(r"([a-z_][a-z0-9_]*)\s*\(", piece.lower()):
                preds.add(m.group(1))
    return preds


def _md_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Blocksworld PDDL lane + optional Prethinker pilot.")
    p.add_argument("--sample-size", type=int, default=40)
    p.add_argument("--max-objects", type=int, default=4)
    p.add_argument("--planner-depth", type=int, default=12)
    p.add_argument("--run-prethinker", action="store_true")
    p.add_argument("--prethinker-cases", type=int, default=8)
    p.add_argument("--backend", default="ollama")
    p.add_argument("--base-url", default="http://127.0.0.1:11434")
    p.add_argument("--model", default="qwen3.5:9b")
    p.add_argument("--prompt-file", default="modelfiles/semantic_parser_system_prompt.md")
    p.add_argument("--context-length", type=int, default=8192)
    p.add_argument("--prethinker-split-mode", choices=["full", "paragraph", "line"], default="full")
    p.add_argument("--predicate-registry", default="")
    p.add_argument("--strict-registry", action="store_true")
    p.add_argument("--type-schema", default="")
    p.add_argument(
        "--max-zero-hit",
        type=int,
        default=-1,
        help="Fail the run when zero-hit case count exceeds this threshold. Use -1 to disable.",
    )
    p.add_argument(
        "--min-avg-init-hit",
        type=float,
        default=-1.0,
        help="Fail the run when average init predicate hit ratio drops below this threshold. Use -1 to disable.",
    )
    p.add_argument(
        "--min-avg-goal-hit",
        type=float,
        default=-1.0,
        help="Fail the run when average goal predicate hit ratio drops below this threshold. Use -1 to disable.",
    )
    p.add_argument("--summary-json", default="tmp/blocksworld_lane_2026-04-16.summary.json")
    p.add_argument("--summary-md", default="tmp/reports/BLOCKSWORLD_LANE.md")
    p.add_argument("--cases-jsonl", default="tmp/blocksworld_lane_2026-04-16.cases.jsonl")
    p.add_argument("--prolog-rules-out", default="tmp/blocksworld_governor_rules_2026-04-16.pl")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    stamp = _stamp()

    # 1) Pull datasets / domain assets
    planetarium_path = hf_hub_download(
        repo_id="BatsResearch/planetarium",
        repo_type="dataset",
        filename="data/train-00000-of-00001.parquet",
    )
    domain_path = hf_hub_download(
        repo_id="divelab/Sys2Bench",
        repo_type="dataset",
        filename="blocksworld/generated_domain.pddl",
    )

    df = pd.read_parquet(planetarium_path)
    mask = (
        (df["domain"] == "blocksworld")
        & (df["num_objects"] <= int(args.max_objects))
        & (df["is_placeholder"] == 0)
        & (df["init_is_abstract"] == 0)
        & (df["goal_is_abstract"] == 0)
    )
    candidates = df[mask].sort_values(by=["num_objects", "id"]).head(int(args.sample_size))
    if candidates.empty:
        print("[blocksworld-lane] no candidates after filters", file=sys.stderr)
        return 2

    domain_text = Path(domain_path).read_text(encoding="utf-8", errors="replace")
    schemas = _parse_domain_actions(domain_text)
    prolog_text = _render_prolog_rules(schemas)

    prolog_out = Path(str(args.prolog_rules_out))
    if not prolog_out.is_absolute():
        prolog_out = (ROOT / prolog_out).resolve()
    prolog_out.parent.mkdir(parents=True, exist_ok=True)
    prolog_out.write_text(prolog_text, encoding="utf-8")

    # 2) Solve/replay symbolic lane
    case_rows: list[dict[str, Any]] = []
    solved = 0
    unsolved = 0
    planner_expansions = 0
    plan_lengths: list[int] = []

    for _, row in candidates.iterrows():
        row_id = int(row["id"])
        problem_pddl = str(row["problem_pddl"])
        parsed_problem = _parse_problem(problem_pddl)
        objects = list(parsed_problem["objects"])
        init_state = frozenset(parsed_problem["init_pos"])
        goal_pos = set(parsed_problem["goal_pos"])
        goal_neg = set(parsed_problem["goal_neg"])
        grounded = _ground_actions(schemas, objects)
        plan, expansions = _bfs_plan(
            init_state,
            goal_pos,
            goal_neg,
            grounded,
            max_depth=int(args.planner_depth),
        )
        planner_expansions += int(expansions)
        solved_flag = plan is not None
        if solved_flag:
            solved += 1
            plan_lengths.append(len(plan))
            replay_state = init_state
            # quick replay verification
            for action_str in plan:
                name = action_str.split("(", 1)[0]
                args_raw = action_str.split("(", 1)[1].rstrip(")")
                arg_tuple = tuple(x.strip() for x in args_raw.split(",") if x.strip())
                chosen = None
                for cand in grounded:
                    if cand[0] == name and cand[1] == arg_tuple:
                        chosen = cand
                        break
                if chosen is None:
                    replay_state = frozenset()
                    break
                _, _, _, _, add, delete = chosen
                replay_state = frozenset((replay_state - delete) | add)
            replay_ok = _state_satisfies(replay_state, goal_pos, goal_neg)
        else:
            unsolved += 1
            replay_ok = False

        case_rows.append(
            {
                "id": row_id,
                "name": str(row["name"]),
                "num_objects": int(row["num_objects"]),
                "natural_language": str(row["natural_language"]),
                "problem_pddl": problem_pddl,
                "objects": objects,
                "init_fact_count": len(init_state),
                "goal_fact_count": len(goal_pos) + len(goal_neg),
                "planner_solved": solved_flag,
                "plan_length": (len(plan) if isinstance(plan, list) else None),
                "plan": (plan if isinstance(plan, list) else []),
                "replay_verified": replay_ok,
                "planner_expansions": int(expansions),
                "expected_predicates_init": sorted({p for p, _ in init_state}),
                "expected_predicates_goal": sorted({p for p, _ in goal_pos.union(goal_neg)}),
            }
        )

    # 3) Optional Prethinker NL ingestion pilot
    prethinker_rows: list[dict[str, Any]] = []
    if bool(args.run_prethinker):
        pilot_cases = case_rows[: max(0, int(args.prethinker_cases))]
        pilot_dir = ROOT / "tmp" / "blocksworld_lane" / f"pilot_{stamp}"
        pilot_dir.mkdir(parents=True, exist_ok=True)

        for idx, case in enumerate(pilot_cases, start=1):
            story_file = pilot_dir / f"case_{idx:03d}_{case['id']}.txt"
            story_file.write_text(str(case["natural_language"]).strip() + "\n", encoding="utf-8")

            run_id = f"bw_planetarium_case_{case['id']}_{stamp}"
            pipeline_out = ROOT / "tmp" / f"{run_id}.pipeline.json"
            cmd = [
                sys.executable,
                str(RUN_STORY_RAW),
                "--story-file",
                str(story_file),
                "--scenario-name",
                run_id,
                "--pipeline-out",
                str(pipeline_out),
                "--backend",
                str(args.backend),
                "--base-url",
                str(args.base_url),
                "--model",
                str(args.model),
                "--prompt-file",
                str(args.prompt_file),
                "--context-length",
                str(int(args.context_length)),
                "--split-mode",
                str(args.prethinker_split_mode),
                "--write-corpus-on-fail",
            ]
            if str(args.predicate_registry).strip():
                cmd.extend(["--predicate-registry", str(args.predicate_registry)])
            if bool(args.strict_registry):
                cmd.append("--strict-registry")
            if str(args.type_schema).strip():
                cmd.extend(["--type-schema", str(args.type_schema)])
            proc = subprocess.run(cmd, cwd=str(ROOT), check=False)

            report: dict[str, Any] = {}
            if pipeline_out.exists():
                try:
                    report = json.loads(pipeline_out.read_text(encoding="utf-8"))
                except Exception:
                    report = {}
            turns = report.get("turns", [])
            turns = turns if isinstance(turns, list) else []
            parsed_predicates = sorted(_extract_predicates_from_parse([t for t in turns if isinstance(t, dict)]))
            expected_init = set(case.get("expected_predicates_init", []))
            expected_goal = set(case.get("expected_predicates_goal", []))
            parsed_set = set(parsed_predicates)
            init_hit = (len(expected_init.intersection(parsed_set)) / len(expected_init)) if expected_init else 0.0
            goal_hit = (len(expected_goal.intersection(parsed_set)) / len(expected_goal)) if expected_goal else 0.0

            prethinker_rows.append(
                {
                    "case_id": case["id"],
                    "run_id": run_id,
                    "exit_code": int(proc.returncode),
                    "pipeline_status": str(report.get("overall_status", "missing")),
                    "turns_total": int(report.get("turns_total", 0) or 0),
                    "parse_failures": int(report.get("turn_parse_failures", 0) or 0),
                    "apply_failures": int(report.get("turn_apply_failures", 0) or 0),
                    "clarification_requests": int(report.get("turns_clarification_requested", 0) or 0),
                    "parsed_predicates": parsed_predicates,
                    "expected_init_predicates": sorted(expected_init),
                    "expected_goal_predicates": sorted(expected_goal),
                    "init_predicate_hit_ratio": round(init_hit, 6),
                    "goal_predicate_hit_ratio": round(goal_hit, 6),
                    "pipeline_output": str(pipeline_out),
                    "story_file": str(story_file),
                }
            )

    # 4) Persist artifacts
    cases_jsonl = Path(str(args.cases_jsonl))
    if not cases_jsonl.is_absolute():
        cases_jsonl = (ROOT / cases_jsonl).resolve()
    cases_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with cases_jsonl.open("w", encoding="utf-8") as f:
        for case in case_rows:
            f.write(json.dumps(case, ensure_ascii=False) + "\n")

    parsed_pattern_counts: Counter[tuple[str, ...]] = Counter()
    zero_hit_case_ids: list[int] = []
    for row in prethinker_rows:
        pattern = tuple(row.get("parsed_predicates", []))
        parsed_pattern_counts[pattern] += 1
        init_hit = float(row.get("init_predicate_hit_ratio", 0.0) or 0.0)
        goal_hit = float(row.get("goal_predicate_hit_ratio", 0.0) or 0.0)
        if init_hit <= 0.0 and goal_hit <= 0.0:
            zero_hit_case_ids.append(int(row.get("case_id", 0) or 0))
    parsed_pattern_rows = [
        {"count": int(count), "parsed_predicates": list(pattern)}
        for pattern, count in parsed_pattern_counts.most_common()
    ]

    summary = {
        "generated_at_utc": _utc_iso(),
        "settings": {
            "sample_size": int(args.sample_size),
            "max_objects": int(args.max_objects),
            "planner_depth": int(args.planner_depth),
            "run_prethinker": bool(args.run_prethinker),
            "prethinker_cases": int(args.prethinker_cases),
            "backend": str(args.backend),
            "base_url": str(args.base_url),
            "model": str(args.model),
            "prompt_file": str(args.prompt_file),
            "context_length": int(args.context_length),
            "prethinker_split_mode": str(args.prethinker_split_mode),
            "predicate_registry": str(args.predicate_registry),
            "strict_registry": bool(args.strict_registry),
            "type_schema": str(args.type_schema),
            "max_zero_hit": int(args.max_zero_hit),
            "min_avg_init_hit": float(args.min_avg_init_hit),
            "min_avg_goal_hit": float(args.min_avg_goal_hit),
        },
        "sources": {
            "planetarium_train_parquet": str(planetarium_path),
            "sys2bench_domain_pddl": str(domain_path),
            "cases_jsonl": str(cases_jsonl),
            "prolog_rules": str(prolog_out),
        },
        "symbolic_harness": {
            "cases_total": len(case_rows),
            "solved_count": solved,
            "unsolved_count": unsolved,
            "solve_rate": round((float(solved) / float(len(case_rows))) if case_rows else 0.0, 6),
            "avg_plan_length": round(sum(plan_lengths) / len(plan_lengths), 6) if plan_lengths else 0.0,
            "avg_planner_expansions": round(float(planner_expansions) / float(len(case_rows)), 6) if case_rows else 0.0,
            "replay_verified_count": sum(1 for c in case_rows if bool(c.get("replay_verified"))),
        },
        "prethinker_pilot": {
            "cases_total": len(prethinker_rows),
            "pipeline_pass_count": sum(1 for r in prethinker_rows if str(r.get("pipeline_status", "")).lower() == "passed"),
            "avg_init_predicate_hit_ratio": round(
                sum(float(r.get("init_predicate_hit_ratio", 0.0) or 0.0) for r in prethinker_rows) / float(len(prethinker_rows)),
                6,
            )
            if prethinker_rows
            else 0.0,
            "avg_goal_predicate_hit_ratio": round(
                sum(float(r.get("goal_predicate_hit_ratio", 0.0) or 0.0) for r in prethinker_rows) / float(len(prethinker_rows)),
                6,
            )
            if prethinker_rows
            else 0.0,
            "avg_clarification_requests": round(
                sum(float(r.get("clarification_requests", 0.0) or 0.0) for r in prethinker_rows) / float(len(prethinker_rows)),
                6,
            )
            if prethinker_rows
            else 0.0,
            "zero_hit_case_count": int(len(zero_hit_case_ids)),
            "zero_hit_case_ids": sorted(zero_hit_case_ids),
            "parsed_pattern_counts": parsed_pattern_rows,
            "rows": prethinker_rows,
        },
    }

    zero_hit_count = int(summary["prethinker_pilot"]["zero_hit_case_count"])
    avg_init_hit = float(summary["prethinker_pilot"]["avg_init_predicate_hit_ratio"])
    avg_goal_hit = float(summary["prethinker_pilot"]["avg_goal_predicate_hit_ratio"])
    zero_hit_gate_enabled = int(args.max_zero_hit) >= 0
    zero_hit_gate_passed = (zero_hit_count <= int(args.max_zero_hit)) if zero_hit_gate_enabled else True
    avg_init_gate_enabled = float(args.min_avg_init_hit) >= 0.0
    avg_init_gate_passed = (
        avg_init_hit >= float(args.min_avg_init_hit)
        if avg_init_gate_enabled
        else True
    )
    avg_goal_gate_enabled = float(args.min_avg_goal_hit) >= 0.0
    avg_goal_gate_passed = (
        avg_goal_hit >= float(args.min_avg_goal_hit)
        if avg_goal_gate_enabled
        else True
    )
    summary["gates"] = {
        "zero_hit": {
            "enabled": zero_hit_gate_enabled,
            "threshold": int(args.max_zero_hit),
            "observed": zero_hit_count,
            "passed": bool(zero_hit_gate_passed),
            "reason": (
                ""
                if zero_hit_gate_passed
                else f"zero_hit_case_count={zero_hit_count} exceeded threshold={int(args.max_zero_hit)}"
            ),
        },
        "avg_init_hit": {
            "enabled": avg_init_gate_enabled,
            "threshold": float(args.min_avg_init_hit),
            "observed": round(avg_init_hit, 6),
            "passed": bool(avg_init_gate_passed),
            "reason": (
                ""
                if avg_init_gate_passed
                else (
                    f"avg_init_predicate_hit_ratio={avg_init_hit:.6f} "
                    f"fell below threshold={float(args.min_avg_init_hit):.6f}"
                )
            ),
        },
        "avg_goal_hit": {
            "enabled": avg_goal_gate_enabled,
            "threshold": float(args.min_avg_goal_hit),
            "observed": round(avg_goal_hit, 6),
            "passed": bool(avg_goal_gate_passed),
            "reason": (
                ""
                if avg_goal_gate_passed
                else (
                    f"avg_goal_predicate_hit_ratio={avg_goal_hit:.6f} "
                    f"fell below threshold={float(args.min_avg_goal_hit):.6f}"
                )
            ),
        },
    }

    summary_json = Path(str(args.summary_json))
    if not summary_json.is_absolute():
        summary_json = (ROOT / summary_json).resolve()
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 5) Markdown report
    md_lines: list[str] = []
    md_lines.append("# Blocksworld Lane (Pilot)")
    md_lines.append("")
    md_lines.append(f"- Generated UTC: `{summary['generated_at_utc']}`")
    md_lines.append(f"- Sample size: `{len(case_rows)}`")
    md_lines.append(f"- Model: `{args.model}`")
    md_lines.append("")
    md_lines.append("## Symbolic Harness (PDDL Import -> Replay)")
    md_lines.append("")
    sh = summary["symbolic_harness"]
    md_lines.append(f"- Cases total: `{sh['cases_total']}`")
    md_lines.append(f"- Solve rate: `{sh['solve_rate']}` (`{sh['solved_count']}/{sh['cases_total']}`)")
    md_lines.append(f"- Replay verified count: `{sh['replay_verified_count']}`")
    md_lines.append(f"- Avg plan length: `{sh['avg_plan_length']}`")
    md_lines.append(f"- Avg planner expansions: `{sh['avg_planner_expansions']}`")
    md_lines.append("")
    md_lines.append("## Prethinker Ingestion Pilot")
    md_lines.append("")
    ph = summary["prethinker_pilot"]
    md_lines.append(f"- Cases run: `{ph['cases_total']}`")
    md_lines.append(f"- Pipeline pass count: `{ph['pipeline_pass_count']}`")
    md_lines.append(f"- Avg init predicate hit ratio: `{ph['avg_init_predicate_hit_ratio']}`")
    md_lines.append(f"- Avg goal predicate hit ratio: `{ph['avg_goal_predicate_hit_ratio']}`")
    md_lines.append(f"- Avg clarification requests: `{ph['avg_clarification_requests']}`")
    md_lines.append(f"- Zero-hit cases (init=0 and goal=0): `{ph['zero_hit_case_count']}`")
    gate = summary.get("gates", {}).get("zero_hit", {})
    if isinstance(gate, dict) and bool(gate.get("enabled")):
        md_lines.append(
            f"- Zero-hit gate: `{'pass' if bool(gate.get('passed')) else 'FAIL'}` (observed `{int(gate.get('observed', 0) or 0)}` <= threshold `{int(gate.get('threshold', 0) or 0)}`)"
        )
    init_gate = summary.get("gates", {}).get("avg_init_hit", {})
    if isinstance(init_gate, dict) and bool(init_gate.get("enabled")):
        md_lines.append(
            f"- Avg init hit gate: `{'pass' if bool(init_gate.get('passed')) else 'FAIL'}` "
            f"(observed `{float(init_gate.get('observed', 0.0) or 0.0):.6f}` >= threshold `{float(init_gate.get('threshold', 0.0) or 0.0):.6f}`)"
        )
    goal_gate = summary.get("gates", {}).get("avg_goal_hit", {})
    if isinstance(goal_gate, dict) and bool(goal_gate.get("enabled")):
        md_lines.append(
            f"- Avg goal hit gate: `{'pass' if bool(goal_gate.get('passed')) else 'FAIL'}` "
            f"(observed `{float(goal_gate.get('observed', 0.0) or 0.0):.6f}` >= threshold `{float(goal_gate.get('threshold', 0.0) or 0.0):.6f}`)"
        )
    if int(ph.get("zero_hit_case_count", 0) or 0) > 0:
        zero_ids = ", ".join(str(x) for x in (ph.get("zero_hit_case_ids", []) or []))
        md_lines.append(f"- Zero-hit case IDs: `{zero_ids}`")
    md_lines.append("")
    if prethinker_rows:
        md_lines.append("| Case | Pipeline | Init Hit | Goal Hit | Clarifications | Parsed Predicates |")
        md_lines.append("|---|---:|---:|---:|---:|---|")
        for row in prethinker_rows:
            preds = ", ".join(row.get("parsed_predicates", [])[:8])
            md_lines.append(
                _md_table_row(
                    [
                        str(row.get("case_id", "")),
                        str(row.get("pipeline_status", "")),
                        f"{float(row.get('init_predicate_hit_ratio', 0.0) or 0.0):.3f}",
                        f"{float(row.get('goal_predicate_hit_ratio', 0.0) or 0.0):.3f}",
                        str(int(row.get("clarification_requests", 0) or 0)),
                        preds,
                    ]
                )
            )
        md_lines.append("")
        md_lines.append("### Parsed Predicate Patterns")
        md_lines.append("")
        md_lines.append("| Count | Parsed Predicates |")
        md_lines.append("|---:|---|")
        for pattern_row in ph.get("parsed_pattern_counts", []):
            if not isinstance(pattern_row, dict):
                continue
            count = int(pattern_row.get("count", 0) or 0)
            preds = pattern_row.get("parsed_predicates", [])
            if not isinstance(preds, list):
                preds = []
            pattern_text = ", ".join(str(x) for x in preds) if preds else "(none)"
            md_lines.append(_md_table_row([str(count), pattern_text]))
        md_lines.append("")
    md_lines.append("## Artifacts")
    md_lines.append("")
    md_lines.append(f"- Summary JSON: `{summary_json}`")
    md_lines.append(f"- Case inventory: `{cases_jsonl}`")
    md_lines.append(f"- Generated governor Prolog scaffold: `{prolog_out}`")
    md_lines.append("")

    summary_md = Path(str(args.summary_md))
    if not summary_md.is_absolute():
        summary_md = (ROOT / summary_md).resolve()
    summary_md.parent.mkdir(parents=True, exist_ok=True)
    summary_md.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")

    print(f"[blocksworld-lane] summary_json={summary_json}")
    print(f"[blocksworld-lane] summary_md={summary_md}")
    print(f"[blocksworld-lane] cases_jsonl={cases_jsonl}")
    print(f"[blocksworld-lane] prolog_rules={prolog_out}")
    if zero_hit_gate_enabled and not zero_hit_gate_passed:
        print(
            f"[blocksworld-lane] FAIL gate zero-hit: observed={zero_hit_count} threshold={int(args.max_zero_hit)}",
            file=sys.stderr,
        )
        return 10
    if avg_init_gate_enabled and not avg_init_gate_passed:
        print(
            "[blocksworld-lane] FAIL gate avg-init-hit: "
            f"observed={avg_init_hit:.6f} threshold={float(args.min_avg_init_hit):.6f}",
            file=sys.stderr,
        )
        return 11
    if avg_goal_gate_enabled and not avg_goal_gate_passed:
        print(
            "[blocksworld-lane] FAIL gate avg-goal-hit: "
            f"observed={avg_goal_hit:.6f} threshold={float(args.min_avg_goal_hit):.6f}",
            file=sys.stderr,
        )
        return 12
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
