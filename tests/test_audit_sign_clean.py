from scripts.audit_sign_clean import build_report


def test_sign_clean_audit_blocks_claims_when_free_text_routing_exists() -> None:
    report = build_report(max_regex_rows=20)

    assert report["schema_version"] == "prethinker_sign_clean_audit_v1"
    assert report["claim_status"] == "blocked"
    assert report["summary"]["status"] == "fail"
    assert report["summary"]["blocker_count"] >= 1
    assert report["summary"]["free_text_semantic_routing_count"] > 0


def test_sign_clean_audit_has_no_raw_utterance_or_legacy_vocabulary_blockers() -> None:
    report = build_report(max_regex_rows=20)
    blocker_classes = {row["class"] for row in report["blockers"]}

    assert "raw_utterance_semantic_regex" not in blocker_classes
    assert "high_risk_corpus_shaped_active_vocabulary" not in blocker_classes
    assert "free_text_semantic_routing" in blocker_classes
    assert report["summary"]["raw_utterance_semantic_regex_count"] == 0
    assert report["summary"]["high_risk_active_vocabulary_count"] == 0
