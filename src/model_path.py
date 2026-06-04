"""Model serving-path metadata for measurement discipline.

The old harness recorded a model slug and a transport backend. That is not
enough for reproducible stamps because the same slug can be served through
different providers, quantizations, routing policies, and request templates.
This module keeps that measurement metadata explicit without exposing secrets.
"""

from __future__ import annotations

import os
import json
import time
from typing import Any
from urllib.parse import urlparse
import urllib.error
import urllib.parse
import urllib.request


TRUTHY = {"1", "true", "yes", "y", "on"}
FALSY = {"0", "false", "no", "n", "off"}
REDACTED = "[redacted]"
SENSITIVE_METADATA_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "bearer",
    "key",
    "password",
    "secret",
    "token",
}
CONTENT_METADATA_KEYS = {
    "completion",
    "messages",
    "prompt",
}


def split_csv(value: Any) -> list[str]:
    out: list[str] = []
    if isinstance(value, (list, tuple)):
        items = value
    else:
        items = str(value or "").split(",")
    for item in items:
        text = str(item or "").strip()
        if text:
            out.append(text)
    return out


def parse_optional_bool(value: Any) -> bool | None:
    text = str(value or "").strip().lower()
    if not text:
        return None
    if text in TRUTHY:
        return True
    if text in FALSY:
        return False
    raise ValueError(f"expected boolean-like value, got {value!r}")


def is_openrouter_base_url(base_url: str) -> bool:
    return "openrouter.ai" in str(base_url or "").lower()


def openrouter_metadata_headers(base_url: str) -> dict[str, str]:
    if not is_openrouter_base_url(base_url):
        return {}
    raw = (
        os.environ.get("PRETHINKER_OPENROUTER_METADATA")
        or os.environ.get("OPENROUTER_METADATA")
        or "true"
    )
    try:
        enabled = parse_optional_bool(raw)
    except ValueError:
        enabled = True
    if enabled is False:
        return {}
    return {"X-OpenRouter-Experimental-Metadata": "enabled"}


def openrouter_api_key(api_key: str = "") -> str:
    return str(api_key or os.environ.get("OPENROUTER_API_KEY") or os.environ.get("PRETHINKER_API_KEY") or "").strip()


def provider_family(*, backend: str, base_url: str) -> str:
    parsed = urlparse(str(base_url or ""))
    host = (parsed.hostname or "").lower()
    if is_openrouter_base_url(base_url):
        return "openrouter"
    if str(backend or "").strip().lower() == "ollama":
        return "local_ollama" if host in {"", "localhost", "127.0.0.1", "::1"} else "ollama_compatible"
    if str(backend or "").strip().lower() == "lmstudio" and host in {"", "localhost", "127.0.0.1", "::1"}:
        return "local_lmstudio"
    return "openai_compatible"


def openrouter_provider_routing_from_env() -> dict[str, Any]:
    return openrouter_provider_routing(
        order=split_csv(os.environ.get("PRETHINKER_OPENROUTER_PROVIDER_ORDER") or os.environ.get("OPENROUTER_PROVIDER_ORDER")),
        only=split_csv(os.environ.get("PRETHINKER_OPENROUTER_PROVIDER_ONLY") or os.environ.get("OPENROUTER_PROVIDER_ONLY")),
        ignore=split_csv(os.environ.get("PRETHINKER_OPENROUTER_PROVIDER_IGNORE") or os.environ.get("OPENROUTER_PROVIDER_IGNORE")),
        quantizations=split_csv(
            os.environ.get("PRETHINKER_OPENROUTER_QUANTIZATIONS")
            or os.environ.get("OPENROUTER_QUANTIZATIONS")
            or os.environ.get("PRETHINKER_OPENROUTER_QUANTIZATION")
            or os.environ.get("OPENROUTER_QUANTIZATION")
        ),
        allow_fallbacks=parse_optional_bool(
            os.environ.get("PRETHINKER_OPENROUTER_ALLOW_FALLBACKS")
            or os.environ.get("OPENROUTER_ALLOW_FALLBACKS")
        ),
        require_parameters=parse_optional_bool(
            os.environ.get("PRETHINKER_OPENROUTER_REQUIRE_PARAMETERS")
            or os.environ.get("OPENROUTER_REQUIRE_PARAMETERS")
        ),
    )


