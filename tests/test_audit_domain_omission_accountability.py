import json
from pathlib import Path

from scripts.audit_domain_omission_accountability import build_report
from scripts.audit_domain_omission_accountability import _compile_paths


def _compile_payload(*, facts: list[str], notes: list[str]) -> dict:
    return {
        "parsed": {
            "candidate_predicates": [
                {"signature": "domain_omission/5", "args": ["domain", "carrier", "kind", "reason", "source"]}
            ]
        },
        "source_compile": {
            "facts": facts,
            "self_check": {"notes": notes},
        },
    }


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def test_domain_omission_accountability_flags_self_check_only_omission(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=["fda_correspondence_party(letter, party, recipient, firm, source_utterance)."],
            notes=["Signatory explicitly stated as absent; no domain_omission emitted."],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "self_check_omission_without_domain_omission_fact"


def test_domain_omission_accountability_discovers_nested_run_fixture_compile_jsons(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile"
    (compile_root / "run1_chronology").mkdir(parents=True)
    (compile_root / "run1_chronology" / "batch.json").write_text(
        json.dumps({"rows": [{"fixture": "fixture_a"}]}),
        encoding="utf-8",
    )
    compile_json = compile_root / "run1_chronology" / "fixture_a" / "run.json"
    _write(
        compile_json,
        {
            **_compile_payload(
                facts=[],
                notes=["Meeting explicitly not held; no domain_omission emitted."],
            ),
            "active_profile_registry_lens": {
                "allowed_signatures": [
                    "fda_regulatory_meeting/4",
                    "domain_omission/5",
                ],
                "accountability_requirement_count": 1,
            },
        },
    )

    paths = _compile_paths(compile_root=compile_root, compile_jsons=[], fixtures={"fixture_a"})
    report = build_report(paths)

    assert len(paths) == 1
    assert report["summary"]["blocker_count"] == 1
    assert report["rows"][0]["class"] == "self_check_omission_without_domain_omission_fact"


def test_domain_omission_accountability_passes_when_fact_exists(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(letter, 'fda_correspondence_party/5', role_missing, signatory_not_stated, source_utterance)."
            ],
            notes=["Signatory explicitly stated as absent."],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["blocker_count"] == 0


def test_domain_omission_accountability_blocks_invalid_carrier_signature(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "domain_omission(letter, fda_correspondence_party_5, role_missing, signatory_not_stated, source_utterance)."
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "invalid_domain_omission_carrier_signature"
    assert report["rows"][0]["carrier_signature"] == "fda_correspondence_party_5"


def test_domain_omission_accountability_blocks_ordinary_placeholder_carrier(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        _compile_payload(
            facts=[
                "fda_correspondence_party(letter, not_stated, signatory, not_stated, source_utterance).",
                "domain_omission(letter, 'fda_correspondence_party/5', role_missing, signatory_not_stated, source_utterance).",
            ],
            notes=[],
        ),
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "ordinary_carrier_omission_placeholder"
    assert report["rows"][0]["carrier_signature"] == "fda_correspondence_party/5"


def test_domain_omission_accountability_ignores_profiles_without_domain_omission(tmp_path: Path) -> None:
    compile_json = _write(
        tmp_path / "fixture" / "compile.json",
        {
            "parsed": {"candidate_predicates": [{"signature": "fda_warning_letter/5"}]},
            "source_compile": {"facts": [], "self_check": {"notes": ["missing signatory"]}},
        },
    )

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"


def test_domain_omission_accountability_respects_lens_without_accountability_requirements(tmp_path: Path) -> None:
    payload = _compile_payload(
        facts=["fda_violation(violation_1, letter_1, violation_1, quality_unit_failure, src_line_1)."],
        notes=["Signatory explicitly stated as absent; no domain_omission emitted because wrapper carrier is outside this lens."],
    )
    payload["active_profile_registry_lens"] = {
        "id": "violation",
        "allowed_signatures": [
            "fda_violation/5",
            "fda_violation_detail/5",
            "domain_omission/5",
        ],
        "accountability_requirement_count": 0,
    }
    compile_json = _write(tmp_path / "fixture" / "compile.json", payload)

    report = build_report([compile_json])

    assert report["summary"]["status"] == "pass"


def test_domain_omission_accountability_enforces_lens_accountability_requirements(tmp_path: Path) -> None:
    payload = _compile_payload(
        facts=["fda_correspondence_party(letter, party, recipient, firm, src_line_1)."],
        notes=["Signatory explicitly stated as absent; no domain_omission emitted."],
    )
    payload["active_profile_registry_lens"] = {
        "id": "wrapper",
        "allowed_signatures": [
            "fda_correspondence_party/5",
            "domain_omission/5",
        ],
        "accountability_requirement_count": 1,
    }
    compile_json = _write(tmp_path / "fixture" / "compile.json", payload)

    report = build_report([compile_json])

    assert report["summary"]["status"] == "fail"
    assert report["rows"][0]["class"] == "self_check_omission_without_domain_omission_fact"
