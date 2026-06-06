#!/usr/bin/env python3
"""Audit retained CourtListener cache payloads for provider provenance sidecars.

This is an offline governance check. It does not call CourtListener and it does
not decide legal truth. It only prevents retained resolver payloads from becoming
untracked claim evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.report_freshness import apply_markdown_freshness_check  # noqa: E402


DEFAULT_CACHE_DIR = REPO_ROOT / "datasets" / "courtlistener" / "generated" / "cache"
METADATA_SCHEMA = "prethinker.courtlistener_cache_metadata.v1"
DEFAULT_URL_PREFIX = "https://www.courtlistener.com/api/rest/"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--allowed-url-prefix", default=DEFAULT_URL_PREFIX)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-md", type=Path)
    parser.add_argument("--expect-md", type=Path)
    parser.add_argument("--exit-zero", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(cache_dir=args.cache_dir, allowed_url_prefix=args.allowed_url_prefix)
    rendered_md = render_markdown(report)
    if args.expect_md:
        apply_markdown_freshness_check(report=report, expected_path=args.expect_md, rendered_md=rendered_md)
        rendered_md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(rendered_md, encoding="utf-8")
    if not args.out_json and not args.out_md:
        print(json.dumps(report, indent=2, sort_keys=True))
    failed = report["summary"]["status"] != "pass"
    return 0 if args.exit_zero or not failed else 1


def build_report(*, cache_dir: Path = DEFAULT_CACHE_DIR, allowed_url_prefix: str = DEFAULT_URL_PREFIX) -> dict[str, Any]:
    cache_dir = _resolve(cache_dir)
    payload_paths = _payload_paths(cache_dir)
    metadata_paths = _metadata_paths(cache_dir)
    rows = [_audit_payload(path, allowed_url_prefix=allowed_url_prefix) for path in payload_paths]
    payload_names = {path.name for path in payload_paths}
    orphan_metadata = [
        {
            "metadata_file": _display_path(path),
            "errors": [f"orphan_metadata_sidecar:{path.name}"],
        }
        for path in metadata_paths
        if _payload_name_from_metadata(path) not in payload_names
    ]
    blocking_errors = [error for row in rows for error in row["errors"]]
    blocking_errors.extend(error for row in orphan_metadata for error in row["errors"])
    return {
        "schema": "prethinker.courtlistener_cache_provenance_status.v1",
        "cache_dir": _display_path(cache_dir),
        "allowed_url_prefix": allowed_url_prefix,
        "summary": {
            "payload_count": len(payload_paths),
            "metadata_count": len(metadata_paths),
            "payloads_with_metadata": sum(1 for row in rows if row["metadata_file"]),
            "orphan_metadata_count": len(orphan_metadata),
            "blocking_errors": len(blocking_errors),
            "status": "pass" if not blocking_errors else "fail",
        },
        "payloads": rows,
        "orphan_metadata": orphan_metadata,
        "blocking_reasons": blocking_errors,
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# CourtListener Cache Provenance Status",
        "",
        "This report is an offline resolver-provenance gate. It validates retained",
        "CourtListener cache payloads and metadata sidecars; it does not call a live",
        "resolver and does not verify legal propositions.",
        "",
        f"- Cache dir: `{report['cache_dir']}`",
        f"- Allowed URL prefix: `{report['allowed_url_prefix']}`",
        f"- Payloads: `{summary['payload_count']}`",
        f"- Metadata sidecars: `{summary['metadata_count']}`",
        f"- Payloads with metadata: `{summary['payloads_with_metadata']}`",
        f"- Orphan metadata sidecars: `{summary['orphan_metadata_count']}`",
        f"- Blocking errors: `{summary['blocking_errors']}`",
        f"- Status: `{summary['status']}`",
        "",
        "## Payloads",
        "",
    ]
    rows = report.get("payloads") or []
    if rows:
        lines.extend(["| Payload | Metadata | Method | URL | Errors |", "| --- | --- | --- | --- | --- |"])
        for row in rows:
            errors = ", ".join(f"`{error}`" for error in row["errors"]) or "`[]`"
            lines.append(
                f"| `{row['payload_file']}` | `{row['metadata_file']}` | `{row['method']}` | "
                f"`{row['url']}` | {errors} |"
            )
    else:
        lines.append("_No retained CourtListener cache payloads._")
    if report.get("orphan_metadata"):
        lines.extend(["", "## Orphan Metadata", "", "| Metadata | Errors |", "| --- | --- |"])
        for row in report["orphan_metadata"]:
            errors = ", ".join(f"`{error}`" for error in row["errors"]) or "`[]`"
            lines.append(f"| `{row['metadata_file']}` | {errors} |")
    return "\n".join(lines) + "\n"


def _audit_payload(path: Path, *, allowed_url_prefix: str) -> dict[str, Any]:
    errors: list[str] = []
    metadata_path = path.with_name(f"{path.stem}.meta.json")
    metadata: dict[str, Any] = {}
    _load_json(path, errors=errors, label="payload_json")
    if not metadata_path.exists():
        errors.append("missing_metadata_sidecar")
    else:
        payload = _load_json(metadata_path, errors=errors, label="metadata_json")
        metadata = payload if isinstance(payload, dict) else {}
        errors.extend(_metadata_errors(metadata, payload_path=path, allowed_url_prefix=allowed_url_prefix))
    return {
        "payload_file": _display_path(path),
        "metadata_file": _display_path(metadata_path) if metadata_path.exists() else "",
        "method": str(metadata.get("method") or ""),
        "url": str(metadata.get("url") or ""),
        "errors": errors,
    }


def _metadata_errors(metadata: dict[str, Any], *, payload_path: Path, allowed_url_prefix: str) -> list[str]:
    errors: list[str] = []
    if metadata.get("schema") != METADATA_SCHEMA:
        errors.append("metadata_schema_mismatch")
    if metadata.get("provider") != "courtlistener":
        errors.append("metadata_provider_not_courtlistener")
    method = str(metadata.get("method") or "")
    if method not in {"GET", "POST"}:
        errors.append(f"metadata_method_invalid:{method or 'missing'}")
    url = str(metadata.get("url") or "")
    if not url.startswith(allowed_url_prefix):
        errors.append("metadata_url_outside_allowed_prefix")
    body_sha256 = str(metadata.get("body_sha256") or "")
    if method == "GET" and body_sha256:
        errors.append("metadata_get_body_sha256_must_be_empty")
    if method == "POST" and not SHA256_RE.match(body_sha256):
        errors.append("metadata_post_body_sha256_invalid")
    if metadata.get("cache_file") != payload_path.name:
        errors.append("metadata_cache_file_mismatch")
    return errors


def _payload_paths(cache_dir: Path) -> list[Path]:
    if not cache_dir.exists():
        return []
    return sorted(path for path in cache_dir.glob("*.json") if not path.name.endswith(".meta.json"))


def _metadata_paths(cache_dir: Path) -> list[Path]:
    if not cache_dir.exists():
        return []
    return sorted(cache_dir.glob("*.meta.json"))


def _payload_name_from_metadata(path: Path) -> str:
    return f"{path.name[:-len('.meta.json')]}.json"


def _load_json(path: Path, *, errors: list[str], label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - this is an audit, report exact failure class in errors.
        errors.append(f"{label}_invalid:{exc.__class__.__name__}")
        return {}


def _resolve(path: Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
