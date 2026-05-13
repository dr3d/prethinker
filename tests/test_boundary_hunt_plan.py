from pathlib import Path

from scripts.plan_boundary_hunt import build_report, render_markdown


def test_boundary_hunt_plan_classifies_compile_surface_classes(tmp_path: Path) -> None:
    qa_path = tmp_path / "domain_bootstrap_qa_sample.json"
    qa_path.write_text(
        """
{
  "qa_file": "C:/prethinker/datasets/story_worlds/sample_probe/qa.md",
  "rows": [
    {
      "id": "q001",
      "utterance": "Who approved the current permit?",
      "reference_answer": "Person A.",
      "queries": ["permit_status(Permit, Status)."],
      "reference_judge": {"verdict": "miss"},
      "failure_surface": {
        "surface": "compile_surface_gap",
        "rationale": "No predicate links the approver to the permit authority."
      }
    },
    {
      "id": "q002",
      "utterance": "When did the corrected status become effective?",
      "reference_answer": "May 5.",
      "queries": ["status_at(Item, Date, Status)."],
      "reference_judge": {"verdict": "partial"},
      "failure_surface": {
        "surface": "compile_surface_gap",
        "rationale": "The status exists but the corrected effective date is absent."
      }
    },
    {
      "id": "q003",
      "utterance": "What is the current status?",
      "reference_answer": "active",
      "queries": ["status_at(Item, Date, Status)."],
      "reference_judge": {"verdict": "exact"},
      "failure_surface": {"surface": "not_applicable", "rationale": "exact"}
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    report = build_report([qa_path])

    assert report["summary"]["question_count"] == 3
    assert report["summary"]["not_exact"] == 2
    assert report["summary"]["failure_surface_counts"] == {"compile_surface_gap": 2}
    assert report["summary"]["compile_surface_class_counts"] == {
        "wrong_authority_envelope": 1,
        "wrong_temporal_envelope": 1,
    }


def test_boundary_hunt_markdown_renders_samples(tmp_path: Path) -> None:
    qa_path = tmp_path / "domain_bootstrap_qa_sample.json"
    qa_path.write_text(
        """
{
  "rows": [
    {
      "id": "q001",
      "utterance": "How many active items remain?",
      "reference_answer": "3.",
      "queries": ["item_status(Item, active)."],
      "reference_judge": {"verdict": "miss"},
      "failure_surface": {
        "surface": "compile_surface_gap",
        "rationale": "The count is not emitted as a compact coordinate."
      }
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    markdown = render_markdown(build_report([qa_path]))

    assert "# Boundary Hunt Plan" in markdown
    assert "`wrong_granularity`" in markdown
    assert "How many active items remain?" in markdown


def test_boundary_hunt_plan_classifies_hybrid_join_classes(tmp_path: Path) -> None:
    qa_path = tmp_path / "domain_bootstrap_qa_sample.json"
    qa_path.write_text(
        """
{
  "rows": [
    {
      "id": "q001",
      "utterance": "What is the final expiration date after the tolling interval and granted extension?",
      "reference_answer": "May 19.",
      "queries": ["permit_status(Permit, issued).", "tolling_event(Permit, Event, Start, End).", "extension_granted(Permit, Extension, Date, Days)."],
      "reference_judge": {"verdict": "miss"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "The atomic facts exist but the deadline calculation is not assembled."
      }
    },
    {
      "id": "q002",
      "utterance": "Who authorized access while the item was in physical custody?",
      "reference_answer": "The governing body.",
      "queries": ["item_custody(Item, Holder, Status).", "access_event(Event, Viewer, Item, Authority)."],
      "reference_judge": {"verdict": "partial"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "Custody and access authority are present but not bound together."
      }
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    report = build_report([qa_path])
    markdown = render_markdown(report)

    assert report["summary"]["hybrid_join_class_counts"] == {
        "authority_custody_join": 1,
        "temporal_rule_join": 1,
    }
    assert "`temporal_rule_join`" in markdown
    assert "`authority_custody_join`" in markdown


def test_boundary_hunt_plan_classifies_status_timeline_density(tmp_path: Path) -> None:
    qa_path = tmp_path / "domain_bootstrap_qa_sample.json"
    qa_path.write_text(
        """
{
  "rows": [
    {
      "id": "q001",
      "utterance": "How many items remain unresolved at packet close?",
      "reference_answer": "3.",
      "queries": ["item_status(Item, unresolved)."],
      "reference_judge": {"verdict": "miss"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "The rows exist but require status aggregation at the end state."
      }
    },
    {
      "id": "q002",
      "utterance": "What is the current authoritative layer of record?",
      "reference_answer": "revision layer.",
      "queries": ["layer_effective_period(Layer, Start, End)."],
      "reference_judge": {"verdict": "partial"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "The answer requires current record-of-authority resolution."
      }
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    report = build_report([qa_path])

    assert report["summary"]["status_timeline_density_class_counts"] == {
        "superseded_record_of_authority": 1,
        "status_count_aggregation": 1,
    }


def test_boundary_hunt_plan_classifies_status_count_evidence_shape(tmp_path: Path) -> None:
    qa_path = tmp_path / "domain_bootstrap_qa_sample.json"
    qa_path.write_text(
        """
{
  "rows": [
    {
      "id": "q001",
      "utterance": "How many items remain unresolved?",
      "reference_answer": "3.",
      "queries": ["item_status(Item, unresolved)."],
      "reference_judge": {"verdict": "miss"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "The query retrieves status rows but needs a count."
      }
    },
    {
      "id": "q002",
      "utterance": "How many violations are documented?",
      "reference_answer": "5.",
      "queries": ["event_status(Event, invalid).", "penalty_applied(Event, Penalty, active)."],
      "reference_judge": {"verdict": "partial"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "The answer requires union across event status and penalty predicates."
      }
    },
    {
      "id": "q003",
      "utterance": "How many records are in the stated total?",
      "reference_answer": "23.",
      "queries": ["tree_status(Tree, protected)."],
      "reference_judge": {"verdict": "miss"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "The explicit count is present only in source_record_text_atom."
      }
    },
    {
      "id": "q004",
      "utterance": "If the status reclassification is adopted, how many total units would there be?",
      "reference_answer": "157.",
      "queries": ["total_unit_count(Count)."],
      "reference_judge": {"verdict": "miss"},
      "failure_surface": {
        "surface": "hybrid_join_gap",
        "rationale": "The existing total is present but the counterfactual increment must be added."
      }
    }
  ]
}
""".strip(),
        encoding="utf-8",
    )

    report = build_report([qa_path])

    assert report["summary"]["status_count_evidence_class_counts"] == {
        "counterfactual_increment_count": 1,
        "explicit_source_count": 1,
        "multi_predicate_union_count": 1,
        "single_predicate_status_count": 1,
    }
