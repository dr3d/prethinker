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

## 2026-05-29 Incident Review: Why English Fell From 98.5% To 80.5%

Observed regression:

- Pre-clean R5 English ugly full replay: `197 / 1 / 2` over `200` (`98.5%`)
- Post-sign-clean R9 English ugly full replay: `161 / 22 / 17` over `200` (`80.5%`)
- Hygiene stayed clean: `0` compatibility rows, `0` runtime load errors, `0` write proposals
- Sign-clean audit passed before and after the R9 measurement

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
  - compile recurring answer-bearing source windows into admitted surfaces;
  - let deterministic code join over `query_intents[]` and admitted source records;
  - keep Python blind to raw human utterance semantics except for syntax, IDs, dates, and source-contained structure.

First exact-to-miss triage:

The cleanest residue is the `16` rows that moved from exact to miss. They show
that the old failure-surface label is too blunt: many rows labeled
`compile_surface_gap` still have the needed answer text inside admitted
`source_record_*` rows. The missing piece is delivery through a sign-clean
query surface.

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
- Start with reusable sign-clean delivery for source windows and section/item
  lists, but promote genuinely recurring event/date/legal/roster/negative
  assertion facts into compile artifacts instead of query-time rescues.
