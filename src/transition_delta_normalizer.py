"""Deterministic transition/delta observation normalizer.

This module is deliberately audit-only for now. It reads already-admitted
compile facts and reports canonical transition/delta observations without
changing the runtime KB, compile prompts, or QA selection.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


Fact = tuple[str, tuple[str, ...]]


def parse_fact(clause: str) -> Fact | None:
    text = str(clause or "").strip()
    if text.endswith("."):
        text = text[:-1].strip()
    match = re.fullmatch(r"([a-z][A-Za-z0-9_]*)\((.*)\)", text)
    if not match:
        return None
    predicate = match.group(1)
    args = _split_args(match.group(2))
    if args is None:
        return None
    return predicate, tuple(args)


def normalize_transition_delta_facts(facts: list[str]) -> list[dict[str, Any]]:
    parsed = [item for clause in facts if (item := parse_fact(clause))]
    observations: list[dict[str, Any]] = []

    before_snapshots: dict[str, list[tuple[str, str]]] = defaultdict(list)
    after_snapshots: dict[str, list[tuple[str, str]]] = defaultdict(list)
    absent_by_field: dict[str, list[str]] = defaultdict(list)
    transition_timestamps = {
        args[0]: args[1]
        for predicate, args in parsed
        if predicate == "transition_timestamp" and len(args) >= 2
    }
    transition_reasons = {
        args[0]: args[1]
        for predicate, args in parsed
        if predicate == "transition_reason" and len(args) >= 2
    }

    for predicate, args in parsed:
        if predicate == "supersedes" and len(args) == 2:
            successor, predecessor = args
            observations.append(
                {
                    "kind": "supersession",
                    "successor": successor,
                    "predecessor": predecessor,
                    "source_predicate": predicate,
                }
            )
        elif predicate == "form_replaced" and len(args) >= 2:
            predecessor, successor = args[:2]
            observation = {
                "kind": "supersession",
                "successor": successor,
                "predecessor": predecessor,
                "source_predicate": predicate,
            }
            if len(args) >= 3:
                observation["source"] = args[2]
            observations.append(observation)
        elif predicate == "transition_occurred" and len(args) >= 4:
            subject, old_value, new_value, event = args[:4]
            observation = {
                "kind": "status_transition",
                "subject": subject,
                "old_value": old_value,
                "new_value": new_value,
                "event": event,
                "source_predicate": predicate,
            }
            if event in transition_timestamps:
                observation["timestamp"] = transition_timestamps[event]
            if subject in transition_reasons:
                observation["reason"] = transition_reasons[subject]
            observations.append(observation)
        elif predicate == "policy_field_changed" and len(args) == 4:
            field, old_value, new_value, subject = args
            observations.append(
                {
                    "kind": "value_transition",
                    "subject": subject,
                    "field": field,
                    "old_value": old_value,
                    "new_value": new_value,
                    "source_predicate": predicate,
                }
            )
        elif predicate == "policy_field_added" and len(args) >= 2:
            observation = {
                "kind": "field_added",
                "field": args[0],
                "subject": args[1],
                "source_predicate": predicate,
            }
            if len(args) >= 3:
                observation["new_value"] = args[2]
            observations.append(observation)
        elif predicate == "policy_field_removed" and len(args) >= 3:
            field, predecessor, successor = args[:3]
            observations.append(
                {
                    "kind": "field_removed",
                    "field": field,
                    "predecessor": predecessor,
                    "successor": successor,
                    "source_predicate": predicate,
                }
            )
        elif predicate == "field_unchanged" and len(args) >= 3:
            value, field, source = args[:3]
            observations.append(
                {
                    "kind": "field_unchanged",
                    "field": field,
                    "value": value,
                    "source": source,
                    "source_predicate": predicate,
                }
            )
        elif predicate == "field_value_snapshot" and len(args) == 4:
            obj, field, value, phase = args
            if phase == "before":
                before_snapshots[field].append((obj, value))
            elif phase == "after":
                after_snapshots[field].append((obj, value))
        elif predicate == "field_absent" and len(args) == 2:
            obj, field = args
            absent_by_field[field].append(obj)

    for field in sorted(set(before_snapshots) & set(after_snapshots)):
        for predecessor, old_value in before_snapshots[field]:
            for successor, new_value in after_snapshots[field]:
                observations.append(
                    {
                        "kind": "value_transition",
                        "field": field,
                        "old_value": old_value,
                        "new_value": new_value,
                        "predecessor": predecessor,
                        "successor": successor,
                        "source_predicate": "field_value_snapshot",
                    }
                )

    for field, objects in sorted(absent_by_field.items()):
        unique_objects = sorted(set(objects))
        if len(unique_objects) >= 2:
            observations.append(
                {
                    "kind": "absence_persistence",
                    "field": field,
                    "objects": unique_objects,
                    "source_predicate": "field_absent",
                }
            )

    return observations


def summarize_observations(observations: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for observation in observations:
        kind = str(observation.get("kind") or "unknown")
        counts[kind] = counts.get(kind, 0) + 1
    return {
        "observation_count": len(observations),
        "kind_counts": dict(sorted(counts.items())),
    }


def _split_args(text: str) -> tuple[str, ...] | None:
    args: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
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
            depth -= 1
            if depth < 0:
                return None
            current.append(char)
            continue
        if char == "," and depth == 0:
            args.append(_clean_arg("".join(current)))
            current = []
            continue
        current.append(char)
    if quote or depth != 0:
        return None
    if current or text.strip():
        args.append(_clean_arg("".join(current)))
    return tuple(args)


def _clean_arg(value: str) -> str:
    item = str(value or "").strip()
    if len(item) >= 2 and item[0] == item[-1] and item[0] in {"'", '"'}:
        return item[1:-1]
    return item
