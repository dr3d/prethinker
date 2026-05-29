# Sign-Clean Recovery Worksheet

## 2026-05-29 Stop-Claim Status

Initial status: blocked.

Current status after the free-text semantic-routing audit update: blocked again.

Prethinker was not sign-clean at the start of this worksheet. A narrower version of `scripts/audit_sign_clean.py` passed after raw-utterance routing was cut, but that audit drew the boundary at the wrong field name. The stricter free-text semantic-routing audit now blocks claims again.

This is not a score regression note. It is an instrument-governance correction. The active repo still contains leakage that can shape measurements:

- high-risk corpus-shaped compatibility vocabulary in active runtime code;
- Python-side semantic routing over raw English utterances;
- Python-side semantic routing over free-text source/display fields.

The existing active leakage audit was too narrow. It caught known fixture names and answer phrases, but it did not fail the repo for retired compatibility vocabulary, raw utterance regex routing, or free-text source-ledger routing. That let old adapters and query-side English/source-text heuristics remain near the instrument while the score story moved forward.

## Superseded Stop-Claim Gate

This was the first stop-claim gate. It is preserved here as history, not as the current definition of sign-clean:

```powershell
python scripts\audit_sign_clean.py --out-json C:\prethinker_tmp_archive\sign_clean_audit_20260529.json --out-md C:\prethinker_tmp_archive\sign_clean_audit_20260529.md
```

Historical expected result at this point in the cleanup: fail.

Observed blocker classes:

- `high_risk_corpus_shaped_active_vocabulary`
- `raw_utterance_semantic_regex`

The rule was simple but incomplete: if this audit failed, claims were blocked. Later work showed that passing this version was not sufficient, because it did not see semantic routing over free-text source/display fields.

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

At that moment, after this cut:

- `high_risk_active_vocabulary_count = 0`
- `raw_utterance_semantic_regex_count = 0`
- the narrower `scripts/audit_sign_clean.py` status was: `pass`

This restored the sign-clean gate only for the audited classes. It did not prove scores were unchanged, and it did not prove the instrument was clean. The later free-text semantic-routing audit supersedes this pass and blocks claims again.

## Recovery Order

1. Remove or quarantine retired native compatibility adapters from active runtime surfaces. Disabled-by-default is not enough when a flag can re-enable corpus-shaped behavior.
2. Remove or quarantine Python semantic routing over free-text source/display fields. Classification is not containment.
3. Replace raw utterance routing and free-text source-display routing with LLM-authored `query_intents[]`, typed compile surfaces, or deterministic joins over structured artifacts only.
4. Keep structural parsers only when they operate on syntax or typed values: Prolog terms, source-row IDs, dates already parsed into typed slots, identifiers already in typed slots, numeric values already in typed slots, and display normalization that does not decide answer relevance.
5. Re-run English regression fixtures after cleanup, because score drops are possible if prior gains depended on leaked shape.
6. Only after the strict sign-clean audit passes: rerun fresh ugly/public fixtures and native stamps as claim-bearing measurements.

## Operating Rule

No Python-side semantic interpretation of human utterances or free-text source/display prose. Query language understanding belongs to the query compiler. Source prose understanding belongs to the compile/model layer and must appear as typed admitted structure before Python can use it for answer-bearing joins. Python may validate syntax, execute admitted queries, score deterministic evidence, and render audited outputs.

No research fixture shape in the active instrument. If a mechanism is real, it must be renamed, generalized, tested on unlike documents, and promoted through a sign-clean audit.

## 2026-05-29 Free-Text Routing Audit Correction

Claude's critique exposed a sharper boundary problem:

- The first sign-clean audit blocked Python semantic routing over raw `utterance` and `question`.
- It did not block the same operation when performed over source-ledger prose fields such as `SourceTextDisplay`, `WindowTextDisplay`, `source_record_text_atom`, or normalized source labels.
- That was a definitional leak: the audit tested field names rather than the operation.

New audit:

```powershell
python scripts\audit_free_text_semantic_routing.py --out-json C:\prethinker_tmp_archive\free_text_semantic_routing_audit_20260529.json --out-md C:\prethinker_tmp_archive\free_text_semantic_routing_audit_20260529.md
python scripts\audit_sign_clean.py --out-json C:\prethinker_tmp_archive\sign_clean_audit_free_text_blocked_20260529.json --out-md C:\prethinker_tmp_archive\sign_clean_audit_free_text_blocked_20260529.md
```

For archive-only reporting while the gate is known to be blocked, add
`--exit-zero`. The strict gate omits it and exits nonzero.

Observed:

