import json
import zipfile
from pathlib import Path

from scripts.import_source_oracle_review import import_review_zip


FIXTURE_ID = "fda_warning_letter_domain_transfer_002"


def _write_zip(path: Path, entries: dict[str, str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        for name, text in entries.items():
            archive.writestr(name, text)
    return path


def _proposal(path: Path, **overrides: object) -> Path:
    payload = {
        "schema": "domain_predicate_proposal_v1",
        "proposal_id": "demo_source_oracle_proposal_v1",
        "candidate_signature": "demo_oracle/3",
        **overrides,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _manifest(**overrides: object) -> str:
    payload = {
        "schema": "demo_source_oracle_review_v1",
        "reviewer": "external_source_only_agent",
        "outputs": {
            FIXTURE_ID: {
                "expected_fact_count": 0,
                "forbidden_fact_count": 0,
                "source_only_basis": "source-only fixture packet",
            }
        },
        **overrides,
    }
    return json.dumps(payload, indent=2)


def test_import_source_oracle_review_copies_review_outputs_only(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(),
            f"{FIXTURE_ID}/expected_facts.pl": "demo_oracle(Row, alpha, Src).\n",
            f"{FIXTURE_ID}/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
            f"{FIXTURE_ID}/source.md": "This source prose must not be retained.\n",
            "expected_facts_TEMPLATE.pl": "template\n",
            "review_notes.md": "Notes may be retained.\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")

    report = import_review_zip(
        zip_path=package,
        proposal_path=proposal,
        dest_root=tmp_path / "reviews",
        review_id="demo_source_oracle_review_20260605",
    )

    assert report["summary"]["status"] == "pass"
    review_dir = tmp_path / "reviews" / "demo_source_oracle_review_20260605"
    assert (review_dir / "manifest.json").exists()
    assert (review_dir / FIXTURE_ID / "expected_facts.pl").read_text(encoding="utf-8") == "demo_oracle(Row, alpha, Src).\n"
    assert (review_dir / FIXTURE_ID / "forbidden_facts.pl").exists()
    assert (review_dir / "review_notes.md").exists()
    assert not (review_dir / FIXTURE_ID / "source.md").exists()
    assert f"{FIXTURE_ID}/source.md" in report["dropped_entries"]
    normalized = json.loads((review_dir / "manifest.json").read_text(encoding="utf-8"))
    assert normalized["predicate"] == "demo_oracle/3"
    assert normalized["outputs"][FIXTURE_ID]["expected_fact_count"] == 1
    assert normalized["outputs"][FIXTURE_ID]["source_files"] == [
        "datasets/compile_micro_fixtures/fda_warning_letter_domain_transfer_002/source.md"
    ]


def test_import_source_oracle_review_derives_review_id_from_zip_when_missing(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "returned packet.zip",
        {
            "manifest.json": _manifest(),
            f"{FIXTURE_ID}/expected_facts.pl": "demo_oracle(Row, alpha, Src).\n",
            f"{FIXTURE_ID}/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")

    report = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "pass"
    assert report["review_id"] == "demo_source_oracle_proposal_v1_returned_packet"


def test_import_source_oracle_review_refuses_overwrite_without_flag(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(),
            f"{FIXTURE_ID}/expected_facts.pl": "demo_oracle(Row, alpha, Src).\n",
            f"{FIXTURE_ID}/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")
    dest = tmp_path / "reviews"

    first = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=dest, review_id="demo_review")
    second = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=dest, review_id="demo_review")

    assert first["summary"]["status"] == "pass"
    assert second["summary"]["status"] == "fail"
    assert "destination_exists:demo_review" in second["errors"]


def test_import_source_oracle_review_dry_run_does_not_write(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(),
            f"{FIXTURE_ID}/expected_facts.pl": "demo_oracle(Row, alpha, Src).\n",
            f"{FIXTURE_ID}/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")
    dest = tmp_path / "reviews"

    report = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=dest, dry_run=True)

    assert report["summary"]["status"] == "pass"
    assert report["summary"]["dry_run"] is True
    assert not dest.exists()


def test_import_source_oracle_review_blocks_wrong_fact_shape(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(),
            f"{FIXTURE_ID}/expected_facts.pl": "wrong_oracle(Row, alpha, Src).\n",
            f"{FIXTURE_ID}/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")

    report = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "fail"
    assert "audit:expected_facts.pl:line_1:predicate_mismatch:wrong_oracle" in report["errors"]


def test_import_source_oracle_review_blocks_missing_source_fixture(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(outputs={"missing_fixture_001": {}}),
            "missing_fixture_001/expected_facts.pl": "demo_oracle(Row, alpha, Src).\n",
            "missing_fixture_001/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")

    report = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "fail"
    assert "source_file_not_found_for_fixture:missing_fixture_001" in report["errors"]


def test_import_source_oracle_review_blocks_explicit_model_output_exposure(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(reviewer_read_model_outputs=True),
            f"{FIXTURE_ID}/expected_facts.pl": "demo_oracle(Row, alpha, Src).\n",
            f"{FIXTURE_ID}/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")

    report = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "fail"
    assert "returned_manifest_declares_model_output_exposure" in report["errors"]


def test_import_source_oracle_review_blocks_explicit_non_source_only_manifest(tmp_path: Path) -> None:
    package = _write_zip(
        tmp_path / "review.zip",
        {
            "manifest.json": _manifest(source_only_review=False),
            f"{FIXTURE_ID}/expected_facts.pl": "demo_oracle(Row, alpha, Src).\n",
            f"{FIXTURE_ID}/forbidden_facts.pl": "demo_oracle(_, forbidden_value, _).\n",
        },
    )
    proposal = _proposal(tmp_path / "proposal.json")

    report = import_review_zip(zip_path=package, proposal_path=proposal, dest_root=tmp_path / "reviews")

    assert report["summary"]["status"] == "fail"
    assert "returned_manifest_declares_not_source_only" in report["errors"]
