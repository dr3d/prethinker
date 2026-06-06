from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.audit_courtlistener_cache_provenance import build_report, render_markdown


def test_courtlistener_cache_provenance_accepts_empty_cache(tmp_path: Path) -> None:
    report = build_report(cache_dir=tmp_path / "missing")

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["payload_count"] == 0
    assert "No retained CourtListener cache payloads" in render_markdown(report)


def test_courtlistener_cache_provenance_accepts_payload_with_metadata(tmp_path: Path) -> None:
    payload = tmp_path / "abc.json"
    payload.write_text(json.dumps({"results": []}), encoding="utf-8")
    (tmp_path / "abc.meta.json").write_text(
        json.dumps(
            {
                "schema": "prethinker.courtlistener_cache_metadata.v1",
                "provider": "courtlistener",
                "method": "GET",
                "url": "https://www.courtlistener.com/api/rest/v4/search/?q=Brown",
                "body_sha256": "",
                "payload_sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
                "cache_file": "abc.json",
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    report = build_report(cache_dir=tmp_path)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["payload_count"] == 1
    assert report["summary"]["payloads_with_metadata"] == 1
    assert report["payloads"][0]["payload_sha256"] == hashlib.sha256(payload.read_bytes()).hexdigest()
    assert report["payloads"][0]["errors"] == []
    assert "Payload SHA-256" in render_markdown(report)


def test_courtlistener_cache_provenance_rejects_missing_metadata(tmp_path: Path) -> None:
    (tmp_path / "abc.json").write_text(json.dumps({"results": []}), encoding="utf-8")

    report = build_report(cache_dir=tmp_path)

    assert report["summary"]["status"] == "fail"
    assert "missing_metadata_sidecar" in report["payloads"][0]["errors"]


def test_courtlistener_cache_provenance_rejects_orphan_metadata(tmp_path: Path) -> None:
    (tmp_path / "abc.meta.json").write_text(
        json.dumps(
            {
                "schema": "prethinker.courtlistener_cache_metadata.v1",
                "provider": "courtlistener",
                "method": "GET",
                "url": "https://www.courtlistener.com/api/rest/v4/search/?q=Brown",
                "body_sha256": "",
                "payload_sha256": "0" * 64,
                "cache_file": "abc.json",
            },
        ),
        encoding="utf-8",
    )

    report = build_report(cache_dir=tmp_path)

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["orphan_metadata_count"] == 1
    assert "orphan_metadata_sidecar:abc.meta.json" in report["orphan_metadata"][0]["errors"]


def test_courtlistener_cache_provenance_rejects_bad_metadata_shape(tmp_path: Path) -> None:
    (tmp_path / "abc.json").write_text(json.dumps({"results": []}), encoding="utf-8")
    (tmp_path / "abc.meta.json").write_text(
        json.dumps(
            {
                "schema": "wrong",
                "provider": "courtlistener",
                "method": "POST",
                "url": "https://example.test/not-courtlistener",
                "body_sha256": "not-a-digest",
                "payload_sha256": "not-a-digest",
                "cache_file": "other.json",
            },
        ),
        encoding="utf-8",
    )

    report = build_report(cache_dir=tmp_path)

    errors = report["payloads"][0]["errors"]
    assert "metadata_schema_mismatch" in errors
    assert "metadata_url_outside_allowed_prefix" in errors
    assert "metadata_post_body_sha256_invalid" in errors
    assert "metadata_payload_sha256_invalid" in errors
    assert "metadata_cache_file_mismatch" in errors


def test_courtlistener_cache_provenance_rejects_payload_digest_mismatch(tmp_path: Path) -> None:
    payload = tmp_path / "abc.json"
    payload.write_text(json.dumps({"results": []}), encoding="utf-8")
    (tmp_path / "abc.meta.json").write_text(
        json.dumps(
            {
                "schema": "prethinker.courtlistener_cache_metadata.v1",
                "provider": "courtlistener",
                "method": "GET",
                "url": "https://www.courtlistener.com/api/rest/v4/search/?q=Brown",
                "body_sha256": "",
                "payload_sha256": "0" * 64,
                "cache_file": "abc.json",
            },
        ),
        encoding="utf-8",
    )

    report = build_report(cache_dir=tmp_path)

    assert report["summary"]["status"] == "fail"
    assert "metadata_payload_sha256_mismatch" in report["payloads"][0]["errors"]