- `free_text_semantic_routing` blocker count: `458`
- `raw_utterance_semantic_regex_count`: `0`
- `high_risk_active_vocabulary_count`: `0`
- `claim_status`: `blocked`

Source-ledger dependency audit:

```powershell
python scripts\audit_source_ledger_dependency.py C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\qa_r5_full_clean --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\source_ledger_dependency_r5_preclean.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\source_ledger_dependency_r5_preclean.md
python scripts\audit_source_ledger_dependency.py C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\qa_full_clean --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\source_ledger_dependency_r9.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\source_ledger_dependency_r9.md
```

Dependency findings:

- Pre-clean R5 exact rows: `197`
  - direct-only exact: `0`
  - mixed source-ledger/direct exact: `166`
  - source-ledger-only exact: `31`
- Post-clean R9 exact rows: `161`
  - direct-only exact: `47`
  - mixed source-ledger/direct exact: `83`
  - source-ledger-only exact: `31`

Read:

- Source ledgers are not automatically invalid. They are valid as provenance and citation surfaces.
- Source ledgers are unsafe as query-time semantic retrieval substrates when Python tokenizes, regexes, or substring-matches their free-text display values.
- The 98.5% score was more source-ledger-dependent than the prior notes made clear: direct-only exact was `0 / 197`.
- The R9 score is not the typed-thesis floor. It is an upper bound on the still-contaminated post-raw-utterance-cut path. R9 direct-only exact was `47 / 200 = 23.5%`; the real post-enforcement score is somewhere below `80.5%` until the free-text path is actually disabled and rerun.
- The sign-clean standard is now: Python may use typed source-record slots and source-row IDs, but may not derive answer-bearing semantics by reparsing free-text source displays.

## 2026-05-29 Typed-Artifact Recall Ceiling Proxy

Question:

- Could sign-clean Prethinker reach `95%` on this bounded regulatory/public-document distribution by query/join work alone?
- Or is the compile pass currently failing to put enough answer-bearing material into typed artifacts?

Diagnostic:

```powershell
python scripts\audit_typed_artifact_recall.py --dataset-root datasets\real_world_transfer\fresh_ugly_public_20260529_01 --compile-root C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_r1_20260529\compile_r1 --out-json C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\typed_artifact_recall_20260529.json --out-md C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\typed_artifact_recall_20260529.md
```

Method:

- Compare each of the `200` oracle/reference answers against compile artifacts only.
- Ignore all `source_record_*` predicates.
- Report two deterministic recall proxies:
  - `typed_any`: all non-`source_record_*` compile facts, including possible prose-like normalized atoms.
  - `typed_strict`: non-`source_record_*` facts after excluding prose-like atoms and display/text/label predicates.
- Predicate names do not count as answer tokens; only typed argument values contribute coverage.
- This is not proof that a query layer can derive an answer. It is a ceiling/de-risking proxy for whether answer material exists in typed artifacts at all.

Findings:

- `typed_any`: `62` likely available, `72` partial, `66` not available over `200`.
  - likely rate: `31.0%`
  - partial-or-likely rate: `67.0%`
  - average token coverage: `0.622`
  - full numeric coverage: `88 / 153` rows with numbers
- `typed_strict`: `33` likely available, `78` partial, `89` not available over `200`.
  - likely rate: `16.5%`
  - partial-or-likely rate: `55.5%`
  - average token coverage: `0.486`
  - full numeric coverage: `78 / 153` rows with numbers

Read:

- The present typed compile artifacts do not support a plausible `95%` sign-clean QA score by query/join work alone.
- The information is usually present in the source text, but it is not yet being admitted into typed slots at the needed recall.
- The binding blocker is compile recall into typed/source-contained structure, not merely query routing.
- Useful query/join work still matters, but only after the compiler emits enough answer-bearing typed facts for deterministic joins to operate on.

Updated 95% condition:

- A real `95%` claim on this bounded regulatory/public-document distribution remains theoretically possible because source coverage is high.
- It is not reachable from the current typed artifact inventory.
- The next phase must raise typed compile recall first, then rebuild query intent and deterministic joins over those typed surfaces.
- No source-window or question-genre surface counts unless it survives unlike-document validation and does not require Python to parse source prose.

## 2026-05-29 Surface-Coverage Diagnostic

Question:

- How did a broken instrument reach `98.5%` on unseen documents?
- Was the score mostly document-generalization, or did question-shape and surface-token retrieval transfer to new documents?

Diagnostic artifact:

- `C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\surface_coverage_diagnostic_20260529.json`
- `C:\prethinker_tmp_archive\fresh_ugly_public_20260529_01_post_signclean_20260529\surface_coverage_diagnostic_20260529.md`

Method:

