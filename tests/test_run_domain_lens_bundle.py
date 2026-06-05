import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.run_domain_lens_bundle import (
    LensSpec,
    _build_atom_audit_command,
    _build_lens_compile_command,
    _build_reconcile_command,
    _build_score_command,
    _build_value_domain_audit_command,
    _load_registry_lenses,
    _load_summary,
    _parse_lens_domain_hints,
    _selected_lenses,
)


def test_load_registry_lenses_and_select_requested(tmp_path: Path) -> None:
    registry = tmp_path / "registry.json"
    registry.write_text(
        json.dumps(
            {
                "lenses": [
                    {"id": "wrapper", "purpose": "Wrapper facts."},
                    {"id": "timeline", "purpose": "Timeline facts."},
                ]
            }
        ),
        encoding="utf-8",
    )

    lenses = _load_registry_lenses(registry)

    assert [lens.lens_id for lens in lenses] == ["wrapper", "timeline"]
    assert _selected_lenses(lenses, ["timeline"]) == [LensSpec("timeline", "Timeline facts.")]
    with pytest.raises(ValueError, match="unknown lens"):
        _selected_lenses(lenses, ["missing"])


def test_parse_lens_domain_hints_requires_lens_prefix() -> None:
    assert _parse_lens_domain_hints(["wrapper=Use wrapper only."]) == {
        "wrapper": "Use wrapper only."
    }

    with pytest.raises(ValueError, match="lens_id=hint"):
        _parse_lens_domain_hints(["Use wrapper only."])


def test_build_lens_compile_command_restricts_registry_lens() -> None:
    args = SimpleNamespace(
        domain_hint="Base domain.",
        backend="lmstudio",
        model="qwen/test",
        base_url="http://127.0.0.1:1234",
        temperature=0,
        top_p=1.0,
        top_k=20,
        num_ctx=65536,
        max_tokens=12000,
        timeout=420,
    )

    command = _build_lens_compile_command(
        text_file=Path("source.md"),
        profile_registry=Path("registry.json"),
        lens=LensSpec("timeline", "Timeline facts."),
        lens_hint="",
        args=args,
    )

    assert command[0] == sys.executable
    assert "--profile-registry-lens" in command
    assert command[command.index("--profile-registry-lens") + 1] == "timeline"
    assert "--use-profile-registry-direct" in command
    assert "--compile-source" in command
    assert "--require-source-compile-ok" in command
    hint = command[command.index("--domain-hint") + 1]
    assert "Base domain." in hint
    assert "Lens timeline: Timeline facts." in hint
    assert "Do not place source prose" in hint


def test_build_lens_compile_command_can_use_source_pass_ops_schema() -> None:
    args = SimpleNamespace(
        domain_hint="",
        backend="lmstudio",
        model="qwen/test",
        base_url="http://127.0.0.1:1234",
        temperature=0,
        top_p=1.0,
        top_k=20,
        num_ctx=65536,
        max_tokens=12000,
        timeout=420,
        focused_pass_ops_schema=True,
        compile_plan_passes=True,
        profile_registry_lens_plan=True,
    )

    command = _build_lens_compile_command(
        text_file=Path("source.md"),
        profile_registry=Path("registry.json"),
        lens=LensSpec("wrapper", "Wrapper facts."),
        lens_hint="",
        args=args,
    )

    assert "--focused-pass-ops-schema" in command
    assert "--compile-plan-passes" in command
    assert "--profile-registry-lens-plan" in command


def test_score_command_enforces_forbidden_without_requiring_full_support() -> None:
    command = _build_score_command(
        fixture="fixture_1",
        union_jsons=[Path("run1.json"), Path("run2.json")],
        out_json=Path("summary.json"),
        out_md=Path("summary.md"),
        support_threshold=2,
        matcher="constant_slot",
        apply_domain_reducers=True,
    )

    assert "--enforce-no-forbidden" in command
    assert "--enforce-supported" not in command
    assert "--apply-domain-reducers" in command
    assert command.count("--compile-json") == 2


def test_atom_audit_command_can_enforce_lens_scope() -> None:
    command = _build_atom_audit_command(
        compile_root=Path("lens-root"),
        out_json=Path("audit.json"),
        out_md=Path("audit.md"),
        enforce_lens_scope=True,
    )

    assert "--enforce-atom-shape" in command
    assert "--enforce-registered-signatures" in command
    assert "--enforce-lens-scope" in command


def test_value_domain_audit_command_bites_by_default() -> None:
    command = _build_value_domain_audit_command(
        compile_root=Path("union-root"),
        out_json=Path("value-domains.json"),
        out_md=Path("value-domains.md"),
    )

    assert "audit_carrier_value_domains.py" in command[1]
    assert "--compile-root" in command
    assert command[command.index("--compile-root") + 1] == "union-root"
    assert "--out-json" in command
    assert "--out-md" in command
    assert "--exit-zero" not in command


def test_reconcile_command_uses_value_support_without_exit_zero() -> None:
    command = _build_reconcile_command(
        fixture="fixture_1",
        union_jsons=[Path("run1.json"), Path("run2.json")],
        out_json=Path("reconcile.json"),
        out_md=Path("reconcile.md"),
        min_support=2,
    )

    assert "reconcile_typed_micro_compiles.py" in command[1]
    assert "--fixture-id" in command
    assert command[command.index("--fixture-id") + 1] == "fixture_1"
    assert "--min-support" in command
    assert command[command.index("--min-support") + 1] == "2"
    assert "--support-mode" in command
    assert command[command.index("--support-mode") + 1] == "value"
    assert command.count("--compile-json") == 2
    assert "--exit-zero" not in command


def test_load_summary_understands_reconcile_artifact_shape(tmp_path: Path) -> None:
    artifact = tmp_path / "reconcile.json"
    artifact.write_text(
        json.dumps(
            {
                "source_compile": {
                    "unique_fact_count": 2,
                    "governed_reconciliation": {
                        "fixture_id": "fixture_1",
                        "input_count": 3,
                        "min_support": 2,
                        "support_mode": "value",
                        "fact_support": [{"fact": "a."}, {"fact": "b."}],
                        "singleton_fact_count": 0,
                        "skipped_count": 1,
                        "conflicts": [{"type": "conflict"}],
                    },
                }
            }
        ),
        encoding="utf-8",
    )

    assert _load_summary(artifact) == {
        "fixture_id": "fixture_1",
        "input_count": 3,
        "min_support": 2,
        "support_mode": "value",
        "reconciled_fact_count": 2,
        "singleton_fact_count": 0,
        "conflict_count": 1,
        "skipped_count": 1,
        "fact_support_count": 2,
    }
