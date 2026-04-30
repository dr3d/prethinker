from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


def _normalize_active_profile(value: object, default: str = "general") -> str:
    aliases = {
        "default": "general",
        "general": "general",
        "auto": "auto",
        "medical": "medical@v0",
        "medical@v0": "medical@v0",
        "legal": "legal_courtlistener@v0",
        "legal_courtlistener": "legal_courtlistener@v0",
        "legal_courtlistener@v0": "legal_courtlistener@v0",
        "courtlistener": "legal_courtlistener@v0",
        "sec": "sec_contracts@v0",
        "sec_contracts": "sec_contracts@v0",
        "sec_contracts@v0": "sec_contracts@v0",
        "contracts": "sec_contracts@v0",
        "story": "story_world@v0",
        "story_world": "story_world@v0",
        "story_world@v0": "story_world@v0",
        "probate": "probate@v0",
        "probate@v0": "probate@v0",
    }
    requested = str(value or default).strip().lower()
    return aliases.get(requested, aliases.get(str(default or "general").strip().lower(), "general"))


def _normalize_reply_surface_policy(value: object, default: str = "deterministic_template") -> str:
    allowed = {
        "deterministic",
        "deterministic_template",
    }
    requested = str(value or default).strip().lower()
    if requested not in allowed:
        requested = str(default or "deterministic_template").strip().lower() or "deterministic_template"
    return requested


@dataclass
class GatewayConfig:
    front_door_uri: str = "prethink://local/front-door"
    active_profile: str = "general"
    reply_surface_policy: str = "deterministic_template"
    served_llm_provider: str = "lmstudio"
    served_llm_model: str = "qwen/qwen3.6-35b-a3b"
    served_llm_base_url: str = "http://127.0.0.1:1234"
    served_llm_context_length: int = 16384
    served_llm_timeout: int = 120
    served_handoff_mode: str = "never"
    compiler_mode: str = "strict"
    compiler_prompt_mode: str = "auto"
    compiler_model: str = "qwen/qwen3.6-35b-a3b"
    compiler_backend: str = "lmstudio"
    compiler_base_url: str = "http://127.0.0.1:1234"
    compiler_context_length: int = 16384
    compiler_timeout: int = 120
    compiler_prompt_file: str = "modelfiles/blank_prompt.md"
    semantic_ir_enabled: bool = True
    semantic_ir_model: str = "qwen/qwen3.6-35b-a3b"
    semantic_ir_context_length: int = 16384
    semantic_ir_timeout: int = 120
    semantic_ir_temperature: float = 0.0
    semantic_ir_top_p: float = 0.82
    semantic_ir_top_k: int = 20
    semantic_ir_thinking: bool = False
    clarification_eagerness: float = 0.75
    require_final_confirmation: bool = True
    strict_mode: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


class ConfigStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load()

    def _load(self) -> GatewayConfig:
        if not self.path.exists():
            config = GatewayConfig()
            self.save(config)
            return config
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        sanitized = self._sanitize(payload)
        sanitized = self._migrate_semantic_ir_defaults(payload, sanitized)
        return GatewayConfig(**self._enforce_invariants(sanitized))

    def _migrate_semantic_ir_defaults(self, raw_payload: dict, sanitized: dict) -> dict:
        """Move older gateway config files onto the current Semantic IR console path.

        This only upgrades values that are absent or still equal to the old stock
        defaults, so explicit operator choices survive.
        """
        migrated = dict(sanitized)
        old_model_values = {"qwen3.5:9b", "qwen/qwen3.5-9b", "q:latest"}

        def _int_or_zero(value: object) -> int:
            try:
                return int(value or 0)
            except Exception:
                return 0

        if "semantic_ir_enabled" not in raw_payload:
            migrated["semantic_ir_enabled"] = True
        if str(raw_payload.get("semantic_ir_model", "")).strip() in {"", "qwen3.6:35b"}:
            migrated["semantic_ir_model"] = "qwen/qwen3.6-35b-a3b"

        compiler_model = str(raw_payload.get("compiler_model", "")).strip()
        if compiler_model in old_model_values:
            migrated["compiler_model"] = "qwen/qwen3.6-35b-a3b"
        if str(raw_payload.get("compiler_backend", "")).strip().lower() in {"", "ollama"} and compiler_model in old_model_values:
            migrated["compiler_backend"] = "lmstudio"
        if str(raw_payload.get("compiler_base_url", "")).strip() in {"", "http://127.0.0.1:11434"} and compiler_model in old_model_values:
            migrated["compiler_base_url"] = "http://127.0.0.1:1234"
        if _int_or_zero(raw_payload.get("compiler_timeout", 0)) in {0, 60} and compiler_model in old_model_values:
            migrated["compiler_timeout"] = 120

        served_model = str(raw_payload.get("served_llm_model", "")).strip()
        if served_model in old_model_values:
            migrated["served_llm_model"] = "qwen/qwen3.6-35b-a3b"

        return migrated

    def _sanitize(self, payload: dict) -> dict:
        allowed = GatewayConfig().__dict__.keys()
        sanitized = {key: payload[key] for key in allowed if key in payload}
        if "active_profile" in sanitized:
            sanitized["active_profile"] = _normalize_active_profile(sanitized["active_profile"])
        if "reply_surface_policy" in sanitized:
            sanitized["reply_surface_policy"] = _normalize_reply_surface_policy(
                sanitized["reply_surface_policy"]
            )
        if "compiler_context_length" in sanitized:
            try:
                sanitized["compiler_context_length"] = max(512, int(sanitized["compiler_context_length"]))
            except Exception:
                sanitized.pop("compiler_context_length", None)
        if "served_llm_context_length" in sanitized:
            try:
                sanitized["served_llm_context_length"] = max(512, int(sanitized["served_llm_context_length"]))
            except Exception:
                sanitized.pop("served_llm_context_length", None)
        if "compiler_timeout" in sanitized:
            try:
                sanitized["compiler_timeout"] = max(5, int(sanitized["compiler_timeout"]))
            except Exception:
                sanitized.pop("compiler_timeout", None)
        if "semantic_ir_context_length" in sanitized:
            try:
                sanitized["semantic_ir_context_length"] = max(512, int(sanitized["semantic_ir_context_length"]))
            except Exception:
                sanitized.pop("semantic_ir_context_length", None)
        if "semantic_ir_timeout" in sanitized:
            try:
                sanitized["semantic_ir_timeout"] = max(5, int(sanitized["semantic_ir_timeout"]))
            except Exception:
                sanitized.pop("semantic_ir_timeout", None)
        if "semantic_ir_temperature" in sanitized:
            try:
                value = float(sanitized["semantic_ir_temperature"])
                if value < 0.0:
                    value = 0.0
                if value > 2.0:
                    value = 2.0
                sanitized["semantic_ir_temperature"] = value
            except Exception:
                sanitized.pop("semantic_ir_temperature", None)
        if "semantic_ir_top_p" in sanitized:
            try:
                value = float(sanitized["semantic_ir_top_p"])
                if value < 0.0:
                    value = 0.0
                if value > 1.0:
                    value = 1.0
                sanitized["semantic_ir_top_p"] = value
            except Exception:
                sanitized.pop("semantic_ir_top_p", None)
        if "semantic_ir_top_k" in sanitized:
            try:
                sanitized["semantic_ir_top_k"] = max(1, int(sanitized["semantic_ir_top_k"]))
            except Exception:
                sanitized.pop("semantic_ir_top_k", None)
        if "served_llm_timeout" in sanitized:
            try:
                sanitized["served_llm_timeout"] = max(5, int(sanitized["served_llm_timeout"]))
            except Exception:
                sanitized.pop("served_llm_timeout", None)
        if "served_handoff_mode" in sanitized:
            mode = str(sanitized["served_handoff_mode"]).strip().lower()
            if mode not in {"never", "fallback_only", "on_other", "always"}:
                mode = "fallback_only"
            sanitized["served_handoff_mode"] = mode
        if "served_llm_provider" in sanitized:
            backend = str(sanitized["served_llm_provider"]).strip().lower()
            if backend not in {"ollama", "lmstudio"}:
                backend = "ollama"
            sanitized["served_llm_provider"] = backend
        if "compiler_mode" in sanitized:
            mode = str(sanitized["compiler_mode"]).strip().lower()
            if mode not in {"strict", "auto", "heuristic"}:
                mode = "strict"
            sanitized["compiler_mode"] = mode
        if "compiler_backend" in sanitized:
            backend = str(sanitized["compiler_backend"]).strip().lower()
            if backend not in {"ollama", "lmstudio"}:
                backend = "ollama"
            sanitized["compiler_backend"] = backend
        if "clarification_eagerness" in sanitized:
            try:
                value = float(sanitized["clarification_eagerness"])
                if value < 0.0:
                    value = 0.0
                if value > 1.0:
                    value = 1.0
                sanitized["clarification_eagerness"] = value
            except Exception:
                sanitized.pop("clarification_eagerness", None)
        if "strict_mode" in sanitized:
            sanitized["strict_mode"] = bool(sanitized["strict_mode"])
        if "require_final_confirmation" in sanitized:
            sanitized["require_final_confirmation"] = bool(sanitized["require_final_confirmation"])
        if "semantic_ir_enabled" in sanitized:
            sanitized["semantic_ir_enabled"] = bool(sanitized["semantic_ir_enabled"])
        if "semantic_ir_thinking" in sanitized:
            sanitized["semantic_ir_thinking"] = bool(sanitized["semantic_ir_thinking"])
        if "compiler_prompt_mode" in sanitized:
            mode = str(sanitized["compiler_prompt_mode"]).strip().lower()
            if mode not in {"auto", "always", "never"}:
                mode = "auto"
            sanitized["compiler_prompt_mode"] = mode
        return sanitized

    def _enforce_invariants(self, payload: dict) -> dict:
        # "Strict bouncer" means no served-LLM bypasses around deterministic gating.
        if bool(payload.get("strict_mode", True)):
            payload["compiler_mode"] = "strict"
            payload["served_handoff_mode"] = "never"
            payload["require_final_confirmation"] = True
        return payload

    def get(self) -> GatewayConfig:
        return self._config

    def update(self, updates: dict) -> GatewayConfig:
        payload = self._config.to_dict()
        payload.update(self._sanitize(updates))
        payload = self._enforce_invariants(payload)
        self._config = GatewayConfig(**payload)
        self.save(self._config)
        return self._config

    def save(self, config: GatewayConfig) -> None:
        self.path.write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")
