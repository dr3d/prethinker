from pathlib import Path

from scripts.run_domain_bootstrap_qa_batch import _build_command, _build_job, _render_md, _summarize, _summarize_existing_job


def test_qa_batch_accepts_markdown_answer_key_without_oracle(tmp_path: Path) -> None:
    dataset_root = tmp_path / "datasets"
    compile_root = tmp_path / "compiles"
    out_root = tmp_path / "qa"
    fixture = "markdown_answer_fixture"
    fixture_dir = dataset_root / fixture
    compile_dir = compile_root / fixture
    fixture_dir.mkdir(parents=True)
    compile_dir.mkdir(parents=True)
    (fixture_dir / "qa.md").write_text("1. What happened?\n\n## Answers\n\n1. It happened.\n", encoding="utf-8")
    (compile_dir / "domain_bootstrap_file_20260512T000000Z_source_model.json").write_text("{}", encoding="utf-8")

    job = _build_job(fixture, dataset_root=dataset_root, compile_root=compile_root, out_root=out_root)
    command = _build_command(
        job,
        model="test-model",
        base_url="http://example.test/v1",
        limit=3,
        timeout=10,
        evidence_bundle=False,
        classify_failure_surfaces=True,
        cache=False,
    )

    assert job.oracle_jsonl is None
    assert job.judge_reference_answers is True
    assert "--oracle-jsonl" not in command
    assert "--judge-reference-answers" in command
    assert "--classify-failure-surfaces" in command
    assert "--no-cache" in command
    assert "--helper-companion-row-limit" in command
    assert command[command.index("--helper-companion-row-limit") + 1] == "0"
    assert "--include-legacy-native-helper-adapters" not in command

    legacy_command = _build_command(
        job,
        model="test-model",
        base_url="http://example.test/v1",
        limit=3,
        timeout=10,
        evidence_bundle=False,
        classify_failure_surfaces=True,
        cache=False,
        include_legacy_native_helper_adapters=True,
    )
    assert "--include-legacy-native-helper-adapters" in legacy_command


def test_qa_batch_stamp_command_can_run_with_helpers_genuinely_off(tmp_path: Path) -> None:
    dataset_root = tmp_path / "datasets"
    compile_root = tmp_path / "compiles"
    out_root = tmp_path / "qa"
    fixture = "stamp_fixture"
    fixture_dir = dataset_root / fixture
    compile_dir = compile_root / fixture
    fixture_dir.mkdir(parents=True)
    compile_dir.mkdir(parents=True)
    (fixture_dir / "qa.md").write_text("1. What happened?\n\n## Answers\n\n1. It happened.\n", encoding="utf-8")
    (compile_dir / "domain_bootstrap_file_20260512T000000Z_source_model.json").write_text("{}", encoding="utf-8")

    job = _build_job(fixture, dataset_root=dataset_root, compile_root=compile_root, out_root=out_root)
    command = _build_command(
        job,
        model="test-model",
        base_url="http://example.test/v1",
        limit=3,
        timeout=10,
        evidence_bundle=True,
        classify_failure_surfaces=True,
        cache=False,
        helper_companion_row_limit=0,
        include_legacy_native_helper_adapters=False,
    )

    assert "--helper-companion-row-limit" in command
    assert command[command.index("--helper-companion-row-limit") + 1] == "0"
    assert "--include-legacy-native-helper-adapters" not in command
    assert "--no-cache" in command


def test_qa_batch_summary_rolls_up_helper_pressure() -> None:
    summary = _summarize(
        [
            {
                "fixture": "fixture_a",
                "returncode": 0,
                "qa_json": "qa_a.json",
                "summary": {
                    "question_count": 10,
                    "judge_exact": 10,
                    "judge_partial": 0,
                    "judge_miss": 0,
                    "helper_class_summary": {
                        "row_count": 600,
                        "helper_class_counts": {"candidate-helper": 400, "clean-helper": 200},
                        "companion_row_totals": {"roster_state_support": 600},
                    },
                },
            },
            {
                "fixture": "fixture_b",
                "returncode": 0,
                "qa_json": "qa_b.json",
                "summary": {
                    "question_count": 10,
                    "judge_exact": 5,
                    "judge_partial": 3,
                    "judge_miss": 2,
                    "helper_class_summary": {
                        "row_count": 0,
                        "helper_class_counts": {},
                        "companion_row_totals": {},
                    },
                },
            },
        ],
        lanes=2,
        base_timeout=90,
        effective_timeout=90,
    )

    helper_pressure = summary["helper_pressure_summary"]
    assert summary["totals"]["judge_exact"] == 15
    assert helper_pressure["row_count"] == 600
    assert helper_pressure["helper_rows_per_exact"] == 40.0
    assert helper_pressure["candidate_helper_share"] == 0.6667
    assert helper_pressure["pressure_label"] == "high_candidate_helper_pressure"
    assert helper_pressure["companion_row_totals"] == {"roster_state_support": 600}

    markdown = _render_md(summary)
    assert "Helper pressure" in markdown
    assert "high_candidate_helper_pressure" in markdown


def test_qa_batch_can_summarize_existing_artifact(tmp_path: Path) -> None:
    job = type(
        "Job",
        (),
        {
            "fixture": "fixture_a",
            "out_dir": tmp_path,
        },
    )()
    (tmp_path / "domain_bootstrap_qa_20260512T000000Z_qa_model.json").write_text(
        '{"summary":{"question_count":1,"judge_exact":1}}\n',
        encoding="utf-8",
    )

    result = _summarize_existing_job(job)

    assert result["returncode"] == 0
    assert result["summary"]["judge_exact"] == 1
    assert result["stdout_tail"] == ""
