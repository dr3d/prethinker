# Sign-Clean Recovery Worksheet

## 2026-05-29 Stop-Claim Status

Initial status: blocked.

Current status after the 2026-05-29 recovery cuts: sign-clean audit passes for the audited leakage classes.

Prethinker was not sign-clean at the start of this worksheet. Public accuracy, product-readiness, and benchmark claims were blocked until `scripts/audit_sign_clean.py` passed.

This is not a score regression note. It is an instrument-governance correction. The active repo still contains two classes of leakage that can shape measurements:

- high-risk corpus-shaped compatibility vocabulary in active runtime code;
- Python-side semantic routing over raw English utterances.

The existing active leakage audit was too narrow. It caught known fixture names and answer phrases, but it did not fail the repo for retired compatibility vocabulary or raw utterance regex routing. That let old adapters and query-side English heuristics remain near the instrument while the score story moved forward.

## Current Stop-Claim Gate

New audit:

```powershell
python scripts\audit_sign_clean.py --out-json C:\prethinker_tmp_archive\sign_clean_audit_20260529.json --out-md C:\prethinker_tmp_archive\sign_clean_audit_20260529.md
```

Current expected result: fail.

Observed blocker classes:

- `high_risk_corpus_shaped_active_vocabulary`
- `raw_utterance_semantic_regex`

The rule is simple: if this audit fails, claims are blocked. Fresh QA scores can be used as internal research signals only.

## 2026-05-29 First Containment Cut

The main QA runner no longer adds Python-authored query hints or source-record companions from raw utterance text in `run_one_question`. It now executes only:

- model-authored Semantic IR queries;
- validated evidence-bundle plan queries when explicitly enabled;
- deterministic filtering/deduplication/row limiting over those query results.

The old companion functions still exist in the file and therefore the sign-clean audit must continue to fail. This cut is containment, not absolution. The next cleanup pass must remove or move those retired functions out of active runtime code.

## 2026-05-29 Retired Vocabulary Cut

Removed the first high-risk corpus-shaped vocabulary set from active runtime scripts:

- school-roster compatibility support names;
- homeroom/student compatibility predicates;
- retired industrial-sensor support names;
- parser markers tied to the old roster fixture shape.

After this cut, `scripts/audit_sign_clean.py` reports `high_risk_active_vocabulary_count = 0`.

Remaining blocker: raw utterance semantic regex definitions in active code. The runtime containment cut prevents the main QA path from calling the largest raw-utterance companion stack, but the definitions are still in active code and must be removed, moved to historical artifacts, or replaced by intent-driven/source-record-only mechanisms before claims are unblocked.

## 2026-05-29 Raw-Utterance Regex Cut

The raw-utterance regex blocker is cleared.

Changes:

- removed the retired complementary/anchor hint-query functions from active QA code;
- stopped QA scoring helpers from using raw utterance regex guards for ratio/date-range support checks;
- removed medical-profile regex rescues that converted clarification text into facts on the Python side;
- tightened the regex governance audit so it blocks raw `utterance`/`question` semantics specifically instead of treating every source-record `text` parser as human-language routing.

After this cut:

- `high_risk_active_vocabulary_count = 0`
- `raw_utterance_semantic_regex_count = 0`
- `scripts/audit_sign_clean.py` status: `pass`

This restores the sign-clean gate for the audited classes. It does not prove scores are unchanged; the next measurement must be an English regression run because containment deliberately removed paths that may have inflated prior QA results.

## Recovery Order

1. Remove or quarantine retired native compatibility adapters from active runtime surfaces. Disabled-by-default is not enough when a flag can re-enable corpus-shaped behavior.
2. Replace raw utterance semantic routing with LLM-authored `query_intents[]` or deterministic routing over compiled artifacts only.
3. Keep structural parsers that operate on admitted source records, Prolog syntax, dates, identifiers, and display normalization, but classify them explicitly.
4. Re-run English regression fixtures after cleanup, because score drops are possible if prior gains depended on leaked shape.
5. Only after sign-clean passes: rerun fresh ugly/public fixtures and native stamps as claim-bearing measurements.

## Operating Rule

No Python-side semantic interpretation of human utterances. Query language understanding belongs to the query compiler. Python may validate syntax, execute admitted queries, score deterministic evidence, and render audited outputs.

No research fixture shape in the active instrument. If a mechanism is real, it must be renamed, generalized, tested on unlike documents, and promoted through a sign-clean audit.