def apply_openrouter_provider_env(
    *,
    order: Any = None,
    only: Any = None,
    ignore: Any = None,
    quantizations: Any = None,
    allow_fallbacks: Any = None,
    require_parameters: Any = None,
) -> None:
    values = {
        "PRETHINKER_OPENROUTER_PROVIDER_ORDER": order,
        "PRETHINKER_OPENROUTER_PROVIDER_ONLY": only,
        "PRETHINKER_OPENROUTER_PROVIDER_IGNORE": ignore,
        "PRETHINKER_OPENROUTER_QUANTIZATIONS": quantizations,
        "PRETHINKER_OPENROUTER_ALLOW_FALLBACKS": allow_fallbacks,
        "PRETHINKER_OPENROUTER_REQUIRE_PARAMETERS": require_parameters,
    }
    for name, value in values.items():
        text = ",".join(split_csv(value)) if isinstance(value, (list, tuple)) else str(value or "").strip()
        if text:
            os.environ[name] = text


def openrouter_provider_routing(
    *,
    order: list[str] | tuple[str, ...] | None = None,
    only: list[str] | tuple[str, ...] | None = None,
    ignore: list[str] | tuple[str, ...] | None = None,
    quantizations: list[str] | tuple[str, ...] | None = None,
    allow_fallbacks: bool | None = None,
    require_parameters: bool | None = None,
) -> dict[str, Any]:
    provider: dict[str, Any] = {}
    if order:
        provider["order"] = list(order)
    if only:
        provider["only"] = list(only)
    if ignore:
        provider["ignore"] = list(ignore)
    if quantizations:
        provider["quantizations"] = list(quantizations)
    if allow_fallbacks is not None:
        provider["allow_fallbacks"] = bool(allow_fallbacks)
    if require_parameters is not None:
        provider["require_parameters"] = bool(require_parameters)
    return provider


def sanitized_openrouter_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, inner in value.items():
            text_key = str(key)
            lowered = text_key.lower().replace("-", "_")
            if lowered in SENSITIVE_METADATA_KEYS or any(part in SENSITIVE_METADATA_KEYS for part in lowered.split("_")):
                out[text_key] = REDACTED
            elif lowered in CONTENT_METADATA_KEYS:
                out[text_key] = REDACTED
            else:
                out[text_key] = sanitized_openrouter_metadata(inner)
        return out
    if isinstance(value, list):
        return [sanitized_openrouter_metadata(item) for item in value]
    return value


def local_lmstudio_model_metadata(
    *,
    backend: str,
    base_url: str,
    model: str,
    timeout: int = 2,
    urlopen: Any = None,
) -> dict[str, Any]:
    """Return observed local LM Studio model metadata without prompt content.

    LM Studio's OpenAI-compatible endpoint does not honor the harness
    `context_length` field directly. The loaded-model metadata is therefore an
    instrument condition, especially loaded context and quantization.
    """

    if provider_family(backend=backend, base_url=base_url) != "local_lmstudio":
        return {}
    base = str(base_url or "").rstrip("/")
    if not base:
        return {}
    metadata: dict[str, Any] = {
        "schema_version": "local_lmstudio_model_metadata_v1",
        "status": "not_attempted",
        "requested_model": str(model or ""),
    }
    getter = urlopen or urllib.request.urlopen
    try:
        models_payload = _get_json(base + "/v1/models", getter=getter, timeout=timeout)
        metadata["v1_models"] = _local_lmstudio_models_summary(models_payload)
    except Exception as exc:
        metadata["v1_models"] = {"status": "failed", "error": str(exc)[:300]}
    try:
        model_path = urllib.parse.quote(str(model or "").strip(), safe="/._:-")
        model_payload = _get_json(base + "/api/v0/models/" + model_path, getter=getter, timeout=timeout)
        metadata["api_v0_model"] = _local_lmstudio_model_summary(model_payload)
        metadata["status"] = "retrieved"
    except Exception as exc:
        metadata["api_v0_model"] = {"status": "failed", "error": str(exc)[:300]}
        v1_models = metadata.get("v1_models") if isinstance(metadata.get("v1_models"), dict) else {}
        metadata["status"] = "partial" if v1_models.get("status") == "retrieved" else "failed"
    return metadata


def _get_json(url: str, *, getter: Any, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url, method="GET")
    with getter(request, timeout=max(1, int(timeout))) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("endpoint returned non-object JSON")
    return payload


def _local_lmstudio_models_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"status": "unavailable"}
    rows = payload.get("data")
    ids: list[str] = []
    if isinstance(rows, list):
        for row in rows:
            if isinstance(row, dict) and str(row.get("id") or "").strip():
                ids.append(str(row.get("id")).strip())
    return {
        "status": "retrieved",
        "model_count": len(ids),
        "model_ids": ids[:40],
        "model_ids_omitted": max(0, len(ids) - 40),
    }


