# Pre-think Control Plane Contract (Phase 0 Freeze)

Version: `v0`  
Status: Drafted for local MCP scaffold

This contract defines the minimal request/response shapes for pre-think interposition.

## Tool: `pre_think`

Purpose: classify an inbound utterance into one routing mode before final assistant handling.

Request:

```json
{
  "utterance": "string (required)"
}
```

Response:

```json
{
  "status": "success|validation_error",
  "result_type": "pre_think_packet",
  "packet": {
    "utterance": "string",
    "mode": "short_circuit|forward_with_facts|block_or_clarify",
    "signals": {
      "looks_like_query": true,
      "looks_like_write": false
    },
    "requires_user_confirmation": true,
    "clarification_eagerness": 0.75,
    "source_of_truth": "prolog_kb",
    "note": "string"
  },
  "state": {
    "enabled": true,
    "all_turns_require_prethink": false,
    "clarification_eagerness": 0.75,
    "require_final_confirmation": true
  }
}
```

## Tool: `set_pre_think_session`

Purpose: mutate session-level policy toggles.

Request:

```json
{
  "enabled": true,
  "all_turns_require_prethink": false,
  "clarification_eagerness": 0.75,
  "require_final_confirmation": true
}
```

All fields optional; omitted fields retain previous value.

Response:

```json
{
  "status": "success",
  "result_type": "session_updated",
  "state": {
    "enabled": true,
    "all_turns_require_prethink": false,
    "clarification_eagerness": 0.75,
    "require_final_confirmation": true
  }
}
```

## Tool: `show_pre_think_state`

Purpose: inspect active session state.

Request:

```json
{}
```

Response:

```json
{
  "status": "success",
  "result_type": "session_state",
  "state": {
    "enabled": true,
    "all_turns_require_prethink": false,
    "clarification_eagerness": 0.75,
    "require_final_confirmation": true
  }
}
```

## Deterministic Runtime Tools (Phase 1 Included)

- `query_rows`
- `assert_fact`
- `assert_rule`
- `retract_fact`

These delegate to the local deterministic runtime and are never commit-authoritative based on LLM output alone.

## Non-negotiable Trust Rule

If uncertainty is present on write-path turns, served-LLM assistance is advisory only.

Commit authority must include at least one:

1. deterministic KB disambiguation, or
2. explicit user confirmation.

