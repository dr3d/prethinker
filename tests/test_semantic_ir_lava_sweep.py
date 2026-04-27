from __future__ import annotations

from scripts.run_semantic_ir_lava_sweep import apply_mapped_directly, select_base_cases
from scripts.run_semantic_ir_lava_sweep import LavaCase
from src.mcp_server import PrologMCPServer


def test_lava_direct_apply_records_but_skips_queries_by_default():
    server = PrologMCPServer()
    mapped = {
        "intent": "query",
        "admission_diagnostics": {
            "clauses": {
                "facts": ["parent(noel, rhea)."],
                "rules": ["ancestor(X, Y) :- parent(X, Y)."],
                "queries": ["ancestor(noel, rhea)."],
                "retracts": [],
            }
        },
    }

    result = apply_mapped_directly(server, mapped)

    assert result["status"] == "success"
    assert result["writes_applied"] == 2
    assert result["errors"] == []
    assert result["operations"][-1]["tool"] == "query_rows"
    assert result["operations"][-1]["result"]["status"] == "skipped"
    assert server.query_rows("ancestor(noel, rhea).")["status"] == "success"


def test_lava_balanced_sampling_spreads_source_families():
    cases = [
        LavaCase(id=f"rung_{i}", source="kb_scenario:rung_many", utterance=f"rung {i}")
        for i in range(12)
    ]
    cases.extend(
        [
            LavaCase(id="medical", source="medical", utterance="Mara's pressure is high."),
            LavaCase(id="legal", source="dataset:legal_seed", utterance="Court held X."),
            LavaCase(id="story", source="goldilocks", utterance="Goldilocks found porridge."),
        ]
    )

    import random

    selected = select_base_cases(cases, limit=4, mode="balanced", rng=random.Random(7))
    sources = {case.source.split(":", 1)[0] for case in selected}

    assert len(selected) == 4
    assert {"medical", "dataset", "goldilocks"} <= sources
