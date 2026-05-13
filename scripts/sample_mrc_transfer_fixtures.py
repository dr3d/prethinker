#!/usr/bin/env python3
"""Sample external MRC records into Prethinker incoming fixture shape.

The sampler is intentionally an intake tool, not architecture. It writes small
answer-isolated fixtures under tmp/ so new datasets can pressure the compiler
without turning dataset vocabulary into substrate.
"""

from __future__ import annotations

import argparse
import csv
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
    config_name = "default" if bool(args.no_config) else str(args.config)
    if args.source_format == "squad":
        written = write_squad_fixtures(
            records=records,
            out_root=args.out_root,
            dataset_name=args.dataset,
            config_name=config_name,
            split=args.split,
            limit=args.limit,
            offset=args.offset,
        )
    elif args.source_format == "cuad":
        written = write_cuad_fixtures(
            records=records,
            out_root=args.out_root,
            dataset_name=args.dataset,
            config_name=config_name,
            split=args.split,
            limit=args.limit,
            offset=args.offset,
        )
    elif args.source_format == "maud":
        written = write_maud_fixtures(
            records=records,
            out_root=args.out_root,
            dataset_name=args.dataset,
            config_name=config_name,
            split=args.split,
            limit=args.limit,
            offset=args.offset,
        )
    else:
        written = write_race_fixtures(
            records=records,
            out_root=args.out_root,
            dataset_name=args.dataset,
            config_name=config_name,
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
            "Sample RACE-, SQuAD-, CUAD-, or MAUD-style machine-reading-comprehension records into "
            "Prethinker incoming fixtures with answers isolated in oracle.jsonl."
        )
    )
    parser.add_argument(
        "--source-format",
        choices=["race", "squad", "cuad", "maud"],
        default="race",
        help="Input dataset schema to normalize.",
    )
    parser.add_argument("--dataset", default="ehovy/race", help="HuggingFace dataset name.")
    parser.add_argument("--config", default="high", help="HuggingFace config/subset name.")
    parser.add_argument("--no-config", action="store_true", help="Call HuggingFace load_dataset without a config.")
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
    parser.add_argument(
        "--local-csv",
        type=Path,
        help="Read MAUD CSV rows from disk instead of HuggingFace.",
    )
    parser.add_argument(
        "--local-json",
        type=Path,
        help="Read CUAD SQuAD-style JSON from disk instead of HuggingFace.",
    )
    parser.add_argument(
        "--max-questions-per-record",
        type=int,
        default=4,
        help="Maximum extractive questions to keep per CUAD contract sample.",
    )
    parser.add_argument(
        "--cuad-answer-window",
        type=int,
        default=1400,
        help="Characters of source context to keep on each side of a CUAD answer span.",
    )
    parser.add_argument(
        "--cuad-max-answer-chars",
        type=int,
        default=800,
        help="Skip CUAD answer spans longer than this unless no shorter answer is available.",
    )
    parser.add_argument(
        "--maud-max-text-chars",
        type=int,
        default=5000,
        help="Maximum MAUD excerpt characters per sampled row before bounded trimming.",
    )
    parser.add_argument(
        "--maud-max-answer-chars",
        type=int,
        default=400,
        help="Skip MAUD answer values longer than this unless no shorter answer is available.",
    )
    parser.add_argument(
        "--maud-data-type",
        default="main",
        help="MAUD data_type to prefer, or 'any'.",
    )
    return parser.parse_args()


