# Provider Runtime Discipline Note

Date: 2026-05-27

This note records the runtime lesson from the non-English wild batch and the
Q8 LM Studio probes. Future Prethinker measurements should not treat a model
name alone as the reproducibility unit.

## Short Read

For stamps, transfer claims, and row-level variance work, use OpenRouter as the
default measured lane until a local lane proves benchmark equivalence.

Local LM Studio on the 5090 remains useful for tiny smoke tests, package/API
development, and narrow affected-row probes. It is not currently economical or
stable enough for broad compiles, QA batches, or release claims.

The reproducibility unit is:

```text
Prethinker code + lens/profile + source corpus + model artifact + provider/backend
+ quantization + serving template + loaded context + decoding params
+ timeout/retry policy + lane/cache discipline
```

## What We Learned

The same named model, `qwen/qwen3.6-35b-a3b`, produced materially different
compile behavior through local LM Studio and OpenRouter. This was not just
judge noise or a row-level QA fluctuation; admitted/skipped compile-surface
counts moved by enough to change the instrument's behavior.

OpenRouter metadata capture showed that even a single OpenRouter model slug can
route through multiple providers during one compile. In the metadata smoke run,
the per-call providers included Ambient, Parasail, AkashML, and Ambient again.
That means the provider/backend is part of the measurement condition.

Local LM Studio metadata showed that the local model was loaded as GGUF Q8_0
with the `qwen35moe` architecture and a loaded context of 65536 tokens. The
harness `--num-ctx` value is recorded in artifacts, but it does not currently
control LM Studio OpenAI-compatible requests; LM Studio uses the GUI-loaded
model context. Local artifacts therefore need observed local server metadata,
not only requested harness settings.

## Timing Findings

Representative local Q8 probes on 2026-05-27:

```text
tiny raw chat completion:
0.97s

de_corporate_001 q001, old compile artifact, Semantic IR/query path only:
37.61s

de_corporate_001 q001, old compile artifact, full judged QA:
132.83s

de_corporate_001 fresh compile-source on local Q8 / 64K:
321.68s
```

The 32K local context attempt failed before generation because the packed QA
prompt required more than 53K tokens:

```text
n_keep: 53522 >= n_ctx: 32768
```

The practical read is that current Prethinker prompts are prefill-heavy. The
local 5090 path was observed with low GPU utilization and hot CPU load, so the
runtime bottleneck is not solved merely by switching from a lower quantization
to Q8_0.

## Current Policy

Use OpenRouter for:

- full native stamps;
- ugly public transfer batches;
- non-English transfer batches;
- corpus-level claims;
- provider-variance investigations where metadata is captured.

Use local LM Studio for:

- one-row smoke tests;
- package/API development;
- very small affected-set probes;
- debugging prompt shape and artifact writing;
- experiments that explicitly measure local runtime behavior.

Do not compare LM Studio and OpenRouter results as equivalent unless the run
records enough metadata to explain the serving path.

## Required Metadata Discipline

For OpenRouter calls, artifacts should preserve:

- requested model slug;
- sanitized request settings;
- OpenRouter generation id;
- provider/backend returned by generation metadata;
- normalized model id from generation metadata;
- token counts and cost when available;
- metadata lookup status and retry history.

For LM Studio calls, artifacts should preserve:

- `/v1/models` response where available;
- `/api/v0/models/<model-id>` response where available;
- quantization;
- architecture;
- compatibility type;
- loaded context length;
- max context length;
- loaded/unloaded state;
- GUI-loaded context, because harness `--num-ctx` is not currently authoritative
  for the OpenAI-compatible local endpoint.

## Road Back To Product Work

The provider/runtime lesson should redirect effort, not trap the project in
runtime tuning. The next useful work is:

1. Keep OpenRouter as the measured research lane.
2. Keep local LM Studio metadata capture on compile, QA, batch, and baseline
   artifacts so local probes are labeled honestly.
3. Compact QA/query prompt context so large rows do not require 50K+ tokens.
4. Resume non-English and ugly public blocker work under captured metadata.
5. Treat local 5090 optimization as optional infrastructure work unless it
   becomes necessary for cost control.

The important product signal remains the quality of the compiled evidence layer,
QA behavior, gates, hygiene counters, and transfer results on fresh messy
documents. Runtime choice is an instrument condition, not the product thesis.

## Model Migration Protocol

Once the research lane stabilizes, it is reasonable to revisit a previous local
Q4 Qwen path if it was faster or more reliable in practice. That should be
treated as a model migration, not as a drop-in runtime toggle.

The migration question is:

```text
How much work is required to recover the same SLA after changing model artifact,
provider, quantization, context, or serving backend?
```

Recommended protocol:

1. Freeze the current reference lane:
   - code revision;
   - model path;
   - provider/backend;
   - decoding settings;
   - corpus slice;
   - artifact schema.
2. Run a small locked calibration pack on the reference lane:
   - native slice;
   - ugly public slice;
   - non-English slice;
   - one or two known hard fixtures.
3. Run the same pack on the candidate lane with no repairs.
4. Diff at row and compile-surface level:
   - exact/partial/miss churn;
   - gate pass/hold movement;
   - admitted/skipped predicate counts;
   - failure-surface distribution;
   - compatibility/runtime/write hygiene;
   - latency and cost.
5. Classify the movement:
   - old failures fixed;
   - old exact rows regressed;
   - new repeated failure mechanisms;
   - random variance;
   - provider/runtime artifact differences.
6. Retune only with mechanism-shaped fixes:
   - no fixture vocabulary;
   - no document-shape leakage;
   - no broad helper paths that win a target row while creating churn;
   - no direct corpus-specific answer patches.
7. Re-run the locked pack for N=2 or N=3 cycles if variance is suspected.
8. Confirm on a fresh ugly heldout batch before calling the candidate lane
   product-ready.

Promotion standard:

```text
Candidate lane is viable only if it recovers quality, preserves hygiene,
reduces or holds variance, and improves either latency, cost, or operational
control enough to justify the migration.
```

This is the discipline Prethinker needs for any future model swap, not only the
local Q4/Q8 Qwen question.
