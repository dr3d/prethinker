# Narrative Transfer Worksheet

This worksheet tracks narrative-fiction and known-prose probes separately from
native, real-world transfer, and product-release measurements.

Narrative probes are useful for source-bounded reasoning, alias handling,
fictional-claim containment, and prior-knowledge discipline. They are not
evidence that Prethinker generalizes to messy operational documents.

## 2026-05-23 Sherlock Holmes Pilot

Dataset:

```text
datasets/narrative_transfer/sherlock_holmes_pilot_2026_05
```

Fixture:

```text
holmes_001_red_headed_league
```

Purpose:

- Source-bounded narrative QA over public-domain prose.
- Prior-containment check on a famous story the base model may already know.
- Pressure on aliases, fabricated in-story claims, retrospective narration,
  and reader-knowledge provenance.

Compile:

```text
model: qwen/qwen3.6-35b-a3b via OpenRouter
rough score: 0.884
quality verdict: poor
admitted/skipped: 175 / 8
risk count: 5
notable gate signal: source-claim carrier offered but partially undelivered
```

The initial compile wrapper hit a shell timeout after writing the artifact; the
orphaned Python processes were stopped and the existing artifact was summarized.

QA:

```text
questions: 25
exact / partial / miss: 20 / 1 / 4
exact rate: 80.0%
compatibility rows: 0
runtime load errors: 0
QA write proposals: 0
failure surfaces: 5 compile_surface_gap
```

Artifact archive:

```text
C:\prethinker_tmp_archive\work_20260523_record_narrative_ach
```

Non-exact rows:

- q012 miss: Mr. Merryweather was known as bank chairman/director, but the KB
  did not link him to presence in the vault.
- q021 partial: Vincent Spaulding and John Clay were represented separately
  without an explicit alias/identity link.
- q022 miss: Ezekiah Hopkins was compiled as a benefactor without preserving
  that the benefactor story is fabricated cover.
- q023 miss: Watson's retrospective framing was not emitted.
- q025 miss: the KB had the tunnelling plan and Holmes speech, but not the
  reader-knowledge provenance that the plan is learned through Holmes's later
  explanation.

Read:

- The 80% exact score is useful but not a product headline.
- Failures are narrative-specific compile surfaces: alias revelation,
  fictional-cover status, narrator temporal frame, and explanation provenance.
- The probe did not show obvious prior leakage in the scored rows; the weaker
  behavior was under-compilation of story-discourse structure.
- Next narrative work, if pursued, should add explicit narrative-discourse
  carriers rather than tune the real-world transfer harness around fiction.
