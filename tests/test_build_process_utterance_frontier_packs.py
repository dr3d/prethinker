import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "build_process_utterance_frontier_packs.py"
SPEC = importlib.util.spec_from_file_location("build_process_utterance_frontier_packs", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_distill_correction_setup_turns_builds_prior_holder_assertion():
    turns = MODULE._distill_correction_setup_turns("actually no, cart is with Mara not Scott")
    assert turns == [{"utterance": "remember that cart is with Scott"}]


def test_normalized_tags_handles_hyphenated_and_spaced_tags():
    tags = MODULE._normalized_tags(["over-clarification", "temporal mismatch", ""])
    assert "over_clarification" in tags
    assert "temporal_mismatch" in tags
