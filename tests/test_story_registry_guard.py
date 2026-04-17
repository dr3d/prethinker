from scripts.story_registry_guard import (
    infer_registry_profile,
    registry_profile_mismatch_message,
)


def test_infer_registry_profile_general_variants():
    assert infer_registry_profile("modelfiles/predicate_registry.json") == "general"
    assert infer_registry_profile("modelfiles/predicate_registry.general.json") == "general"


def test_infer_registry_profile_domain_specific():
    assert infer_registry_profile("modelfiles/predicate_registry.blocksworld.json") == "blocksworld"


def test_registry_profile_mismatch_detects_story_vs_blocksworld():
    message = registry_profile_mismatch_message(
        "modelfiles/predicate_registry.blocksworld.json",
        label="mid_pack",
        story_path="tmp/story_inputs/mid.txt",
        allow_cross_domain_registry=False,
    )
    assert "blocksworld" in message
    assert "allow-cross-domain-registry" in message


def test_registry_profile_mismatch_allows_override():
    message = registry_profile_mismatch_message(
        "modelfiles/predicate_registry.blocksworld.json",
        label="mid_pack",
        story_path="tmp/story_inputs/mid.txt",
        allow_cross_domain_registry=True,
    )
    assert message == ""
