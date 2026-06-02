from pathlib import Path

from scripts.run_domain_transfer_gate import build_steps, render_markdown


def test_domain_transfer_gate_builds_expected_forbidden_and_integrity_steps(tmp_path: Path) -> None:
    compile_root = tmp_path / "compile_root"
    compile_paths = [
        tmp_path / "run1.json",
        tmp_path / "run2.json",
        tmp_path / "run3.json",
    ]

    steps = build_steps(
        fixture="fda_transfer_demo",
        compile_root=compile_root,
        compile_paths=compile_paths,
        support_threshold=2,
        matcher="constant_slot",
        out_dir=tmp_path / "out",
        include_tests=False,
    )

    assert [step["name"] for step in steps] == [
        "typed_micro_series_expected_forbidden",
        "research_integrity_gate",
    ]
    summary_cmd = steps[0]["cmd"]
    assert "--enforce-supported" in summary_cmd
    assert "--enforce-no-forbidden" in summary_cmd
    assert summary_cmd.count("--compile-json") == 3
    assert summary_cmd[summary_cmd.index("--matcher") + 1] == "constant_slot"

    integrity_cmd = steps[1]["cmd"]
    assert "scripts/run_research_integrity_gate.py" in integrity_cmd
    assert "--compile-root" in integrity_cmd
    assert "--skip-tests" in integrity_cmd


def test_domain_transfer_gate_markdown_reports_failed_steps() -> None:
    markdown = render_markdown(
        {
            "fixture": "demo",
            "out_dir": "out",
            "summary": {"status": "fail", "step_count": 2, "failed_steps": 1},
            "steps": [
                {"name": "typed_micro_series_expected_forbidden", "status": "pass", "returncode": 0},
                {"name": "research_integrity_gate", "status": "fail", "returncode": 1},
            ],
        }
    )

    assert "- Status: `fail`" in markdown
    assert "| `research_integrity_gate` | `fail` | 1 |" in markdown