def _load_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.limit < 1:
        raise SystemExit("--limit must be positive")
    if args.offset < 0:
        raise SystemExit("--offset must be zero or positive")
    if args.source_format == "cuad":
        records = _load_cuad_records(args)
        return _select_records(records, limit=args.limit, offset=args.offset, strategy=args.sample_strategy, seed=args.seed)
    if args.source_format == "maud":
        records = _load_maud_records(args)
        return _select_records(records, limit=args.limit, offset=args.offset, strategy=args.sample_strategy, seed=args.seed)
    if args.local_jsonl:
        raw_records = _load_local_jsonl(args.local_jsonl)
        records = _coerce_squad_records(raw_records) if args.source_format == "squad" else _coerce_race_records(raw_records)
        return _select_records(records, limit=args.limit, offset=args.offset, strategy=args.sample_strategy, seed=args.seed)

    load_dataset = _import_huggingface_load_dataset()
    config = "" if bool(args.no_config) else str(args.config)
    dataset = load_dataset(args.dataset, config, split=args.split) if config.strip() else load_dataset(args.dataset, split=args.split)
    records = _coerce_squad_records(dict(record) for record in dataset) if args.source_format == "squad" else _coerce_race_records(dict(record) for record in dataset)
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


def _load_cuad_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    if int(args.max_questions_per_record) < 1:
        raise SystemExit("--max-questions-per-record must be positive")
    if int(args.cuad_answer_window) < 100:
        raise SystemExit("--cuad-answer-window must be at least 100")

    if args.local_json:
        payload = json.loads(args.local_json.read_text(encoding="utf-8-sig"))
    else:
        payload = _download_cuad_json(dataset_name=str(args.dataset))
    return _coerce_cuad_records(
        payload,
        max_questions_per_record=int(args.max_questions_per_record),
        answer_window=int(args.cuad_answer_window),
        max_answer_chars=int(args.cuad_max_answer_chars),
    )


def _load_maud_records(args: argparse.Namespace) -> list[dict[str, Any]]:
    if int(args.max_questions_per_record) < 1:
        raise SystemExit("--max-questions-per-record must be positive")
    if int(args.maud_max_text_chars) < 200:
        raise SystemExit("--maud-max-text-chars must be at least 200")
    if args.local_csv:
        rows = _load_local_csv(args.local_csv)
    else:
        rows = _download_maud_csv(dataset_name=str(args.dataset), split=str(args.split))
    return _coerce_maud_records(
        rows,
        max_questions_per_record=int(args.max_questions_per_record),
        max_text_chars=int(args.maud_max_text_chars),
        max_answer_chars=int(args.maud_max_answer_chars),
        data_type=str(args.maud_data_type),
    )


def _download_maud_csv(*, dataset_name: str, split: str) -> list[dict[str, Any]]:
    split_name = split if split in {"train", "dev", "test"} else "dev"
    path = _hf_download_file(
        dataset_name=dataset_name,
        filename=f"MAUD_v1/MAUD_{split_name}.csv",
    )
    return _load_local_csv(path)


def _hf_download_file(*, dataset_name: str, filename: str) -> Path:
    removed_entries: list[str] = []
    for entry in list(sys.path):
        candidate = Path(entry or os.getcwd()).resolve()
        if candidate == REPO_ROOT:
            sys.path.remove(entry)
            removed_entries.append(entry)

    try:
        from huggingface_hub import hf_hub_download  # type: ignore[import-not-found]
    except ImportError as exc:
        raise SystemExit(
            "huggingface_hub is not installed. Install it or pass a local dataset file."
        ) from exc
    finally:
        for entry in reversed(removed_entries):
            sys.path.insert(0, entry)

    return Path(hf_hub_download(repo_id=dataset_name, repo_type="dataset", filename=filename))


