import os
import urllib.error

from src.model_path import (
    apply_openrouter_provider_env,
    local_lmstudio_model_metadata,
    model_serving_path_metadata,
    openrouter_generation_metadata,
    openrouter_metadata_headers,
    openrouter_provider_routing_from_env,
    provider_family,
    refresh_openrouter_generation_metadata_entries,
)


def test_provider_family_distinguishes_openrouter_from_local_lmstudio() -> None:
    assert provider_family(backend="lmstudio", base_url="http://127.0.0.1:1234") == "local_lmstudio"
    assert provider_family(backend="lmstudio", base_url="https://openrouter.ai/api/v1") == "openrouter"


def test_openrouter_provider_routing_from_env_records_pinning_without_secrets(monkeypatch) -> None:
    monkeypatch.setenv("PRETHINKER_OPENROUTER_PROVIDER_ORDER", "provider-a, provider-b")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_PROVIDER_ONLY", "provider-a")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_QUANTIZATIONS", "int4,fp16")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_ALLOW_FALLBACKS", "false")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_REQUIRE_PARAMETERS", "true")
    monkeypatch.setenv("OPENROUTER_API_KEY", "do-not-record")

    routing = openrouter_provider_routing_from_env()

    assert routing == {
        "allow_fallbacks": False,
        "only": ["provider-a"],
        "order": ["provider-a", "provider-b"],
        "quantizations": ["int4", "fp16"],
        "require_parameters": True,
    }
    assert "do-not-record" not in str(routing)


