# Harbor Frontier Baseline

Date: 2026-04-26

## Purpose

`harbor_frontier` is the next held-out Semantic IR stress pack. It is designed
to be harder than Silverton by combining cross-document provenance, temporal
causality, alias ambiguity, medical boundary pressure, partial corrections,
default/exception rules, and durable mutation risk.

The pack is intentionally uncomfortable. It should expose places where
`semantic_ir_v1` needs richer workspace fields or where deterministic admission
needs more explicit source, temporal, type, and mutation contracts.

## Runnable Pack

The pack is registered in:

```powershell
python scripts\run_semantic_ir_prompt_bakeoff.py --scenario-group harbor_frontier
```

A first local LM Studio run used:

```powershell
python scripts\run_semantic_ir_prompt_bakeoff.py `
  --backend lmstudio `
  --model qwen/qwen3.6-35b-a3b `
  --scenario-group harbor_frontier `
  --variants best_guarded_v2 `
  --timeout 300 `
  --num-ctx 16384 `
  --max-tokens 4096
```

Raw JSONL and trace outputs stay under `tmp/` and are not committed.

## First Baseline

The first rich-logging pass produced:

| Metric | Result |
|---|---:|
| Scenarios | 14 |
| JSON valid | 14/14 |
| Schema valid | 14/14 |
| Exact decision labels | 11/14 |
| Average rough score | 0.91 |
| Average latency | 5.9s |

The trace renderer can inspect the run with:

```powershell
python scripts\render_semantic_ir_trace.py <harbor_jsonl> --out tmp\semantic_ir_trace_views\harbor_frontier.trace.md
```

## What Broke Usefully

- `harbor_correction_date_not_identity`: the model committed a correction using
  the unresolved alias atom `m_vale` instead of over-grounding to Mira or Mara.
  This may be acceptable, but the pack currently expects `mixed` until alias
  mutation policy is made explicit.
- `harbor_absence_of_finding_not_negative`: the model proposed one safe positive
  fact and one unsupported negative assertion. The mapper now projects this
  shape to `mixed`, because only the positive fact can be admitted.
- `harbor_group_exception_known_members`: the model eagerly expanded "all
  nurses except Omar" into individual writes. This is the next hard policy
  question: whether enumerated-context group expansion is admissible, and under
  what provenance/quantifier contract.

## Immediate Design Lesson

The pack is already doing its job. The strongest next frontier is not JSON or
basic extraction. It is the boundary between:

- facts directly asserted by a document or speaker;
- facts derived from quantified/group statements;
- negative statements that are absence-of-finding rather than durable negation;
- correction targets that use unresolved aliases;
- temporal/effective-date consequences that should not become timeless facts.

Future work should add admission-level scoring for `must_admit`,
`must_not_admit`, `must_skip_reason`, and temporal/source/mutation boundaries.
