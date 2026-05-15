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

    observations.extend(_source_record_table_transition_observations(parsed))
    return observations


def _source_record_table_transition_observations(parsed: list[Fact]) -> list[dict[str, Any]]:
    sections: dict[str, str] = {}
    fields_by_row: dict[str, dict[str, str]] = defaultdict(dict)

    for predicate, args in parsed:
        if predicate == "source_record_section" and len(args) >= 2:
            sections[args[0]] = args[1]
        elif predicate == "source_record_field" and len(args) >= 3:
            row, field, value = args[:3]
            fields_by_row[row][field] = value

    if not fields_by_row:
        return []

    rows: list[dict[str, str]] = []
    for row, fields in fields_by_row.items():
        item = {"row": row, "section": sections.get(row, "")}
        item.update(fields)
        rows.append(item)

    observations: list[dict[str, Any]] = []
    for key_field in ("zone", "record", "document", "item", "subject"):
        value_pairs = (("order", "new_order"), ("status", "new_status"), ("state", "new_state"), ("value", "new_value"))
        old_rows = [row for row in rows if key_field in row]
        for old_field, new_field in value_pairs:
            before = [row for row in old_rows if old_field in row]
            after = [row for row in old_rows if new_field in row]
            if not before or not after:
                continue
            before_by_key = _first_by_key(before, key_field)
            after_by_key = _first_by_key(after, key_field)
            for key in sorted(set(before_by_key) & set(after_by_key)):
                old_row = before_by_key[key]
                new_row = after_by_key[key]
                old_value = _normalize_transition_value(old_row[old_field])
                new_value = _normalize_transition_value(new_row[new_field])
                if not old_value or not new_value:
                    continue
                observations.append(
                    {
                        "kind": "source_record_value_transition",
                        "subject": key,
                        "field": old_field,
                        "old_value": old_value,
                        "new_value": new_value,
                        "predecessor": old_row["row"],
                        "successor": new_row["row"],
                        "predecessor_section": old_row.get("section", ""),
                        "successor_section": new_row.get("section", ""),
                        "source_predicate": "source_record_field",
                    }
                )
            for key in sorted(set(after_by_key) - set(before_by_key)):
                new_row = after_by_key[key]
                new_value = _normalize_transition_value(new_row[new_field])
                if not new_value:
                    continue
                observations.append(
                    {
                        "kind": "source_record_subject_added",
                        "subject": key,
                        "field": old_field,
                        "new_value": new_value,
                        "successor": new_row["row"],
                        "successor_section": new_row.get("section", ""),
                        "source_predicate": "source_record_field",
                    }
                )

    return _dedupe_observations(observations)


def _first_by_key(rows: list[dict[str, str]], key_field: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get(key_field, "")
        if key and key not in result:
            result[key] = row
    return result


def _normalize_transition_value(value: str) -> str:
    item = str(value or "").strip()
    for prefix in ("downgraded_to_", "upgraded_to_", "changed_to_", "set_to_"):
        if item.startswith(prefix):
            item = item[len(prefix) :]
            break
    for suffix in ("_unchanged", "_current"):
        if item.endswith(suffix):
            item = item[: -len(suffix)]
            break
    return item


def _dedupe_observations(observations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for observation in observations:
        key = repr(sorted(observation.items()))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(observation)
    return deduped


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
