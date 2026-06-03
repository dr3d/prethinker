import json
from pathlib import Path

from scripts.union_domain_bootstrap_compiles import _slug, main


def _write_run(path: Path, facts: list[str], *, lens_id: str) -> Path:
    path.write_text(
        json.dumps(
            {
                "model": "qwen/test",
                "profile_registry_lens": lens_id,
                "active_profile_registry_lens": {
                    "id": lens_id,
                    "allowed_signatures": ["fda_warning_letter/5"],
                },
                "source_compile": {
                    "facts": facts,
                    "rules": [],
                    "queries": [],
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_union_does_not_preserve_single_active_lens_metadata(tmp_path, monkeypatch) -> None:
    left = _write_run(
        tmp_path / "wrapper.json",
        ["fda_warning_letter(letter_1, cder, firm_a, v_2026_01_01, source_1)."],
        lens_id="wrapper",
    )
    right = _write_run(
        tmp_path / "violation.json",
        ["fda_violation(violation_1, letter_1, violation_1, contamination_control, source_2)."],
        lens_id="violation",
    )
    out_dir = tmp_path / "out"

    monkeypatch.setattr(
        "sys.argv",
        [
            "union_domain_bootstrap_compiles.py",
            "--run-json",
            str(left),
            "--run-json",
            str(right),
            "--out-dir",
            str(out_dir),
            "--label",
            "test-union",
            "--no-runtime-validation",
        ],
    )

    assert main() == 0
    out_json = next(out_dir.glob("*.json"))
    payload = json.loads(out_json.read_text(encoding="utf-8"))

    assert payload["mode"] == "deterministic_compile_union"
    assert "active_profile_registry_lens" not in payload
    assert payload["profile_registry_lens"] == ""
    assert "no single active lens" in payload["profile_registry_lens_note"]
    assert payload["union_source_compile"]["source_runs"] == [str(left), str(right)]


def test_union_slug_limit_keeps_nested_bundle_filenames_short() -> None:
    assert len(_slug("sec-form-8k-skeleton-transfer-002-r3-local-qwen-wrapper-date-boundary", limit=48)) == 48
    assert _slug("qwen/qwen3.6-35b-a3b", limit=32) == "qwen-qwen3-6-35b-a3b"