def test_model_serving_path_metadata_is_reproducibility_surface_not_secret_surface(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-value")

    metadata = model_serving_path_metadata(
        backend="lmstudio",
        base_url="https://openrouter.ai/api/v1",
        model="qwen/qwen3.6-35b-a3b",
        temperature=0.0,
        top_p=0.82,
        top_k=20,
        context_length=32768,
        max_tokens=12000,
        timeout=900,
        run_role="compile",
        cache_enabled=False,
        lanes=1,
        fresh_compile=True,
        seed=12345,
        provider_routing={"allow_fallbacks": False},
        observed_runtime={"schema_version": "local_lmstudio_model_metadata_v1", "quantization": "Q8_0"},
    )

    assert metadata["schema_version"] == "model_serving_path_v1"
    assert metadata["provider_family"] == "openrouter"
    assert metadata["provider_routing"] == {"allow_fallbacks": False}
    assert metadata["decoding"]["top_k"] is None
    assert metadata["decoding"]["top_k_requested"] == 20
    assert metadata["decoding"]["top_k_effective"] is None
    assert metadata["decoding"]["seed"] == 12345
    assert metadata["execution"]["lanes"] == 1
    assert metadata["observed_runtime"]["quantization"] == "Q8_0"
    assert "secret-value" not in str(metadata)


def test_model_serving_path_metadata_records_ollama_top_k_as_effective() -> None:
    metadata = model_serving_path_metadata(
        backend="ollama",
        base_url="http://127.0.0.1:11434",
        model="qwen3:local",
        temperature=0.0,
        top_p=0.82,
        top_k=20,
    )

    assert metadata["provider_family"] == "local_ollama"
    assert metadata["decoding"]["top_k"] == 20
    assert metadata["decoding"]["top_k_requested"] == 20
    assert metadata["decoding"]["top_k_effective"] == 20


def test_local_lmstudio_model_metadata_records_loaded_context_and_quantization() -> None:
    captured_urls: list[str] = []

    class FakeResponse:
        def __init__(self, body: bytes):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return self.body

    def fake_urlopen(request, timeout):
        captured_urls.append(request.full_url)
        if request.full_url.endswith("/v1/models"):
            return FakeResponse(b'{"data":[{"id":"qwen/qwen3.6-35b-a3b"},{"id":"other/model"}]}')
        return FakeResponse(
            b"{"
            b'"id":"qwen/qwen3.6-35b-a3b",'
            b'"type":"vlm",'
            b'"publisher":"qwen",'
            b'"arch":"qwen35moe",'
            b'"compatibility_type":"gguf",'
            b'"quantization":"Q8_0",'
            b'"loaded_context_length":65536,'
            b'"max_context_length":262144,'
            b'"path":"C:/Users/private/model.gguf"'
            b"}"
        )

    metadata = local_lmstudio_model_metadata(
        backend="lmstudio",
        base_url="http://127.0.0.1:1234",
        model="qwen/qwen3.6-35b-a3b",
        urlopen=fake_urlopen,
    )

    assert metadata["schema_version"] == "local_lmstudio_model_metadata_v1"
    assert metadata["status"] == "retrieved"
    assert metadata["v1_models"]["model_ids"] == ["qwen/qwen3.6-35b-a3b", "other/model"]
    assert metadata["api_v0_model"]["quantization"] == "Q8_0"
    assert metadata["api_v0_model"]["loaded_context_length"] == 65536
    assert metadata["api_v0_model"]["arch"] == "qwen35moe"
    assert "private" not in str(metadata).lower()
    assert captured_urls == [
        "http://127.0.0.1:1234/v1/models",
        "http://127.0.0.1:1234/api/v0/models/qwen/qwen3.6-35b-a3b",
    ]


def test_local_lmstudio_model_metadata_skips_non_local_openai_compatible_path() -> None:
    metadata = local_lmstudio_model_metadata(
        backend="lmstudio",
        base_url="https://openrouter.ai/api/v1",
        model="qwen/qwen3.6-35b-a3b",
        urlopen=lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not call network")),
    )

    assert metadata == {}


def test_apply_openrouter_provider_env_sets_only_explicit_values(monkeypatch) -> None:
    for name in list(os.environ):
        if name.startswith("PRETHINKER_OPENROUTER_"):
            monkeypatch.delenv(name, raising=False)

    apply_openrouter_provider_env(order="provider-a", allow_fallbacks="false")

    assert os.environ["PRETHINKER_OPENROUTER_PROVIDER_ORDER"] == "provider-a"
    assert os.environ["PRETHINKER_OPENROUTER_ALLOW_FALLBACKS"] == "false"
    assert "PRETHINKER_OPENROUTER_PROVIDER_ONLY" not in os.environ


def test_openrouter_metadata_headers_are_enabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("PRETHINKER_OPENROUTER_METADATA", raising=False)

    headers = openrouter_metadata_headers("https://openrouter.ai/api/v1")

    assert headers == {"X-OpenRouter-Experimental-Metadata": "enabled"}
    assert openrouter_metadata_headers("http://127.0.0.1:1234") == {}


def test_openrouter_generation_metadata_retrieves_actual_serving_path_without_content_or_keys(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-key")
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return (
                b'{"data":{'
                b'"id":"gen-123",'
                b'"model":"qwen/qwen3.6-35b-a3b",'
                b'"provider_name":"Io Net",'
                b'"router":"openrouter",'
                b'"latency":321,'
                b'"tokens_prompt":11,'
                b'"tokens_completion":7,'
                b'"total_cost":"0.0000042"'
                b"}}"
            )

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["authorization"] = request.headers.get("Authorization")
        return FakeResponse()

    metadata = openrouter_generation_metadata(
        raw_response={
            "id": "gen-123",
            "model": "qwen/qwen3.6-35b-a3b",
            "usage": {"prompt_tokens": 11, "completion_tokens": 7, "cost": 0.0000042},
            "choices": [{"finish_reason": "stop", "native_finish_reason": "stop"}],
            "openrouter_metadata": {
                "provider": "Io Net",
                "attempt": 1,
                "messages": [{"role": "user", "content": "do not record"}],
            },
        },
        request_payload={
            "model": "qwen/qwen3.6-35b-a3b",
            "messages": [{"role": "user", "content": "private prompt text"}],
            "temperature": 0,
            "top_p": 0.82,
            "provider": {"only": ["io-net"]},
        },
        base_url="https://openrouter.ai/api/v1",
        timeout=5,
        call_role="semantic_ir",
        urlopen=fake_urlopen,
    )

    assert metadata["schema_version"] == "openrouter_generation_metadata_v1"
    assert metadata["generation_lookup"]["status"] == "retrieved"
    assert metadata["generation"]["provider_name"] == "Io Net"
    assert metadata["generation"]["model"] == "qwen/qwen3.6-35b-a3b"
    assert metadata["request"]["message_count"] == 1
    assert metadata["request"]["provider"] == {"only": ["io-net"]}
    assert metadata["response"]["openrouter_metadata"]["messages"] == "[redacted]"
    assert "private prompt text" not in str(metadata)
    assert "secret-key" not in str(metadata)
    assert captured["authorization"] == "Bearer secret-key"


def test_openrouter_generation_metadata_retries_transient_generation_not_found(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-key")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_GENERATION_LOOKUP_ATTEMPTS", "2")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_GENERATION_LOOKUP_BACKOFF_SECONDS", "0")
    calls = {"count": 0}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self) -> bytes:
            return b'{"data":{"id":"gen-123","provider_name":"SiliconFlow","model":"qwen/qwen3.6-35b-a3b-20260415"}}'

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", hdrs=None, fp=None)
        return FakeResponse()

    metadata = openrouter_generation_metadata(
        raw_response={"id": "gen-123"},
        request_payload={"model": "qwen/qwen3.6-35b-a3b"},
        base_url="https://openrouter.ai/api/v1",
        timeout=5,
        urlopen=fake_urlopen,
    )

    assert calls["count"] == 2
    assert metadata["generation_lookup"]["status"] == "retrieved"
    assert metadata["generation_lookup"]["attempts"] == 2
    assert metadata["generation"]["provider_name"] == "SiliconFlow"


def test_refresh_openrouter_generation_metadata_entries_updates_failed_lookup_in_place(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "secret-key")
    monkeypatch.setenv("PRETHINKER_OPENROUTER_GENERATION_LOOKUP_ATTEMPTS", "1")

    def fake_generation_metadata(**kwargs):
        return {
            "schema_version": "openrouter_generation_metadata_v1",
            "generation_id": kwargs["raw_response"]["id"],
            "generation_lookup": {"status": "retrieved", "attempts": 1},
            "generation": {"provider_name": "Ambient", "model": "qwen/qwen3.6-35b-a3b-20260415"},
        }

    import src.model_path as model_path

    monkeypatch.setattr(model_path, "openrouter_generation_metadata", fake_generation_metadata)
    entry = {
        "schema_version": "openrouter_generation_metadata_v1",
        "generation_id": "gen-123",
        "generation_lookup": {"status": "failed", "http_status": 404},
        "request": {"model": "qwen/qwen3.6-35b-a3b"},
        "response": {"model": "qwen/qwen3.6-35b-a3b-20260415"},
    }
    entries = [entry]

    refreshed = refresh_openrouter_generation_metadata_entries(entries)

    assert refreshed[0] is entry
    assert entry["generation_lookup"]["status"] == "retrieved"
    assert entry["generation"]["provider_name"] == "Ambient"


def test_refresh_openrouter_generation_metadata_entries_preserves_already_retrieved_entry() -> None:
    entry = {
        "schema_version": "openrouter_generation_metadata_v1",
        "generation_id": "gen-123",
        "generation_lookup": {"status": "retrieved", "attempts": 1},
        "generation": {"provider_name": "WandB"},
        "request": {"model": "qwen/qwen3.6-35b-a3b"},
    }

    refreshed = refresh_openrouter_generation_metadata_entries([entry])

    assert refreshed[0] is entry
    assert entry["generation_lookup"]["status"] == "retrieved"
    assert entry["generation"]["provider_name"] == "WandB"
    assert entry["request"]["model"] == "qwen/qwen3.6-35b-a3b"
