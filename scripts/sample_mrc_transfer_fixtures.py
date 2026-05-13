#!/usr/bin/env python3
"""Sample external MRC records into Prethinker incoming fixture shape.

The sampler is intentionally an intake tool, not architecture. It writes small
answer-isolated fixtures under tmp/ so new datasets can pressure the compiler
without turning dataset vocabulary into substrate.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT_ROOT = REPO_ROOT / "tmp" / "mrc_transfer_samples"


def main() -> int:
    args = _parse_args()
    records = _load_records(args)
    written = write_race_fixtures(
        records=records,
        out_root=args.out_root,
        dataset_name=args.dataset,
        config_name=args.config,
        split=args.split,
        limit=args.limit,
        offset=args.offset,
    )
    for path in written:
        print(path)
    print(f"wrote {len(written)} fixture(s) to {args.out_root}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Sample RACE-style machine-reading-comprehension records into "
            "Prethinker incoming fixtures with answers isolated in oracle.jsonl."
        )
    )
    parser.add_argument("--dataset", default="ehovy/race", help="HuggingFace dataset name.")
    parser.add_argument("--config", default="high", help="HuggingFace config/subset name.")
    parser.add_argument("--split", default="validation", help="HuggingFace split to sample.")
    parser.add_argument("--limit", type=int, default=5, help="Number of passages to write.")
    parser.add_argument("--offset", type=int, default=0, help="Starting record offset.")
    parser.add_argument(
        "--sample-strategy",
        choices=["first", "even", "random"],
        default="first",
        help="How to choose passage-level records after grouping.",
    )
    parser.add_argument("--seed", type=int, default=13, help="Seed for --sample-strategy random.")
    parser.add_argument(
        "--out-root",
        type=Path,
        default=DEFAULT_OUT_ROOT,
        help="Output directory for incoming fixture folders.",
    )
    parser.add_argument(
        "--local-jsonl",
        type=Path,
        help="Read RACE-shaped records from local JSONL instead of HuggingFace.",
    )
    return parser.parse_args()


def _load_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.limit < 1:
        raise SystemExit("--limit must be positive")
    if args.offset < 0:
        raise SystemExit("--offset must be zero or positive")
    if args.local_jsonl:
        records = _coerce_race_records(_load_local_jsonl(args.local_jsonl))
        return _select_records(records, limit=args.limit, offset=args.offset, strategy=args.sample_strategy, seed=args.seed)

    load_dataset = _import_huggingface_load_dataset()
    dataset = load_dataset(args.dataset, args.config, split=args.split)
    records = _coerce_race_records(dict(record) for record in dataset)
    return _select_records(records, limit=args.limit, offset=args.offset, strategy=args.sample_strategy, seed=args.seed)


def _select_records(
    records: Sequence[dict[str, Any]],
    *,
    limit: int,
    offset: int,
    strategy: str,
    seed: int,
) -> list[dict[str, Any]]:
    candidates = list(records[offset:])
    if strategy == "first" or limit >= len(candidates):
        return candidates[:limit]
    if strategy == "even":
        if limit == 1:
            return [candidates[0]]
        last = len(candidates) - 1
        indexes = [round(position * last / (limit - 1)) for position in range(limit)]
        return [candidates[index] for index in indexes]
    if strategy == "random":
        rng = random.Random(seed)
        indexes = sorted(rng.sample(range(len(candidates)), limit))
        return [candidates[index] for index in indexes]
    raise ValueError(f"unknown sample strategy: {strategy}")


def _import_huggingface_load_dataset() -> Any:
    """Import HuggingFace datasets even though this repo has a datasets/ dir."""

    removed_entries: list[str] = []
    for entry in list(sys.path):
        candidate = Path(entry or os.getcwd()).resolve()
        if candidate == REPO_ROOT:
            sys.path.remove(entry)
            removed_entries.append(entry)

    existing = sys.modules.get("datasets")
    if existing is not None and not hasattr(existing, "load_dataset"):
        sys.modules.pop("datasets", None)

    try:
        import datasets as hf_datasets  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit(
            "HuggingFace datasets is not installed. Install it in this environment "
            "or pass --local-jsonl with RACE-shaped records."
        ) from exc
    finally:
        for entry in reversed(removed_entries):
            sys.path.insert(0, entry)

    load_dataset = getattr(hf_datasets, "load_dataset", None)
    if load_dataset is None:
        location = getattr(hf_datasets, "__file__", None) or getattr(hf_datasets, "__path__", None)
        raise SystemExit(
            "Imported a module named 'datasets' without load_dataset "
            f"({location}). Pass --local-jsonl or install/use HuggingFace datasets."
        )
    return load_dataset


def _load_local_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))
    return records


def _coerce_race_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return passage-level records from either RACE schema variant."""

    prepared = [dict(record) for record in records]
    if not prepared:
        return []

    if "questions" in prepared[0] and "answers" in prepared[0]:
        return prepared

    if not {"article", "question", "options", "answer"} <= set(prepared[0]):
        return prepared

    grouped: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(prepared):
        article = str(record.get("article") or "")
        example_id = str(record.get("example_id") or record.get("id") or f"record_{index:05d}")
        key = f"{example_id}\n{article}"
        if key not in grouped:
            grouped[key] = {
                "article": article,
                "questions": [],
                "options": [],
                "answers": [],
                "example_id": example_id,
            }
        grouped[key]["questions"].append(record.get("question"))
        grouped[key]["options"].append(record.get("options"))
        grouped[key]["answers"].append(record.get("answer"))
    return list(grouped.values())


