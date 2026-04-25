from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


def _normalize_active_profile(value: object, default: str = "general") -> str:
    aliases = {
        "default": "general",
        "general": "general",
        "medical": "medical@v0",
        "medical@v0": "medical@v0",
    }
    requested = str(value or default).strip().lower()
    return aliases.get(requested, aliases.get(str(default or "general").strip().lower(), "general"))


def _normalize_reply_surface_policy(value: object, default: str = "deterministic_template") -> str:
    allowed = {
        "deterministic",
        "deterministic_template",
        "freethinker_humanize",
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
    served_llm_provider: str = "ollama"
    served_llm_model: str = "qwen3.5:9b"
    served_llm_base_url: str = "http://127.0.0.1:11434"
    served_llm_context_length: int = 16384
    served_llm_timeout: int = 60
    served_handoff_mode: str = "never"
    compiler_mode: str = "strict"
    compiler_prompt_mode: str = "auto"
    compiler_model: str = "qwen3.5:9b"
    compiler_backend: str = "ollama"
    compiler_base_url: str = "http://127.0.0.1:11434"
    compiler_context_length: int = 8192
    compiler_timeout: int = 60
    compiler_prompt_file: str = "modelfiles/semantic_parser_system_prompt.md"
    semantic_ir_enabled: bool = False
    semantic_ir_model: str = "qwen3.6:35b"
    semantic_ir_context_length: int = 16384
    semantic_ir_timeout: int = 120
    semantic_ir_temperature: float = 0.0
    semantic_ir_top_p: float = 0.82
    semantic_ir_top_k: int = 20
    semantic_ir_thinking: bool = False
    clarification_eagerness: float = 0.75
    freethinker_resolution_policy: str = "off"
    freethinker_model: str = "qwen3.5:9b"
    freethinker_backend: str = "ollama"
    freethinker_base_url: str = "http://127.0.0.1:11434"
    freethinker_context_length: int = 16384
    freethinker_timeout: int = 60
    freethinker_temperature: float = 0.2
    freethinker_thinking: bool = False
    freethinker_prompt_file: str = "modelfiles/freethinker_system_prompt.md"
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
        return GatewayConfig(**self._enforce_invariants(sanitized))

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
        if "freethinker_context_length" in sanitized:
            try:
                sanitized["freethinker_context_length"] = max(512, int(sanitized["freethinker_context_length"]))
            except Exception:
                sanitized.pop("freethinker_context_length", None)
        if "freethinker_timeout" in sanitized:
            try:
                sanitized["freethinker_timeout"] = max(5, int(sanitized["freethinker_timeout"]))
            except Exception:
                sanitized.pop("freethinker_timeout", None)
        if "freethinker_temperature" in sanitized:
            try:
                value = float(sanitized["freethinker_temperature"])
                if value < 0.0:
                    value = 0.0
                if value > 2.0:
                    value = 2.0
                sanitized["freethinker_temperature"] = value
            except Exception:
                sanitized.pop("freethinker_temperature", None)
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
        if "freethinker_backend" in sanitized:
            backend = str(sanitized["freethinker_backend"]).strip().lower()
            if backend not in {"ollama", "lmstudio"}:
                backend = "ollama"
            sanitized["freethinker_backend"] = backend
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
        if "freethinker_thinking" in sanitized:
            sanitized["freethinker_thinking"] = bool(sanitized["freethinker_thinking"])
        if "semantic_ir_enabled" in sanitized:
            sanitized["semantic_ir_enabled"] = bool(sanitized["semantic_ir_enabled"])
        if "semantic_ir_thinking" in sanitized:
            sanitized["semantic_ir_thinking"] = bool(sanitized["semantic_ir_thinking"])
        if "compiler_prompt_mode" in sanitized:
            mode = str(sanitized["compiler_prompt_mode"]).strip().lower()
            if mode not in {"auto", "always", "never"}:
                mode = "auto"
            sanitized["compiler_prompt_mode"] = mode
        if "freethinker_resolution_policy" in sanitized:
            mode = str(sanitized["freethinker_resolution_policy"]).strip().lower()
            if mode not in {"off", "advisory_only", "grounded_reference", "conservative_contextual"}:
                mode = "off"
            sanitized["freethinker_resolution_policy"] = mode
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