def _download_cuad_json(*, dataset_name: str) -> dict[str, Any]:
    path = _hf_download_file(dataset_name=dataset_name, filename="CUAD_v1/CUAD_v1.json")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _load_local_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _coerce_cuad_records(
    payload: dict[str, Any],
    *,
    max_questions_per_record: int,
    answer_window: int,
    max_answer_chars: int,
) -> list[dict[str, Any]]:
    """Return contract-level excerpt records from CUAD SQuAD-style JSON."""

    records: list[dict[str, Any]] = []
    for doc_index, doc in enumerate(payload.get("data", [])):
        if not isinstance(doc, dict):
            continue
        title = str(doc.get("title") or f"contract_{doc_index:05d}")
        paragraph = _first_cuad_paragraph(doc)
        if paragraph is None:
            continue
        context = str(paragraph.get("context") or "")
        if not context.strip():
            continue
        qas = paragraph.get("qas") if isinstance(paragraph.get("qas"), list) else []
        selected = _select_cuad_qas(
            qas,
            max_questions=max_questions_per_record,
            max_answer_chars=max_answer_chars,
        )
        if not selected:
            continue
        windows = _cuad_windows_for_qas(selected, context=context, answer_window=answer_window)
        records.append(
            {
                "context": _render_cuad_excerpt_context(title=title, context=context, windows=windows),
                "questions": [_cuad_question_text(str(item.get("question") or "")) for item in selected],
                "answers": [_cuad_reference_answer(item) for item in selected],
                "question_ids": [
                    str(item.get("id") or f"{doc_index:05d}_{index:03d}")
                    for index, item in enumerate(selected)
                ],
                "categories": [_cuad_question_category(str(item.get("question") or "")) for item in selected],
                "title": title,
                "example_id": title,
                "source_span_count": len(windows),
            }
        )
    return records


def _first_cuad_paragraph(doc: dict[str, Any]) -> dict[str, Any] | None:
    paragraphs = doc.get("paragraphs")
    if not isinstance(paragraphs, list):
        return None
    for paragraph in paragraphs:
        if isinstance(paragraph, dict) and str(paragraph.get("context") or "").strip():
            return paragraph
    return None


def _select_cuad_qas(
    qas: Sequence[Any],
    *,
    max_questions: int,
    max_answer_chars: int,
) -> list[dict[str, Any]]:
    eligible: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    seen_categories: set[str] = set()
    for item in qas:
        if not isinstance(item, dict) or bool(item.get("is_impossible")):
            continue
        if not _cuad_answers(item):
            continue
        reference = _cuad_reference_answer(item)
        if not reference:
            continue
        category = _cuad_question_category(str(item.get("question") or "")).casefold()
        row = dict(item)
        if len(reference) <= max_answer_chars and category not in seen_categories:
            eligible.append(row)
            seen_categories.add(category)
        else:
            fallback.append(row)
    selected = eligible[:max_questions]
    if len(selected) < max_questions:
        selected.extend(fallback[: max_questions - len(selected)])
    return selected[:max_questions]


def _cuad_answers(item: dict[str, Any]) -> list[dict[str, Any]]:
    answers = item.get("answers")
    if not isinstance(answers, list):
        return []
    cleaned: list[dict[str, Any]] = []
    seen: set[str] = set()
    for answer in answers:
        if not isinstance(answer, dict):
            continue
        text = str(answer.get("text") or "").strip()
        if not text or text.casefold() in seen:
            continue
        try:
            start = int(answer.get("answer_start"))
        except (TypeError, ValueError):
            continue
        seen.add(text.casefold())
        cleaned.append({"text": text, "answer_start": start})
    return cleaned


def _cuad_reference_answer(item: dict[str, Any]) -> str:
    answers = _cuad_answers(item)
    return " | ".join(str(answer["text"]).strip() for answer in answers[:3] if str(answer["text"]).strip())


def _cuad_windows_for_qas(
    qas: Sequence[dict[str, Any]],
    *,
    context: str,
    answer_window: int,
) -> list[tuple[int, int]]:
    windows: list[tuple[int, int]] = []
    for item in qas:
        for answer in _cuad_answers(item):
            start = max(0, int(answer["answer_start"]) - answer_window)
            end = min(len(context), int(answer["answer_start"]) + len(str(answer["text"])) + answer_window)
            windows.append((start, end))
    return _merge_windows(windows)