def _local_lmstudio_model_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"status": "unavailable"}
    allowed_keys = (
        "id",
        "object",
        "type",
        "publisher",
        "arch",
        "compatibility_type",
        "quantization",
        "state",
        "max_context_length",
        "loaded_context_length",
        "model_file",
        "size_bytes",
    )
    summary: dict[str, Any] = {"status": "retrieved"}
    for key in allowed_keys:
        if key in payload:
            summary[key] = sanitized_openrouter_metadata(payload.get(key))
    return summary


def openrouter_request_metadata(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    metadata: dict[str, Any] = {}
    for key in (
        "model",
        "models",
        "route",
        "provider",
        "temperature",
        "top_p",
        "top_k",
        "min_p",
        "max_tokens",
        "seed",
        "stop",
        "response_format",
        "reasoning_effort",
        "reasoning",
        "include_reasoning",
        "think",
        "thinking",
        "stream",
    ):
        if key in payload:
            metadata[key] = sanitized_openrouter_metadata(payload.get(key))
    messages = payload.get("messages")
    if isinstance(messages, list):
        metadata["message_count"] = len(messages)
        metadata["message_character_count"] = sum(
            len(str(message.get("content", ""))) for message in messages if isinstance(message, dict)
        )
    if "prompt" in payload:
        metadata["prompt_character_count"] = len(str(payload.get("prompt") or ""))
    return metadata


def openrouter_response_metadata(raw_response: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(raw_response, dict):
        return {}
    choices = raw_response.get("choices")
    first = choices[0] if isinstance(choices, list) and choices and isinstance(choices[0], dict) else {}
    response: dict[str, Any] = {}
    for key in ("id", "object", "created", "model", "usage", "openrouter_metadata"):
        if key in raw_response:
            response[key] = sanitized_openrouter_metadata(raw_response.get(key))
    for key in ("finish_reason", "native_finish_reason"):
        if key in first:
            response[key] = sanitized_openrouter_metadata(first.get(key))
    return response


def openrouter_generation_id(raw_response: dict[str, Any] | None) -> str:
    if not isinstance(raw_response, dict):
        return ""
    return str(raw_response.get("id") or "").strip()


def openrouter_generation_metadata(
    *,
    raw_response: dict[str, Any] | None,
    request_payload: dict[str, Any] | None = None,
    api_key: str = "",
    base_url: str = "",
    timeout: int = 20,
    call_role: str = "",
    urlopen: Any = None,
) -> dict[str, Any]:
    if not is_openrouter_base_url(base_url):
        return {}
    generation_id = openrouter_generation_id(raw_response)
    metadata: dict[str, Any] = {
        "schema_version": "openrouter_generation_metadata_v1",
        "call_role": str(call_role or ""),
        "generation_id": generation_id,
        "request": openrouter_request_metadata(request_payload),
        "response": openrouter_response_metadata(raw_response),
        "generation_lookup": {"status": "not_attempted"},
    }
    if not generation_id:
        metadata["generation_lookup"] = {"status": "missing_generation_id"}
        return metadata
    key = openrouter_api_key(api_key)
    if not key:
        metadata["generation_lookup"] = {"status": "missing_api_key"}
        return metadata
    getter = urlopen or urllib.request.urlopen
    endpoint = "https://openrouter.ai/api/v1/generation"
    url = endpoint + "?" + urllib.parse.urlencode({"id": generation_id})
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"}, method="GET")
    attempts = _openrouter_generation_lookup_attempts()
    backoff_seconds = _openrouter_generation_lookup_backoff_seconds()
    last_failure: dict[str, Any] = {}
    for attempt in range(1, attempts + 1):
        try:
            with getter(request, timeout=max(1, int(timeout))) as response:
                payload = json.loads(response.read().decode("utf-8"))
            data = payload.get("data") if isinstance(payload, dict) else payload
            metadata["generation_lookup"] = {
                "status": "retrieved",
                "endpoint": endpoint,
                "attempts": attempt,
            }
            metadata["generation"] = sanitized_openrouter_metadata(data)
            return metadata
        except urllib.error.HTTPError as exc:
            error_text = exc.read().decode("utf-8", errors="replace")[:500]
            last_failure = {
                "status": "failed",
                "http_status": int(exc.code),
                "error": error_text,
                "attempts": attempt,
            }
            if int(exc.code) != 404 or attempt >= attempts:
                break
        except Exception as exc:
            last_failure = {"status": "failed", "error": str(exc)[:500], "attempts": attempt}
            if attempt >= attempts:
                break
        time.sleep(max(0.0, backoff_seconds) * attempt)
    metadata["generation_lookup"] = last_failure or {"status": "failed", "attempts": attempts}
    return metadata


def refresh_openrouter_generation_metadata_entries(
    entries: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    api_key: str = "",
    timeout: int = 20,
) -> list[dict[str, Any]]:
    refreshed: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        updated = refresh_openrouter_generation_metadata_entry(entry, api_key=api_key, timeout=timeout)
        if updated is not entry:
            entry.clear()
            entry.update(updated)
        refreshed.append(entry)
    return refreshed


def refresh_openrouter_generation_metadata_entry(
    entry: dict[str, Any],
    *,
    api_key: str = "",
    timeout: int = 20,
) -> dict[str, Any]:
    if not isinstance(entry, dict):
        return {}
    lookup = entry.get("generation_lookup") if isinstance(entry.get("generation_lookup"), dict) else {}
    if lookup.get("status") == "retrieved" and isinstance(entry.get("generation"), dict):
        return entry
    generation_id = str(entry.get("generation_id") or "").strip()
    if not generation_id:
        return entry
    refreshed = openrouter_generation_metadata(
        raw_response={"id": generation_id},
        request_payload=entry.get("request") if isinstance(entry.get("request"), dict) else {},
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        timeout=timeout,
        call_role=str(entry.get("call_role") or ""),
    )
    updated = dict(entry)
    if isinstance(refreshed.get("generation_lookup"), dict):
        updated["generation_lookup"] = refreshed["generation_lookup"]
    if isinstance(refreshed.get("generation"), dict):
        updated["generation"] = refreshed["generation"]
    return updated


def _openrouter_generation_lookup_attempts() -> int:
    raw = os.environ.get("PRETHINKER_OPENROUTER_GENERATION_LOOKUP_ATTEMPTS") or os.environ.get(
        "OPENROUTER_GENERATION_LOOKUP_ATTEMPTS"
    )
    try:
        return max(1, min(8, int(str(raw or "4").strip())))
    except ValueError:
        return 4


def _openrouter_generation_lookup_backoff_seconds() -> float:
    raw = os.environ.get("PRETHINKER_OPENROUTER_GENERATION_LOOKUP_BACKOFF_SECONDS") or os.environ.get(
        "OPENROUTER_GENERATION_LOOKUP_BACKOFF_SECONDS"
    )
    try:
        return max(0.0, min(10.0, float(str(raw or "1.0").strip())))
    except ValueError:
        return 1.0


def model_serving_path_metadata(
    *,
    backend: str,
    base_url: str,
    model: str,
    temperature: float,
    top_p: float,
    top_k: int | None = None,
    context_length: int | None = None,
    max_tokens: int | None = None,
    timeout: int | None = None,
    run_role: str = "",
    cache_enabled: bool | None = None,
    lanes: int | None = None,
    fresh_compile: bool | None = None,
    seed: Any | None = None,
    provider_routing: dict[str, Any] | None = None,
    observed_runtime: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provider = dict(provider_routing or {})
    family = provider_family(backend=backend, base_url=base_url)
    requested_top_k = None if top_k is None else int(top_k)
    effective_top_k = requested_top_k if str(backend or "").strip().lower() == "ollama" else None
    metadata = {
        "schema_version": "model_serving_path_v1",
        "run_role": str(run_role or ""),
        "transport_backend": str(backend or ""),
        "provider_family": family,
        "base_url": str(base_url or ""),
        "model": str(model or ""),
        "provider_routing": provider,
        "decoding": {
            "temperature": float(temperature),
            "top_p": float(top_p),
            "top_k": effective_top_k,
            "top_k_requested": requested_top_k,
            "top_k_effective": effective_top_k,
            "top_k_note": "sent only on the Ollama chat path; OpenAI-compatible LM Studio/OpenRouter requests do not carry top_k",
            "context_length": None if context_length is None else int(context_length),
            "max_tokens": None if max_tokens is None else int(max_tokens),
        },
        "execution": {
            "timeout_seconds": None if timeout is None else int(timeout),
            "lanes": None if lanes is None else int(lanes),
            "cache_enabled": cache_enabled,
            "fresh_compile": fresh_compile,
        },
    }
    if seed is not None:
        metadata["decoding"]["seed"] = seed
    if isinstance(observed_runtime, dict) and observed_runtime:
        metadata["observed_runtime"] = sanitized_openrouter_metadata(observed_runtime)
    return metadata