- Compare each oracle/reference answer against:
  - the fixture source text;
  - the pre-clean R5 evidence bundle;
  - the post-raw-utterance-cut R9 evidence bundle.
- Measure normalized phrase presence, token coverage, and numeric coverage.

Key findings:

- All `200` rows:
  - source phrase present: `163 / 200`
  - R5 evidence phrase present: `162 / 200`
  - R9 evidence phrase present: `101 / 200`
  - average source token coverage: `0.976`
  - average R5 evidence token coverage: `0.966`
  - average R9 evidence token coverage: `0.670`
- Rows that fell from R5 exact to R9 non-exact (`38` rows):
  - source phrase present: `31 / 38`
  - R5 evidence phrase present: `31 / 38`
  - R9 evidence phrase present: `5 / 38`
  - average source token coverage: `0.969`
  - average R5 evidence token coverage: `0.969`
  - average R9 evidence token coverage: `0.338`
  - average evidence-token drop from R5 to R9: `0.631`
- Rows that fell from R5 exact to R9 miss (`16` rows):
  - source phrase present: `13 / 16`
  - R5 evidence phrase present: `13 / 16`
  - R9 evidence phrase present: `2 / 16`
  - average R5 evidence token coverage: `0.967`
  - average R9 evidence token coverage: `0.339`

Read:

- The unseen documents were new, but the QA/task distribution was not new.
- The pre-clean stack transferred because it was tuned to recurring legal/regulatory question shapes: identifiers, dates, dispositions, chronology, citations, signatories, and list extraction.
- Most reference answers were surface-present in the source text, so source-ledger/free-text retrieval looked strong on new documents.
- The R5 score largely measured whether the support stack surfaced the right source phrase to the LLM judge.
- R9 dropped because the evidence bundle stopped showing the judge those phrases, not because the source documents ceased to contain them.
- The `80.5%` R9 result is closer to the typed/structured thesis than the `98.5%` R5 score, but it is still an upper bound, not a floor, because free-text source-routing remains active elsewhere.

Conclusion:

- The high unseen score was not answer memorization.
- It was question-genre transfer plus extraction-friendly oracle design plus judge-visible surface-token presentation.
- That explains how the system could score above `95%` on unseen documents while still violating the sign-clean thesis.

## 2026-05-29 Incident Review: Why English Fell From 98.5% To 80.5%

Observed regression:

- Pre-clean R5 English ugly full replay: `197 / 1 / 2` over `200` (`98.5%`)
- Post-raw-utterance-cut R9 English ugly full replay: `161 / 22 / 17` over `200` (`80.5%`)
- Hygiene stayed clean: `0` compatibility rows, `0` runtime load errors, `0` write proposals
- The narrower raw-utterance sign-clean audit passed before and after the R9 measurement
- The stricter free-text semantic-routing audit now blocks claims

Root cause:

- The high pre-clean score depended heavily on Python-side raw-question routing in `run_one_question`.
- The removed block appended many source-record companion surfaces after model query execution.
- Those companions used the raw human `utterance` to activate support rows such as:
  - `source_record_question_overlap_support`
  - `source_record_semantic_target_display_support`
  - `source_record_semantic_target_window_support`
  - `source_record_named_section_window_support`
  - `source_record_section_list_detail_support`
  - `source_record_obligation_bundle_support`
  - `source_record_dated_event_inventory_support`
  - `source_record_contact_signatory_support`
  - `source_record_ratio_calculation_support`
  - `source_record_event_date_range_support`
  - many related source-record aggregate surfaces

What made this a governance breach:

- These rows were query-only and generally source-contained, not durable KB mutations.
- They did not appear to use oracle/reference answers directly.
- But they let Python inspect the raw English question and decide which source-record evidence to retrieve.
- That violated the project rule that language understanding belongs to the model-authored query compiler, not to Python regex/token heuristics.

Row-level evidence:

- `38` rows moved from exact to non-exact after the cut.
- The regressed rows disproportionately lost source-record companion support:
  - `source_record_question_overlap_support`
  - `source_record_semantic_target_display_support`
  - `source_record_semantic_target_window_support`
  - broad `source_record_label` / `source_record_text_atom` / source-window evidence
- Examples:
  - `court_order_ugly_003 q019` lost the source-row window containing the exact Figures 2A/2B comparison against Song '656.
  - `osha_incident_ugly_007 q015` lost the source rows carrying Ex. P-1 page ranges.
  - `sec_material_event_ugly_007 q019` lost the `Other Errors` window containing the enumerated error types.
  - `fda_warning_ugly_007 q024` lost the contact-signatory companion row carrying the FDA reply email and attention line.

The crime, stated plainly:

