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
   research-viable.

Promotion standard:

```text
Candidate lane is viable only if it recovers quality, preserves hygiene,
reduces or holds variance, and improves either latency, cost, or operational
control enough to justify the migration.
```

This is the discipline Prethinker needs for any future model swap, not only the
local Q4/Q8 Qwen question.

## Compile / Query Split Certification

The product may want different model paths for different phases:

```text
compile model path:
  high source fidelity, schema discipline, conservative admission

query model path:
  cheap/local if possible, strong intent parsing, answer-shape selection,
  citation-disciplined rendering over admitted evidence
```

That split is economically attractive, but it creates a tuning-overlap risk.
The compile model shapes the artifact vocabulary, predicate density, source
ledger surface, and diagnostics. The query model then learns to route against
that artifact shape. A query lane can look good because it has adapted to one
compiler's omissions and idioms, while a compile lane can look good because the
query path has been tuned to compensate for it.

Treat a compile/query pair as a certified product lane, not as two independent
model swaps.

Required comparison matrix before promoting a split lane:

```text
reference compile + reference query
reference compile + candidate query
candidate compile + reference query
candidate compile + candidate query
```

Read the four cells separately:

- If `reference compile + candidate query` regresses, the local/cheap query
  model does not yet understand the governed query contract.
- If `candidate compile + reference query` regresses, the new compiler changed
  artifact shape or coverage.
- If only `candidate compile + candidate query` looks good, suspect paired
  overfitting: the two paths may be compensating for each other's quirks.
- If both cross-pairs hold and the paired lane holds, the split is much more
  research-viable.

Calibration fixtures for this matrix should include:

- direct lookup rows;
- source-record/list/identifier rows;
- table and section-coordinate rows;
- chronology/date/quantity rows;
- conflict/source-claim rows;
- ACH/evidence-matrix payloads if the query model proposes overlay inputs;
- one fresh ugly heldout slice that did not shape either lane.

Retuning rules:

- Tune compile for source preservation and admitted-surface quality.
- Tune query for intent emission, evidence selection, clarification, and
  renderer discipline.
- Do not tune query to hide compile omissions as if they were established
  facts.
- Do not tune compile around one query model's preferred predicate names unless
  the names are part of a documented shared contract.
- Record failures as compile-surface, query-surface, hybrid-join, or
  answer-surface gaps before repairing.

Promotion standard:

```text
A split lane is viable when each cross-pair remains within SLA, hygiene counters
stay clean, and the paired lane improves latency/cost/control without hiding
new compile/query coupling.
```

Local query remains the right product target, but it has to be certified as a
query lane over stable compiled artifacts, not merely tested with the same
compiler it was implicitly tuned beside.

## Future Decoding-Settings Probe

Do not casually change decoding settings inside a stamp or transfer claim.
Settings are part of the reproducibility unit. A decoding probe belongs in its
own locked experiment lane, with row-level churn analysis and no simultaneous
architecture repair.

The only current decoding hypothesis worth carrying forward is source-fidelity
pressure from `top_p`.

Legacy observed defaults from the variance investigation:

```text
temperature: 0.0
top_p: 0.82
top_k: 20 in semantic settings, but not sent on LM Studio/OpenRouter paths
thinking: off
reasoning_effort: none
min_p: not exposed
```

Hypothesis:

```text
For compile/extraction work, top_p < 1.0 may prune rare but source-critical
tokens: proper names, citation strings, unusual legal phrasing, identifiers,
and non-English fragments. A top_p=1.0 arm might improve source fidelity
without changing the architecture.
```

If tested, run only the smallest useful A/B:

1. Freeze code, model slug, provider path, source corpus, prompt/schema
   versions, cache policy, and judge settings.
2. Compare legacy `top_p=0.82` against the current claim-lane `top_p=1.0`.
3. Do not treat `top_k` as an OpenRouter/LM Studio audit-lane lever unless the
   payload actually sends it; on recent measured paths it was a no-op.
