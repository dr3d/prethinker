# CourtListener Legal Domain

`legal_courtlistener@v0` is the legal-source starter domain in the profile
catalog.

Its purpose is not legal advice, outcome prediction, or broad precedent
reasoning. It is a pressure lane for source-grounded legal intake: claims,
findings, holdings, docket events, citations, party roles, judge identities,
document provenance, ambiguity, and conflict.

## Why This Domain

The current three-domain stack has complementary pressure:

- `medical@v0`: ontology and entity normalization
- `legal_courtlistener@v0`: provenance, ambiguity, claim versus finding
- `sec_contracts@v0`: obligations, rights, conditions, rules, temporal triggers

CourtListener is useful because legal text regularly separates speech acts from
truth:

```text
The complaint alleged X, but the court found only Y.
```

The desired behavior is not:

```prolog
finding(court, case, x, source).
```

It is:

```prolog
claim_made(complaint, subject, x, source).
finding(court, case, y, source).
```

This domain also stresses a second boundary:

```text
Case A cites Case B.
```

should become:

```prolog
cites_case(case_a, case_b).
```

not an unsupported endorsement, agreement, overruling, or follows-precedent
fact.

## Current Adapter

- profile: `modelfiles/profile.legal_courtlistener.v0.json`
- adapter: `adapters/courtlistener/`
- synthetic fixture:
  `datasets/courtlistener/samples/legal_seed_synthetic_5.jsonl`
- generated live data path, ignored:
  `datasets/courtlistener/generated/`
- generic profile smoke runner:
  `scripts/run_domain_profile_smoke.py`

The adapter currently supports:

- token-based CourtListener REST search
- local raw-response caching
- tolerant opinion/search-result normalization
- harness case generation
- legal predicate contracts

Live CourtListener calls require `COURTLISTENER_API_TOKEN`. Generated raw
responses and live JSONL harness slices stay local and ignored unless a small
fixture is intentionally curated.

## First Live Smoke

The first legal live smoke generated two ignored 10-record harness slices:

- `breach of lease`
- `summary judgment`

Then a Semantic IR smoke ran synthetic legal boundary cases and selected live
metadata cases through `qwen/qwen3.6-35b-a3b` via LM Studio structured output.

Observed behavior:

- all legal smoke cases emitted valid `semantic_ir_v1` JSON
- live CourtListener metadata committed case captions, courts, dates, judges,
  parties, and citations with the legal predicate palette
- allegation language stayed in `claim_made/4` while explicit court findings
  used `finding/4`
- citation language committed only `cites_case/2`, not endorsement
- docket language committed `docket_entry/4`, not `holding/3`
- ambiguous `J. Smith` emitted `candidate_identity/2` candidates while the
  resolved `judge_on_case/2` write was blocked

This is the profile-palette path we want: legal-specific predicates and
boundaries improve the model's proposal without adding English phrase patches to
the generic mapper.

## Current Gaps

- The model often labels legal boundary turns as `commit` even when the mapper
  projects `mixed` because some operations are provisional or blocked.
- Live opinion search snippets are metadata-heavy; richer source text will be
  needed before holding-versus-dicta pressure is meaningful.
- The current palette has basic citation and finding predicates, but not broad
  precedent-status predicates. That omission is intentional for now.
- Provenance is present in context and trace records, but a durable provenance
  predicate may be worth adding once the legal KB shape is clearer.
- Identity ambiguity is currently handled by `candidate_identity/2` plus blocked
  resolved writes; multi-turn identity repair is still future work.

## Open Questions

- Should `candidate_identity/2` be treated as a safe durable fact, a provisional
  fact, or a separate side table?
- Which source metadata deserves durable KB admission versus trace-only
  provenance?
- How should the mapper score legal `mixed` turns where the safe metadata writes
  are admitted but legal interpretation is quarantined?
- When should a CourtListener excerpt be admitted as `document_states/4` instead
  of a more semantic `finding/4` or `holding/3`?
- How should legal dockets, opinions, and parties share identity across records?
