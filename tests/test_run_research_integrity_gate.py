from pathlib import Path

from scripts.run_research_integrity_gate import build_steps


def test_research_integrity_gate_builds_artifact_audits_when_compile_root_present(tmp_path: Path) -> None:
    steps = build_steps(
        compile_root=tmp_path / "compiles",
        fixtures=["fixture_a", "fixture_b"],
        out_dir=tmp_path / "out",
        include_tests=False,
    )

    names = [step["name"] for step in steps]
    assert names == [
        "sign_clean_audit",
        "atom_shape_audit",
        "carrier_value_domain_audit",
        "domain_omission_accountability_audit",
    ]
    atom_cmd = steps[1]["cmd"]
    assert "--enforce-atom-shape" in atom_cmd
    assert "--enforce-registered-signatures" in atom_cmd
    assert "--enforce-lens-scope" in atom_cmd
    assert atom_cmd[atom_cmd.index("--max-examples") + 1] == "1000"
    assert atom_cmd.count("--fixture") == 2


def test_research_integrity_gate_can_build_code_only_gate(tmp_path: Path) -> None:
    steps = build_steps(
        compile_root=None,
        fixtures=[],
        out_dir=tmp_path / "out",
        include_tests=True,
    )

    assert [step["name"] for step in steps] == ["sign_clean_audit", "focused_governance_tests"]
