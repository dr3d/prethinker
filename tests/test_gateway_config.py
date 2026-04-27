import tempfile
import unittest
from pathlib import Path

from ui_gateway.gateway.config import ConfigStore


class GatewayConfigTests(unittest.TestCase):
    def test_freethinker_defaults_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            config = store.get().to_dict()
            self.assertEqual(config.get("active_profile"), "general")
            self.assertEqual(config.get("reply_surface_policy"), "deterministic_template")
            self.assertEqual(config.get("freethinker_resolution_policy"), "off")
            self.assertEqual(config.get("freethinker_model"), "qwen3.5:9b")
            self.assertEqual(config.get("freethinker_temperature"), 0.2)
            self.assertFalse(config.get("freethinker_thinking"))
            self.assertEqual(config.get("compiler_backend"), "lmstudio")
            self.assertEqual(config.get("compiler_model"), "qwen/qwen3.6-35b-a3b")
            self.assertTrue(config.get("semantic_ir_enabled"))
            self.assertEqual(config.get("semantic_ir_model"), "qwen/qwen3.6-35b-a3b")
            self.assertEqual(config.get("semantic_ir_temperature"), 0.0)
            self.assertEqual(config.get("semantic_ir_top_p"), 0.82)
            self.assertEqual(config.get("semantic_ir_top_k"), 20)
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
                    "freethinker_temperature": 9,
                    "freethinker_thinking": 1,
                }
            ).to_dict()
            self.assertEqual(updated.get("freethinker_resolution_policy"), "off")
            self.assertEqual(updated.get("freethinker_backend"), "ollama")
            self.assertEqual(updated.get("freethinker_context_length"), 512)
            self.assertEqual(updated.get("freethinker_timeout"), 5)
            self.assertEqual(updated.get("freethinker_temperature"), 2.0)
            self.assertTrue(updated.get("freethinker_thinking"))

    def test_invalid_semantic_ir_settings_are_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            updated = store.update(
                {
                    "semantic_ir_enabled": 1,
                    "semantic_ir_context_length": 128,
                    "semantic_ir_timeout": 0,
                    "semantic_ir_temperature": 9,
                    "semantic_ir_top_p": 4,
                    "semantic_ir_top_k": 0,
                    "semantic_ir_thinking": 1,
                }
            ).to_dict()
            self.assertTrue(updated.get("semantic_ir_enabled"))
            self.assertEqual(updated.get("semantic_ir_context_length"), 512)
            self.assertEqual(updated.get("semantic_ir_timeout"), 5)
            self.assertEqual(updated.get("semantic_ir_temperature"), 2.0)
            self.assertEqual(updated.get("semantic_ir_top_p"), 1.0)
            self.assertEqual(updated.get("semantic_ir_top_k"), 1)
            self.assertTrue(updated.get("semantic_ir_thinking"))

    def test_invalid_active_profile_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            updated = store.update({"active_profile": "wizard-doctor"}).to_dict()
            self.assertEqual(updated.get("active_profile"), "general")

    def test_active_profile_accepts_auto_and_domain_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            self.assertEqual(store.update({"active_profile": "auto"}).to_dict().get("active_profile"), "auto")
            self.assertEqual(
                store.update({"active_profile": "courtlistener"}).to_dict().get("active_profile"),
                "legal_courtlistener@v0",
            )
            self.assertEqual(
                store.update({"active_profile": "contracts"}).to_dict().get("active_profile"),
                "sec_contracts@v0",
            )

    def test_invalid_reply_surface_policy_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            updated = store.update({"reply_surface_policy": "poetic"}).to_dict()
            self.assertEqual(updated.get("reply_surface_policy"), "deterministic_template")

    def test_invalid_served_provider_is_sanitized(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            updated = store.update({"served_llm_provider": "mystery"}).to_dict()
            self.assertEqual(updated.get("served_llm_provider"), "ollama")

    def test_strict_mode_invariants_override_related_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ConfigStore(Path(tmpdir) / "gateway_config.json")
            updated = store.update(
                {
                    "strict_mode": True,
                    "compiler_mode": "auto",
                    "served_handoff_mode": "always",
                    "require_final_confirmation": False,
                }
            ).to_dict()
            self.assertEqual(updated.get("compiler_mode"), "strict")
            self.assertEqual(updated.get("served_handoff_mode"), "never")
            self.assertTrue(updated.get("require_final_confirmation"))


if __name__ == "__main__":
    unittest.main()
