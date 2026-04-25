from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "build_umls_semantic_network_kb.py"
SPEC = importlib.util.spec_from_file_location("build_umls_semantic_network_kb", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_semantic_network_kb_writes_manifest_json_and_facts(tmp_path):
    net_dir = tmp_path / "NET"
    out_dir = tmp_path / "out"
    net_dir.mkdir()
    (net_dir / "SRDEF").write_text(
        "STY|T047|Disease or Syndrome|B2.2.1.2.1|A condition.||||dsyn|\n"
        "RL|T151|affects|R3|Affects relation.||||affects|affected_by\n",
        encoding="utf-8",
    )
    (net_dir / "SRSTR").write_text(
        "Disease or Syndrome|isa|Finding|D\n",
        encoding="utf-8",
    )

    manifest = MODULE.build_semantic_network_kb(net_dir, out_dir)

    assert manifest["missing_required_files"] == []
    assert manifest["counts"]["semantic_types"] == 1
    assert manifest["counts"]["semantic_relations"] == 1
    assert (out_dir / "manifest.json").exists()
    assert (out_dir / "semantic_network.json").exists()
    facts = (out_dir / "semantic_network_facts.pl").read_text(encoding="utf-8")
    assert "umls_semantic_parent(disease_or_syndrome, finding, 'D')." in facts


def test_build_semantic_network_kb_reports_missing_required_files(tmp_path):
    manifest = MODULE.build_semantic_network_kb(tmp_path / "missing", tmp_path / "out")

    assert manifest["missing_required_files"] == ["srdef", "srstr"]
    assert manifest["counts"]["semantic_types"] == 0
