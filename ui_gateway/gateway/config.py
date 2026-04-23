from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class GatewayConfig:
    front_door_uri: str = "prethink://local/front-door"
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
    clarification_eagerness: float = 0.75
    freethinker_resolution_policy: str = "off"
    freethinker_model: str = "qwen3.5:9b"
    freethinker_backend: str = "ollama"
    freethinker_base_url: str = "http://127.0.0.1:11434"
    freethinker_context_length: int = 16384
    freethinker_timeout: int = 60
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