- The instrument was not mostly learning direct compile surfaces.
- It was partly being propped up by a Python-side semantic retrieval layer over the raw question.
- That layer was tempting because it was source-grounded and often correct, but it made the architecture look more mature than it was.
- The 98.5% score was therefore not a valid sign-clean product claim.

Important distinction:

- This was not classic answer-key leakage.
- It was not primarily fixture-name leakage on the May 29 English batch.
- It was a boundary violation: Python performed semantic query interpretation from English utterances.

Recovery implication:

- Do not restore the raw-question companion block.
- Rebuild the useful capability through sign-clean routes:
  - improve model-authored `query_intents[]`;
  - compile recurring answer-bearing facts and relations into typed admitted surfaces;
  - let deterministic code join over `query_intents[]` and typed admitted structure;
  - keep Python blind to raw human utterance semantics and free-text source/display semantics except for syntax, IDs, dates, and typed source-contained structure.

First exact-to-miss triage:

The cleanest residue is the `16` rows that moved from exact to miss. They show
that the old failure-surface label is too blunt: many rows labeled
`compile_surface_gap` still have the needed answer text inside admitted
`source_record_*` rows. The missing piece is delivery through a sign-clean
query surface.

This table is diagnostic, not a rebuild plan. Rows marked "query support" must
not be repaired by reintroducing selected source-window delivery. A repair is
claim-bearing only if it uses structured query intent plus typed admitted slots,
or promotes a genuinely recurring fact/relation into the compile artifact and
survives unlike-document transfer.

| Row | R9 label | Incident classification | Why |
| --- | --- | --- | --- |
| `court_order_ugly_003 q011` | answer surface | answer/render | The compact claim-range atom was present, but the judge could not read `6_9` / `12_21` as source-stated ranges. |
| `court_order_ugly_003 q019` | compile surface | query support | The source row containing the Figures 2A/2B comparison existed; old semantic-target/window support delivered it. |
| `court_order_ugly_003 q020` | compile surface | query support or compile promotion | The source row contains the Song '525 direct-disclosure reasoning; current queries retrieve only high-level findings. |
| `court_order_ugly_003 q024` | compile surface | query support or compile promotion | The source row contains "clogged or collapsed pores" and the inherency reasoning. |
| `fda_warning_ugly_007 q024` | compile surface | query support or compile promotion | Old contact-signatory support found the reply email and attention line from source text; current query only finds a partial attention field. |
| `fda_warning_ugly_007 q025` | compile surface | compile promotion | The repeat-offender narrative needs admitted chronology/source-claim surfaces, not a broad raw-question rescue. |
| `labor_board_ugly_003 q003` | compile surface | compile promotion | Common Board-member participation across summarized decisions should be a compiled roster/intersection surface. |
| `labor_board_ugly_003 q011` | query surface | query support | The source line contains the ALJ, date, and case numbers; current structured queries fail to retrieve that line. |
| `osha_incident_ugly_007 q013` | query surface | query support | The footnote/source-of-timing row exists; old note-marker/overlap delivery found it. |
| `osha_incident_ugly_007 q014` | compile surface | compile promotion | The legal-standard elements are present, but the cited case authority needs a direct admitted surface. |
| `osha_incident_ugly_007 q015` | query surface | query support | Exhibit/page ranges exist in source rows; old semantic-target/window support delivered them. |
| `osha_incident_ugly_007 q018` | query surface | query support or compile promotion | Rope and D-ring characteristics exist in the worksite source row; a physical-characteristic surface may be warranted. |
| `osha_incident_ugly_007 q020` | compile surface | query support or compile promotion | Irwin's "never did" admissions exist in source text; repeated admission lists may deserve a direct source-claim surface. |
| `procurement_contract_ugly_003 q010` | compile surface | compile promotion | The December 3 notification and December 17 protest filing are event-date facts that should compile directly. |
| `puc_order_ugly_003 q024` | query surface | query support or compile promotion | The "no opposition/no objection" statements exist in source text; recurring negative-assertion surfaces are likely useful. |
| `sec_material_event_ugly_007 q019` | compile surface | query support or compile promotion | The "Other Errors" item list exists in a section window; recurring section-list enumeration may compile directly. |

Working read:

- The missing 18 points are not one mechanism.
- They are mostly the loss of a broad source-record retrieval layer that used
  raw question text.
- The first rebuild should focus on exact-to-miss rows, not partial rows.
- Do not start with reusable source-window delivery. Start with genuinely
  recurring event/date/legal/roster/negative-assertion facts and typed relation
  surfaces, then test each new surface on unlike documents so question-genre
  tuning does not get laundered into the compiler.
