#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import umls_mvp  # noqa: E402


DEFAULT_NET_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "NET"
DEFAULT_OUT_DIR = ROOT / "tmp" / "licensed" / "umls" / "2025AB" / "semantic_network_kb"


def _utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def build_semantic_network_kb(net_dir: Path, out_dir: Path) -> dict:
    network = umls_mvp.load_semantic_network(net_dir)
    counts = {
        "semantic_types": len(network.get("semantic_types", []) or []),
        "semantic_relations": len(network.get("semantic_relations", []) or []),
        "structure_rows": len(network.get("structure", []) or []),
        "inherited_ui_relations": len(network.get("inherited_ui_relations", []) or []),
        "inherited_name_relations": len(network.get("inherited_name_relations", []) or []),
    }
    missing_files = [
        name
        for name, path in (network.get("files", {}) or {}).items()
        if name in {"srdef", "srstr"} and not str(path or "").strip()
    ]
    manifest = {
        "kb_id": "umls_semantic_network",
        "generated_at_utc": _utc_now(),
        "net_dir": str(net_dir),
        "out_dir": str(out_dir),
        "files": dict(network.get("files", {}) or {}),
        "missing_required_files": missing_files,
        "counts": counts,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    umls_mvp.write_json(out_dir / "manifest.json", manifest)
    umls_mvp.write_json(out_dir / "semantic_network.json", network)
    (out_dir / "semantic_network_facts.pl").write_text(
        umls_mvp.render_semantic_network_facts(network),
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a local UMLS Semantic Network Prolog KB.")
    parser.add_argument("--net-dir", type=Path, default=DEFAULT_NET_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()
    manifest = build_semantic_network_kb(args.net_dir, args.out_dir)
    print(json.dumps(manifest["counts"], indent=2))
    if manifest["missing_required_files"]:
        print("MISSING:", ", ".join(manifest["missing_required_files"]))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