def write_race_fixtures(
    *,
    records: Iterable[dict[str, Any]],
    out_root: Path,
    dataset_name: str,
    config_name: str,
    split: str,
    limit: int,
    offset: int = 0,
) -> list[Path]:
    out_root.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for local_index, record in enumerate(records):
        if len(written) >= limit:
            break
        global_index = offset + local_index
        fixture_name = _fixture_name(
            dataset_name=dataset_name,
            config_name=config_name,
            split=split,
            index=global_index,
            example_id=str(record.get("example_id") or record.get("id") or ""),
        )
        fixture_dir = out_root / fixture_name
        _write_race_fixture(
            record=record,
            fixture_dir=fixture_dir,
            dataset_name=dataset_name,
            config_name=config_name,
            split=split,
            fixture_name=fixture_name,
            source_index=global_index,
        )
        written.append(fixture_dir)
    return written


def _write_race_fixture(
    *,
    record: dict[str, Any],
    fixture_dir: Path,
    dataset_name: str,
    config_name: str,
    split: str,
    fixture_name: str,
    source_index: int,
) -> None:
    article = _required_text(record, "article")
    questions = _required_sequence(record, "questions")
    options = _required_sequence(record, "options")
    answers = _required_sequence(record, "answers")
    if not (len(questions) == len(options) == len(answers)):
        raise ValueError(
            f"{fixture_name}: questions/options/answers length mismatch "
            f"({len(questions)}/{len(options)}/{len(answers)})"
        )

    fixture_dir.mkdir(parents=True, exist_ok=True)
    example_id = str(record.get("example_id") or record.get("id") or source_index)

    (fixture_dir / "source.md").write_text(
        "\n".join(
            [
                "# External MRC Passage",
                "",
                f"- Dataset: `{dataset_name}`",
                f"- Config: `{config_name}`",
                f"- Split: `{split}`",
                f"- Example id: `{example_id}`",
                "",
                "## Passage",
                "",
                article.strip(),
                "",
            ]
        ),
        encoding="utf-8",
    )

    qa_lines = [
        f"# {fixture_name} QA",
        "",
        "Questions only. Multiple-choice options are shown, but the answer key is isolated in `oracle.jsonl`.",
        "",
    ]
    oracle_rows: list[dict[str, Any]] = []
    for index, question in enumerate(questions, start=1):
        qid = f"q{index:03d}"
        option_values = _string_options(options[index - 1], fixture_name=fixture_name, qid=qid)
        answer_label, answer_text = _resolve_answer(
            answers[index - 1],
            option_values=option_values,
            fixture_name=fixture_name,
            qid=qid,
        )
        qa_lines.append(f"{index}. {str(question).strip()}")
        for option_index, option_text in enumerate(option_values):
            qa_lines.append(f"   {_option_label(option_index)}. {option_text}")
        qa_lines.append("")
        oracle_rows.append(
            {
                "id": qid,
                "source_id": f"{example_id}:{qid}",
                "category": "external_mrc_multiple_choice",
                "reference_answer": f"{answer_label}. {answer_text}",
                "answer": f"{answer_label}. {answer_text}",
                "answer_key": answer_label,
            }
        )

    (fixture_dir / "qa.md").write_text("\n".join(qa_lines), encoding="utf-8")
    (fixture_dir / "oracle.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in oracle_rows) + "\n",
        encoding="utf-8",
    )
    (fixture_dir / "fixture_notes.md").write_text(
        "\n".join(
            [
                "# Fixture Notes",
                "",
                "- External MRC transfer sample; do not treat dataset wording as architecture.",
                "- `qa.md` contains questions and option surfaces only.",
                "- `oracle.jsonl` contains the answer key for scoring after compilation/QA.",
                "- Samples are generated under `tmp/` by default; git remains the archive for code, not dataset bulk storage.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _required_text(record: dict[str, Any], key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"record missing non-empty {key!r}")
    return value


def _required_sequence(record: dict[str, Any], key: str) -> Sequence[Any]:
    value = record.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"record missing sequence {key!r}")
    return value


def _string_options(raw_options: Any, *, fixture_name: str, qid: str) -> list[str]:
    if not isinstance(raw_options, Sequence) or isinstance(raw_options, (str, bytes)):
        raise ValueError(f"{fixture_name}:{qid}: options must be a sequence")
    options = [str(option).strip() for option in raw_options if str(option).strip()]
    if len(options) < 2:
        raise ValueError(f"{fixture_name}:{qid}: expected at least two options")
    return options


def _resolve_answer(
    raw_answer: Any,
    *,
    option_values: Sequence[str],
    fixture_name: str,
    qid: str,
) -> tuple[str, str]:
    answer_text = str(raw_answer).strip()
    if not answer_text:
        raise ValueError(f"{fixture_name}:{qid}: blank answer")

    letter_index = ord(answer_text.upper()) - ord("A") if len(answer_text) == 1 else -1
    if 0 <= letter_index < len(option_values):
        return _option_label(letter_index), option_values[letter_index]

    if answer_text.isdigit():
        numeric = int(answer_text)
        if 0 <= numeric < len(option_values):
            return _option_label(numeric), option_values[numeric]
        if 1 <= numeric <= len(option_values):
            index = numeric - 1
            return _option_label(index), option_values[index]

    for index, option in enumerate(option_values):
        if option.casefold() == answer_text.casefold():
            return _option_label(index), option

    raise ValueError(f"{fixture_name}:{qid}: answer {raw_answer!r} does not match options")


def _option_label(index: int) -> str:
    return chr(ord("A") + index)


def _fixture_name(
    *,
    dataset_name: str,
    config_name: str,
    split: str,
    index: int,
    example_id: str,
) -> str:
    dataset_slug = _slug(dataset_name.split("/")[-1])
    config_slug = _slug(config_name)
    split_slug = _slug(split)
    suffix = _slug(example_id)[-24:] if example_id else f"{index:05d}"
    return f"{dataset_slug}_{config_slug}_{split_slug}_{index:05d}_{suffix}"


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    return slug or "sample"


if __name__ == "__main__":
    raise SystemExit(main())
