# Prethinker Console

This folder contains a local MVP for a product-style front door to Prethinker. It adds:

- a local web chat UI
- a backend endpoint that represents `prethink://` ingress
- a tiny config surface for served-LLM and compiler defaults
- runtime hooks bound to real pre-think + deterministic core runtime tools
- one-click session export for post-mortem JSON traces

The UI is now wired to the canonical interactive utterance entryway in `src/mcp_server.py`, so manual console turns exercise the same shared server path instead of a UI-only parser fork.

## Run

From the repo root:

```powershell
python ui_gateway/main.py
```

Then open:

```text
http://127.0.0.1:8765
```

For a ready-made manual test script, see [CONSOLE_TRYBOOK.md](https://github.com/dr3d/prethinker/blob/main/docs/CONSOLE_TRYBOOK.md).

Direct file-open also works now:

```text
file:///.../ui_gateway/static/index.html
```

In `file://` mode the UI defaults API calls to `http://127.0.0.1:8765`.
You can override with `?apiBase=...` if needed.

Optional:

```powershell
python ui_gateway/main.py --host 0.0.0.0 --port 9000
```

If you want your old `prethink:1234` endpoint style, run:

```powershell
python ui_gateway/main.py --host prethink --port 1234
```

Or bind localhost and map `prethink` in your hosts file.

## Strict Bouncer Mode

Prethinker Console supports a strict-lock preset (button: `Apply Strict Bouncer Lock`), and strict mode invariants are enforced server-side.

When strict mode is on:

- `compiler_mode` is forced to `strict`
- `served_handoff_mode` is forced to `never`
- `require_final_confirmation` is forced to `true`

This keeps the console as a hard MITM bouncer and prevents served-LLM bypass paths during controlled Q&A/clarification loops.

## What It Does

- `POST /api/prethink`
  - accepts `{ "session_id": "...", "utterance": "..." }`
  - returns a phaseful envelope: `ingest`, `clarify`, `commit`, `answer`
- `GET /api/config`
  - returns current local console config
- `POST /api/config`
  - persists config to `ui_gateway/state/gateway_config.json`
- `GET /api/session/reset`
  - resets the current in-memory session
- `GET /api/session/state?session_id=...`
  - returns full turn trace for post-mortem analysis

Slash commands in chat (`/` prefix) are handled deterministically (not NL-routed):

- `/help`
- `/kb [limit]`
- `/state`
- `/config`
- `/cancel`

The backend uses stdlib only: `http.server`, `argparse`, `json`, and small helper modules.

## Architecture Diagram

```text
browser chat UI
  -> /api/prethink
    -> prethink://local/front-door classifier (strict compiler)
      -> clarify gate
        -> deterministic Prolog tools (assert/query/retract)
          -> grounded answer envelope
```

## File Map

- `main.py`: local entrypoint
- `gateway/server.py`: HTTP server and endpoints
- `gateway/phases.py`: turn orchestration and phase envelopes
- `gateway/runtime_hooks.py`: real integration seam for pre-think + deterministic runtime calls
- `gateway/config.py`: local config persistence
- `gateway/session_store.py`: in-memory session state
- `static/index.html`: chat UI shell
- `static/app.js`: browser client
- `static/styles.css`: visual treatment
- `state/gateway_config.json`: default local config persisted by the UI/server

## Sample Transcript

```text
user> Remember that it ships next week.

console ingest> route=write ambiguity=0.79 reasons=[pronoun_reference_detected]
console clarify> Clarify before commit: name the concrete subject, predicate, and object for 'Remember that it ships next week.'
console commit> blocked
console answer> Clarify before commit: name the concrete subject, predicate, and object for 'Remember that it ships next week.'

user> The launch plan ships next week.

console ingest> clarification follow-up received
console clarify> resolved via reframed
console commit> applied
console answer> Deterministic commit complete: 1 mutation(s) applied.

user> Is the launch plan delayed?

console ingest> route=query ambiguity=0.18
console clarify> skipped
console commit> skipped
console answer> Query succeeded with 1 row(s).
```

## Batch Testing Through The Console

Use the runner to execute a turnset through the same HTTP front door used by the UI:

```powershell
python scripts/run_gateway_turnset.py `
  --turns stories/excursions/hn_midground_v3/turnsets/hn_signal_notification_forensics_turnset_v1.json `
  --base-url http://prethink:1234 `
  --strict-lock
```

Artifacts are written under:

- `tmp/runs/gateway_sessions/<timestamp>_<label>/responses.json`
- `tmp/runs/gateway_sessions/<timestamp>_<label>/session_summary.json`
- `tmp/runs/gateway_sessions/<timestamp>_<label>/transcript.md`

## Integration TODOs

Next wiring targets:

- Served-LLM handoff:
  - call the configured served LLM after deterministic routing and optional mutation/query complete
- Durable sessions:
  - persist session/turn state beyond process lifetime
- Streaming and auth:
  - add production-grade transport behavior

## Notes

- Sessions are in memory only for this MVP.
- Config persists locally to JSON.
- Runtime mutations are deterministic via core runtime tools and isolated to `kb_store/ui_gateway_live`.
