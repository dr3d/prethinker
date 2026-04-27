from __future__ import annotations

import argparse
import json
from pathlib import Path

from adapters.courtlistener.client import CourtListenerClient
from adapters.courtlistener.normalize import normalize_opinion_record
from adapters.courtlistener.to_harness import record_to_harness_case


def sample_search_to_harness(*, query: str, limit: int, out: Path) -> Path:
    client = CourtListenerClient()
    raw = client.search(q=query, page_size=limit)
    results = raw.get("results", []) if isinstance(raw, dict) else []
    cases = []
    for index, row in enumerate(results[:limit], start=1):
        if not isinstance(row, dict):
            continue
        record = normalize_opinion_record(row)
        cases.append(record_to_harness_case(record, index=index).to_dict())
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case, ensure_ascii=False, sort_keys=True) + "\n")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a small CourtListener Semantic IR harness JSONL sample.")
    parser.add_argument("--query", default="breach of lease")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--out", type=Path, default=Path("datasets/courtlistener/generated/courtlistener_sample.jsonl"))
    args = parser.parse_args()
    path = sample_search_to_harness(query=args.query, limit=max(1, args.limit), out=args.out)
    print(path)


if __name__ == "__main__":
    main()
