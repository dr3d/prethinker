import json
import zipfile
from pathlib import Path

from scripts.import_candidate_oracle_review import import_review_zip


def _write_zip(path: Path, entries: dict[str, str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in entries.items():
            archive.writestr(name, text)
    return path


def _manifest(**overrides: object) -> str:
    payload = {
        "review_id": "demo_review_20260605",
        "fixture_id": "demo_fixture",
        "predicate": "demo_candidate/3",
        "reviewer_blind_to_model_outputs": True,
        "reviewer_read_forbidden_inputs": False,
        "source_files": ["datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002/source.md"],
        "created_at": "2026-06-05",
        **overrides,
    }
    return json.dumps(payload, indent=2)


def test_import_candidate_oracle_review_copies_only_review_files(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(),
            "expected_facts.pl": "demo_candidate(Row, alpha, Src).\n",
            "forbidden_facts.pl": "demo_candidate(_, forbidden_value, _).\n",
            "README.md": "# Review\n",
            "adjudication_notes.md": "Source-only notes.\n",
            "source.md": "This source prose must not be retained.\n",
        },
    )
    dest = tmp_path / "reviews"

    report = import_review_zip(zip_path=package, dest_root=dest)

    assert report["summary"]["status"] == "pass"
    review_dir = dest / "demo_review_20260605"
    assert (review_dir / "manifest.json").exists()
    assert (review_dir / "candidate_expected_facts.pl").read_text(encoding="utf-8") == "demo_candidate(Row, alpha, Src).\n"
    assert (review_dir / "candidate_forbidden_facts.pl").exists()
    assert not (review_dir / "source.md").exists()
    assert "source.md" in report["dropped_entries"]


def test_import_candidate_oracle_review_supports_output_template_prefix(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002/source.md": "not imported\n",
            "output_template/manifest.json": _manifest(),
            "output_template/candidate_expected_facts.pl": "demo_candidate(Row, alpha, Src).\n",
            "output_template/candidate_forbidden_facts.pl": "demo_candidate(_, forbidden_value, _).\n",
            "output_template/README.md": "# Review\n",
        },
    )

    report = import_review_zip(zip_path=package, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "pass"
    assert report["review_id"] == "demo_review_20260605"
    assert "datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002/source.md" in report["dropped_entries"]


def test_import_candidate_oracle_review_supports_same_review_id_fixture_bundle(tmp_path: Path) -> None:
    bundle_id = "demo_bundle_review_20260605"
    fixture_a = "fda_warning_letter_domain_transfer_001"
    fixture_b = "fda_warning_letter_domain_transfer_002"
    package = _write_zip(
        tmp_path / "review_bundle.zip",
        {
            f"candidate_oracle_reviews/{bundle_id}/{fixture_a}/manifest.json": _manifest(
                review_id=bundle_id,
                fixture_id=fixture_a,
                source_files=[f"fixtures/{fixture_a}/source.md"],
            ),
            f"candidate_oracle_reviews/{bundle_id}/{fixture_a}/candidate_expected_facts.pl": "demo_candidate(Row, alpha, Src).\n",
            f"candidate_oracle_reviews/{bundle_id}/{fixture_a}/candidate_forbidden_facts.pl": "demo_candidate(_, forbidden_value, _).\n",
            f"candidate_oracle_reviews/{bundle_id}/{fixture_b}/manifest.json": _manifest(
                review_id=bundle_id,
                fixture_id=fixture_b,
                source_files=[f"fixtures/{fixture_b}/source.md"],
            ),
            f"candidate_oracle_reviews/{bundle_id}/{fixture_b}/candidate_expected_facts.pl": "demo_candidate(Row, beta, Src).\n",
            f"candidate_oracle_reviews/{bundle_id}/{fixture_b}/candidate_forbidden_facts.pl": "demo_candidate(_, forbidden_value, _).\n",
            f"candidate_oracle_reviews/{bundle_id}/summary.md": "# Bundle summary\n",
        },
    )
    dest = tmp_path / "reviews"

    report = import_review_zip(zip_path=package, dest_root=dest)

    assert report["summary"]["status"] == "pass"
    assert len(report["imported_reviews"]) == 2
    review_a = dest / f"{bundle_id}_{fixture_a}"
    review_b = dest / f"{bundle_id}_{fixture_b}"
    assert review_a.exists()
    assert review_b.exists()
    manifest = json.loads((review_a / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["review_id"] == f"{bundle_id}_{fixture_a}"
    assert manifest["bundle_review_id"] == bundle_id
    assert manifest["source_files"] == [f"datasets/compile_micro_fixtures/{fixture_a}/source.md"]


def test_import_candidate_oracle_review_blocks_unfilled_template(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "template.zip",
        {
            "output_template/manifest.json": _manifest(fixture_id="REPLACE_WITH_FIXTURE_ID"),
            "output_template/candidate_expected_facts.pl": "% Add facts here.\n",
            "output_template/candidate_forbidden_facts.pl": "% Add facts here.\n",
        },
    )

    report = import_review_zip(zip_path=package, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "fail"
    assert "audit:manifest_placeholder:fixture_id" in report["errors"]
    assert "audit:review_has_no_expected_or_forbidden_facts" in report["errors"]


def test_import_candidate_oracle_review_surfaces_audit_warnings(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(predicate="fda_response_documentation_gap/5"),
            "candidate_expected_facts.pl": (
                "fda_response_documentation_gap("
                "Gap, violation_1, cfr_21_211_113_b, supporting_documentation, Src).\n"
            ),
            "candidate_forbidden_facts.pl": (
                "fda_response_documentation_gap(_, _, _, 'Your response is inadequate.', _).\n"
            ),
        },
    )

    report = import_review_zip(zip_path=package, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["warnings"] >= 1
    assert any("audit:candidate_forbidden_facts.pl:line_1:forbidden_atom_shape:" in warning for warning in report["warnings"])


def test_import_candidate_oracle_review_refuses_overwrite_without_flag(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(),
            "candidate_expected_facts.pl": "demo_candidate(Row, alpha, Src).\n",
            "candidate_forbidden_facts.pl": "demo_candidate(_, forbidden_value, _).\n",
        },
    )
    dest = tmp_path / "reviews"

    first = import_review_zip(zip_path=package, dest_root=dest)
    second = import_review_zip(zip_path=package, dest_root=dest)

    assert first["summary"]["status"] == "pass"
    assert second["summary"]["status"] == "fail"
    assert "destination_exists:demo_review_20260605" in second["errors"]


def test_import_candidate_oracle_review_dry_run_does_not_write(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(),
            "candidate_expected_facts.pl": "demo_candidate(Row, alpha, Src).\n",
            "candidate_forbidden_facts.pl": "demo_candidate(_, forbidden_value, _).\n",
        },
    )
    dest = tmp_path / "reviews"

    report = import_review_zip(zip_path=package, dest_root=dest, dry_run=True)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["dry_run"] is True
    assert not (dest / "demo_review_20260605").exists()


def test_import_candidate_oracle_review_failed_dry_run_reports_dry_run(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "template.zip",
        {
            "output_template/manifest.json": _manifest(fixture_id="REPLACE_WITH_FIXTURE_ID"),
            "output_template/candidate_expected_facts.pl": "% Add facts here.\n",
            "output_template/candidate_forbidden_facts.pl": "% Add facts here.\n",
        },
    )

    report = import_review_zip(zip_path=package, dest_root=tmp_path / "reviews", dry_run=True)

    assert report["summary"]["status"] == "fail"
    assert report["summary"]["dry_run"] is True
