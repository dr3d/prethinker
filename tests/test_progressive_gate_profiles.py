import unittest

from scripts.run_story_progressive_gulp import (
    ENGLISH_STRICT_GATE_DEFAULTS,
    MULTILINGUAL_EXPERIMENTAL_GATES,
    _detect_story_language_profile,
    _resolve_gate_value,
)


class ProgressiveGateProfileTests(unittest.TestCase):
    def test_detect_story_language_profile_non_english(self) -> None:
        profile = _detect_story_language_profile(
            "La madre de Scott estaba en la casa. Su hermano llego despues."
        )
        self.assertEqual(profile.get("profile"), "non_english")

    def test_resolve_gate_value_uses_profile_default_when_unmodified(self) -> None:
        value = _resolve_gate_value(
            requested=float(ENGLISH_STRICT_GATE_DEFAULTS["coverage"]),
            english_default=float(ENGLISH_STRICT_GATE_DEFAULTS["coverage"]),
            profile_default=float(MULTILINGUAL_EXPERIMENTAL_GATES["coverage"]),
        )
        self.assertAlmostEqual(
            value,
            float(MULTILINGUAL_EXPERIMENTAL_GATES["coverage"]),
            places=6,
        )

    def test_resolve_gate_value_preserves_user_override(self) -> None:
        value = _resolve_gate_value(
            requested=0.77,
            english_default=float(ENGLISH_STRICT_GATE_DEFAULTS["coverage"]),
            profile_default=float(MULTILINGUAL_EXPERIMENTAL_GATES["coverage"]),
        )
        self.assertAlmostEqual(value, 0.77, places=6)


if __name__ == "__main__":
    unittest.main()
