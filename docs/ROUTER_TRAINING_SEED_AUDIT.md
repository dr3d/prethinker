# Router Training Seed Audit

Last updated: 2026-04-28

This note treats `docs/data/router_training/router_training_seed_v1.jsonl` as a
router contract surface, not as a fine-tuning corpus. The seed is useful for
making the router schema, prompt, and profile-choice expectations rigorous, but
it is too small and uneven to claim broad routing generalization.

## Snapshot

The current seed has 164 examples.

Profile distribution:

| Expected profile | Count |
| --- | ---: |
| `legal_courtlistener@v0` | 40 |
| `probate@v0` | 38 |
| `medical@v0` | 31 |
| `sec_contracts@v0` | 27 |
| `story_world@v0` | 26 |
| `bootstrap` | 2 |

Source distribution:

| Source family | Count |
| --- | ---: |
| `semantic_ir_lava_pack_v2` | 35 |
| `semantic_ir_lava_pack_v4` | 25 |
| `silverton` | 18 |
| `semantic_ir_lava_pack_v3` | 17 |
| `harbor` | 14 |
| `medical` | 11 |
| `semantic_ir_cross_turn_frontier_pack_v1` | 8 |
| `multilingual_probe` | 8 |
| `ledger` | 8 |
| `glitch` | 6 |
| `courtlistener` | 5 |
| `sec_contracts` | 5 |
| `goldilocks` | 4 |

## What Is Represented

- Legal/probate boundary tension is present, but not dense enough. A keyword
  audit found about 10 examples that contain both legal and probate pressure.
  That is enough to define the failure class, not enough to exhaust it.
- Legal/medical tension is represented by about 8 examples, mostly deposition,
  pharmacy-log, clinic-note, and clinical-advice-in-legal-context cases.
- Temporal pressure is common. About half the seed mentions dates, intervals,
  deadlines, before/after language, expiry, or corrected temporal anchors.
- Multilingual and code-switched routing pressure is present, but the examples
  are still curated rather than broad natural usage.
- Query boundaries are common, which is good for testing whether routing
  remains stable when an utterance mixes updates, questions, and rules.

## Thin Spots

- Bootstrap is too thin: only 2 examples. That means the current seed cannot
  really characterize when the router should request bootstrap review instead
  of forcing a known profile.
- Legal/probate taxonomy tension needs more near misses. The recurring hard
  case is not "legal" versus "not legal"; it is whether a turn should load
  generic legal-source context or probate-specific inheritance/witness/charter
  context.
- Multi-domain turns should include more primary-profile-plus-secondary-profile
  audit expectations, not just a single expected profile label.
- Router examples currently validate profile choice more than context choice.
  The next seed should explicitly check `context_audit`: why this profile, why
  not the runner-up, which context modules should be loaded, and what risks were
  detected.

## Recommended Additions

Add 60-100 examples before considering the seed "contract-complete":

- 20 bootstrap/unexpected-domain examples across games, household rules,
  manufacturing logs, school policies, lab protocols, and fictional systems.
- 20 legal/probate boundary examples where court filings discuss estates,
  probate petitions quote court orders, beneficiaries make claims, and source
  documents disagree with witness testimony.
- 15 legal/medical and contract/medical examples where the right primary
  profile depends on source authority rather than vocabulary.
- 15 multilingual/noisy examples that preserve domain routing under misspelling,
  code switching, and foreign-language negation.
- 10 temporal-query examples where the router must keep legal/contract/story
  profile selection stable while the compiler handles date anchors and queries.

## Use In Evaluation

Score the router seed on:

- exact profile choice;
- bootstrap versus forced-profile behavior;
- secondary profile candidates;
- context-audit explanation quality;
- risk flags and retrieval hints;
- downstream anti-coupling diagnostics after the compiler/mapper pass.

The seed should help make the router stricter and more inspectable. It should
not become another place where Python learns language-specific routing rules.
