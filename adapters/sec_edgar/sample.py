from __future__ import annotations

import argparse
import json
from pathlib import Path

from adapters.sec_edgar.client import SecEdgarClient
from adapters.sec_edgar.normalize import normalize_submission_filing
from adapters.sec_edgar.to_harness import record_to_harness_case


def sample_submissions_to_harness(*, cik: str, limit: int, out: Path) -> Path:
    client = SecEdgarClient()
    submission = client.submissions(cik)
    cases = []
    recent = submission.get("filings", {}).get("recent", {}) if isinstance(submission.get("filings"), dict) else {}
    forms = recent.get("form", []) if isinstance(recent, dict) else []
    total = min(max(1, int(limit)), len(forms) if isinstance(forms, list) else 0)
    for index in range(total):
        record = normalize_submission_filing(submission, index)
        cases.append(record_to_harness_case(record, index=index + 1).to_dict())
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(case, ensure_ascii=False, sort_keys=True) + "\n")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a small SEC EDGAR Semantic IR harness JSONL sample.")
    parser.add_argument("--cik", required=True, help="Company CIK, with or without leading zeros.")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--out", type=Path, default=Path("datasets/sec_edgar/generated/sec_sample.jsonl"))
    args = parser.parse_args()
    path = sample_submissions_to_harness(cik=args.cik, limit=max(1, args.limit), out=args.out)
    print(path)


if __name__ == "__main__":
    main()