4. Keep thinking/reasoning off for benchmark claims. If thinking is tested,
   wall it off as a separate experimental lane because it adds cost and
   provider-behavior variance.
5. Exclude `min_p` unless a specific failure points to prose-quality filtering;
   the known problem class is source fidelity, not fluent generation.
6. Stratify row churn by source-fidelity hardness, not only aggregate score:
   non-ASCII rows, citation/identifier rows, proper-name rows, exact-quote
   rows, and rare-token rows should move disproportionately if the hypothesis
   is real.
7. Promote a settings change only if it improves the targeted strata, preserves
   ordinary exact rows, keeps compatibility/runtime/write hygiene at zero, and
   repeats under at least an N=2 draw or unlike transfer slice.

Stop the settings lane if movement is uniform, random, or mostly churn between
previously exact rows. The goal is not to tune prose. The goal is to preserve
source-contained facts more faithfully.

## 2026-06-04 Model Variance Pre-Registration

The next Qwen/Gemma/runtime excursion is pre-registered in:

```text
docs/MODEL_VARIANCE_PRE_REGISTRATION_20260604.md
```

That protocol treats model/runtime variation as a robustness measurement, not a
model-selection contest. It freezes SEC Form 8-K compile-fact and atom-query
anchors, requires all cells to be reported, and explicitly forbids keeping the
best model, seed, temperature, or fixture result as the claim. Gemma, when
available, is a dense-model control. Qwen fixed-seed local LM Studio runs are a
reference variance cell, not proof of determinism.

The first completed cell under that protocol was the SEC transfer_003 five-row
atom-query smoke, using a retained Qwen-compiled typed artifact:

```text
C:\prethinker_tmp_archive\model_variance_prereg_20260604\sec_t003_atom_query_variance_20260604
```

Result summary:

```text
Qwen local temp 0, N=5:
  product exact: 23 / 25
  typed-plan replay: 23 / 25, pass
  redacted rejudge: 23 / 25, 0 prose-dependent, pass

Qwen local temp 0.2, N=3:
  product exact: 13 / 15
  typed-plan replay: 13 / 15, pass
  redacted rejudge: 12 / 15, blocked by one normalized-name partial

Qwen local temp 0.5, N=3:
  product exact: 13 / 15
  typed-plan replay: 13 / 15, pass
  redacted rejudge: 13 / 15, pass

Gemma 4 12B local dense control, operator-observed Q8, temp 0, N=5:
  product exact: 25 / 25
  typed-plan replay: 25 / 25, pass
  redacted rejudge: 24 / 25, blocked by one normalized-name partial

Gemma 4 12B local dense control, Q4_K_M, temp 0, N=5, random local seed:
  product exact: 25 / 25
  typed-plan replay: 25 / 25, pass
  redacted rejudge: 25 / 25, 0 prose-dependent, pass
  metadata: arch=gemma4, compatibility_type=gguf, quantization=Q4_K_M,
    loaded_context_length=65536
```

Read: Gemma Q4 is the cleanest tiny query-control arm so far, and it is slightly
faster than the Q8 control on this machine. It is still not a model migration:
the cell used one five-row query anchor over a Qwen-compiled typed artifact.
The stricter finding is that Qwen temp-0 query planning should be reported as a
4-5/5 band on this anchor rather than as a single favorable 5/5 point, and
nonzero temperature did not remove the query-surface jitter.

The cell also exposed a local metadata bug: when the harness used a `/v1`
base URL, the LM Studio metadata helper appended another `/v1` and therefore
missed model-list and quantization details. That has been fixed for future
artifacts. The completed cell's Gemma Q8 detail is operator-observed plus
post-fix metadata validation, not a field recovered in the original run JSON.
The later Gemma Q4 arm was generated after the fix and therefore records
quantization and loaded-context metadata in each draw artifact.