def _merge_windows(windows: Sequence[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[tuple[int, int]] = []
    for start, end in sorted(windows):
        if not merged or start > merged[-1][1] + 200:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    return merged


def _render_cuad_excerpt_context(*, title: str, context: str, windows: Sequence[tuple[int, int]]) -> str:
    lines = [
        f"Contract title: {title}",
        "",
        "The following are bounded excerpts from the contract source text.",
        "",
    ]
    for index, (start, end) in enumerate(windows, start=1):
        excerpt = context[start:end].strip()
        lines.extend(
            [
                f"## Excerpt {index}",
                "",
                f"[excerpt begins at contract character {start}]",
                "",
                excerpt,
                "",
                f"[excerpt ends at contract character {end}]",
                "",
            ]
        )
    return "\n".join(lines).strip()


def _cuad_question_category(question: str) -> str:
    match = re.search(r'"([^"]+)"', question)
    if match:
        return match.group(1).strip()
    detail = question.split("Details:", 1)[0]
    return re.sub(r"\s+", " ", detail).strip() or "contract_text"


def _cuad_question_text(question: str) -> str:
    category = _cuad_question_category(question)
    details = ""
    if "Details:" in question:
        details = re.sub(r"\s+", " ", question.split("Details:", 1)[1]).strip()
    if details:
        return f'What contract text relates to "{category}"? Details: {details}'
    return f'What contract text relates to "{category}"?'


def _coerce_maud_records(
    rows: Iterable[dict[str, Any]],
    *,
    max_questions_per_record: int,
    max_text_chars: int,
    max_answer_chars: int,
    data_type: str,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    fallback: dict[str, list[dict[str, Any]]] = {}
    preferred_type = data_type.casefold().strip()
    for index, raw_row in enumerate(rows):
        row = dict(raw_row)
        if preferred_type != "any" and str(row.get("data_type") or "").casefold() != preferred_type:
            continue
        contract_name = str(row.get("contract_name") or f"contract_{index:05d}").strip()
        text = _clean_external_text(str(row.get("text") or "")).strip()
        answer = _clean_external_text(str(row.get("answer") or "")).strip()
        question = _clean_external_text(str(row.get("question") or "")).strip()
        if not contract_name or not text or not answer or not question:
            continue
        if answer == "<NONE>" or len(answer) > max_answer_chars:
            continue
        item = {
            "text": _bounded_maud_text(text, answer=answer, max_text_chars=max_text_chars),
            "question": _maud_question_text(row),
            "answer": answer,
            "question_id": str(row.get("id") or f"{index:05d}"),
            "text_type": _clean_external_text(str(row.get("text_type") or "")).strip(),
            "category": _clean_external_text(str(row.get("category") or "")).strip(),
            "data_type": _clean_external_text(str(row.get("data_type") or "")).strip(),
        }
        key = contract_name
        if key not in grouped:
            grouped[key] = {
                "context": "",
                "questions": [],
                "answers": [],
                "question_ids": [],
                "categories": [],
                "text_types": [],
                "title": contract_name,
                "example_id": contract_name,
                "source_span_count": 0,
            }
            fallback[key] = []
        target = grouped[key]["questions"]
        if len(target) < max_questions_per_record and item["text_type"] not in grouped[key]["text_types"]:
            _append_maud_item(grouped[key], item)
        else:
            fallback[key].append(item)

    for key, items in fallback.items():
        record = grouped[key]
        for item in items:
            if len(record["questions"]) >= max_questions_per_record:
                break
            _append_maud_item(record, item)
    for record in grouped.values():
        record["context"] = _render_maud_context(
            title=str(record["title"]),
            excerpts=record.pop("_excerpts", []),
        )
    return [record for record in grouped.values() if record["questions"]]


def _append_maud_item(record: dict[str, Any], item: dict[str, Any]) -> None:
    excerpts = record.setdefault("_excerpts", [])
    excerpts.append(item)
    record["questions"].append(item["question"])
    record["answers"].append(item["answer"])
    record["question_ids"].append(item["question_id"])
    record["categories"].append(item["category"])
    record["text_types"].append(item["text_type"])
    record["source_span_count"] = int(record.get("source_span_count") or 0) + 1


def _bounded_maud_text(text: str, *, answer: str, max_text_chars: int) -> str:
    if len(text) <= max_text_chars:
        return text
    answer_index = text.casefold().find(answer.casefold()) if answer else -1
    if answer_index >= 0:
        half = max_text_chars // 2
        start = max(0, answer_index - half)
        end = min(len(text), start + max_text_chars)
        start = max(0, end - max_text_chars)
        return text[start:end].strip()
    return text[:max_text_chars].strip()


def _maud_question_text(row: dict[str, Any]) -> str:
    question = _clean_external_text(str(row.get("question") or "")).strip()
    subquestion = _clean_external_text(str(row.get("subquestion") or "")).strip()
    text_type = _clean_external_text(str(row.get("text_type") or "")).strip()
    category = _clean_external_text(str(row.get("category") or "")).strip()
    parts = [f"What is the answer for: {question}"]
    if subquestion and subquestion != "<NONE>":
        parts.append(f"Subquestion: {subquestion}")
    if text_type:
        parts.append(f"Text type: {text_type}")
    if category:
        parts.append(f"Category: {category}")
    return " ".join(parts)


def _render_maud_context(*, title: str, excerpts: Sequence[dict[str, Any]]) -> str:
    lines = [
        f"Contract name: {title}",
        "",
        "The following are bounded excerpts from merger-agreement source text.",
        "",
    ]
    for index, item in enumerate(excerpts, start=1):
        lines.extend(
            [
                f"## Excerpt {index}",
                "",
                f"- Text type: {item.get('text_type') or 'unspecified'}",
                f"- Category: {item.get('category') or 'unspecified'}",
                "",
                str(item.get("text") or "").strip(),
                "",
            ]
        )
    return "\n".join(lines).strip()


def _clean_external_text(value: str) -> str:
    replacements = {
        "â€œ": '"',
        "â€": '"',
        "â€˜": "'",
        "â€™": "'",
        "â€“": "-",
        "â€”": "-",
        "â€¦": "...",
        "Â§": "Section",
        "Â": "",
    }
    cleaned = value
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned


def _coerce_squad_records(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return context-level records from SQuAD-style question rows."""

    grouped: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        context = str(record.get("context") or "")
        if not context.strip():
            continue
        answer_texts = (record.get("answers") or {}).get("text") if isinstance(record.get("answers"), dict) else None
        if not answer_texts:
            continue
        title = str(record.get("title") or "untitled")
        row_id = str(record.get("id") or f"record_{index:05d}")
        key = f"{title}\n{context}"
        if key not in grouped:
            grouped[key] = {
                "context": context,
                "questions": [],
                "answers": [],
                "question_ids": [],
                "title": title,
                "example_id": row_id,
            }
        grouped[key]["questions"].append(record.get("question"))
        grouped[key]["answers"].append(str(answer_texts[0]).strip())
        grouped[key]["question_ids"].append(row_id)
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


def write_squad_fixtures(
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
            config_name=config_name or "default",
            split=split,
            index=global_index,
            example_id=str(record.get("title") or record.get("example_id") or ""),
        )
        fixture_dir = out_root / fixture_name
        _write_squad_fixture(
            record=record,
            fixture_dir=fixture_dir,
            dataset_name=dataset_name,
            config_name=config_name or "default",
            split=split,
            fixture_name=fixture_name,
            source_index=global_index,
        )
        written.append(fixture_dir)
    return written


def write_cuad_fixtures(
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
            config_name=config_name or "default",
            split=split,
            index=global_index,
            example_id=str(record.get("title") or record.get("example_id") or ""),
        )
        fixture_dir = out_root / fixture_name
        _write_cuad_fixture(
            record=record,
            fixture_dir=fixture_dir,
            dataset_name=dataset_name,
            config_name=config_name or "default",
            split=split,
            fixture_name=fixture_name,
            source_index=global_index,
        )
        written.append(fixture_dir)
    return written


def write_maud_fixtures(
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
            config_name=config_name or "default",
            split=split,
            index=global_index,
            example_id=str(record.get("title") or record.get("example_id") or ""),
        )
        fixture_dir = out_root / fixture_name
        _write_maud_fixture(
            record=record,
            fixture_dir=fixture_dir,
            dataset_name=dataset_name,
            config_name=config_name or "default",
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
        option_clause = " ".join(
            f"{_option_label(option_index)}. {option_text}"
            for option_index, option_text in enumerate(option_values)
        )
        qa_lines.append(f"{index}. {str(question).strip()} Options: {option_clause}")
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


def _write_squad_fixture(
    *,
    record: dict[str, Any],
    fixture_dir: Path,
    dataset_name: str,
    config_name: str,
    split: str,
    fixture_name: str,
    source_index: int,
) -> None:
    context = _required_text(record, "context")
    questions = _required_sequence(record, "questions")
    answers = _required_sequence(record, "answers")
    question_ids = record.get("question_ids") if isinstance(record.get("question_ids"), Sequence) else []
    if len(questions) != len(answers):
        raise ValueError(f"{fixture_name}: questions/answers length mismatch ({len(questions)}/{len(answers)})")

    fixture_dir.mkdir(parents=True, exist_ok=True)
    title = str(record.get("title") or "untitled")
    example_id = str(record.get("example_id") or title or source_index)

    (fixture_dir / "source.md").write_text(
        "\n".join(
            [
                "# External Extractive QA Passage",
                "",
                f"- Dataset: `{dataset_name}`",
                f"- Config: `{config_name}`",
                f"- Split: `{split}`",
                f"- Title: `{title}`",
                f"- Example id: `{example_id}`",
                "",
                "## Passage",
                "",
                context.strip(),
                "",
            ]
        ),
        encoding="utf-8",
    )

    qa_lines = [
        f"# {fixture_name} QA",
        "",
        "Questions only. Reference answers are isolated in `oracle.jsonl`.",
        "",
    ]
    oracle_rows: list[dict[str, Any]] = []
    for index, question in enumerate(questions, start=1):
        qid = f"q{index:03d}"
        answer = str(answers[index - 1]).strip()
        if not answer:
            raise ValueError(f"{fixture_name}:{qid}: blank answer")
        source_qid = str(question_ids[index - 1]).strip() if index - 1 < len(question_ids) else qid
        qa_lines.append(f"{index}. {str(question).strip()}")
        oracle_rows.append(
            {
                "id": qid,
                "source_id": f"{source_qid}:{qid}",
                "category": "external_extract_answer",
                "reference_answer": answer,
                "answer": answer,
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
                "- External extractive-QA transfer sample; do not treat dataset wording as architecture.",
                "- `source.md` contains the passage context.",
                "- `qa.md` contains open-ended questions only.",
                "- `oracle.jsonl` contains reference answer spans for after-the-fact scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_cuad_fixture(
    *,
    record: dict[str, Any],
    fixture_dir: Path,
    dataset_name: str,
    config_name: str,
    split: str,
    fixture_name: str,
    source_index: int,
) -> None:
    context = _required_text(record, "context")
    questions = _required_sequence(record, "questions")
    answers = _required_sequence(record, "answers")
    question_ids = record.get("question_ids") if isinstance(record.get("question_ids"), Sequence) else []
    categories = record.get("categories") if isinstance(record.get("categories"), Sequence) else []
    if len(questions) != len(answers):
        raise ValueError(f"{fixture_name}: questions/answers length mismatch ({len(questions)}/{len(answers)})")

    fixture_dir.mkdir(parents=True, exist_ok=True)
    title = str(record.get("title") or "untitled_contract")
    example_id = str(record.get("example_id") or title or source_index)
    span_count = int(record.get("source_span_count") or 0)

    (fixture_dir / "source.md").write_text(
        "\n".join(
            [
                "# External Legal Contract Excerpts",
                "",
                f"- Dataset: `{dataset_name}`",
                f"- Config: `{config_name}`",
                f"- Split: `{split}`",
                f"- Title: `{title}`",
                f"- Example id: `{example_id}`",
                f"- Excerpt count: `{span_count}`",
                "",
                "## Contract Excerpts",
                "",
                context.strip(),
                "",
            ]
        ),
        encoding="utf-8",
    )

    qa_lines = [
        f"# {fixture_name} QA",
        "",
        "Questions only. Reference contract spans are isolated in `oracle.jsonl`.",
        "",
    ]
    oracle_rows: list[dict[str, Any]] = []
    for index, question in enumerate(questions, start=1):
        qid = f"q{index:03d}"
        answer = str(answers[index - 1]).strip()
        if not answer:
            raise ValueError(f"{fixture_name}:{qid}: blank answer")
        source_qid = str(question_ids[index - 1]).strip() if index - 1 < len(question_ids) else qid
        category = str(categories[index - 1]).strip() if index - 1 < len(categories) else "contract_text"
        qa_lines.append(f"{index}. {str(question).strip()}")
        oracle_rows.append(
            {
                "id": qid,
                "source_id": f"{source_qid}:{qid}",
                "category": "external_legal_contract_extract",
                "reference_answer": answer,
                "answer": answer,
                "contract_category": category,
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
                "- External legal-domain transfer sample; do not treat CUAD wording as architecture.",
                "- `source.md` contains bounded answer-neighborhood excerpts, not full contracts.",
                "- `qa.md` contains extraction questions only.",
                "- `oracle.jsonl` contains reference contract spans for after-the-fact scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_maud_fixture(
    *,
    record: dict[str, Any],
    fixture_dir: Path,
    dataset_name: str,
    config_name: str,
    split: str,
    fixture_name: str,
    source_index: int,
) -> None:
    context = _required_text(record, "context")
    questions = _required_sequence(record, "questions")
    answers = _required_sequence(record, "answers")
    question_ids = record.get("question_ids") if isinstance(record.get("question_ids"), Sequence) else []
    categories = record.get("categories") if isinstance(record.get("categories"), Sequence) else []
    text_types = record.get("text_types") if isinstance(record.get("text_types"), Sequence) else []
    if len(questions) != len(answers):
        raise ValueError(f"{fixture_name}: questions/answers length mismatch ({len(questions)}/{len(answers)})")

    fixture_dir.mkdir(parents=True, exist_ok=True)
    title = str(record.get("title") or "untitled_contract")
    example_id = str(record.get("example_id") or title or source_index)
    span_count = int(record.get("source_span_count") or 0)

    (fixture_dir / "source.md").write_text(
        "\n".join(
            [
                "# External Merger Agreement QA Excerpts",
                "",
                f"- Dataset: `{dataset_name}`",
                f"- Config: `{config_name}`",
                f"- Split: `{split}`",
                f"- Contract: `{title}`",
                f"- Example id: `{example_id}`",
                f"- Excerpt count: `{span_count}`",
                "",
                "## Agreement Excerpts",
                "",
                context.strip(),
                "",
            ]
        ),
        encoding="utf-8",
    )

    qa_lines = [
        f"# {fixture_name} QA",
        "",
        "Questions only. MAUD labels/reference answers are isolated in `oracle.jsonl`.",
        "",
    ]
    oracle_rows: list[dict[str, Any]] = []
    for index, question in enumerate(questions, start=1):
        qid = f"q{index:03d}"
        answer = str(answers[index - 1]).strip()
        if not answer:
            raise ValueError(f"{fixture_name}:{qid}: blank answer")
        source_qid = str(question_ids[index - 1]).strip() if index - 1 < len(question_ids) else qid
        category = str(categories[index - 1]).strip() if index - 1 < len(categories) else "maud"
        text_type = str(text_types[index - 1]).strip() if index - 1 < len(text_types) else ""
        qa_lines.append(f"{index}. {str(question).strip()}")
        oracle_rows.append(
            {
                "id": qid,
                "source_id": f"{source_qid}:{qid}",
                "category": "external_merger_agreement_answer",
                "reference_answer": answer,
                "answer": answer,
                "maud_category": category,
                "maud_text_type": text_type,
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
                "- External MAUD legal-domain transfer sample; do not treat MAUD labels as architecture.",
                "- `source.md` contains bounded merger-agreement excerpts, not full contracts.",
                "- `qa.md` contains question/field surfaces only.",
                "- `oracle.jsonl` contains reference labels/answers for after-the-fact scoring.",
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
