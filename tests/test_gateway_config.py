import tempfile
import unittest
from pathlib import Path

from ui_gateway.gateway.config import ConfigStore


class GatewayConfigTests(unittest.TestCase):
    def test_freethinker_defaults_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            config = store.get().to_dict()
            self.assertEqual(config.get("freethinker_resolution_policy"), "off")
            self.assertEqual(config.get("freethinker_model"), "qwen3.5:9b")
            self.assertEqual(
                config.get("freethinker_prompt_file"),
                "modelfiles/freethinker_system_prompt.md",
            )

    def test_invalid_freethinker_settings_are_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            updated = store.update(
                {
                    "freethinker_resolution_policy": "wild_guessing",
                    "freethinker_backend": "unknown",
                    "freethinker_context_length": 128,
                    "freethinker_timeout": 0,
                }
            ).to_dict()
            self.assertEqual(updated.get("freethinker_resolution_policy"), "off")
            self.assertEqual(updated.get("freethinker_backend"), "ollama")
            self.assertEqual(updated.get("freethinker_context_length"), 512)
            self.assertEqual(updated.get("freethinker_timeout"), 5)


if __name__ == "__main__":
    unittest.main()
