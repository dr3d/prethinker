import unittest

from kb_pipeline import (
    _clarification_policy_decision,
    _detect_utterance_language_profile,
    _pre_normalize_utterance,
)


class LanguageProfileRoutingTests(unittest.TestCase):
    def test_detects_english_profile(self) -> None:
        profile = _detect_utterance_language_profile(
            "Goldilocks walked through the forest and found a house."
        )
        self.assertEqual(profile.get("profile"), "english")

    def test_detects_non_english_profile(self) -> None:
        profile = _detect_utterance_language_profile(
            "La madre de Scott estaba en la casa y su hermano tambien."
        )
        self.assertEqual(profile.get("profile"), "non_english")

    def test_detects_mixed_profile(self) -> None:
        profile = _detect_utterance_language_profile(
            "En enero de 2021, Nora was the director and la contable era Elias."
        )
        self.assertEqual(profile.get("profile"), "mixed")

    def test_pre_normalizer_applies_multilingual_normalization(self) -> None:
        normalized, events = _pre_normalize_utterance(
            "La madre de Scott es Ann y su hermano es Blake."
        )
        self.assertIn("mother", normalized.lower())
        self.assertIn("brother", normalized.lower())
        self.assertTrue(
            any(
                isinstance(row, dict)
                and str(row.get("kind", "")).strip() == "multilingual_phrase_normalization"
                for row in events
            )
        )

    def test_pre_normalizer_handles_spanish_role_phrase(self) -> None:
        normalized, events = _pre_normalize_utterance(
            "En enero de 2021, la contable era Elias Shore."
        )
        lowered = normalized.lower()
        self.assertIn("in january", lowered)
        self.assertIn("bookkeeper", lowered)
        self.assertTrue(
            any(
                isinstance(row, dict)
                and str(row.get("kind", "")).strip() == "multilingual_phrase_normalization"
                for row in events
            )
        )

    def test_pre_normalizer_skips_explicit_logic_calls(self) -> None:
        text = "parent(scott, madre)."
        normalized, events = _pre_normalize_utterance(text)
        self.assertEqual(normalized, text)
        self.assertFalse(
            any(
                isinstance(row, dict)
                and str(row.get("kind", "")).strip() == "multilingual_phrase_normalization"
                for row in events
            )
        )

    def test_non_english_profile_increases_clarification_pressure_for_writes(self) -> None:
        parsed = {
            "intent": "assert_fact",
            "logic_string": "parent(ann, scott).",
            "ambiguities": [],
            "needs_clarification": False,
            "uncertainty_score": 0.22,
        }
        english_decision = _clarification_policy_decision(
            parsed=parsed,
            clarification_eagerness=0.2,
            utterance="Ann is Scott's parent.",
            language_profile={"profile": "english", "confidence": 0.9},
        )
        foreign_decision = _clarification_policy_decision(
            parsed=parsed,
            clarification_eagerness=0.2,
            utterance="La madre de Scott es Ann.",
            language_profile={"profile": "non_english", "confidence": 0.9},
        )
        self.assertFalse(bool(english_decision.get("request_clarification")))
        self.assertTrue(bool(foreign_decision.get("request_clarification")))
        self.assertGreater(
            float(foreign_decision.get("effective_uncertainty", 0.0)),
            float(english_decision.get("effective_uncertainty", 0.0)),
        )


if __name__ == "__main__":
    unittest.main()
