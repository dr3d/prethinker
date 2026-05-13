#!/usr/bin/env python3
"""Render the fixture trace prototype into a self-contained HTML file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_TRACE = HERE / "trace_events.json"
DEFAULT_TEMPLATE = HERE / "index.template.html"
DEFAULT_OUT = HERE / "index.html"


def render(*, trace_path: Path, template_path: Path, out_path: Path) -> None:
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    template = template_path.read_text(encoding="utf-8")
    embedded = json.dumps(trace, ensure_ascii=False, indent=2)
    out_path.write_text(template.replace("__TRACE_DATA__", embedded), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    render(trace_path=args.trace, template_path=args.template, out_path=args.out)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
