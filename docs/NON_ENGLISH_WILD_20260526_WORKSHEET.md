# Non-English Wild Transfer Worksheet - 2026-05-26

## Purpose

Measure whether the current compile/query architecture transfers beyond English source documents without adding source-language vocabulary or fixture-shaped rules to the instrument.

Batch: `datasets/real_world_transfer/fresh_non_english_wild_20260526_01`

Shape:

- 8 real public-record fixtures.
- 200 QA rows.
- Source languages: French, German, Spanish, Japanese.
- 25 QA rows per fixture.
- Question mix per fixture: source-language, English, and mixed/translation-status rows.

Discipline:

- No source-language vocabulary was added to prompts, code branches, or deterministic query parsing.
- The fixes below are structural harness/instrument fixes: oracle id normalization, bounded judge/classifier payloads, and exact source display preservation.
- Compatibility rows stayed disabled with `--compatibility-adapter-row-limit 0`.

## Preflight

Validation artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_validation2_20260526.md`

Result:

- Status: pass.
- Fixtures: 8 / 8.
- Issues: 0.
- Warnings: 0.
- Oracle completeness: 25 rows per fixture.

Notes:

- Japanese `qa_authored_with_answers.md` answer-count detection was incomplete under the existing validator style, but `oracle.jsonl` was complete. The validator now treats complete oracle rows as sufficient when markdown answer formatting is unfamiliar.
- QA oracle ids in this batch used fixture-prefixed forms plus `original_id` values like `Q1`; the QA runner now indexes structural aliases such as `q001`.

## R1 Compile

Artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_r1_20260526\compile_r1_summary.md`

Result:

- Parsed OK: 8 / 8.
- Compile gate: 7 pass / 1 hold.
- Candidate predicates: 144.
- Compile admitted / skipped: 522 / 164.

Fixture read:

- French, German, and Spanish compiles were mostly healthy.
- `ja_regulator_001` passed but had a high skipped share.
- `ja_corporate_001` held with profile/schema and zero-yield pressure.

Important early clue:

The Japanese source-record ledger preserved exact source rows, but deterministic `source_record_text_atom`/`source_record_cell` atomization was ASCII-oriented. Non-ASCII rows could collapse into `text_key` plus line number without a queryable verbatim display value.

## R1 QA

Initial QA artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_r1_20260526\qa_r1b_summary.md`

Result:

- Exact / partial / miss: 147 / 10 / 38.
- Exact rate: 73.5% on 200 rows.
- Runtime errors: 0.
- Write proposal rows: 0.
- Compatibility rows: 0.

R1 by source language:

- German: 44 / 2 / 4.
- French: 46 / 0 / 4.
- Spanish: 39 / 5 / 5 plus one judge-uncertain row before targeted rerun.
- Japanese: 18 / 3 / 25 plus four judge-uncertain rows before targeted rerun.

Interpretation:

- The architecture did not collapse on non-English generally.
- Japanese was the hard break.
- The hard break was not just "the model does not know Japanese"; multiple misses pointed to source-row addressability loss, table/cell display loss, and overbroad raw table query results.

## Harness Fixes

### Oracle Join

Change:

- `load_oracle()` now indexes structural aliases:
  - direct `id`
  - lowercase `id`
  - normalized `original_id` such as `Q1` -> `q001`
  - fixture-prefixed ids such as `document_q01` -> `q001`

Reason:

This is scorer bookkeeping only. It does not parse natural-language queries or source text.

### Judge And Classifier Payload Bounds

Change:

- Reference-judge payloads now compact oversized `query_results`.
- Failure-surface classifier payloads use the same bounded query-result view and a smaller clause slice when needed.

Reason:

Japanese table rows produced broad source-record queries with thousands of rows. The LLM judge/classifier was hitting context limits. The bounded view preserves:

- query
- predicate
- status
- row count
- variables
- bound constants
- compact reasoning basis
- sampled rows with omitted counts

This does not alter KB contents or query results; it prevents diagnostic prompts from becoming invalid.

### Exact Source Display Preservation

Change:

`source_record_ledger_facts()` now emits verbatim display predicates:

- `source_record_text_display/2`
- `source_record_label_display/2`
- `source_record_section_display/2`
- `source_record_cell_display/3`
- `source_record_cell_header_display/3`

Reason:

The existing normalized atom path is useful for ASCII/identifier-heavy sources, but it can be lossy for non-ASCII rows. Display predicates are source-addressability facts only. They preserve exact printed text without asserting semantic truth.

Query planner guidance was also updated generically:

- Use `source_record_*_display` predicates for exact printed source text when those signatures are present.
- Treat them as source addressability rows, not semantic claims.

## Display Probe

The first probe targeted only the two Japanese fixtures. This is mechanism evidence, not a clean full-batch restamp.

Artifacts:

- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_probe_20260526\compile_display_probe_summary.md`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_probe_20260526\compile_display_probe_ja_regulator_summary.md`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_probe_20260526\qa_display_probe_summary.md`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_probe_20260526\qa_display_probe_ja_regulator_summary.md`

Japanese corporate:

- Before targeted display probe: 7 / 2 / 16.
- After display probe: 17 / 3 / 5.
- Hygiene: 0 runtime, 0 write proposals, 0 compatibility rows.
- Compile gate still held because financial-table pass planning had zero-yield pressure.

Recovered examples:

- representative/person row.
- fiscal period/date row.
- total assets/net assets/equity ratio row.
- annual dividend composition.
- fleet inventory totals.
- share buyback and cancellation details.
- bond issue terms and use of proceeds.
- interest-bearing debt total.

Regression:

- One segment-list row moved exact -> partial due wrong-column/segment selection. This is useful churn, not a clean win.

Japanese regulator:

- Before display probe: 10 / 2 / 13.
- After display probe: 16 / 2 / 7.
- Hygiene: 0 runtime, 0 write proposals, 0 compatibility rows.
- Compile gate clean after display probe.

Recovered examples:

- publication date.
- named representatives.
- reporting deadline/cadence.
- era-date conversion.
- remediation category list.
- legal-violation explanation rows.

Regression:

- One legal-citation row moved exact -> miss, suggesting remaining query-selection/compile-surface tension around statute/article threading.

## Mixed Corrected Read

This is not a single clean rerun. It combines:

- R1b for unaffected fixtures.
- R1c targeted rerun for the Spanish scorer row affected by context/oracle harness issues.
- Display-probe reruns for the two Japanese fixtures.

Mixed corrected aggregate:

- Exact / partial / miss: 161 / 14 / 25.
- Exact rate: 80.5% on 200 rows.
- Runtime/write/compatibility rows: 0 / 0 / 0.

The honest claim:

The first non-English wild batch started around the low 70s, with Japanese carrying most of the loss. A structural, language-agnostic source-display repair recovered a large share of Japanese misses, moving the mixed read to about 80%. This is promising mechanism evidence, not yet a benchmark claim.

## Clean Display Rerun

After the display repair, the full 8-fixture batch was rerun from scratch.

Compile artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_full_20260526\compile_display_full_summary.md`

Compile result:

- Parsed OK: 8 / 8.
- Compile gate: 7 pass / 1 hold.
- Candidate predicates: 129.
- Compile admitted / skipped: 562 / 39.
- Held fixture: `fr_regulator_001`.
- Hold reason: `profile_schema_contract:repeated_structure_role_mismatch:legal_obligation/3`.

QA artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_full_20260526\qa_display_full_summary.md`

QA result:

- Exact / partial / miss: 163 / 14 / 23.
- Exact rate: 81.5%.
- Runtime errors: 0.
- Write proposal rows: 0.
- Compatibility rows: 0.

By source language:

- German: 44 / 2 / 4.
- Spanish: 40 / 4 / 6.
- French: 47 / 1 / 2.
- Japanese: 32 / 7 / 11.

By category:

- Direct fact: 31 / 0 / 1.
- Source coordinate: 25 / 2 / 5.
- List/table/identifier: 30 / 4 / 6.
- Dates/deadlines/sequence: 27 / 3 / 2.
- Obligation/violation/condition: 21 / 4 / 7.
- Cross-section/exception/negation: 21 / 1 / 2.
- Premise check: 8 / 0 / 0.

Failure-surface distribution:

- Compile surface gap: 31 rows.
- Query surface gap: 4 rows.
- Hybrid join gap: 2 rows.

Read:

The clean rerun confirms the display repair was real but not sufficient for 90% multilingual transfer. The architecture now handles French/German strongly, Spanish reasonably, and Japanese no longer collapses, but Japanese remains the hardest source language group at 64% exact and 78% exact+partial.

## Gate Scorer Adjudication

The full display rerun held `fr_regulator_001` even though QA scored 24 / 1 / 0. The first hold named `legal_obligation/3`; a focused retry then shifted the same profile-shape issue to `source_supports/4`.

Focused artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_regulator_gate_probe_20260526\compile_fr_regulator_gate_probe_summary.md`

Rescored existing-artifact summary:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_regulator_gate_probe_20260526\compile_fr_regulator_gate_probe_rescored_summary.md`

Full-batch rescored existing-artifact summary:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_full_20260526\compile_display_full_rescored2_summary.md`

Diagnosis:

The repeated-structure gate was correctly blocking unkeyed per-record properties, but it was too strict for provenance/global lookup predicates accidentally listed as repeated-structure properties. A row like `source_supports/4` is a provenance lookup surface, not a property that should be keyed to each repeated record. Treating it as fatal made the compile gate noisier without improving QA discipline.

Repair:

- `profile_bootstrap_score()` now separates fatal `repeated_structure_role_mismatch_refs` from diagnostic-only `repeated_structure_lookup_property_refs`.
- The fatal guard still catches true per-record property mismatches where the first role is not a record id, record, or subject.
- Batch/file/profile reports now render lookup-property refs explicitly.

Saved-profile recompute after the scorer repair:

- Rough score: 1.0.
- Fatal repeated-structure role mismatch refs: [].
- Diagnostic lookup-property refs: [`source_supports/4`].
- `--summarize-existing --quality-gate` decision: pass, 1 / 0.
- Full 8-fixture `--summarize-existing --quality-gate` decision after scorer repair: pass, 8 / 0.

Follow-up tightening:

The first scorer repair over-reported lookup-property diagnostics for property predicates whose first role already contained `id`, such as an instrument-id row. That did not affect gate pass/fail, but it muddied the diagnostic bucket. The scorer now treats record-keyed/id-keyed properties as keyed first, and only classifies lookup properties when the first role is not already a record id, record, or subject.

## Remaining Blockers

1. Dense financial-table pass planning.

`ja_corporate_001` still had compile-gate hold pressure despite QA gains. The remaining misses cluster around EPS/BPS, segment-column selection, ONE/equity-method income threading, J-GAAP/IFRS/English-version status, and segment restatement/methodology wording.

2. Legal citation/article threading.

`ja_regulator_001` remaining misses cluster around SESC source attribution, Banking Act / FIEA article threading, date chains, and violation-category decomposition.

3. Query-selection over display rows.

Display facts preserve exact rows, but the query planner still sometimes misses the right display predicate or over-relies on neighboring structured facts. Next repairs should be query-planner discipline or generic source-display evidence bundles, not language-specific regex.

4. Failure-surface classifier rerun.

The classifier now has bounded payloads, but earlier artifacts contain a few classifier context-limit labels. The next clean rerun should produce cleaner taxonomy.

## Next Move

The next improvement pass should target structural classes visible in the clean rerun:

1. `fr_regulator_001` gate hold.

Resolved as a gate-scoring false hold on existing artifacts. Confirm in the next clean affected-set compile, but do not spend another repair pass on this fixture unless the hold returns with a new reason.

2. Japanese table/value carriers.

Remaining Japanese misses cluster around table column selection, legal citation threading, date-chain threading, and exact translation/status claims. Keep the fix generic: source-display evidence bundles, table header/cell alignment, and citation-thread carriers.

3. Spanish obligation/procurement residuals.

Spanish is now 40 / 4 / 6. Remaining misses are mostly obligation/condition and list/table details, not direct facts.

4. Query planner over/under-retrieval.

The query-surface count is low but still meaningful. Inspect the 4 query-surface rows before adding more display or compile carriers.

Do not tune against individual source-language strings. Adjudicate by structural class: display preservation, table column selection, legal citation threading, chronology, or query planner over/under-retrieval.

## Display Evidence Judge Probe

Problem:

Some Japanese rows retrieved the relevant `source_record_*_display` row but the QA judge still treated the row as a compile-surface gap because a narrower semantic predicate was absent. That is a scorer/answer-surface problem when the displayed row itself is admitted KB evidence.

Repair:

- Added judge policy stating that `source_record_text_display`, `source_record_label_display`, `source_record_section_display`, `source_record_cell_display`, and `source_record_cell_header_display` are admitted source-addressability rows.
- Added classifier policy so display rows count as admitted KB rows; if they plainly contain support but the judge misses it, the failure should be `answer_surface_gap`, not `compile_surface_gap`.
- Extended deterministic reference-support recognition to include display predicates when the returned display text directly contains the reference surface.

Frozen-query rejudge artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_evidence_judge_probe_20260526\frozen_japanese_rejudge_display_policy.md`

Frozen-query rejudge result:

- Rows rejudged: 18 Japanese non-exact rows from the clean display rerun.
- Improved / same / regressed: 3 / 15 / 0.
- Improvements:
  - `ja_corporate_001:q006` miss -> exact.
  - `ja_regulator_001:q007` miss -> exact.
  - `ja_regulator_001:q008` partial -> exact.

If applied as a frozen rejudge only, the 8-fixture clean display score would move from 163 / 14 / 23 to 166 / 13 / 21, or 83.0% exact. This is not a full fresh QA rerun claim.

Fresh Japanese QA replay artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_evidence_judge_probe_20260526\qa_display_evidence_judge_probe_summary.md`

Fresh replay result:

- `ja_corporate_001`: 19 / 2 / 4, improved from 16 / 4 / 5.
- `ja_regulator_001`: 15 / 2 / 8, down from 16 / 3 / 6.
- Aggregate Japanese fresh replay: 34 / 4 / 12, exact +2 but miss +1 against the old Japanese slice.

Read:

The judge repair is real on frozen evidence, but fresh replay changed query plans and introduced churn. The next blocker is therefore query-planner variance/overbinding on Japanese rows, not more display-evidence policy.

## Query Stability Probe

Problem:

The fresh Japanese replay changed query plans enough to move rows both directions. The cleanest recurring pattern was overbound lowercase slot labels and lossy source-row context. Examples included fused slot constants such as `eventdesc`, `actionmufjbank`, `legalbasemufjbank`, `reporttypemufjbank`, and `deadlinemufjbank`.

Repair:

- Broadened placeholder repair for fused slot-label atoms after the literal query misses.
- The repair keeps real constants bound when the literal query succeeds.
- The repair keeps source/domain constants such as organization ids and action-type atoms bound; it only promotes fused slot-like labels to variables after a failed literal query.
- Extended source-row context companions so returned source rows carry `source_record_*_display` evidence as well as normalized atoms.

Local verification:

- The overbound query `administrative_action(actionmufjbank, corp_mufj_bank, business_improvement_order, legalbasemufjbank).` now repairs to `administrative_action(Actionmufjbank, corp_mufj_bank, business_improvement_order, Legalbasemufjbank).` after the literal miss.
- Against saved `ja_regulator_001` compile facts, section/label source-row companions now bring the exact Japanese display rows alongside the lossy atoms.

Hosted probe artifacts:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_query_stability_probe_20260526\qa_query_stability_probe_summary.md`

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_query_stability_probe2_20260526\qa_query_stability_probe2_summary.md`

First hosted probe, before display-context companion:

- `ja_corporate_001`, first 18: 12 / 1 / 5 versus clean-display baseline first 18 of 11 / 3 / 4.
- `ja_regulator_001`, first 18: 9 / 4 / 5 versus clean-display baseline first 18 of 11 / 3 / 4.

Second hosted probe, after display-context companion:

- `ja_regulator_001`, first 18: 13 / 1 / 4.
- Hygiene: runtime/write/compatibility stayed 0 / 0 / 0.
- Improved rows versus clean-display baseline:
  - `q004` miss -> exact: SESC source attribution recovered from display row context.
  - `q007` miss -> exact: Banking Act article threading recovered from display row context.
  - `q009` partial -> exact: entity/representative names recovered with display evidence.
- Regressed rows versus clean-display baseline:
  - `q012` partial -> miss: literal meaning / regulatory-pain-point translation remains weak.
  - `q013` exact -> miss: English translation/acronym distinction remains judge/planner unstable.

Read:

The display-context companion is a real structural repair. It improves rows where the compiled source row had the right evidence but normalized atoms were too lossy. The remaining hard Japanese rows are not basic source preservation anymore; they are cross-language meaning/translation and legal-concept distinction. Do not patch those with fixture strings or acronym special cases. The next clean work is a generic translation/alias evidence surface, probably query-only and source-grounded, that distinguishes source-stated translations from model-supplied translations.

## Verification

Code/tests after the repair:

- `python -m pytest -q` -> 1866 passed, 2 subtests passed.
- `python -m py_compile src\profile_bootstrap.py scripts\run_domain_bootstrap_file_batch.py scripts\run_domain_bootstrap_file.py scripts\run_profile_bootstrap.py scripts\run_domain_bootstrap_qa.py` -> pass.
- Active instrument leakage audit -> pass, 0 forbidden hits, 10 existing warning hits.
- Utterance regex governance audit -> informational; existing semantic-trigger debt remains, but the new oracle-id normalization regexes are structural scorer bookkeeping.

Audit artifacts:

- `C:\prethinker_tmp_archive\active_instrument_leakage_after_non_english_display_repair_20260526.md`
- `C:\prethinker_tmp_archive\active_instrument_leakage_after_non_english_gate_judge_20260526.md`
- `C:\prethinker_tmp_archive\active_instrument_leakage_after_non_english_gate_judge2_20260526.md`
- `C:\prethinker_tmp_archive\active_instrument_leakage_after_query_stability_probe_20260526.md`
- `C:\prethinker_tmp_archive\utterance_regex_governance_after_non_english_display_repair_20260526.md`

## Source-Grounded Alias / Translation Support

Problem:

The remaining Japanese hard rows exposed a safety distinction, not just a recall gap. The compiled KB may contain English canonical atoms such as normalized action types, while the source document may not visibly state those English translations or acronyms. Treating the canonical atom as source-stated translation would leak model language into the answer surface.

Repair:

- Added query-only `source_record_alias_translation_support`.
- It is activated from semantic `query_intents`, not by regexing the raw user utterance.
- It reads only admitted `source_record_*_display` rows.
- It extracts high-confidence parenthetical alias/translation pairs such as `Long Form (LF)` or `source-language term (English Term)`.
- It also handles visible ASCII-to-ASCII bilingual/equivalence pairs such as `Sistema de Pagos (Payment System)` without relying on a source-language-specific word list.
- It does not read profile prose, predicate names, normalized atoms, or raw source files.
- It does not write durable facts.
- The judge policy now treats these rows as answer-bearing only when the alias/translation is visibly paired in source display text.

Local verification:

- Positive acronym support: source display `The Long Equipment Name (LEN)` yields `PrimaryDisplay=The Long Equipment Name`, `AliasDisplay=LEN`.
- Positive translation support: source display `Oficina técnica (Technical Office)` yields `PrimaryDisplay=Oficina técnica`, `AliasDisplay=Technical Office`.
- ASCII bilingual support: source display `Sistema de Pagos (Payment System)` yields `AliasKind=parenthetical_equivalence`.
- Negative guard: a canonical atom such as `business_improvement_order` does not produce translation support when the display row does not visibly state that term.
- Intent guard: the companion does not activate from raw utterance text alone; it requires semantic intent activation.

Actual-batch spot check:

- On the saved `ja_regulator_001` compile, the q013 semantic intent asks for English terminology for the two administrative action types.
- `source_record_alias_translation_support` produced no rows, because the Japanese source display rows did not visibly pair those terms with English acronyms/translations.
- Read: this is correct behavior. The current instrument should not mark that row exact unless the source bundle itself contains the English terminology, or a separate admitted authority/source supplies it.

Verification artifacts:

- `C:\prethinker_tmp_archive\active_instrument_leakage_after_alias_translation_support_20260526.md`
- `C:\prethinker_tmp_archive\utterance_regex_governance_after_alias_translation_support_20260526.md`

Code/tests after the repair:

- `python -m pytest -q tests\test_domain_bootstrap_qa.py -k alias_translation` -> 6 passed, 370 deselected.
- `python -m pytest -q tests\test_domain_bootstrap_qa.py` -> 376 passed.
- `python -m pytest -q` -> 1872 passed, 2 subtests passed.
- `python -m py_compile scripts\run_domain_bootstrap_qa.py src\profile_bootstrap.py scripts\run_domain_bootstrap_file_batch.py scripts\run_domain_bootstrap_file.py scripts\run_profile_bootstrap.py` -> pass.
- Active instrument leakage audit -> pass, 0 forbidden hits, 10 existing warning hits.
- Utterance regex governance audit -> informational; new alias/translation regexes are classified as source-display structural extraction, not raw-utterance semantic triggers.

Next blocker:

The alias/translation lane is now safer, but it is intentionally conservative. Remaining non-English work should move to one of two places:

1. Source-bundle completeness: include official bilingual/translated source rows when a QA item asks for official English terminology.
2. Query-side semantic retrieval: use semantic intent to locate relevant non-English source rows without relying on English token overlap or source-language fixture terms.

## Semantic Target Display / Window Retrieval

Problem:

The alias/translation repair made the translation boundary safer, but Japanese q012 exposed a query-side retrieval problem. The row asks about a source-local term and why it is the regulatory pain point. The first replay could preserve/retrieve the exact source-local term, but the legal explanation was split into nearby list rows under the same sections. Retrieval of the term row alone was not enough.

Repairs:

- Added `source_record_semantic_target_display_support`.
- It is activated from semantic `query_intents.target_terms`, not from raw utterance regexes.
- It reads only admitted `source_record_*_display` rows.
- It preserves Unicode/source-local target matching and skips ASCII snake_case canonical terms as primary display targets.
- Added guarded Unicode-fragment expansion for long non-ASCII target terms, so a longer source-local term can retrieve repeated shorter source-local fragments elsewhere in the document.
- Added `source_record_semantic_target_window_support`.
- It expands semantic target display hits to bounded same-section neighboring rows using admitted `source_record_row` line/section metadata and `source_record_text_display`.
- Added Semantic IR surface-preservation guidance and a safety retry when a non-ASCII query loses all non-ASCII target surfaces by replacing them with ASCII/canonical target terms.
- Added a multi-part judge policy: if one substantive answer part is supported and another is missing, score `partial`, not `miss`.

Probe artifacts:

- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_semantic_target_probe_20260526`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_semantic_surface_retry_probe_20260526`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_semantic_fragment_probe_20260526`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_semantic_window_probe_20260526`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_semantic_window_judge_probe_20260526`

Result:

- q012 moved from miss to partial on the final one-row probe.
- The support rows now include the exact source-local term rows plus same-section legal rows containing the relevant statutory provisions.
- The remaining missing part is the literal English translation. That is not source-stated in the source bundle, so exact would be overclaiming unless a translation authority or bilingual source row is admitted.
- q013 remains a true data/source-bundle gap for official English terminology/acronyms.

Read:

This is the right kind of progress. It improves multilingual retrieval and scorer calibration without sneaking source-language vocabulary or model translations into the instrument. It also clarifies that some non-English QA rows need a product decision: either allow an answer-rendering translation lens explicitly, or require bilingual/authority source material when the oracle asks for official English terminology.

Verification:

- `python -m pytest -q` -> 1881 passed, 2 subtests passed.
- Active instrument leakage audit -> pass, 0 forbidden hits, 10 existing warning hits.
- Utterance regex governance audit -> informational; new regexes are source-display / Unicode-structure readers, not raw-utterance semantic triggers.
- `C:\prethinker_tmp_archive\active_instrument_leakage_after_semantic_target_window_20260526.md`
- `C:\prethinker_tmp_archive\utterance_regex_governance_after_semantic_target_window_20260526.md`

## Non-English Repair Batch Replay

Purpose:

Test whether the non-English display and semantic-intent repairs remain clean
when replayed against the held Japanese rows and then against the full
eight-fixture non-English wild batch.

Repairs in this batch:

- Semantic IR surface-preservation retry now catches the case where a
  non-ASCII query loses its source-local target and keeps only ASCII or acronym
  targets.
- Unicode/source-display reference support recognizes admitted
  `source_record_semantic_target_display_support` and
  `source_record_semantic_target_window_support` rows as answer-bearing
  source-display evidence.
- Elapsed-date support can use semantic target dates and source-display date
  surfaces, including explicitly supported era-date conversion.
- Parenthetical role/name support reads only admitted source-display
  parentheticals and activates only after a person-role query result exists.
- Document chronology can activate from `document_chronology` semantic intent,
  not only from old English raw-utterance triggers.
- Deadline-rule examples can expand admitted quarter-end rules into
  deterministic calendar examples.
- Era-date conversion is represented as deterministic calendar authority, not
  as source-stated evidence.

Held-row targeted replay:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_regression_replay_final_held6_20260527`

Rows:

- `ja_regulator_001:q007`
- `ja_regulator_001:q008`
- `ja_regulator_001:q009`
- `ja_regulator_001:q015`
- `ja_regulator_001:q016`
- `ja_regulator_001:q017`

Result:

```text
6 exact / 0 partial / 0 miss
0 runtime load errors
0 write proposals
0 compatibility rows
```

Read:

This is mechanism evidence only. It shows that the named source-display,
chronology, parenthetical role/name, deadline-rule, and calendar-authority
repairs address the held rows without hygiene leakage. It is not a corpus
claim.

Hosted full-batch attempts:

- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_full_qa_after_non_english_repairs_20260527`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_full_qa_after_non_english_repairs_or_20260527`

These two attempts are not score-bearing. They failed provider/auth/model
configuration and produced `parsed_ok: 0` / `judge_uncertain: 25` style fixture
rows.

Valid hosted full-batch rerun:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_full_qa_after_non_english_repairs_or_valid_20260527`

Model and lane conditions:

- OpenRouter
- `qwen/qwen3.6-35b-a3b`
- 6 lanes
- no QA cache
- compatibility row limit 0

Result:

```text
166 exact / 19 partial / 15 miss over 200 rows
83.0% exact
0 runtime load errors
0 write proposals
0 compatibility rows
```

Per fixture:

```text
de_corporate_001:           21 / 1 / 3
de_regulator_001:           21 / 3 / 1
es_public_procurement_001:  18 / 5 / 2
es_regulator_001:           20 / 3 / 2
fr_eu_official_001:         23 / 1 / 1
fr_regulator_001:           24 / 0 / 1
ja_corporate_001:           20 / 4 / 1
ja_regulator_001:           19 / 2 / 4
```

Compared to the earlier clean display rerun (`163 / 14 / 23`), this is:

```text
+3 exact
+5 partial
-8 miss
```

Residual non-exact shape:

```text
34 non-exact rows
19 partial
15 miss

compile_surface_gap: 27
answer_surface_gap: 3
query_surface_gap: 2
hybrid_join_gap: 1
judge_uncertain: 1
```

Read:

The held-row repairs transfer enough to reduce misses, but the full-batch lift
is modest. The remaining non-exact rows are mostly compile/source-bundle gaps,
not runtime hygiene failures. Several residual rows ask for official English
terminology, abbreviations, or translation distinctions that are not visibly
source-stated in the current bundle. Those should not be patched with source
language or fixture strings. They need either an admitted bilingual/authority
source-bundle decision or an explicit answer-rendering translation policy.

Next focus:

- Inspect the two query-surface rows first; if source-display evidence already
  carries the answer, improve generic display-reference recognition.
- Then inspect Japanese corporate table/value rows as a structured table
  carrier class.
- Keep official-translation rows out of mechanism repair unless the source
  bundle contains an admitted translation authority.

## Query/Display Residue Repair Pass

Purpose:

Work the first remaining non-English blockers without adding source-language,
fixture-name, or oracle-answer vocabulary to the active instrument.

Repairs:

1. Reference shorthand initialism support.

   The French legal-citation row had admitted source-display text for the full
   legal instrument name, while the reference used an acronym shorthand. Added a
   generic initialism matcher for reference scoring only: if all other
   reference tokens are present in admitted display text, a short missing
   alphabetic token can be satisfied by initials of significant displayed
   words. This is scorer reconciliation, not source knowledge.

2. Source-record display argument repair.

   `source_record_*_display` facts can contain commas inside displayed table
   cells. The runtime clause string may no longer preserve the quote boundary,
   so generic comma splitting truncated display values such as `5,772.50` to
   `5`. The Prolog argument splitter now respects quoted text, and
   source-record display predicates repair overflow arguments back to their
   declared display arity.

3. Semantic target table-cell value support.

   Added query-only `source_record_semantic_target_cell_value_support`. It joins
   an admitted `source_record_cell_header_display` row matched by structured
   `query_intents[].target_terms` to the same-row same-column
   `source_record_cell_display` value. It only uses admitted source-record table
   display rows and writes no durable facts.

4. Numeric-measure reference support for semantic display rows.

   When semantic target display/window/cell-value rows carry all decimal or
   thousands-form numeric measures in the reference answer, the deterministic
   scorer can treat the reference as supported. This avoids requiring a narrower
   semantic predicate when the table display already contains the answer.

5. Response-envelope precedence.

   Exact governed reference support now renders the QA response envelope as
   `established` even if the Semantic IR self-check retained stale clarification
   questions. The clarification text remains in the envelope as diagnostic
   context.

Probe artifacts:

- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_initialism_reference_q006_probe_20260527`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_table_value_probe_20260527`
- `C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_table_value_envelope_probe_20260527`

Targeted results:

```text
fr_eu_official_001:q006 -> exact
ja_corporate_001:q008  -> exact
ja_corporate_001:q011  -> exact
0 runtime load errors
0 write proposals
0 compatibility rows
```

The final table-value/envelope replay for `q008,q011` returned:

```text
2 exact / 0 partial / 0 miss
response_envelope_counts: {"established": 2}
```

Read:

This is mechanism evidence, not a fresh corpus score. The repairs are
structural:

- full-name display can satisfy an acronym shorthand when the source text
  already provides the expansion;
- table headers can carry values through admitted same-row/same-column cell
  display;
- comma-bearing display cells must survive runtime parsing intact;
- stale clarification pressure should not override exact governed evidence in
  the product-facing envelope.

Important non-repair:

`ja_corporate_001:q018` remains a separate adjudication problem. The source row
visibly contains current and prior debt values, and the source-stated delta is
`219,714`, while arithmetic from `913,806 - 694,091` gives `219,715`, matching
the oracle. Do not silently patch this as exact. It needs an explicit policy
choice between source-stated delta and deterministic derived arithmetic when
they differ by rounding.

Verification:

- `python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q` -> 491 passed, 2 subtests passed.
- `python -m py_compile scripts\run_domain_bootstrap_qa.py src\semantic_ir.py` -> pass.
- Active instrument leakage audit -> pass, 0 forbidden hits, 10 existing warning hits.
- Utterance regex governance audit -> informational.
- Active-code grep for this batch's fixture/source names and source-local terms -> no hits outside tests/docs/datasets.

Next blocker:

Adjudicate the `q018` source-stated-versus-derived arithmetic policy before
touching that lane. After that, inspect the Spanish procurement row as a mixed
planner/source-bundle issue: the KB contains `advertising_budget`, but the
planner did not query it, and the two-year maintenance obligation is currently
source-display evidence rather than a durable duration predicate.

## Structured Obligation Bundle Query Repair

Date: 2026-05-27

Focus:

`es_public_procurement_001:q018` asked for a compact list of financial and
contractual obligations. The compiled KB already contained the missing
`advertising_budget` fact, and source-record display rows preserved the
maintenance duration. The query plan reached guarantees, milestones, and a
source section window, but it did not ask the already-compiled budget predicate
or gather the same-subject obligation surface as a bundle.

Diagnosis:

This is a structured query-bundle gap, not a Spanish-vocabulary gap. The
Semantic IR already produced a structured list intent with financial and
contractual constraints. The failure was that the query lane stopped after a few
predicate shapes instead of collecting the existing obligation/amount/duration
facts and numeric source-display rows that belong to the same answer shape.

Change:

Added `source_record_obligation_bundle_support` as a query-only support surface.
It activates from `query_intents[]`, not from raw utterance text. It writes no
durable facts and does not introduce fixture/source terms. The companion
combines:

- existing compiled fact predicates with generic obligation, amount, budget,
  guarantee, milestone, duration, cost, expense, fee, payment, deadline, remedy,
  or requirement predicate surfaces;
- admitted source-record display rows that visibly carry numeric, currency, or
  duration quantities.

Local probe:

Using the archived compile for `es_public_procurement_001`, the companion
returned 45 support rows and surfaced the missing supports:

- `advertising_budget(expediente_6012400294, 9000)`
- definitive and complementary `guarantee_percentage(..., 5)`
- `milestone_requirement(...)` rows
- source display for the advertising cap row
- source display for the two-year maintenance duration row

Hosted targeted replay:

Artifact:

`C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_obligation_bundle_q018_probe_20260527`

Command shape:

```text
python scripts\run_domain_bootstrap_qa.py --run-json <archived es_public_procurement_001 compile> --qa-file datasets\real_world_transfer\fresh_non_english_wild_20260526_01\es_public_procurement_001\qa.md --oracle-jsonl datasets\real_world_transfer\fresh_non_english_wild_20260526_01\es_public_procurement_001\oracle.jsonl --only-ids q018 --base-url https://openrouter.ai/api/v1 --model qwen/qwen3.6-35b-a3b --temperature 0 --no-cache --judge-reference-answers --classify-failure-surfaces
```

Result:

```text
q018 -> exact
judge_exact: 1
judge_partial: 0
judge_miss: 0
runtime_load_error_count: 0
write_proposal_rows: 0
compatibility rows: 0
response_envelope_counts: {"established": 1}
failure_surface_counts: {"not_applicable": 1}
```

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q
-> 494 passed, 2 subtests passed

python -m py_compile scripts\run_domain_bootstrap_qa.py src\semantic_ir.py
-> pass

active instrument leakage audit
-> pass, 0 forbidden hits, 10 existing warning hits

active-code grep for non-English fixture/source names and source-local terms
-> no hits under src/ or scripts/ outside tests
```

## Cross-Language Chronology And Residue Probes

Date: 2026-05-27

Focus:

After the Spanish display-surface repairs, the next question was whether the
same mechanisms transferred to other non-English rows or whether the remaining
failures were different shapes. I ran targeted probes rather than a full rerun.

Mechanism change:

The existing `source_record_dated_event_inventory_support` surface now carries
local display context around each matched date instead of repeating an entire
paragraph for every date. This preserves nearby identifiers/action phrases such
as a decision number next to a date while reducing unrelated date noise.

The reference adjudicator also has a narrow dated-event inventory exactness
check: when deterministic source-record dated-event support contains every
referenced date and every referenced hyphenated/alphanumeric identifier, with
high token coverage, it can support a chronology answer even if narrower
durable predicates such as `decision_id/1` are sparse.

Tightening after test review: the dated-event exactness check also verifies that
the referenced dates appear in the same order in dated-event item rows. This
prevents a broad date inventory from passing merely because it contains the same
date set somewhere in the document.

This is still query-only/source-record support. It writes no durable fact and
uses no fixture/source vocabulary.

Targeted recoveries:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q015_planner_variance_probe_20260527

fr_eu_official_001:q015 -> exact
Read: planner variance; no new mechanism required.
```

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_reg_q016_dated_inventory_order_guard_probe_20260527

fr_regulator_001:q016 -> exact
Read: source row contained the three date/id/action items; the repair makes the
dated-event inventory compact and lets source-record chronology evidence carry
the answer without requiring custom durable decision predicates.
```

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_de_reg_q016_publication_date_probe_20260527

de_regulator_001:q016 -> exact
Read: the publication date and finality language were already source-grounded.
This is a query/exposure recovery, not a compile-language change.
```

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q013_legal_service_probe_20260527

fr_eu_official_001:q013 -> exact
Read: targeted replay recovered the legal-service/name row cleanly.
```

Still not clean:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_de_corp_q010_margin_replaced_probe_20260527

de_corporate_001:q010 -> miss
Read: real derived-finance pressure. The source states old margin and new
absolute operating result/revenue values, but the expected ~5.6% requires
calculating operating result divided by revenue and knowing that this is the
operative margin. Do not fake with a narrow fixture patch.
```

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_q005_q022_hybrid_probe_20260527

ja_regulator_001:q005 -> miss
ja_regulator_001:q022 -> miss

Read: q005 appears to conflict with the source. The source heading for the
bank's business-improvement order points to the financial-instruments statute,
while the reference names banking-law report-demand provisions. q022 remains a
deeper cross-section comparison problem.
```

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_corp_q012_equity_method_probe_20260527

ja_corporate_001:q012 -> partial
Read: still a table/numeric contribution blocker.
```

Projected effect, not a corpus claim:

```text
Last full non-English run:
171 / 15 / 14 = 85.5%

Targeted recoveries since that run:
es_public_procurement_001: q005, q008, q016
es_regulator_001: q015, q016
fr_eu_official_001: q013, q015
fr_regulator_001: q016
de_regulator_001: q016

Approximate projected state if all targeted recoveries reproduce in a full rerun:
180 / 10 / 10 = 90.0%
```

Discipline note:

The projected 90.0% is a planning estimate only. It is not a replacement for a
full rerun because several recoveries are targeted replays and some were
planner-variance recoveries. A full non-English rerun is the right confirmation
after the next blocker pass or before publishing any non-English number.

## Spanish Regulator Display-Surface Repairs

Date: 2026-05-27

Focus:

`es_regulator_001` still had a mix of source-grounded misses after the broader
non-English rerun. Two were clean repairs and two remain honest blockers:

- `q015`: source-stated notification / disposition dates were available in
  query-only source-record date support, but the reference judge discounted that
  support relative to primitive procedural-event rows.
- `q016`: the source states the two appeal windows and forums, including the
  two-month court appeal line, but the display-surface collector did not expose
  the relevant admitted `source_record_text_display` row to the semantic-target
  companion.
- `q011`: still unresolved. The source contains circular description language,
  while the oracle compresses it into a higher-level operational summary. Do not
  patch to that wording.
- `q024`: still unresolved. The row requires cross-section aggravator synthesis
  across volume, sensitivity, and exposure signals.

Changes:

- Reference-judge policy now treats query-only `source_record_*_support` rows as
  non-mutating source evidence rather than lower-trust guesses. For
  source-stated text, dates, labels, and quoted values, admitted source-record
  display/support can override a conflicting primitive semantic predicate.
- `_source_record_display_surfaces()` now queries admitted display predicates
  directly instead of walking runtime clause reprs. The old collector missed
  some rich display rows even though `runtime.query_rows(...)` could retrieve
  them.
- Semantic-target matching now includes a token-spaced variant for hyphenated
  phrases and a conservative long-target token-overlap match for `phrase_literal`
  targets. This is intentionally source-display-only and lower scoring.

Targeted replays:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q015_date_inventory_policy_probe_20260527

q015 -> exact
hygiene: 0 runtime, 0 write proposals, 0 compatibility
```

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q016_semantic_overlap_probe_20260527

q016 -> exact
hygiene: 0 runtime, 0 write proposals, 0 compatibility
```

Unresolved targeted checks:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q011_display_surface_probe_20260527

q011 -> miss
```

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q024_display_surface_probe_20260527

q024 -> miss
```

Read:

The recovered rows are transfer-shaped because they expose admitted source
display more reliably and judge query-only source support on its actual status:
non-mutating source evidence. They do not introduce Spanish fixture language or
source-local terms into active code.

The remaining regulator misses are not good candidates for narrow patching yet.
`q011` looks like oracle/source abstraction mismatch, and `q024` is a genuine
cross-section synthesis blocker.

Verification after the Spanish regulator repairs:

```text
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q
-> 510 passed, 2 subtests passed

syntax compile check for scripts\run_domain_bootstrap_qa.py and src\semantic_ir.py
-> pass

active instrument leakage audit
-> pass, 0 forbidden hits, 10 existing warning hits

utterance regex governance audit
-> informational, 0 parse errors

active-code grep for non-English fixture/source names and source-local terms
-> no hits under src/ or scripts/ outside tests
```

## Display-Surface Collector And Spanish Regulator Transfer

Date: 2026-05-27

Focus:

After the Spanish procurement chronology repair, test whether the same
structured source-display support transfers to a different Spanish document
shape.

`es_regulator_001:q015`:

The row asks for a six-date procedural chronology. The new dated-event inventory
surface found the source dates, but the first replay still failed because the
judge treated `source_record_dated_event_inventory_support` as lower-trust
because it is query-only. That was a policy error: query-only means
non-mutating, not speculative.

Change:

Added explicit reference-judge policy:

```text
query-only source_record_*_support rows are non-mutating evidence surfaces, not lower-trust guesses.
When a primitive semantic predicate conflicts with admitted source-record display/support, prefer source-record display/support for source-stated text, dates, labels, and quoted values.
```

Targeted replay:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q015_date_inventory_policy_probe_20260527

q015 -> exact
judge_exact: 1
hygiene: 0 runtime, 0 write proposals, 0 compatibility
```

`es_regulator_001:q016`:

Initial read incorrectly treated the appeal deadline as external-law pressure.
Source inspection showed this was wrong: the resolution tail contains the
appeal route and deadline in admitted source text:

```text
recurso contencioso administrativo ... Audiencia Nacional ... plazo de dos meses
```

Diagnosis:

The source row was queryable through `source_record_text_display/2`, but the
display-surface companion collector was walking runtime clause representations
instead of querying the admitted display predicates directly. Some rich display
rows were available through `runtime.query_rows(...)` but absent from the
collector's fact-row walk. That made semantic-target, alias, date, address, and
similar display companions partially blind.

Change:

Reworked `_source_record_display_surfaces()` to query the admitted display
predicates directly:

- `source_record_text_display/2`
- `source_record_label_display/2`
- `source_record_section_display/2`
- `source_record_cell_display/3`
- `source_record_cell_header_display/3`

Also added two generic semantic-target matching improvements:

- punctuation-normalized token-spaced variants, so a structured target like
  `x-y` can match source display `x y`;
- conservative token-overlap matching for long structured target phrases, so a
  target phrase can match a source row where the key terms are present but not
  contiguous.

Targeted replay:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q016_semantic_overlap_probe_20260527

q016 -> exact
judge_exact: 1
hygiene: 0 runtime, 0 write proposals, 0 compatibility
```

Additional probes:

```text
es_regulator_001:q011 -> still miss
es_regulator_001:q024 -> still miss
```

Read:

The display-surface collector fix is more important than the single recovered
row. It means source-display companions were under-seeing admitted text in some
messy documents. The q016 recovery is evidence that this affects real
non-English transfer, not only one fixture. q011 and q024 should remain open:
q011 currently looks like a compressed-interpretation/oracle-scope problem, and
q024 needs cross-section aggravator synthesis rather than a simple display
retrieval.

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q
-> 510 passed, 2 subtests passed

syntax compile check for scripts\run_domain_bootstrap_qa.py and src\semantic_ir.py
-> pass

active instrument leakage audit
-> pass, 0 forbidden hits, 10 existing warning hits

utterance regex governance audit
-> informational, 0 parse errors

active-code grep for non-English fixture/source names and source-local terms
-> no hits under src/ or scripts/ outside tests
```

Read:

This is mechanism evidence, not a corpus claim. It says the structured-intent
lane can carry a generic "financial/contractual obligation list" question across
languages without raw utterance keyword handling. The next corpus-level question
is whether this reduces misses without churn when the full non-English batch is
rerun.

Next blocker:

Return to `ja_corporate_001:q018`: decide the source-stated-versus-derived
arithmetic policy. That row is not the same class as the Spanish obligation
bundle. It should not be patched by broad obligation support.

## Table Delta Arithmetic Support

Date: 2026-05-27

Focus:

`ja_corporate_001:q018` asks for a period-end value and change from a
prior-period table. The source table preserves current value, prior value, and a
source-stated change. In the total row, the source-stated change differs by one
unit from direct subtraction:

```text
prior: 694,091
current: 913,806
source-stated change: 219,714
derived current-prior change: 219,715
```

Diagnosis:

This is not a compile-only gap. It is an arithmetic/support-surface gap with an
honesty requirement. The system should be allowed to compute `current - prior`
when both values are admitted source display, but it must not hide a discrepancy
between the source-stated change and the derived change.

Change:

Added `source_record_table_delta_check_support` as a query-only arithmetic
support surface. It activates only from structured `query_intents[]` with
generic comparison/change/difference constraints. It does not read the raw
utterance and does not use source-local vocabulary. It scans admitted
source-record display table rows, keeps rows where the third numeric cell is
consistent with `current - prior` within a small rounding tolerance, and returns
both:

- the source-stated delta;
- the derived delta;
- the delta difference;
- derived percentage displays, labeled as calculations.

Local probe:

Using the real `ja_corporate_001` compiled artifact, the support row for
`src_line_0301` is:

```text
prior 694,091; current 913,806; source-stated change +219,714; derived change +219,715; derived percent 31.6551% (1dp rounded 31.7%, 1dp truncated 31.6%); source-stated/derived delta difference +1
```

The local deterministic reference-support check returns true for:

```text
913,806 vs 694,091 (prior period); +219,715 (+31.6%)
```

Hosted probes:

```text
table_delta_probe2 -> exact, but initial table-delta trigger was too narrow and support did not fire
table_delta_probe3 -> miss due planner parse variance / empty query row; not mechanism evidence
table_delta_probe4 -> exact with source_record_table_delta_check_support present
```

`table_delta_probe4` predicate set:

```text
debt_detail
source_record_obligation_bundle_support
source_record_semantic_target_display_support
source_record_semantic_target_window_support
source_record_table_delta_check_support
```

Read:

This keeps the row exact without pretending the source and derived values are the
same. The product-facing answer surface still needs to preserve this
distinction: source-stated change and computed change are different evidence
claims when they disagree.

Verification after the obligation-bundle and table-delta repairs:

```text
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q
-> 500 passed, 2 subtests passed

python -m py_compile scripts\run_domain_bootstrap_qa.py src\semantic_ir.py
-> pass

active instrument leakage audit
-> pass, 0 forbidden hits, 10 existing warning hits

utterance regex governance audit
-> informational, 0 parse errors

active-code grep for non-English fixture/source names and source-local terms
-> no hits under src/ or scripts/ outside tests
```

Next blocker:

Run the fresh non-English batch with the current repairs to measure whether the
two fixed mechanisms reduce misses without moving residue into adjacent rows.

## Current Repair Full Rerun And Address-Line Tightening

Date: 2026-05-27

Full batch rerun:

```text
Dataset: datasets\real_world_transfer\fresh_non_english_wild_20260526_01
Compile root: C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_full_20260526\compile_display_full
QA artifact: C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_repairs_full_qa_20260527\qa
Model: qwen/qwen3.6-35b-a3b via OpenRouter
Lanes: 6
Cache: disabled
```

Result:

```text
200 rows
171 / 15 / 14 = 85.5% exact
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per fixture:

```text
de_corporate_001:       21 / 1 / 3
de_regulator_001:       22 / 2 / 1
es_public_procurement_001: 19 / 4 / 2
es_regulator_001:       20 / 4 / 1
fr_eu_official_001:     23 / 0 / 2
fr_regulator_001:       24 / 0 / 1
ja_corporate_001:       22 / 1 / 2
ja_regulator_001:       20 / 3 / 2
```

Comparison to the previous display-full baseline:

```text
baseline: 163 / 14 / 23
current:  171 / 15 / 14
delta:    +8 exact, +1 partial, -9 miss

changed rows: 28
improved rows: 21
regressed rows: 7

partial -> exact: 8
miss -> partial: 7
miss -> exact: 6
exact -> partial: 3
exact -> miss: 3
partial -> miss: 1
```

Remaining non-exact rows:

```text
partial: 15
miss: 14

compile_surface_gap: 21
query_surface_gap: 4
hybrid_join_gap: 2
answer_surface_gap: 1
judge_uncertain: 1
```

Regression adjudication:

- `de_regulator_001:q020` appears to be an oracle defect, not a system
  regression. The reference says retailers received fines, while the source
  explicitly says the participating retailers did not receive fine notices.
- `fr_eu_official_001:q015` is planner parse variance: the row produced no
  query plan (`parsed_ok=0`, `query_rows=0`), so it should not be treated as
  mechanism evidence.
- The other regressions need row-level review before any mechanism changes.

Address-line repair:

`es_public_procurement_001:q008` asked for the appellate body and location. The
compile had a durable `recourse_authority` row but the wrong `entity_address`
row, while the admitted source display row contained the correct tribunal name
and postal address. The existing address-block support was raw-English and
U.S.-postal-shaped, so it did not fire.

Added `source_record_address_line_support` as a query-only source-display
surface. It activates only from structured `query_intents[]` address/location
intent, including target terms such as "where is it located" when those terms
come from the Semantic IR plan. It does not inspect the raw utterance and does
not write durable facts.

The first probe showed the right row, but also pulled page/reference rows that
looked postal-ish. The detector was tightened to require local address
structure around the postal candidate: a short address-like number before the
candidate and a locality-like text span after it. This removed BOE page and
reference rows while preserving the tribunal address.

Targeted replay after tightening:

```text
Artifact: C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_q008_address_line_tight_probe2_20260527
q008 -> exact
judge_exact: 1
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Address support after tightening:

```text
AddressLineCount: 3
src_line_0166: appellate tribunal row, postal code 28010
src_line_0170: information-service row, postal code 28003
src_line_0017: contracting entity address row, postal code 28029
```

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q
-> 505 passed, 2 subtests passed

python -m py_compile scripts\run_domain_bootstrap_qa.py src\semantic_ir.py
-> pass

active instrument leakage audit
-> pass, 0 forbidden hits, 10 existing warning hits

utterance regex governance audit
-> informational, 0 parse errors

active-code grep for non-English fixture/source names and source-local terms
-> no hits under src/ or scripts/ outside tests
```

Read:

The non-English corpus improved materially but is not release-clean. The
cleanest current blockers are still compile-surface coverage and planner parse
variance, not hygiene failure. The q008 address repair is useful mechanism
evidence, but it should become a corpus claim only after an affected-slice or
full-batch rerun.

## Spanish Procurement Affected-Slice Rerun

Date: 2026-05-27

Purpose:

After the q008 address-line repair, rerun the affected Spanish procurement
fixture to measure churn before spending a full 200-row non-English rerun.

Operator note:

Two attempted batch-wrapper runs returned all rows ambiguous because
`PRETHINKER_API_KEY` was set in the shell environment and takes precedence over
`OPENROUTER_API_KEY`. Those runs are invalid operator artifacts. The valid run
below explicitly set both `PRETHINKER_API_KEY` and `OPENROUTER_API_KEY` to the
OpenRouter key from `.env.local`.

Valid fixture rerun:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_public_procurement_tight_address_batch_qa3_20260527\qa

Fixture:
es_public_procurement_001

Rows:
25

Result:
21 / 3 / 1

Hygiene:
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
parsed plans: 25 / 25
```

Comparison to the previous full non-English rerun for the same fixture:

```text
previous: 19 / 4 / 2
current:  21 / 3 / 1

changed verdict rows:
q005: partial -> exact
q008: miss -> exact

regressions:
none observed
```

Remaining non-exact rows after q008:

```text
q013: miss
q016: partial
q019: partial
q024: partial
```

Adjudication:

- `q013` asks for a common English technical translation and whether it appears
  in BOE vs DOUE. The source evidence available to Prethinker contains the
  Spanish term and source-publication metadata, but not the PED/PSD translation
  or an explicit translation-presence claim. Treat as external-knowledge /
  external-document pressure, not a source-grounded compile repair.
- `q019` asks for the 15-business-day recourse period. The source points to RDL
  3/2020 article 121 but does not state the duration. Treat as external-law
  resolution pressure, not a source-only row.
- `q024` asks for LCSP articles 203-207 and a typical 20% modification limit.
  The source points to the PCAP/contract terms but does not include those
  details. Treat as external-document/legal-reference pressure.
- `q016` is the remaining source-grounded repair candidate: all date evidence is
  in admitted source display or compiled date facts, but it was not compactly
  packaged for chronology judgment.

## Structured Date Inventory Repair

Date: 2026-05-27

Focus:

`es_public_procurement_001:q016` asks for chronological ordering of four
source-grounded events. The existing query results carried the evidence across
several surfaces:

- `publication_date(..., 2024_08_13)`
- `submission_deadline(..., 2024_09_05t12_00)`
- source display for DOUE submission: `02 de agosto de 2024`
- source display for modifying notice publication: `22 de agosto de 2024`

The reference judge repeatedly treated the split evidence as partial, especially
when the Semantic IR intent varied between `ordered_labeled_entry` and
`document_chronology`.

Change:

Extended the existing `source_record_dated_event_inventory_support` surface
rather than introducing a new helper. It now has a structured-intent activation
path:

- activates from `query_intents[]` with `ordered_labeled_entry` or chronology
  intent/constraints;
- does not inspect raw utterance text for the new path;
- scans admitted `source_record_text_display` / `source_record_cell_display`
  rows for text-form date mentions using generic day-year structure;
- keeps raw-utterance activation only for the pre-existing English inventory
  path.

Tightening:

The first implementation picked up statute-like identifiers such as `3/2020`.
The display-date parser now requires a letter-bearing middle span between day
and year for text-form dates, which keeps rows like `13 de agosto de 2024` and
drops bare cross-reference shapes like `3/2020`.

Targeted q016 replay:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_q016_structured_date_inventory_tight_probe2_20260527

q016 -> exact
judge_exact: 1
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Four-row residue replay:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_residue_q013_q016_q019_q024_probe_20260527

q013 -> miss
q016 -> exact
q019 -> partial
q024 -> miss

aggregate: 1 / 1 / 2
hygiene: 0 runtime, 0 write proposals, 0 compatibility
```

Read:

The date repair is source-grounded and transfer-shaped: it packages admitted
date-bearing source display rows under a structured chronology intent. The other
three Spanish procurement residues should not be patched inside the instrument;
they are external-knowledge/external-document rows. This distinction matters for
the non-English score: some of the remaining gap is not caused by language
handling or compile failure, but by oracle scope exceeding the supplied source
document.

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q
-> 508 passed, 2 subtests passed

python -m py_compile scripts\run_domain_bootstrap_qa.py src\semantic_ir.py
-> pass

active instrument leakage audit
-> pass, 0 forbidden hits, 10 existing warning hits

utterance regex governance audit
-> informational, 0 parse errors

active-code grep for non-English fixture/source names and source-local terms
-> no hits under src/ or scripts/ outside tests
```

## Local LM Studio Serial Compile + QA Probe

Date: 2026-05-27

Purpose:

Measure whether the full non-English wild batch can run against local LM Studio
on the 5090, one fixture at a time, and capture wallclock cost before deciding
whether local is a practical path for broader multilingual stamps.

Scope:

```text
Dataset:
datasets/real_world_transfer/fresh_non_english_wild_20260526_01

Run artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_local_lmstudio_serial_compile_source_20260527

Model/provider path:
qwen/qwen3.6-35b-a3b via local LM Studio

Lane discipline:
compile lanes: 1
QA lanes: 1
fixture order: dataset order
compile mode: fresh compile with --compile-source
QA mode: no cache, 25 questions per fixture
```

Note:

A prior profile-only launch without `--compile-source` was stopped and excluded.
The measurements below are from the corrected compile-source run.

Aggregate result:

```text
wallclock: 2:01:55

QA:
165 / 25 / 10 = 82.5%

hygiene:
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0

failure surfaces:
compile_surface_gap: 22
hybrid_join_gap: 4
query_surface_gap: 6
answer_surface_gap: 3
```

Per-fixture timing and score:

```text
de_corporate_001:          compile 135s, QA 858s, 20 / 2 / 3
de_regulator_001:          compile 138s, QA 714s, 24 / 1 / 0
es_public_procurement_001: compile 128s, QA 781s, 20 / 4 / 1
es_regulator_001:          compile 152s, QA 792s, 20 / 5 / 0
fr_eu_official_001:        compile 161s, QA 753s, 23 / 0 / 2
fr_regulator_001:          compile 120s, QA 697s, 25 / 0 / 0
ja_corporate_001:          compile 290s, QA 775s, 18 / 5 / 2
ja_regulator_001:          compile 158s, QA 661s, 15 / 8 / 2
```

Timing read:

```text
total compile time: 21.4 minutes
average compile time: 2.7 minutes per fixture
total QA time: 100.5 minutes
average QA time: 12.6 minutes per fixture
```

Interpretation:

Local LM Studio is viable for serial compiles and does not destabilize hygiene,
but one-lane local QA is slow enough that broad multilingual QA remains an
overnight-style path unless parallelized carefully. The score landed below the
latest OpenRouter non-English run, with the main loss concentrated in Japanese
fixtures, especially `ja_regulator_001`. Treat this as provider/path variance
plus fresh-compile variance until row-level diff proves otherwise.

Next useful comparison:

Run a row-level diff between this local serial result and the latest OpenRouter
non-English result before tuning anything. If losses cluster around known
compile-surface carriers, it is a normal repair target. If they are judge/render
drift, this is a provider selection issue, not an instrument issue.

## OpenRouter vs Local Provider-Path Variance Probe

Date: 2026-05-27

Purpose:

Measure whether the same named model behaves equivalently when hosted through
OpenRouter instead of local LM Studio. This was run immediately after the local
serial probe, using the same dataset, same serial lane discipline, fresh
compile-source artifacts, and no QA cache.

Scope:

```text
Dataset:
datasets/real_world_transfer/fresh_non_english_wild_20260526_01

OpenRouter artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_openrouter_serial_compile_source_variance_20260527

Local comparison artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_local_lmstudio_serial_compile_source_20260527

Model:
qwen/qwen3.6-35b-a3b

OpenRouter base URL recorded by run wrapper:
https://openrouter.ai/api/v1

Lane discipline:
compile lanes: 1
QA lanes: 1
compile mode: fresh compile with --compile-source
QA mode: no cache, 25 questions per fixture
```

Run caveat:

All fixture compile and QA phases returned `rc=0`. The final summary step failed
because the wrapper still referenced stale script names
`scripts\summarize_domain_bootstrap_batch.py` and
`scripts\summarize_domain_bootstrap_qa_batch.py`. Aggregate numbers below were
therefore computed from the per-fixture QA JSON/log summaries, not from the
overwritten one-fixture batch summary files.

Metadata caveat:

Some raw compile JSON still reports `"backend": "lmstudio"` even inside the
OpenRouter artifact. The run wrapper log records the OpenRouter base URL and
model at launch. This is a harness metadata bug: benchmark artifacts should
record compile provider path and QA provider path directly in the per-fixture
JSON, not only in wrapper logs.

Aggregate comparison:

```text
OpenRouter serial:
174 / 14 / 12 = 87.0%

Local LM Studio serial:
165 / 25 / 10 = 82.5%

Delta:
+9 exact, -11 partial, +2 miss

Hygiene:
OpenRouter runtime/write/compatibility: 0 / 0 / 0
Local runtime/write/compatibility:      0 / 0 / 0
```

Timing comparison:

```text
OpenRouter phase sum: 2:49:23
Local phase sum:      2:01:54

OpenRouter compile total: 3268s
Local compile total:      1283s

OpenRouter QA total:      6895s
Local QA total:           6031s
```

Per-fixture comparison:

```text
fixture                    OR score     local score   exact delta   OR compile/QA     local compile/QA
de_corporate_001           21 / 0 / 4   20 / 2 / 3    +1            176s / 861s       135s / 858s
de_regulator_001           23 / 1 / 1   24 / 1 / 0    -1            197s / 977s       138s / 714s
es_public_procurement_001  20 / 4 / 1   20 / 4 / 1     0            471s / 806s       128s / 781s
es_regulator_001           22 / 3 / 0   20 / 5 / 0    +2            907s / 819s       152s / 792s
fr_eu_official_001         23 / 0 / 2   23 / 0 / 2     0            698s / 1004s      161s / 753s
fr_regulator_001           25 / 0 / 0   25 / 0 / 0     0            232s / 736s       120s / 697s
ja_corporate_001           22 / 2 / 1   18 / 5 / 2    +4            418s / 846s       290s / 775s
ja_regulator_001           18 / 4 / 3   15 / 8 / 2    +3            170s / 848s       158s / 661s
```

Compile artifact comparison:

```text
fixture                    OR admitted/skipped   local admitted/skipped
de_corporate_001           17 / 20               22 / 4
de_regulator_001           46 / 9                63 / 3
es_public_procurement_001  37 / 0                65 / 3
es_regulator_001           88 / 1                51 / 0
fr_eu_official_001         48 / 8                72 / 0
fr_regulator_001           30 / 2                61 / 7
ja_corporate_001           87 / 37               115 / 30
ja_regulator_001           66 / 39               54 / 43
```

Failure surface comparison:

```text
OpenRouter:
compile_surface_gap: 20
hybrid_join_gap: 3
answer_surface_gap: 1
judge_uncertain: 2

Local LM Studio:
compile_surface_gap: 22
hybrid_join_gap: 4
query_surface_gap: 6
answer_surface_gap: 3
```

Read:

Provider-path variance is real and material. OpenRouter scored higher overall,
mainly on the two Japanese fixtures and `es_regulator_001`, but it was slower
in this serial run and produced materially different compile artifacts. The
variance is not monotonic: `de_regulator_001` regressed on OpenRouter, while
several fixtures had the same headline score with different internal surfaces.

Discipline correction:

OpenRouter and local LM Studio should no longer be treated as interchangeable
benchmark conditions, even for the same named model. Future claims need to pin:
compile provider path, QA provider path, model id, lane count, cache mode,
fresh-vs-reused compile state, and artifact root. Existing cross-provider
comparisons should be caveated unless the artifacts prove the provider path was
the same.

Do not tune against this variance yet. The immediate next move is row-level
provider diffing on the changed rows, especially Japanese gains and
`de_regulator_001` regression, to distinguish compile coverage variance from
judge/render variance.

## Row-Level Provider Diff: Local LM Studio Baseline vs OpenRouter Candidate

Date: 2026-05-27

Artifact:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_provider_row_diff_20260527
```

Scope:

This is an `N=1` provider-path diff, not a stability claim. It compares the
local serial compile-source run against the OpenRouter serial compile-source
run for the same eight non-English fixtures.

Aggregate row churn:

```text
rows with detail coverage: 200
changed rows: 26
improved rows: 17
regressed rows: 9

local exact -> OR non-exact: 6
local exact -> OR miss: 3

aggregate headline:
local: 165 / 25 / 10 = 82.5%
OR:    174 / 14 / 12 = 87.0%
delta: +9 exact, -11 partial, +2 miss

regression guard:
fail
```

Verdict movement:

```text
partial -> exact: 13
miss -> exact:    2
miss -> partial:  2

partial -> miss:  3
exact -> partial: 3
exact -> miss:    3
```

Churn by fixture:

```text
ja_regulator_001:          7 changed
ja_corporate_001:          6 changed
es_public_procurement_001: 4 changed
de_regulator_001:          3 changed
de_corporate_001:          2 changed
es_regulator_001:          2 changed
fr_eu_official_001:        2 changed
fr_regulator_001:          0 changed
```

Surface transitions:

```text
query_surface_gap -> not_applicable:   6
compile_surface_gap -> not_applicable: 5
not_applicable -> compile_surface_gap: 5
compile_surface_gap -> compile_surface_gap: 4
answer_surface_gap -> not_applicable:  2
hybrid_join_gap -> not_applicable:     2
not_applicable -> hybrid_join_gap:     1
compile_surface_gap -> judge_uncertain:1
```

Regression rows:

```text
de_corporate_001 q010
partial -> miss; compile_surface_gap -> compile_surface_gap
Reference requires new VW margin assumption "~5.6%"; both runs agree the source
does not directly support that value. This is judge strictness/oracle-scope
pressure, not a clean compile repair target.

de_regulator_001 q016
exact -> partial; not_applicable -> compile_surface_gap
OR lost the local source_detail/procedural_status path carrying publication
date 2024-07-02 and finality; OR instead surfaced decision date 2024-06-10.
This is a real compile/query artifact variance.

de_regulator_001 q025
exact -> miss; not_applicable -> hybrid_join_gap
OR lost local liable_party_role/no_fine_issued_to shape. This is a real
coexistence/negative-constraint artifact variance.

es_public_procurement_001 q013
partial -> miss; compile_surface_gap -> compile_surface_gap
Reference asks for common English PED/PSD and DOUE translation status. The
supplied BOE source does not appear to carry the full answer. This is
oracle/source-scope pressure, not a mechanism repair target unless the fixture
package includes the DOUE document.

es_public_procurement_001 q018
exact -> partial; not_applicable -> compile_surface_gap
OR lost several obligation predicates and the source_record_obligation_bundle
support row that carried advertising cost and maintenance duration. This is a
real compile artifact variance.

fr_eu_official_001 q013
exact -> miss; not_applicable -> compile_surface_gap
Reference asks for French legal-form expansions of SCP/SARL and absence of
English equivalents. OR only supports surface mentions. Local exact may have
overaccepted domain expansion. Treat as source-scope/domain-knowledge pressure
until the source text proves the expansions are explicitly present.

ja_corporate_001 q018
exact -> partial; not_applicable -> compile_surface_gap
Both runs surfaced the core table values, but OR was stricter because the
percentage change is not explicit and the source delta differs by 1. This is
mostly judge/render strictness around derived arithmetic, not a clean compile
repair.

ja_regulator_001 q004
exact -> miss; not_applicable -> compile_surface_gap
OR lost the regulatory_basis_investigation/source-record path carrying SESC.
This is a real compile/query artifact variance.

ja_regulator_001 q010
partial -> miss; compile_surface_gap -> compile_surface_gap
OR compiled generic administrative/source_claim rows, while local carried more
specific legal_article_reference/management_deficiency/regulatory_action rows.
This is a real compile palette variance, but the row was not exact locally
either.
```

Compile-level variance:

```text
fixture                    admitted delta   skipped delta   unique fact delta
de_corporate_001           -5               +16             -5
de_regulator_001           -17              +6              -25
es_public_procurement_001  -28              -3              -25
es_regulator_001           +37              +1              +33
fr_eu_official_001         -24              +8              -27
fr_regulator_001           -31              -5              -29
ja_corporate_001           -28              +7              -9
ja_regulator_001           +12              -4              +24
```

Read:

The OpenRouter run's better headline is not monotonic improvement. It is a
different compile/query instrument with row churn: 17 gains, 9 regressions, and
6 local exact rows lost. Some OR regressions are probably more honest judgments
against over-scoped reference answers, but several are true compile artifact
losses. This proves the serving path affects the compiled evidence layer, not
just the final judge wording.

Restored N-cycle discipline:

```text
N=1 discovery:
  A single provider/path run may identify a signal, but cannot certify
  stability or justify public benchmark claims.

N=2 repeat check:
  Repeat the same provider path, same compile/QA lanes, same cache discipline,
  same params. Compare row churn against the first run. This tells us
  within-path repeatability.

N=3 stamp candidate:
  Three runs under the pinned path. Promote a score only if aggregate score,
  hygiene, compile artifacts, and row verdicts are stable enough to bound
  variance. Baseline-exact regressions must be separately inspected.
```

Provider-path rule:

Do not mix local LM Studio and OpenRouter runs inside one score claim. Compare
them as separate instruments:

```text
Prethinker + qwen/qwen3.6-35b-a3b + local LM Studio path
Prethinker + qwen/qwen3.6-35b-a3b + OpenRouter pinned provider path
```

Next:

Fix run metadata so each per-fixture compile and QA JSON records provider path,
base URL, decoding params, cache mode, lane count, and provider pin. Then run
an `N=2` repeat on the chosen calibration path before drawing repair
conclusions from provider-specific residue.

## Measurement Harness Metadata Repair

Date: 2026-05-27

Purpose:

The provider-path variance probe showed that `backend=lmstudio` was not enough
metadata. In these scripts it means "OpenAI-compatible chat transport," not
"local LM Studio was the provider." That ambiguity let OpenRouter artifacts
look locally served when only the wrapper log proved otherwise.

Change:

Added explicit `model_serving_path_v1` metadata to compile and QA artifacts.

Recorded fields:

```text
transport_backend
provider_family
base_url
model
provider_routing
temperature
top_p
top_k
context_length
max_tokens
timeout_seconds
lanes
cache_enabled
fresh_compile
run_role
```

Provider family is now derived separately from transport backend:

```text
https://openrouter.ai/... + backend=lmstudio -> provider_family=openrouter
http://127.0.0.1:1234 + backend=lmstudio   -> provider_family=local_lmstudio
```

OpenRouter routing controls:

The compile and QA runners, plus their batch wrappers, now accept and forward:

```text
--openrouter-provider-order
--openrouter-provider-only
--openrouter-provider-ignore
--openrouter-quantizations
--openrouter-allow-fallbacks true|false
--openrouter-require-parameters true|false
```

When the base URL is OpenRouter, those controls are sent in the request payload
under `provider` and recorded in `model_serving_path.provider_routing`. API keys
are not recorded.

Files changed:

```text
src/model_path.py
src/semantic_ir.py
scripts/run_domain_bootstrap_file.py
scripts/run_domain_bootstrap_qa.py
scripts/run_domain_bootstrap_file_batch.py
scripts/run_domain_bootstrap_qa_batch.py
tests/test_model_path.py
tests/test_domain_bootstrap_file.py
tests/test_domain_bootstrap_file_batch.py
tests/test_domain_bootstrap_qa_batch.py
```

Stale summary-script finding:

No live repo script still references the missing
`summarize_domain_bootstrap_batch.py` or `summarize_domain_bootstrap_qa_batch.py`
helpers. That failure belonged to the ad hoc archived serial wrapper. The
maintained batch runners already write `compile_batch_summary.*` and
`qa_batch_summary.*` directly.

Verification:

```text
python -m pytest tests\test_model_path.py tests\test_domain_bootstrap_file.py::test_lmstudio_json_schema_adds_openrouter_provider_routing tests\test_domain_bootstrap_file_batch.py::test_compile_batch_command_forwards_openrouter_provider_controls tests\test_domain_bootstrap_qa_batch.py::test_qa_batch_command_forwards_openrouter_provider_controls -q
-> 7 passed

python -m pytest tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_qa_batch.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_model_path.py -q
-> 658 passed

python -m pytest tests\test_semantic_ir_runtime.py -q
-> 94 passed, 2 subtests passed

python -m py_compile src\model_path.py src\semantic_ir.py scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_qa.py scripts\run_domain_bootstrap_file_batch.py scripts\run_domain_bootstrap_qa_batch.py
-> pass
```

Next:

Run an `N=2` repeat only after choosing a calibration path. The strongest
candidate is local LM Studio if we can pin the local model artifact and serving
settings tightly enough; OpenRouter remains useful, but serious OR claims
should use explicit provider routing and `allow_fallbacks=false`.

## OpenRouter Generation Metadata Repair

Date: 2026-05-27

Purpose:

The previous repair recorded what Prethinker requested. That was necessary but
not enough. A benchmark artifact must also record what OpenRouter actually
served, because the same model slug can route through different providers,
quantizations, endpoint health states, fallback attempts, and native parameter
handling.

Change:

Added `openrouter_generation_metadata_v1` capture for OpenRouter-backed LLM
calls. The live compile, QA, Semantic IR, and direct-source baseline paths now:

```text
request X-OpenRouter-Experimental-Metadata: enabled
record sanitized request settings without prompt/source/completion bodies
record response metadata from the chat completion body
look up GET https://openrouter.ai/api/v1/generation?id=<generation_id>
record retrieved generation metadata when available
record lookup failure/missing-key/missing-id as explicit metadata state
```

The captured surface is intended to expose:

```text
generation id
actual provider_name
actual model
router / routing path
latency and generation timing
prompt/completion/native token counts
reasoning/cache token counts when returned
total cost and upstream cost when returned
finish_reason and native_finish_reason
fallback/attempt/router metadata when returned
requested provider routing and decoding settings
```

Privacy boundary:

API keys are never recorded. Prompt/source/completion bodies are not copied into
the metadata surface. The generation-content endpoint is deliberately not called
by default; if needed later, it should be a private debug-only artifact with an
explicit opt-in.

Important correction:

OpenRouter API-key priority is now OpenRouter-specific:

```text
explicit --api-key
OPENROUTER_API_KEY
PRETHINKER_API_KEY
```

This prevents a local/generic `PRETHINKER_API_KEY` placeholder from silently
poisoning OpenRouter metadata lookup.

Files changed:

```text
src/model_path.py
src/semantic_ir.py
scripts/run_domain_bootstrap_file.py
scripts/run_domain_bootstrap_qa.py
scripts/run_direct_source_qa_baseline.py
tests/test_model_path.py
tests/test_domain_bootstrap_file.py
```

Discipline consequence:

Older OpenRouter/local variance comparisons are useful discovery artifacts, but
they are under-instrumented. Future provider/model variance claims should be
labeled by requested path plus retrieved OpenRouter generation metadata, and
should return to the N=1/N=2/N=3 repeat discipline before treating a delta as
architecture signal.

Verification:

```text
python -m py_compile src\model_path.py src\semantic_ir.py scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_qa.py scripts\run_direct_source_qa_baseline.py
-> pass

python -m pytest tests\test_model_path.py tests\test_domain_bootstrap_file.py::test_lmstudio_json_schema_adds_openrouter_provider_routing tests\test_domain_bootstrap_file.py::test_lmstudio_json_schema_retries_empty_content -q
-> 8 passed

python -m pytest tests\test_model_path.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_qa_batch.py -q
-> 660 passed

python -m pytest tests\test_semantic_ir_runtime.py tests\test_direct_source_qa_baseline.py tests\test_compare_domain_bootstrap_compiles.py tests\test_rollup_domain_bootstrap_qa_scorecard.py -q
-> 105 passed, 2 subtests passed

python -m pytest -q
-> 1927 passed, 2 subtests passed
```

## OpenRouter Metadata Live Smoke

Date: 2026-05-27

Artifacts:

```text
C:\prethinker_tmp_archive\openrouter_metadata_smoke_20260527
```

QA smoke:

```text
fixture: de_corporate_001
row: q001
run: one-row QA, no cache, OpenRouter, qwen/qwen3.6-35b-a3b
result: exact
artifact:
C:\prethinker_tmp_archive\openrouter_metadata_smoke_20260527\qa_de_corporate_q001_retry\domain_bootstrap_qa_20260527T164036313797Z_qa_qwen-qwen3-6-35b-a3b.json
```

Metadata result:

```text
semantic_ir_openrouter_generation_metadata present: yes
generation lookup: retrieved
lookup attempts: 4
actual provider: Ambient
actual model: qwen/qwen3.6-35b-a3b-20260415
response router summary: available=5, selected=Ambient
total_cost: 0.00870575
latency: 3369
prompt tokens: 49401
completion tokens: 641
```

Compile smoke:

```text
fixture: de_corporate_001
run: fresh compile-source, OpenRouter, qwen/qwen3.6-35b-a3b
artifact:
C:\prethinker_tmp_archive\openrouter_metadata_smoke_20260527\compile_de_corporate_final2\domain_bootstrap_file_20260527T165033299920Z_source_qwen-qwen3-6-35b-a3b.json
```

Metadata result:

```text
top-level openrouter_generation_metadata entries: 4
call roles: intake_plan_v1, profile_bootstrap_v1, source_entity_ledger_v1, semantic_ir
all generation ids present: yes
all lookups retrieved: yes
providers by call: Ambient, Parasail, Ambient, AkashML
actual model: qwen/qwen3.6-35b-a3b-20260415
source_compile.semantic_ir_openrouter_generation_metadata present: yes
source compile provider: AkashML
compile admitted/skipped: 10 / 4
```

Leakage check:

```text
metadata contains API key: false
metadata contains INPUT_JSON prompt body marker: false
metadata contains checked source phrase: false
metadata contains checked question text: false
```

Important finding:

The same single compile used four different OpenRouter providers across its
LLM calls: Ambient, Parasail, Ambient, and AkashML. The old phrase
`qwen/qwen3.6-35b-a3b via OpenRouter` was therefore not a sufficiently specific
instrument label. Future OR measurements must record and compare per-call
provider routing/generation metadata.

Implementation correction discovered during smoke:

OpenRouter `/generation?id=...` can lag behind the chat response. The first
QA smoke returned response-level router metadata immediately, but an immediate
generation lookup returned 404; a delayed lookup succeeded. The helper now does
bounded retry/backoff and the run writers perform a final refresh before
writing artifacts. This gives early compile calls time to become retrievable
without blocking every individual call for an excessive period.

Regression caught and fixed:

The first final-refresh implementation could clear already-retrieved metadata
entries by mutating a dict against itself. The compile smoke exposed `{}` rows
in `openrouter_generation_metadata`; the helper now preserves already-retrieved
entries and has a regression test for that case.

Verification after smoke fixes:

```text
python -m pytest tests\test_model_path.py tests\test_domain_bootstrap_file.py::test_lmstudio_json_schema_adds_openrouter_provider_routing tests\test_domain_bootstrap_file.py::test_lmstudio_json_schema_retries_empty_content -q
-> 11 passed

python -m py_compile src\model_path.py src\semantic_ir.py scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_qa.py scripts\run_direct_source_qa_baseline.py
-> pass

python -m pytest tests\test_model_path.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_qa.py tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_qa_batch.py tests\test_semantic_ir_runtime.py tests\test_direct_source_qa_baseline.py -q
-> 761 passed, 2 subtests passed

python -m pytest -q
-> 1930 passed, 2 subtests passed
```

## Local LM Studio Q8 Speed Probe

Date: 2026-05-27

Artifacts:

```text
C:\prethinker_tmp_archive\local_q8_speed_probe_20260527
```

Context:

The local default for `qwen/qwen3.6-35b-a3b` was switched from the prior
Q4_K_M-like local path to Q8_0. LM Studio was also changed to load the model
with a smaller context.

LM Studio `/api/v0/models/qwen/qwen3.6-35b-a3b` reported after reload:

```text
quantization: Q8_0
arch: qwen35moe
compatibility_type: gguf
loaded_context_length: 65536
max_context_length: 262144
state: loaded
```

Important metadata correction:

The harness `--num-ctx 32768` value is recorded in `model_serving_path`, but it
does not currently control LM Studio OpenAI-compatible local requests. LM
Studio used the model's loaded context setting, which was 65536 after the GUI
change. Local runs therefore need both requested harness settings and observed
LM Studio loaded-model metadata.

Speed probes:

```text
tiny raw /v1/chat/completions probe
prompt tokens: 15
completion tokens: 8
wallclock: 0.97s

de_corporate_001 q001, old local compile artifact, no cache, full reference judge
wallclock: 132.83s
artifact:
C:\prethinker_tmp_archive\local_q8_speed_probe_20260527\qa_de_corporate_q001_cold\domain_bootstrap_qa_20260527T175836294847Z_qa_qwen-qwen3-6-35b-a3b.json

de_corporate_001 q001, old local compile artifact, no cache, no reference judge / no failure classifier
wallclock: 37.61s
artifact:
C:\prethinker_tmp_archive\local_q8_speed_probe_20260527\qa_de_corporate_q001_no_judge\domain_bootstrap_qa_20260527T175959966014Z_qa_qwen-qwen3-6-35b-a3b.json
```

Read:

The model can answer tiny prompts quickly, so Q8_0 itself is not dead. The slow
path is large-prompt prefill plus QA judging. The user's GPU observation during
the probe was ~10% utilization with CPU hot across roughly 8 cores, so the
current LM Studio Q8 load profile is still not offloading/pre-filling in a way
that makes Prethinker QA economical.

Immediate consequence:

Do not use the local Q8_0 path for broad QA until local loaded-model metadata is
recorded and the LM Studio load profile is tuned. For local Q8 probes, prefer
one-row or very small affected-set probes and separate:

```text
Semantic IR planning only
reference judge only / full judged QA
fresh compile-source
```

## Runtime Regroup Note

Date: 2026-05-27

The reusable provider/runtime finding has been promoted out of this worksheet to
`docs/PROVIDER_RUNTIME_DISCIPLINE_NOTE.md`.

Short policy:

```text
OpenRouter is the measured research lane for stamps and transfer claims.
Local LM Studio / 5090 is a smoke/probe lane until benchmark equivalence is
proven under captured local metadata.
```

The active next work should return to Prethinker quality: prompt-context
compaction, non-English blocker adjudication, ugly-public transfer checks, and
metadata-complete run discipline.

## Metadata-Complete OpenRouter QA Rerun

Date: 2026-05-27

Purpose:

Rerun the full non-English QA batch on OpenRouter after the Spanish address/date
repairs and after provider metadata discipline landed. This uses the archived
display-full compile artifacts and does not recompile.

Artifact:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_metadata_full_qa_20260527\qa
```

Run shape:

```text
dataset: datasets\real_world_transfer\fresh_non_english_wild_20260526_01
compile root: C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_display_full_20260526\compile_display_full
model: qwen/qwen3.6-35b-a3b
base URL: https://openrouter.ai/api/v1
lanes: 6
cache: disabled
effective per-call timeout: 2520s
```

Operator note:

The outer shell command hit the local 30-minute timeout, but the wrapper process
and child fixture runs finished afterward and wrote `qa_batch_summary.json`.
Treat the run as complete because all eight fixture subprocesses returned 0 and
the batch summary was written.

Result:

```text
200 rows
176 / 10 / 14 = 88.0% exact
parsed plans: 200 / 200
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Per fixture:

```text
de_corporate_001:            21 / 1 / 3
de_regulator_001:            25 / 0 / 0
es_public_procurement_001:   21 / 2 / 2
es_regulator_001:            20 / 4 / 1
fr_eu_official_001:          24 / 1 / 0
fr_regulator_001:            25 / 0 / 0
ja_corporate_001:            22 / 1 / 2
ja_regulator_001:            18 / 1 / 6
```

Comparison to previous full non-English rerun:

```text
previous: 171 / 15 / 14
current:  176 / 10 / 14
delta:    +5 exact, -5 partial, unchanged miss
```

Provider metadata:

```text
openrouter generation metadata entries: 557
generation lookups retrieved: 557 / 557
provider counts:
  Ambient: 160
  Parasail: 139
  AkashML: 108
  SiliconFlow: 97
  WandB: 53
```

Read:

The current repairs sharpened partials but did not reduce total misses. The
remaining loss is concentrated in `ja_regulator_001`, plus a smaller set of
German corporate and Spanish source-scope rows. The cleanest real blocker is
not hygiene or compatibility. It is source-display/date/legal-thread coverage,
with several rows correctly exposing external-document or external-law limits.

## Structured Interval Target Repair

Date: 2026-05-27

Focus:

`ja_regulator_001:q008` asked for the SESC recommendation date and the interval
to the FSA order. The full rerun marked it miss even though admitted source
display contained a yearless Japanese date row and admitted metadata contained
the FSA order date.

Observed failure:

```text
query_intents:
  date target_terms: SESC recommendation, 証券取引等監視委員会勧告, FSA order, 行政処分
  unknown target_terms: date interval indication

old result:
  q008 -> miss
  failure surface: query_surface_gap
```

Change:

Extended existing `source_record_elapsed_date_duration_support` activation so
structured `query_intents[]` target terms such as `date interval`, `elapsed`,
`duration`, `days`, or `period` can activate the date-duration companion. This
uses LLM-authored structured intent terms, not raw utterance regex, and writes
no durable facts.

Targeted replay:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_q008_structured_interval_probe_20260527

q008 -> exact
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Key support row:

```text
SupportKind: source_record_semantic_target_date_duration
StartDate: 2024_06_14
StartSourceRow: src_line_0011
EndDate: 2024_06_24
EndSourceField: source_metadata_date_arg_1
ElapsedDays: 10
Duration: 10 days
```

Read:

This is good mechanism evidence for multilingual date intervals. It should
recover one full-batch miss on the next non-English rerun, but do not treat the
one-row replay as a corpus score. The remaining `ja_regulator_001` misses still
look mostly like legal-basis/source-claim compile-surface gaps and
external-translation scope rows.

Affected fixture replay:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_regulator_full_after_interval_20260527\qa

baseline ja_regulator_001 slice: 18 / 1 / 6
replay ja_regulator_001 slice:   19 / 3 / 3
delta: +1 exact, +2 partial, -3 miss
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
wallclock: 1116s
```

Changed rows:

```text
q008: miss -> exact
q013: miss -> partial
q022: miss -> partial
```

Remaining non-exact rows:

```text
q005 miss    legal-basis source/oracle conflict pressure
q010 miss    violation-category decomposition
q012 partial external translation / legal concept pressure
q013 partial external translation / procedural concept pressure
q021 miss    external abbreviation / translation-status pressure
q022 partial authority recommendation/addressee/scope carrier pressure
```

Provider spread for the replay's Semantic IR calls:

```text
AkashML: 7
Ambient: 6
Parasail: 6
SiliconFlow: 4
WandB: 2
```

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 419 passed

python -m pytest tests\test_model_path.py tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_qa_batch.py -q
-> 83 passed

python -m py_compile scripts\run_domain_bootstrap_qa.py
-> pass
```

## Evidence-Plan Display Filter Bridge

Date: 2026-05-27

Focus:

`ja_regulator_001:q022` exposed a structured-query gap rather than a source
language gap. The evidence-bundle planner correctly tried to locate source
display rows containing named source phrases, but expressed that as
`source_record_text_display(...), member('literal', Text)` over a display
variable. The QA runner did not promote those structured literals into
`query_intents[]`, so the semantic-target source-display companions never saw
the useful targets.

Change:

`_query_intents_from_structured_queries()` now extracts literal filters from
source-record display query templates and emits a query-only
`source_location` intent with `source_display_filter` constraint. This is not
raw utterance parsing and does not add source-language vocabulary to code. It
only preserves model-authored structured evidence-plan literals so the existing
semantic-target display/window companions can operate over admitted
`source_record_*_display` rows.

Targeted replay:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_q022_display_filter_probe_20260527

q022: miss -> partial
runtime load errors: 0
write proposal rows: 0
compatibility rows: 0
```

Recovered support:

```text
source_record_semantic_target_display_support: 2 rows
source_record_semantic_target_window_support: 3 rows
key recovered source row: src_line_0011
```

Read:

This is a clean mechanism improvement but not a complete answer. The admitted
source-display window now supports the SESC recommendation target/scope portion
of the row. The remaining gap is the stronger comparison/legal-expansion claim
in the reference answer, which is not preserved as an explicit durable source
claim in the compile artifact. Do not patch this with Japanese strings or FSA
abbreviation knowledge. The generic next question is whether recommendation /
order / addressee / scope claims should be emitted as a source-claim carrier
when a document states one authority recommended that another authority act.

## Authority Recommendation Chain Probe

Date: 2026-05-27

Purpose:

Test whether the remaining q022 gap can be addressed as a generic authority
chain compile-surface problem rather than a source-language patch.

Changes tested:

- Added compile invariant guidance for source-stated chains where one
  authority/source/reviewer/regulator/committee/court/body recommends,
  requests, refers, advises, reports, submits, or directs another body to act.
- Added profile-bootstrap and profile-review guidance that a target-only
  `recommended_action/3` shape is too weak when the source states a recipient
  or addressee body.

Compile probe 1:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_regulator_authority_chain_compile_probe_20260527\compile

parsed OK: true
candidate predicates: 13
compile admitted / skipped: 50 / 7
rough score: 0.875
new useful carrier: recommended_action/3
q022 replay: partial
```

Read:

The compiler emitted recommendation rows, but `recommended_action/3` carried
recommending body, target company, and recommendation type only. It still
dropped the recipient/addressee body, so q022 remained partial.

Compile probe 2:

```text
Artifact:
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_regulator_authority_chain_profile_probe2_20260527\compile

parsed OK: true
candidate predicates: 10
compile admitted / skipped: 49 / 14
rough score: 1.0
new useful carriers: regulatory_action/5 + recommended_by/2
q022 replay: miss
```

Read:

The second profile shape is structurally better: `regulatory_action/5` includes
issuing body and legal basis, and `recommended_by/2` links SESC to recommended
actions. But it still lacks an explicit recipient/addressee relation and the
QA path did not treat `recommended_by + regulatory_action(issuer=FSA)` as
enough to satisfy the reference. This is not a promoted repair. The open
blocker is now named more precisely: recommendation/referral chains need an
explicit addressee/recipient slot or a query/judge policy that can use a
source-stated recommendation-to-action chain without overclaiming equality of
scope.

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 420 passed

python -m pytest tests\test_model_path.py tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_qa_batch.py -q
-> 83 passed

python -m py_compile src\model_path.py src\semantic_ir.py scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_qa.py scripts\run_domain_bootstrap_file_batch.py scripts\run_domain_bootstrap_qa_batch.py scripts\run_direct_source_qa_baseline.py
-> pass
```

## Authority Chain Guard

Date: 2026-05-27

Purpose:

Turn the failed q022 authority-chain probes into reusable instrumentation
rather than another targeted repair.

Change:

`profile_bootstrap_score()` now reports
`recommendation_chain_slot_loss_refs` when a proposed profile clearly contains
a recommendation/request/referral/action chain surface with a source or
recommending body but no explicit recipient/addressee role anywhere in the
candidate predicate palette. Run summaries now print the same refs.

This is diagnostic only. It does not admit new facts, does not affect QA
judgment, and does not infer that an issuing body was the recipient. That
distinction is exactly what the q022 profile probe taught us not to blur.

Archived-probe check:

```text
compile probe 1 fresh score refs:
  ['recommended_action/3']

profile probe 2 fresh score refs:
  ['recommended_by/2']
```

The first draft of the diagnostic also flagged `reporting_interval/2`; that was
a false positive and was tightened before promotion. Reporting frequency is not
an authority-chain slot-loss surface.

Verification:

```text
python -m pytest tests\test_profile_bootstrap.py -q
-> 21 passed

python -m pytest tests\test_domain_bootstrap_file_batch.py tests\test_domain_bootstrap_file.py -q
-> 231 passed

python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 420 passed

python -m py_compile src\profile_bootstrap.py scripts\run_profile_bootstrap.py scripts\run_domain_bootstrap_file.py
-> pass
```

## Source-Support Validation Guard

Date: 2026-05-27

Purpose:

Separate true compiler/query failures from fixture-oracle pressure that depends
on material outside `source.md`. This matters especially for non-English
fixtures where `fixture_notes.md`, `metadata.json`, and authored answer files
may contain domain explanations, English abbreviations, or answer-bearing legal
terms that the compiler must not see as source truth.

Change:

`scripts/validate_fresh_ugly_batch.py` now emits warning-only source-support
diagnostics when distinctive reference-answer terms are absent from `source.md`
but present in `fixture_notes.md` or `metadata.json`.

Validation run:

```text
python scripts\validate_fresh_ugly_batch.py datasets\real_world_transfer\fresh_non_english_wild_20260526_01 --expected-documents 8 --expected-questions 25 --out-json C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_validation_20260527.json --out-md C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_validation_20260527.md

status: pass
fixtures: 8 / 8
issues: 0
warnings: 31
```

Examples:

```text
de_corporate_001:
  q005 Art. 17 MAR and q006 DE000PAH0038 appear in non-source fixture material
  but not in source.md.

ja_regulator_001:
  q005 Banking Act article terms and several English abbreviation/translation
  expectations are visible in non-source materials or require external
  bilingual/legal authority.
```

Read:

This does not invalidate the batch as a transfer thermometer, but it changes how
misses should be classified. Rows whose reference answer depends on fixture
notes, metadata enrichment, authored answer explanations, or external bilingual
authority are not honest instrument repair targets unless those materials are
explicitly admitted as source. The correct action is to mark them
source-support/oracle-scope pressure, not teach the compiler those terms.

Verification:

```text
python -m pytest tests\test_validate_fresh_ugly_batch.py -q
-> 9 passed

python -m py_compile scripts\validate_fresh_ugly_batch.py
-> pass
```

## Regulatory Category And Legal-Caption Probe

Date: 2026-05-27

Purpose:

Work the remaining `ja_regulator_001` category pressure without teaching the
instrument fixture vocabulary. The row shape is generic: regulatory sources
often state action/intervention type, legal basis, duty captions, and
violation/deficiency categories as separate surfaces. The compiler was
preserving action and legal basis, but either lacked a category-capable carrier
or filled it with an umbrella management/system label.

Changes:

- Added a profile-score diagnostic for regulatory/enforcement/compliance
  profiles that propose action/legal/failure surfaces but lack a direct
  violation/deficiency/finding category carrier.
- Wired that diagnostic into compile-batch quality-gate flags and bounded
  retry context.
- Strengthened generic profile and compile guidance:
  - keep violation/deficiency/finding categories separate from action type and
    legal basis;
  - split source-stated coordinated control areas or failure classes into
    separate category rows;
  - preserve captioned legal duty names and inline section labels separately
    from bare article/section identifiers.
- Tightened recommendation-chain diagnostics so direct regulator-to-target
  report-request predicates are not treated as missing recommendation
  recipients.

Probe reads:

```text
bad non-comparable probe:
  mode: intake_plan_passes only
  result: 8 admitted / 67 skipped, verdict poor
  read: invalid comparison because the healthy baseline used flat-plus mode

comparable flat-plus probe:
  38 admitted / 21 skipped
  targeted q010/q011/q018/q019/q022 QA: 4 exact / 1 partial / 0 miss
  read: carrier still too coarse; q010 partial because one duty category was
        not explicit as a category row

quality-retry first compile:
  74 admitted / 10 skipped
  gained violation_category/4
  targeted five-row QA: 4 exact / 0 partial / 1 miss
  read: category carrier existed but only emitted an umbrella category, so q010
        became miss instead of partial

category-itemization probe:
  126 admitted / 67 skipped
  q010 targeted QA: 0 exact / 1 partial / 0 miss
  read: itemization improved category coverage but still missed some
        legal-duty/category labels; do not treat this as solved

legal-caption probe:
  51 admitted / 39 skipped
  compile health: poor, zero-yield pass present
  profile flags: violation-category slot loss remained
  read: rejected; no QA spend
```

Current interpretation:

The useful generic mechanism is real: legal/regulatory documents need a
separate category surface, and category rows should preserve stated itemization.
The remaining `q010` residue should not be polished further against this single
fixture without an unlike-document probe. It may be a mix of source/oracle
granularity, multilingual legal caption preservation, and query-side category
planning. Next evidence should come from another non-English regulatory/legal
fixture or an affected-set rerun, not another one-row prompt tweak.

Verification:

```text
python -m pytest tests\test_profile_bootstrap.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_file_batch.py -q
-> 258 passed

python -m py_compile src\profile_bootstrap.py scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py scripts\run_profile_bootstrap.py
-> pass
```

## Regulatory Affected-Set Transfer Check

Date: 2026-05-27 / 2026-05-28 UTC

Purpose:

Check whether the regulatory category/caption work transfers beyond the single
Japanese regulatory fixture. The affected set was:

```text
de_regulator_001
es_regulator_001
fr_regulator_001
ja_regulator_001
```

Compile run:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_regulatory_affected_compile_20260527\compile
```

Compile read:

```text
de_regulator_001: 34 admitted / 11 skipped, gate clean
es_regulator_001: 69 admitted / 1 skipped, semantic compile healthy, profile repeated-structure hold
fr_regulator_001: 47 admitted / 7 skipped, QA useful but gate held poor due pass_not_ok/zero_yield
ja_regulator_001: 23 admitted / 36 skipped, poor-health hold
```

QA run:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_regulatory_affected_qa_20260527\qa
```

Affected-set QA:

```text
aggregate: 91 / 6 / 3 over 100 rows
hygiene: 0 compatibility rows, 0 runtime load errors, 0 write proposal rows

de_regulator_001: 24 / 1 / 0
es_regulator_001: 22 / 3 / 0
fr_regulator_001: 25 / 0 / 0
ja_regulator_001: 20 / 2 / 3
```

Compared with the prior OpenRouter non-English baseline for these same four
fixtures:

```text
baseline: 88 / 5 / 7
affected: 91 / 6 / 3
row churn: 9 changed rows
improved: 7
regressed: 2
```

Important row-level read:

```text
de_regulator_001 q019 exact -> partial:
  Not an instrument repair target. The oracle itself says the source gives only
  the legal section and that the detailed settlement-practice conditions are
  external/incomplete-in-source pressure.

ja_regulator_001 q011 exact -> partial:
  Real compiler regression. The compile collapsed an initial fixed deadline and
  recurring quarter-end + 15-day cadence into two bare 15 values.
```

Follow-up changes:

- The validator now warns when oracle pressure tags explicitly declare
  incomplete-source/external-source pressure. Refreshed validation:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_validation_after_incomplete_source_guard_20260527.json

status: pass
fixtures: 8 / 8
issues: 0
warnings: 37
new incomplete-source warnings:
  de_regulator_001: q019
  es_public_procurement_001: q020, q024
  ja_corporate_001: q009, q020
```

- The profile and compile guidance now call out reporting/filing/remediation
  obligations with one-time fixed due dates plus recurring cadence/offset. They
  must preserve requirement type, fixed due date, recurrence anchor, offset
  amount/unit, frequency/duration, governed target, and basis/source rather
  than collapsing into bare day counts.

Targeted verification:

```text
ja_regulator_001 reporting-cadence compile:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reporting_cadence_probe_20260527\compile
  59 admitted / 37 skipped
  gate clean

q011 replay:
  1 / 0 / 0
```

Full fixture replay on that clean compile:

```text
ja_regulator_001: 20 / 3 / 2
hygiene: 0 compatibility rows, 0 runtime load errors, 0 write proposal rows
```

Compared with the baseline, the clean `ja_regulator_001` compile recovered
q008 and q013 to exact, recovered q011 back to exact, moved q005 and q022 to
partial, and left q010/q021 as misses. The remaining residue is mostly
source/oracle-scope or multilingual legal-category pressure:

```text
q005: oracle/reference appears to attribute a report-request legal basis to a
      business-improvement order; treat as source/oracle-scope until adjudicated.
q010: still a real category-granularity pressure, but do not polish further on
      this one fixture without unlike-document evidence.
q012: asks for literal translation/definition not directly provided as a source
      definition row.
q021: asks for English abbreviations/translation status not present in the
      Japanese source text.
q022: partly interpretive "expanded to include Banking Act" framing.
```

Verification:

```text
python -m pytest tests\test_validate_fresh_ugly_batch.py tests\test_profile_bootstrap.py tests\test_domain_bootstrap_file.py tests\test_domain_bootstrap_file_batch.py -q
-> 268 passed

python -m py_compile scripts\validate_fresh_ugly_batch.py src\profile_bootstrap.py scripts\run_profile_bootstrap.py scripts\run_domain_bootstrap_file.py scripts\run_domain_bootstrap_file_batch.py
-> pass
```

## Repeated-Structure Gate Calibration

Date: 2026-05-28 UTC

Purpose:

Inspect affected-set compile holds where QA was strong. The goal was not to
lower the gate, but to separate true profile-shape defects from diagnostic
noise.

Read:

```text
es_regulator_001:
  QA: 22 / 3 / 0
  hold reason: repeated-structure properties with generic arg labels
    procedure_date/2, procedure_actor/2, fine_amount/2, fine_basis/2
  read: fair hold; arg_1/arg_2 schemas are weak and should not be silently
        treated as record-keyed.

fr_regulator_001:
  QA: 25 / 0 / 0
  hold reason included both real issues and false positives.
  False-positive examples:
    sanction_type(sanction, type)
    sanction_amount(sanction, amount, currency)
    sanction_deadline(sanction, deadline)
  These are record-keyed even though the first arg says `sanction` rather than
  `sanction_id` or `record_id`.
```

Change:

`profile_bootstrap_score()` now accepts a repeated-structure property as
record-keyed when the first argument contains a noun from the record predicate
name, in addition to the older `id`/`record`/`subject` markers. This keeps
`sanction_type(sanction, type)` from being flagged while still flagging rows
like `observed_conduct(entity, conduct, service)` under a `sanction_record/2`
structure.

Existing artifact rescore:

```text
es_regulator_001 role-mismatch refs:
  unchanged: fine_amount/2, fine_basis/2, procedure_actor/2, procedure_date/2

fr_regulator_001 role-mismatch refs:
  before: affected_scope/2, aggravating_factor/2, consent_status/3,
          legal_interpretation/3, mitigating_factor/2, observed_conduct/3,
          sanction_amount/3, sanction_deadline/2, sanction_type/2,
          sanctioned_by/2, violation_of/2
  after:  affected_scope/2, consent_status/3, legal_interpretation/3,
          observed_conduct/3, sanctioned_by/2, violation_of/2
```

Verification:

```text
python -m pytest tests\test_profile_bootstrap.py tests\test_domain_bootstrap_file_batch.py -q
-> 94 passed

python -m py_compile src\profile_bootstrap.py
-> pass
```

## Residue Adjudication Guard

Date: 2026-05-28 UTC

Purpose:

Before spending more compile-repair effort, separate actual instrument gaps
from rows where the reference answer itself reaches beyond the source package
or needs human source-support adjudication. This is especially important for
non-English probes because translation labels, external legal abbreviations,
and fixture notes can look like compiler gaps when they are really oracle-scope
pressure.

Change:

- `validate_fresh_ugly_batch.py` now emits row-level `warning_details` for:
  - reference terms absent from `source.md`;
  - reference terms absent from `source.md` but present in fixture notes or
    metadata;
  - oracle pressure tags declaring incomplete/external source pressure.
- Added `scripts/adjudicate_qa_residue.py`.
  - Reads QA artifacts and optional validation details.
  - Does not inspect source prose.
  - Does not judge answers.
  - Classifies non-exact rows into repairable compile/query gaps versus
    source/oracle-scope and source-support-adjudication lanes.

Verification:

```text
python -m py_compile scripts\validate_fresh_ugly_batch.py scripts\adjudicate_qa_residue.py
python -m pytest tests\test_validate_fresh_ugly_batch.py tests\test_adjudicate_qa_residue.py -q
-> 12 passed
```

Current combined view:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_residue_adjudication_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_residue_adjudication_20260528.md

QA artifacts: 8
questions: 200
current combined score: 179 / 12 / 9
hygiene: 0 compatibility rows, 0 runtime load errors, 0 write proposal rows

residue classifications before targeted row override:
  declared_source_or_oracle_limit: 2
  source_support_adjudication_needed: 12
  repairable_compile_gap: 6
  needs_adjudication: 1
```

Read:

The phrase `compile_surface_gap` is not sufficient to authorize compiler work.
After row-level source-support guards, most non-English residue is not yet a
clean repair target. Several rows ask for external translations, later-document
facts, inferred/calculated values, redacted measure details, or source notes
that are not cleanly present in the source package. Those should be adjudicated
or corrected as fixture/oracle issues before they influence the instrument.

The remaining clean-ish repair lane is smaller and more generic:

```text
de_corporate_001 q010:
  replacement-metric / range-to-absolute-value pressure. Source states prior
  range and new absolute operating result, while reference asks an inferred
  approximate margin. Treat cautiously as derived-value pressure, not a direct
  fact unless source support is adjudicated.

es_public_procurement_001 q015:
  later amendment/cross-reference observation appears in source package notes
  section and should be preserved as a source-stated amendment fact.

es_public_procurement_001 q019:
  appeal authority is preserved; deadline value is only present by legal
  citation. This is likely legal-citation-to-deadline scope unless the source
  package directly states the duration.

es_regulator_001 q011 / q019:
  redacted/truncated measures and Article 32 rationale. Treat as source-support
  adjudication first; source displays literal ellipses in key measure lists.

ja_corporate_001 q013:
  ownership composition plus English-version availability. The source package
  contains English-version evidence, but parent/shareholding composition needs
  source-support adjudication before becoming a compiler target.
```

Next rule:

Do not fix every non-English non-exact as an instrument defect. First adjudicate
whether the reference answer is source-contained, externally inferred, or
fixture-note-derived. Only source-contained misses should graduate into compile
or query repairs.

## Source-Update Notice Probe

Date: 2026-05-28 UTC

Purpose:

Probe the apparent procurement amendment gap without trusting the old batch
verdict. The disputed row asked whether a later notice modified a submission
deadline; the source package contains a source-record line stating a later
published notice extended the deadline.

Change:

- Added generic profile/compiler guidance for source-stated later notices,
  corrections, amendments, updates, extensions, supersessions, and observation
  notes that change a deadline/status/scope/amount/requirement.
- This is generic product guidance, not fixture-specific vocabulary and not a
  deterministic helper.
- Added row-level override support to `scripts/adjudicate_qa_residue.py` so a
  targeted replay can replace one row in a current score view without replacing
  the whole fixture.

Verification:

```text
python -m py_compile src\profile_bootstrap.py scripts\run_domain_bootstrap_file.py scripts\adjudicate_qa_residue.py
python -m pytest tests\test_profile_bootstrap.py tests\test_domain_bootstrap_file.py tests\test_adjudicate_qa_residue.py tests\test_validate_fresh_ugly_batch.py -q
-> 204 passed
```

Probe artifacts:

```text
new compile:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_update_notice_probe_20260528\compile

targeted QA on new compile:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_update_notice_probe_20260528\qa_q015
  q015: 1 / 0 / 0

targeted QA on old compile, fresh no-cache:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_update_notice_probe_20260528\qa_q015_old_compile_fresh
  q015: 1 / 0 / 0
```

Read:

The row is not proof that the new compile guidance repaired the fixture. The
old compile also answered the row exactly on a fresh targeted replay. The old
batch miss was therefore at least partly QA/judge variance or context-selection
variance, not a confirmed compiler gap.

The new source-update guidance remains useful because the concept is product
generic, but do not score it as a mechanism win from this row alone.

Fresh repair-labeled row replay:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_repairable_row_fresh_replay_20260528

de_corporate_001 q010: 0 / 0 / 1
es_public_procurement_001 q019: 0 / 0 / 1
es_regulator_001 q011/q019: 0 / 2 / 0
ja_corporate_001 q013: 0 / 1 / 0
```

The replay did not dissolve the remaining rows. It made two rows harsher
(`partial -> miss`) and left three partial. This supports the read that the
remaining residue is mostly source-support/oracle-scope pressure plus a very
small set of possible compiler gaps.

Validator update:

Decimal percentage terms such as `5,6 %` are now preserved as distinctive
reference terms during source-support validation. This catches inferred numeric
answers that were previously split into weak one-digit tokens. The German
corporate margin row is now correctly treated as source-support adjudication
pressure because the requested `~5,6 %` value is not present in the source.

Latest row-override view:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_residue_adjudication_row_override3_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_residue_adjudication_row_override3_20260528.md

questions: 200
current row-override score: 180 / 10 / 10
hygiene: 0 compatibility rows, 0 runtime load errors, 0 write proposal rows

residue classifications:
  declared_source_or_oracle_limit: 2
  source_support_adjudication_needed: 15
  repairable_compile_gap: 2
  needs_adjudication: 1
```

Remaining possible repair rows:

```text
es_regulator_001 q019:
  Article 32 violation rationale. Source directly states lack of appropriate
  technical/organizational measures, but the reference also names specific
  examples that are partly redacted or downstream. This needs source-support
  adjudication before a compiler repair.

ja_corporate_001 q013:
  Ownership composition plus English-version availability. Current source
  package search did not reveal the requested parent/shareholding composition.
  Treat as source-support adjudication before compiler work.
```

## ACH-Style ja_regulator Residue Adjudication

Date: 2026-05-28 UTC

Purpose:

Apply the ACH question explicitly to the Japanese regulator residue before any
more compiler or query intervention:

```text
For each row, does the compiled artifact contain the facts needed to answer?
If yes, classify as query/join/rendering pressure.
If no, classify as compile coverage or source/oracle-scope pressure.
```

Inputs:

```text
source fixture:
  datasets\real_world_transfer\fresh_non_english_wild_20260526_01\ja_regulator_001

current compile:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reporting_cadence_probe_20260527\compile\ja_regulator_001\domain_bootstrap_file_20260528T004409761781Z_source_qwen-qwen3-6-35b-a3b.json

current QA:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reporting_cadence_probe_20260527\qa_full\domain_bootstrap_qa_20260528T010155002066Z_qa_qwen-qwen3-6-35b-a3b.json

source-support validation:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_validation_with_row_details2_20260528.json
```

ACH read:

```text
q005:
  asks for the legal basis of the business-improvement order against the bank.
  source line 13 ties the business-improvement order to Financial Instruments
  and Exchange Act article 51-2 / 51, and separately ties report demands to
  Banking Act article 52-31 / 24. The reference asks for Banking Act article 26
  plus article 24; article 26 is absent from the source and only appears in
  fixture notes.

  compiled artifact contains:
    regulatory_action(... entity_mufj, business_improvement_order, norm_fsw_51_2)
    regulatory_action(... entity_mufj, request_for_report, norm_bank_24)
    source_record_text_display(src_line_0013, ...)

  ACH classification:
    source/oracle-scope conflict, not a compiler repair.

q010:
  asks for violation categories. Source rows contain the management/compliance/
  customer-info/backbone language, but the authored answer names sharper
  categories such as "information sharing" and "other-business prohibition
  violation" that are not explicitly present with that granularity.

  compiled artifact contains:
    source rows for the relevant list items;
    broad semantic facts such as action_requirement(...) and
    admits_control_failure(... insufficient_management_system_for_bank_securities_linkage_business).

  compiled artifact does not contain:
    a structured violation-category carrier with the requested category list.

  ACH classification:
    mixed. The source row is present; the semantic category carrier is missing;
    the reference also over-specifies at least two category labels. Do not patch
    this single row until a cleaner source-contained category case repeats.

q012:
  asks for literal English meaning of a Japanese business term and why it is the
  regulatory pain point. The pain-point portion is source-supported by the
  Banking Act article 12 / article 12-2 rows and by source rows about compliance
  and customer information management. The literal English meaning and English
  phrasing are translation/external-knowledge pressure.

  compiled artifact contains:
    source rows for the term and legal pain point;
    admits_control_failure(...);
    source rows for article 12 and article 12-2 customer-information language.

  compiled artifact does not contain:
    a source-stated definition or official English translation.

  ACH classification:
    partial query/source-scope issue, not a compile repair unless product policy
    explicitly permits translation inference as an answer surface.

q013:
  current QA scored exact, but ACH says the exact should be treated carefully.
  The question asks for FSA English-site terminology. Source does not include
  BIO/RSO, "Business Improvement Order", "Report Submission Order", or English
  website status. The compile has internal action-type atoms and the legal
  distinction, but not the claimed external English-site evidence.

  ACH classification:
    suspect exact / external-source leakage. Keep out of repair math; if this
    row matters, the oracle needs either a source package with the English page
    or a source-contained reference answer.

q021:
  asks for standard English abbreviations and whether the release is translated.
  BA/FIEA and translation status are absent from the source and show up in
  notes/metadata validation rather than source text.

  ACH classification:
    source/oracle-scope conflict, not a compiler repair.

q022:
  asks whether the SESC recommendation and FSA orders are identical, and which
  companies the SESC recommendation addressed. Source line 11 supports the
  recommendation chain and names the bank plus securities subsidiary; source
  line 13 supports later FSA actions under both securities and banking statutes.
  The reference's "expanded to include Banking Act" framing is interpretive and
  not stated as such in the source. It also compresses the addressee chain by
  saying FSA Commissioner while source line 11 names both the Prime Minister
  and FSA Commissioner.

  compiled artifact contains:
    source_record_text_display(src_line_0011, ...)
    source_record_text_display(src_line_0013, ...)
    regulatory_action(...) rows for FSA actions.

  compiled artifact does not contain:
    a first-class recommendation event carrier, nor an admitted "expanded from
    SESC scope to Banking Act scope" relation.

  ACH classification:
    mixed source-carrier plus oracle-framing issue. A generic recommendation /
    authority-chain carrier may be worth testing later, but this row is not a
    clean repair target while the reference contains unstated expansion logic.
```

Read:

The ACH pass makes the next move clearer: do not spend a full non-English rerun
or another Japanese-regulator polish pass yet. The six named rows are dominated
by source/oracle-scope pressure and translation/external-reference pressure,
with only one reusable product-shaped hint: a future generic
recommendation/authority-chain carrier may help real regulator documents, but it
should be tested on fresh documents rather than this row.

Failure-surface discipline:

```text
compile-side candidate:
  none clean enough to patch now

query/join-side candidate:
  q012 pain-point join is partially present, but the missing literal translation
  is policy/source-scope, not retrieval

oracle/source-support candidate:
  q005, q013, q021, q022, plus part of q010 and q012

product-policy question:
  Should Prethinker answer translation/abbreviation questions from model
  knowledge when the source package lacks the English/translation source?
  Current discipline says no for scored QA.
```

## Source-Support Adjudication Ledger

Date: 2026-05-28 UTC

Move:

Turn the ACH read into a reusable scoring discipline. Added a batch-level
source-support adjudication ledger:

```text
datasets\real_world_transfer\fresh_non_english_wild_20260526_01\source_support_adjudication_20260528.json
```

The ledger is explicitly outside the instrument path. It is not read by the
compiler, query planner, or runtime. Its purpose is to keep raw score visible
while also marking rows that should not be treated as source-contained
instrument failures until the oracle/source package is repaired.

Added reporting tool:

```text
scripts\score_source_support_adjudication.py
tests\test_source_support_adjudication_score.py
```

Verification:

```text
python -m py_compile scripts\score_source_support_adjudication.py
python -m pytest tests\test_source_support_adjudication_score.py tests\test_adjudicate_qa_residue.py -q
-> 5 passed
```

Generated report:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_source_support_score_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_source_support_score_20260528.md
```

Score view:

```text
raw current row-override score:
  180 / 10 / 10 on 200 rows

reviewed rows:
  6 ja_regulator rows

excluded/review-before-scoring rows:
  q005 oracle_overreach
  q010 ambiguous_requires_review
  q012 external_knowledge_required
  q013 suspect_exact_external_source
  q021 external_knowledge_required
  q022 ambiguous_requires_review

provisional source-contained view after these reviewed rows are set aside:
  179 / 7 / 8 on 194 rows
  exact rate 92.27%
```

Read:

This is not a score-inflation move. It makes the raw score and the
source-contained subset diverge openly. The useful finding is that the Japanese
regulator residue is not currently a clean compiler-repair queue; it is mostly
oracle/source-package cleanup plus one possible future regulator-document
carrier to test on fresh material.

Next source-support move:

Apply the same ledger discipline to the remaining non-English source-support
rows outside `ja_regulator_001`, especially the rows already flagged as
source-support adjudication or declared source/oracle limits. Only after that
should any row graduate into a repair pass.

## Expanded Source-Support Ledger

Date: 2026-05-28 UTC

Move:

Applied the same source-support adjudication discipline to all current
non-English residue rows, not just the six Japanese regulator rows. This keeps
the raw score intact while separating instrument failures from oracle/source
package limits.

Updated report:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_source_support_score_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_source_support_score_20260528.md
```

Score view:

```text
raw current row-override score:
  180 / 10 / 10 on 200 rows
  exact rate 90.00%

reviewed rows:
  21

excluded from source-contained view:
  19

provisional source-contained view:
  179 / 1 / 1 on 181 rows
  exact rate 98.90%
```

Important discipline:

This does not replace the raw score and does not turn excluded rows into wins.
It says those rows should be repaired in the oracle/source package before being
used as instrument-pressure rows. The excluded set is dominated by source
package gaps, external-knowledge requirements, declared source limits, and
oracle overreach.

Remaining source-contained blockers:

```text
fr_eu_official_001 q025:
  current decision vs prior remand join/source-selection problem

ja_corporate_001 q012:
  financial quantity join plus source-contained ratio rendering problem
```

Read:

The next tuning pass should be narrow. The Japanese corporate row is the cleaner
generic compiler/query blocker: source-contained financial amounts are present,
but the structured answer route does not preserve the named affiliate
contribution, the total equity-method line, and the source-contained computed
ratio together. The French EU row is likely a legal-disposition scoping problem:
the current decision needs to be distinguished from prior procedural remands.

## Financial Report Profile Contract Probe

Date: 2026-05-28 UTC

Blocker:

```text
ja_corporate_001 q012
```

Finding:

The previous financial-report intervention asked the profile to preserve six
conceptual fields even though `profile_bootstrap_v1` only supports five argument
roles per candidate predicate. The model exposed that contract mismatch as a
`financial_result/6:args=5` profile defect. This was a harness/profile-governance
bug, not a fixture-specific fact issue.

Changes:

```text
src/profile_bootstrap.py
scripts/run_domain_bootstrap_file.py
tests/test_profile_bootstrap.py
tests/test_domain_bootstrap_file.py
```

The guidance now states the five-slot maximum explicitly. Financial report
profiles should keep period, named scope/entity, metric, value, and unit in the
metric carrier, and use source-coordinate/provenance rows or the source-record
ledger for source/basis when needed. A deterministic profile schema retry now
runs when a profile declares a signature whose `/N` arity does not match its
argument-role list.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_file.py src\profile_bootstrap.py
python -m pytest tests\test_domain_bootstrap_file.py -q -k "financial_report or profile_schema_contract_retry_context or invalid_profile_retry_context or profile_bootstrap_admission_context_guides_quantity_event_palettes"
-> 5 passed

python -m pytest tests\test_profile_bootstrap.py -q
-> 25 passed
```

OpenRouter diagnostic compile:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_financial_report_probe_20260528_retry\compile_ja_corporate\domain_bootstrap_file_20260528T025039775795Z_source_qwen-qwen3-6-35b-a3b.json
```

Compile read:

```text
candidate_predicates: 13
compile_admitted: 168
compile_skipped: 88
candidate_signature_arg_mismatch_refs: []
rough_score: 1.0
```

Targeted q012 QA:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_financial_report_probe_20260528_retry\qa_ja_corporate_q012\domain_bootstrap_qa_20260528T025232503656Z_qa_qwen-qwen3-6-35b-a3b.json
```

Result:

```text
q012: exact
runtime_load_error_count: 0
write_proposal_rows: 0
compatibility rows: 0
```

Read:

This clears the q012 source-contained blocker on targeted replay. The answer
route used direct compiled values for the named contribution and total, with
source-record support still available. Do not promote this to a corpus claim
until the next non-English or mixed transfer rerun. The generic lesson is the
important part: profile arity/governance defects can masquerade as compile
surface gaps, so signature/args mismatch needs to be fixed before reading row
residue as a language or domain failure.

## Current-Disposition Legal Scoping Probe

Date: 2026-05-28 UTC

Blocker:

```text
fr_eu_official_001 q025
```

ACH/source-support read:

The row was source-contained, but the artifact separated the wrong surfaces. It
had current-decision annulment facts and older procedural-history remand facts,
but it did not preserve the current decision's disposition/finality surface
strongly enough. That let the query/judge path combine a current annulment with
an older remand.

Repairs tested:

1. Same-variable evidence-bundle conjunction.

   Added a query-only bundle repair that synthesizes conjunctive Prolog probes
   when evidence-plan templates share variables. This asks whether the same
   act/decision/event has the combined properties before treating a compound
   premise as established. It writes no facts and does not mutate the KB.

2. Current-disposition compile guidance.

   Added generic compile/profile guidance for adjudication, appeal, and review
   documents: preserve the current decision disposition separately from
   procedural history, including the challenged act, deciding body,
   disposition/effect, remand/transfer/final-resolution status, and source/date
   anchor.

3. Repeated-structure role-mismatch retry.

   The first compile probe emitted an unsafe shallow remand carrier by attaching
   a prior remand to the current case id. That compile was rejected. A generic
   profile-schema retry now triggers on repeated-structure role mismatches and
   tells the profile that procedural outcome/remand/disposition predicates must
   anchor to the decision/event/act that actually produced the effect, not a
   global case id.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py scripts\run_domain_bootstrap_file.py src\profile_bootstrap.py
python -m pytest tests\test_domain_bootstrap_qa.py -q -k "evidence_bundle_plan_synthesizes or evidence_bundle_join_probe or evidence_bundle_plan_accepts_conjunctive or post_ingestion_qa_strategy"
-> 5 passed

python -m pytest tests\test_domain_bootstrap_file.py -q -k "profile_schema_contract_retry_context or current_adjudication_disposition"
-> 3 passed

python -m pytest tests\test_profile_bootstrap.py -q -k "bootstrap_guidance_preserves_source_records_reporters_and_conditions"
-> 1 passed
```

Artifacts:

```text
old-compile query-only probe:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q025_same_subject_probe_20260528\domain_bootstrap_qa_20260528T030116740985Z_qa_qwen-qwen3-6-35b-a3b.json

rejected compile with bad shallow remand carrier:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_disposition_compile_probe_20260528\compile\domain_bootstrap_file_20260528T031039299825Z_source_qwen-qwen3-6-35b-a3b.json

clean compile:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_disposition_compile_probe2_20260528\compile\domain_bootstrap_file_20260528T031908689876Z_source_qwen-qwen3-6-35b-a3b.json

targeted q025 QA:
  C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q025_disposition_probe_20260528\domain_bootstrap_qa_20260528T032030962766Z_qa_qwen-qwen3-6-35b-a3b.json
```

Result:

```text
clean compile:
  candidate_predicates: 14
  compile_admitted: 97
  compile_skipped: 0
  rough_score: 1.0
  repeated_structure_role_mismatch_refs: []

q025 targeted QA:
  exact: 1
  partial: 0
  miss: 0
  runtime_load_error_count: 0
  write_proposal_rows: 0
  compatibility rows: 0
```

Read:

The query-only same-variable probe was necessary but not sufficient on the old
compile, which proves the row was not just query-planner sloppiness. The useful
generic mechanism is current-disposition scoping for adjudicative documents plus
role-safe repeated-structure schema review. This clears the q025
source-contained blocker on targeted replay, but it is not a corpus score until
the affected fixture or full non-English batch is rerun.

## Reference-Judge Source-Display Windowing

Date: 2026-05-28 UTC

Affected replay:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_full_fixture_replay_20260528\domain_bootstrap_qa_20260528T034317403081Z_qa_qwen-qwen3-6-35b-a3b.json

fr_eu_official_001 full fixture:
  exact: 23
  partial: 0
  miss: 2
  runtime_load_error_count: 0
  write_proposal_rows: 0
  compatibility rows: 0
```

Read:

The disposition repair recovered q025 in a full-fixture replay, but two
non-exact rows remained. They were not the same kind of blocker:

```text
q013:
  legal-form/acronym definitions. The source bundle names the legal
  representatives but does not visibly define both acronyms or provide English
  equivalents. Treat as source-package/oracle scope, not compiler tuning.

q018:
  source-contained condition in the named paragraph. The compiled/query evidence
  included the exact source_record_text_display row, but the reference judge
  payload compactor clipped long source-display values at their prefix. The
  answer-bearing condition was later in the paragraph, so the judge saw a bad
  excerpt and called a compile gap.
```

Mechanism change:

```text
scripts/run_domain_bootstrap_qa.py
tests/test_domain_bootstrap_qa.py
```

The scorer payload compactor now preserves a short excerpt around terms already
present in the supplied reference answer when a long query-result value must be
compacted. This is QA/scorer-only windowing. It does not inspect the source
document, write facts, mutate the KB, or add source-language vocabulary to the
instrument.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py
python -m pytest tests\test_domain_bootstrap_qa.py -q -k "reference_judge_payload_compaction or reference_judge_payload_compacts or evidence_bundle_plan_synthesizes or evidence_bundle_join_probe"
-> 5 passed
```

Targeted q018 replay after scorer-windowing repair:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q018_compaction_probe_20260528\domain_bootstrap_qa_20260528T034724063589Z_qa_qwen-qwen3-6-35b-a3b.json

q018: exact
runtime_load_error_count: 0
write_proposal_rows: 0
compatibility rows: 0
```

Current read:

French current-disposition q025 and source-display q018 are both recovered on
targeted replay. The remaining French non-exact row is source-package/oracle
scope, not a clean instrument repair target.

## Japanese Corporate Affected-Fixture Replay

Date: 2026-05-28 UTC

Replay artifact:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_corporate_full_fixture_replay_20260528\domain_bootstrap_qa_20260528T040631368263Z_qa_qwen-qwen3-6-35b-a3b.json
```

Result:

```text
ja_corporate_001 full fixture:
  exact: 21
  partial: 1
  miss: 3
  runtime_load_error_count: 0
  write_proposal_rows: 0
  compatibility rows: 0

prior comparable current-metadata run:
  exact: 22
  partial: 1
  miss: 2

row movement:
  q012 miss -> partial
  q013 partial -> miss
  q021 exact -> miss
```

Read:

The financial profile contract repair helped q012 but did not reproduce the
one-row exact in the full-fixture replay. The query results do contain the
source-display row with the reference value, and also contain the rounded
metadata value that the judge latched onto. This is now a judge/unit-scale
variance row, not a clean compile-surface gap.

The q013 and q021 losses are source-package scope, not good instrument tuning
targets:

```text
q013:
  asks for ownership composition and English-version availability. The current
  source package does not visibly contain those facts.

q021:
  asks for IFRS relationship plus English translated Financial Results
  differences. The current source package supports domestic accounting-standard
  status but not the English-version comparison.

q023:
  asks about restated prior-period figures. The replay still does not expose
  source support for the reference answer; treat as source/oracle adjudication
  before compiler work.
```

Immediate consequence:

Do not keep polishing this Japanese corporate fixture. The useful mechanism
signal is already extracted: five-slot financial profile governance repaired
one source-contained amount row from miss to partial, but exactness now depends
on a broader unit-scale/derived-ratio judgment policy that should be tested on
unlike financial documents before promotion.

## English Regression Checkpoint Added

Date: 2026-05-28 UTC

Request:

After sustained non-English work, run an English regression / N=2 checkpoint on
an English ugly-public fixture set that was not part of this exact multilingual
tuning loop.

Why:

The multilingual repairs touched shared query planning, source-display support,
reference judging, profile review, and compile guidance. A clean non-English
improvement would be less meaningful if it quietly regressed English messy
official documents.

Roster item:

```text
Pick an English ugly-public set for N=2 after the current non-English blocker
pass:
  preferred: datasets\real_world_transfer\fresh_ugly_public_20260524_03
  fallback:  datasets\real_world_transfer\fresh_ugly_public_20260526_01

Run shape:
  - OpenRouter only.
  - Same model path and metadata capture discipline.
  - Compile + QA if budget/time permits; QA-only against locked compiles if the
    immediate question is query/judge regression.
  - Report row-level churn, not just headline exact rate.
  - Treat English regression before a fresh multilingual full rerun.
```

## English Locked-Compile N=2 Regression Check

Date: 2026-05-28 UTC

Purpose:

Check whether the shared query/judge work done during the non-English pass
damaged English messy-official-document QA. This is a locked-compile check, not
a recompile check.

Fixture:

```text
dataset: datasets\real_world_transfer\fresh_ugly_public_20260526_01
fixture: nhtsa_ugly_001
locked compile:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_r4_query_intent_20260526\compile_r4\nhtsa_ugly_001\domain_bootstrap_file_20260526T060216002723Z_source_qwen-qwen3-6-35b-a3b.json
```

N=2 artifacts:

```text
C:\prethinker_tmp_archive\english_regression_nhtsa_n2_20260528\qa_pass_1\domain_bootstrap_qa_20260528T042939799984Z_qa_qwen-qwen3-6-35b-a3b.json
C:\prethinker_tmp_archive\english_regression_nhtsa_n2_20260528\qa_pass_2\domain_bootstrap_qa_20260528T044732329940Z_qa_qwen-qwen3-6-35b-a3b.json
```

Scores:

```text
historical R4 locked-compile QA:
  22 / 2 / 1
  hygiene: 0 runtime, 0 write, 0 compatibility

N=2 pass 1:
  20 / 5 / 0
  hygiene: 0 runtime, 0 write, 0 compatibility

N=2 pass 2:
  22 / 3 / 0
  hygiene: 0 runtime, 0 write, 0 compatibility
```

Row movement versus historical R4:

```text
q006: exact -> partial / partial
q014: miss  -> partial / partial
q016: exact -> partial / exact
q022: partial -> partial / exact
```

Read:

The English locked-compile regression check did not show hygiene regression and
did not produce any misses in the N=2 passes. It did expose row-level variance
in the reference judge/planner path and one consistent English downgrade:
adjacent source-record label/value rows were present but not deterministically
accepted when the reference answer wrapped the value in explanatory prose.

Repair:

```text
scripts/run_domain_bootstrap_qa.py
tests/test_domain_bootstrap_qa.py
```

Added a generic scorer-only support check for
`source_record_label_value_pair_support`: when an admitted source-record
label/value support row matches the asked/reference field and at least 80% of a
four-or-more-token value appears in the reference answer, the reference judge can
accept the row without relying on a fresh model judgment. This handles printed
field/value surfaces split across adjacent source rows. It writes no facts and
does not introduce document or source vocabulary.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py
python -m pytest tests\test_domain_bootstrap_qa.py -q -k "label_value_pair_reference_support or source_record_messy_summary_extracts_adjacent_label_value_pair or reference_judge_payload_compaction"
-> 4 passed

q006 targeted replay:
  C:\prethinker_tmp_archive\english_regression_nhtsa_q006_label_value_probe_20260528\domain_bootstrap_qa_20260528T045123394279Z_qa_qwen-qwen3-6-35b-a3b.json
  q006: exact
  hygiene: 0 runtime, 0 write, 0 compatibility

churn-row replay:
  C:\prethinker_tmp_archive\english_regression_nhtsa_churn4_after_label_value_20260528\domain_bootstrap_qa_20260528T045456884578Z_qa_qwen-qwen3-6-35b-a3b.json
  q006: exact
  q014: partial
  q016: partial
  q022: partial
  hygiene: 0 runtime, 0 write, 0 compatibility
```

Current interpretation:

The international work did not obviously break English hygiene or collapse the
locked English fixture. It did reveal that score variance remains material
around long sequence/citation rows, and that English adjacent label/value
support needed a deterministic scorer guard. Before claiming English regression
clean, run either a second locked English fixture N=2 or a current-code
compile+QA mini-cycle on two English fixtures.

## English Locked-Compile N=2 Second Fixture

Date: 2026-05-28 UTC

Fixture:

```text
dataset: datasets\real_world_transfer\fresh_ugly_public_20260526_01
fixture: ntsb_ugly_002
locked compile:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_r4_query_intent_20260526\compile_r4\ntsb_ugly_002\domain_bootstrap_file_20260526T061117147729Z_source_qwen-qwen3-6-35b-a3b.json
```

Artifacts:

```text
historical R4:
  C:\prethinker_tmp_archive\fresh_ugly_public_20260526_01_r4_query_intent_20260526\qa_r4\ntsb_ugly_002\domain_bootstrap_qa_20260526T063223722567Z_qa_qwen-qwen3-6-35b-a3b.json

N=2 pass 1:
  C:\prethinker_tmp_archive\english_regression_ntsb002_n2_20260528\qa_pass_1\domain_bootstrap_qa_20260528T051519942022Z_qa_qwen-qwen3-6-35b-a3b.json

N=2 pass 2:
  C:\prethinker_tmp_archive\english_regression_ntsb002_n2_20260528\qa_pass_2\domain_bootstrap_qa_20260528T053356482078Z_qa_qwen-qwen3-6-35b-a3b.json
```

Scores:

```text
historical R4:
  23 / 2 / 0
  hygiene: 0 runtime, 0 write, 0 compatibility

N=2 pass 1:
  24 / 1 / 0
  hygiene: 0 runtime, 0 write, 0 compatibility

N=2 pass 2:
  24 / 1 / 0
  hygiene: 0 runtime, 0 write, 0 compatibility
```

Row movement:

```text
q017:
  partial in all runs. Remaining issue is second action as structured fact plus
  distance source-display/structured movement join.

q019:
  historical partial -> exact in both N=2 passes. The current query/judge path
  accepts source-display speed evidence over a conflicting structured speed row.
```

English regression read so far:

```text
nhtsa_ugly_001 locked N=2:
  pass 1: 20 / 5 / 0
  pass 2: 22 / 3 / 0
  after label/value repair q006 targeted exact

ntsb_ugly_002 locked N=2:
  pass 1: 24 / 1 / 0
  pass 2: 24 / 1 / 0

combined locked English N=2 sample:
  100 QA row evaluations
  misses: 0
  runtime/write/compatibility rows: 0/0/0
```

Interpretation:

The English regression concern was valid to test. The locked-compile sample does
not show an English collapse after non-English work. It shows stable hygiene,
one repaired adjacent label/value scorer regression, and residual judge/planner
variance on long sequence/citation rows. The next English safety check, if we
need more confidence, should be a current-code compile+QA mini-cycle on two
English fixtures rather than more QA-only replay on locked compiles.

## English Current-Code Compile Smoke

Date: 2026-05-28 UTC

Purpose:

Move beyond locked-compile QA replay and check whether the current compile
guidance itself harms an English messy official document.

Fixture:

```text
dataset: datasets\real_world_transfer\fresh_ugly_public_20260526_01
fixture: ntsb_ugly_002
```

Compile artifact:

```text
C:\prethinker_tmp_archive\english_regression_ntsb002_current_compile_smoke_20260528\compile\domain_bootstrap_file_20260528T054054579697Z_source_qwen-qwen3-6-35b-a3b.json
```

Compile read:

```text
candidate_predicates: 20
compile_admitted: 51
compile_skipped: 1
parsed_ok: true
rough_score: 0.9
candidate_signature_arg_mismatch_refs: []
repeated_structure_role_mismatch_refs: []
```

QA artifact:

```text
C:\prethinker_tmp_archive\english_regression_ntsb002_current_compile_smoke_20260528\qa\domain_bootstrap_qa_20260528T055945613249Z_qa_qwen-qwen3-6-35b-a3b.json
```

QA result:

```text
current-code compile+QA:
  25 / 0 / 0
  hygiene: 0 runtime, 0 write, 0 compatibility

comparison:
  historical R4 locked compile: 23 / 2 / 0
  locked compile N=2 pass 1: 24 / 1 / 0
  locked compile N=2 pass 2: 24 / 1 / 0
```

Rows recovered on current compile:

```text
q017:
  current compile admitted enough source/structured support for both crew
  actions and the 232-foot distance.

q019:
  current query/judge path accepts the 37 mph versus 60 mph source-supported
  comparison and the no-speed-as-factor reading.
```

Interpretation:

This is a small smoke, not an English corpus claim. But it materially lowers the
regression concern: current multilingual/shared compile guidance did not damage
this English fixture and in fact recovered the two historical partials. Combined
with the locked English N=2 sample, the next higher-value work is returning to a
full non-English rerun or running a two-fixture English current-code mini-cycle
only if we want extra English confidence.

## French Current-Disposition Stability Repair

Date: 2026-05-28 UTC

Blocker:

```text
fr_eu_official_001 q025
```

The clean compile already contained the current-disposition facts needed for
the row, including current case metadata, current procedural step rows, current
order rows, and the article application that marks final disposition. The
remaining failure mode was full-run query/judge variance: one targeted run
retrieved enough current-disposition evidence and scored exact, while a later
full-fixture run let older procedural history dominate and scored q025 miss.

Mechanism change:

```text
scripts/run_domain_bootstrap_qa.py
tests/test_domain_bootstrap_qa.py
```

Added `current_adjudication_disposition_support`, a current deterministic
query-only support surface for adjudicative/status-premise rows. It activates
from structured `query_intents` status-like intent plus admitted adjudication
predicates, then inventories admitted `case_metadata`, `procedural_step`,
`order_annulment`, `order_injunction`, `cited_article`, and
`article_applied_to` rows. It sorts latest procedural steps first and links
cited/article-applied rows back to admitted source-record display lines when
the normalized article atom appears in `source_record_text_atom`.

Guardrails:

```text
no fixture names
no source-language trigger terms
no raw utterance regex
no durable facts or rules
survives compatibility row limit 0 as current core-local support
```

Targeted q025 probe:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q025_current_disposition_companion_probe2_20260528\domain_bootstrap_qa_20260528T063259936508Z_qa_qwen-qwen3-6-35b-a3b.json

q025: exact
current_adjudication_disposition_support delivered: 64 rows
runtime_load_error_count: 0
write_proposal_rows: 0
compatibility rows: 0
```

Full French fixture replay:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_full_after_current_disposition_companion_20260528\domain_bootstrap_qa_20260528T065401687809Z_qa_qwen-qwen3-6-35b-a3b.json

fr_eu_official_001:
  exact: 25
  partial: 0
  miss: 0
  runtime_load_error_count: 0
  write_proposal_rows: 0
  compatibility rows: 0
```

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 428 passed

fixture/source-language leakage grep over scripts/src:
-> no hits
```

## 2026-05-28 current-code full QA, adjudication, and short-Unicode target repair

Date: 2026-05-28 UTC

Full current-code QA artifact after the source-record support work:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_full_qa_after_supports_20260528\qa_batch_summary.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_full_qa_after_supports_20260528\qa_batch_summary.md
```

Run conditions:

```text
provider: OpenRouter
model: qwen/qwen3.6-35b-a3b
lanes: 6
cache: disabled
questions: 200
```

Headline:

```text
exact / partial / miss: 172 / 18 / 10
exact rate: 86.0%
runtime_load_error_count: 0
write_proposal_rows: 0
compatibility rows: 0
```

Fixture scores:

```text
de_corporate_001:          21 / 1 / 3
de_regulator_001:          22 / 3 / 0
es_public_procurement_001: 21 / 3 / 1
es_regulator_001:          19 / 6 / 0
fr_eu_official_001:        25 / 0 / 0
fr_regulator_001:          25 / 0 / 0
ja_corporate_001:          22 / 1 / 2
ja_regulator_001:          17 / 4 / 4
```

Read:

This is not a progress score. The full current-code run improved some old misses
into partials but increased judge/source abstraction churn. Against the prior
`175 / 11 / 14` current-best full run, 24 rows changed verdict:

```text
exact -> miss:    2
exact -> partial: 9
miss -> exact:    3
miss -> partial:  4
partial -> exact: 5
partial -> miss:  1
```

The useful signal is the hygiene and residue shape, not the raw exact count.
Hygiene stayed clean at 0/0/0. Residue is concentrated in source-package,
oracle-abstraction, translation, and a small source-contained tail.

Current residue adjudication:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_residue_adjudication_after_supports_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_residue_adjudication_after_supports_20260528.md

residue rows: 28
classifications:
  answer_rendering_gap: 1
  declared_source_or_oracle_limit: 2
  query_planning_gap: 1
  repairable_compile_gap: 5
  source_support_adjudication_needed: 19
```

Source-support adjusted view, using the explicit adjudication ledger in the
dataset:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_source_support_score_after_supports_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_source_support_score_after_supports_20260528.md

raw: 172 / 18 / 10 on 200 rows = 86.0%
reviewed rows: 21
excluded/review-before-scoring rows: 19
provisional source-contained: 171 / 9 / 1 on 181 rows = 94.48%
```

The ten source-contained non-exacts kept in the provisional score were:

```text
de_regulator_001:q012       partial answer_surface_gap
de_regulator_001:q020       partial answer_surface_gap
es_public_procurement_001:q005 partial answer_surface_gap
es_regulator_001:q015       partial query_surface_gap
es_regulator_001:q016       partial compile_surface_gap
es_regulator_001:q024       partial compile_surface_gap
ja_corporate_001:q021       partial compile_surface_gap
ja_regulator_001:q004       miss    compile_surface_gap
ja_regulator_001:q011       partial compile_surface_gap
ja_regulator_001:q016       partial compile_surface_gap
```

Mechanism repair:

`source_record_semantic_target_display_support` was already the right generic
surface for target-term source retrieval, but it rejected two-character
non-ASCII targets. That was an ASCII-biased guard, not a fixture-specific
failure. The guard now permits two-character non-ASCII letter targets while
keeping ASCII terms at the previous minimum length. The repair is driven only by
structured `query_intents[].target_terms`, not by raw utterance parsing or
source-language literals in the instrument.

Targeted probe:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_q004_q022_short_unicode_target_probe_20260528\domain_bootstrap_qa_20260528T121334870490Z_qa_qwen-qwen3-6-35b-a3b.json

q004/q022: 1 / 1 / 0
q004: miss -> exact
q022: miss -> partial
hygiene: 0 runtime / 0 write / 0 compatibility
```

Affected Japanese regulator replay:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_affected_after_short_unicode_target_20260528\domain_bootstrap_qa_20260528T121748830157Z_qa_qwen-qwen3-6-35b-a3b.json

selected rows: q004,q010,q011,q016,q022
previous full-run shape for these rows: 0 / 2 / 3
targeted replay: 3 / 1 / 1
q004 exact
q010 miss
q011 exact
q016 exact
q022 partial
hygiene: 0 runtime / 0 write / 0 compatibility
```

Read:

The short-Unicode repair is worth keeping. It is generic, transfer-safe, and
directly addresses non-English source-location retrieval. `q010` and `q022`
should not be patched further from this fixture alone. They now expose the
source rows, but the remaining disagreement is category abstraction and
recommendation-scope interpretation. Treat them as source/oracle adjudication or
fresh-document confirmation targets, not as an invitation to add Japanese
regulator-shaped code.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py
python -m pytest tests\test_domain_bootstrap_qa.py tests\test_semantic_ir_runtime.py -q
-> 537 passed, 2 subtests passed

python -m pytest -q
-> 1980 passed, 2 subtests passed

fixture/source-language leakage grep over scripts/src/tests for named fixture terms:
-> no hits
```

## 2026-05-28 source-support ledger completion and kept-tail replay

Date: 2026-05-28 UTC

The source-support adjudication ledger was completed for the remaining
non-English current-run tail:

```text
datasets\real_world_transfer\fresh_non_english_wild_20260526_01\source_support_adjudication_20260528.json
```

Important additions:

```text
de_regulator_001:q012
  external legal gloss: source states rechtskräftig, not the full no-appeal /
  administratively-closed explanation.

de_regulator_001:q020
  oracle contradicts retained source: the source says no Bußgeldbescheide were
  issued against the involved dealers, while the reference says AVM + six
  dealers received notices.

ja_corporate_001:q021
  external accounting/translation knowledge: source states Japanese accounting
  basis, but not IFRS contrast, English-version status, or same-values claim.

es_regulator_001:q024
  review-before-scoring: source states Article 83.2 factors and no recidivism
  is cited, but sensitivity/window phrasing is partly interpretive.
```

Updated source-support score:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_source_support_score_after_ledger_completion_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_code_source_support_score_after_ledger_completion_20260528.md

raw: 172 / 18 / 10 on 200 rows = 86.0%
reviewed rows: 31
excluded/review-before-scoring rows: 23
provisional source-contained: 171 / 5 / 1 on 177 rows = 96.61%
```

Kept source-contained non-exacts from the stale full run:

```text
es_public_procurement_001:q005 partial
es_regulator_001:q015 partial
es_regulator_001:q016 partial
ja_regulator_001:q004 miss
ja_regulator_001:q011 partial
ja_regulator_001:q016 partial
```

Targeted replay artifacts:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_public_q005_current_replay_20260528\domain_bootstrap_qa_20260528T122529919553Z_qa_qwen-qwen3-6-35b-a3b.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q015_q016_current_replay_20260528\domain_bootstrap_qa_20260528T122709459471Z_qa_qwen-qwen3-6-35b-a3b.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_affected_after_short_unicode_target_20260528\domain_bootstrap_qa_20260528T121748830157Z_qa_qwen-qwen3-6-35b-a3b.json
```

Targeted replay outcome:

```text
es_public_procurement_001:q005 -> exact
es_regulator_001:q015         -> exact
es_regulator_001:q016         -> exact
ja_regulator_001:q004         -> exact
ja_regulator_001:q011         -> exact
ja_regulator_001:q016         -> exact

hygiene on targeted replays: 0 runtime / 0 write / 0 compatibility
```

Read:

This still does not replace a fresh full rerun. It does mean the latest
non-English batch no longer has an obvious kept source-contained blocker after
explicit source/oracle adjudication. The remaining raw non-exacts are mostly
fixture-source package decisions, oracle overreach, external translation/legal
gloss, or review-before-scoring rows.

Next measurement choices:

```text
1. If we want a refreshed number: rerun full non-English QA once, record row
   churn, and score both raw and source-contained views.

2. If we want stronger product signal: wait for another fresh ugly multilingual
   or mixed-language batch and treat this batch as calibration evidence.

3. Do not add more fixture-shaped query support from this batch unless a fresh
   document repeats the same source-contained failure shape.
```

## 2026-05-28 - Spanish procurement q015/q018 targeted recovery

Purpose:

Keep pushing the non-English residue without admitting fixture/source language
into the instrument. The next clean blockers were two
`es_public_procurement_001` rows:

- `q015`: status/change support existed in an inline source-record field, but
  the query path did not surface the support row.
- `q018`: financial/contractual obligations existed across already-admitted
  budget, guarantee, dependency, and source-record rows, but one Semantic IR
  pass omitted explicit financial constraints and the bundle support did not
  fire.

Mechanisms added:

```text
source_record_status_inline_field_support
source_record_obligation_bundle_support semantic-section fallback
source_record_obligation_bundle_support returned-predicate fallback
```

Discipline:

- query-only support rows
- no durable compiled fact writes
- activated from structured `query_intents`, compiled/runtime facts, returned
  predicate shapes, and source-record topology
- no fixture names or source-language vocabulary in `scripts` or `src`

Probe artifacts:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_public_q015_q018_current_replay_20260528
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_public_q015_q018_status_obligation_probe_20260528
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_public_q015_q018_status_obligation_tight_probe_20260528
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_public_q015_q018_status_obligation_anchor_probe_20260528
```

Final targeted outcome:

```text
q015/q018 current replay before repair: 0 exact / 1 partial / 1 miss
q015/q018 after tightened generic repairs: 2 exact / 0 partial / 0 miss
hygiene: 0 runtime / 0 write proposals / 0 compatibility

q015 support shape:
  source_record_status_inline_field_support rows: 1

q018 support shape:
  source_record_obligation_bundle_support rows: 1
```

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 438 passed

python -m py_compile scripts\run_domain_bootstrap_qa.py
-> pass

fixture/source-language leakage grep over scripts/src:
-> no hits
```

Read:

This is a real mechanism recovery, not a corpus claim. The status row exposed a
generic gap around inline fields that carry status/update payloads. The
obligation row exposed a generic gap where a list-shaped question has enough
compiled financial/obligation evidence nearby, but the Semantic IR pass omits a
specific constraint. Both repairs stay query-only and should be validated in the
next affected-set replay before any headline score moves.

## 2026-05-28 - Spanish affected-set replay and value-set exclusion

Affected Spanish procurement replay after the status/obligation repairs:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_public_residue_replay_after_status_obligation_20260528

selected rows: q010, q013, q015, q018, q019, q024
outcome: 4 exact / 0 partial / 2 miss
hygiene: 0 runtime / 0 write proposals / 0 compatibility
```

Read:

- `q010`, `q015`, `q018`, and `q019` are recovered on replay.
- `q013` asks for an external English technical equivalence not stated in the
  BOE source.
- `q024` asks for contract-modification legal material that is only referenced
  through non-ingested PCAP material.

Those two procurement misses are not safe instrument targets without a product
decision about external/legal-reference expansion.

Spanish regulator replay after the same repairs:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_residue_replay_after_status_obligation_20260528

selected rows: q010, q011, q013, q021, q024
outcome: 2 exact / 2 partial / 1 miss
hygiene: 0 runtime / 0 write proposals / 0 compatibility
```

`q024` was the remaining clean mechanism target. The KB returned an
`aggravating_factor/2` value set, but the query did not surface the absence of
the specific requested subtype. Added:

```text
compiled_value_set_exclusion_support
```

Discipline:

- query-only support row
- activated from structured `query_intents` plus already-returned compiled
  predicate rows
- compares target tokens to returned value atoms
- no raw utterance parsing
- no source-prose parsing
- no durable absence fact

Probe artifact:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q024_value_set_exclusion_probe_20260528

q024 -> exact
hygiene: 0 runtime / 0 write proposals / 0 compatibility
```

Support row shape:

```text
compiled_value_set_exclusion_support:
  Predicate: aggravating_factor
  ReturnedValues: link_to_treatment, sensitive_data
  RequestedTokens: recidivism
```

Spanish regulator affected-set replay after value-set exclusion:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_residue_replay_after_value_set_exclusion_20260528

selected rows: q010, q011, q013, q021, q024
outcome: 3 exact / 0 partial / 2 miss
hygiene: 0 runtime / 0 write proposals / 0 compatibility
```

Read:

- `q010`, `q013`, and `q024` are recovered on replay.
- `q011` is a source/oracle abstraction mismatch: the oracle names four
  compressed security-measure abstractions that are not present as source-stated
  text in the admitted rows.
- `q021` requires an external English legal translation and civil-law
  distinction not stated in the resolution.

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 440 passed

python -m py_compile scripts\run_domain_bootstrap_qa.py
-> pass

fixture/source-language leakage grep over scripts/src:
-> no hits
```

Current blocker read:

The remaining Spanish residue has moved from mechanism pressure to
source-package/oracle-scope pressure. Do not keep tuning Spanish rows unless we
explicitly decide to support external legal glosses or oracle paraphrase
abstractions as product behavior.

## 2026-05-28 - Remaining non-Spanish residue and Japanese action-section probe

Current residue probes against archived compiles and current QA code:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_de_corporate_residue_current_probe_20260528
  selected rows: q005, q006, q010, q018
  outcome: 0 exact / 1 partial / 3 miss

C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_de_regulator_residue_current_probe_20260528
  selected rows: q019, q025
  outcome: 1 exact / 0 partial / 1 miss

C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_residue_current_probe_20260528
  selected rows: q025
  outcome: 1 exact / 0 partial / 0 miss

C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_corporate_residue_current_probe_20260528
  selected rows: q012, q013, q021
  outcome: 1 exact / 0 partial / 2 miss

C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_regulator_residue_current_probe_20260528
  selected rows: q005, q010, q021, q022
  outcome: 0 exact / 2 partial / 2 miss
```

Read:

- `fr_eu_official_001:q025` is recovered on current replay.
- `de_corporate_001` residue is mostly source-package/oracle pressure: legal
  citations, ISIN, and market-abuse-regulation material not clearly admitted in
  source rows.
- `de_regulator_001:q019` depends on settlement-condition practice material
  beyond the press-release surface.
- `ja_corporate_001:q013/q021` depend on external English-version or
  Japanese/English accounting-standard comparison material.
- `ja_regulator_001:q005` is an oracle/source conflict: the source and compiled
  rows show the bank business-improvement order under the financial-instruments
  article, while the oracle expects a Banking Act business-improvement basis.
- `ja_regulator_001:q021` requires external English legal abbreviations and
  translation-status material.
- `ja_regulator_001:q022` remains the already-named recommendation-chain
  compile blocker: the old compile lacks an explicit recipient/addressee
  carrier for the SESC recommendation chain. Profile-bootstrap diagnostics for
  recommendation-chain slot loss already exist; do not patch this with a
  query-only shortcut that invents the chain.

Mechanism probe for `ja_regulator_001:q010`:

Added:

```text
source_record_returned_action_section_support
```

Discipline:

- query-only support row
- activated from structured `query_intents` and already-returned action/legal
  predicate rows
- follows numeric legal-basis tokens from returned values into matching
  `source_record_row` sections
- exposes admitted list rows under those sections
- no source-language strings
- no raw utterance parsing
- no durable violation/category fact

Artifacts:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_q010_returned_action_section_tight_probe_20260528
  q010 -> exact

C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_residue_replay_after_action_section_20260528
  q005/q010/q021/q022 -> 0 exact / 3 partial / 1 miss

C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_ja_reg_q010_returned_action_section_n2_probe_20260528
  q010 -> partial
```

Read:

The action-section support is useful but should not be counted as a recovered
row yet. It moves q010 from a bare `issued_sanction/4` result to visible
source-section detail, but the row remains judge-variable because the oracle
expects "information sharing" as a distinct violation category while the source
rows state bank/securities linkage, compliance posture, customer-information
management, and other-business prohibition. This is probably not a safe
instrument target without an oracle/source-support decision.

Verification:

```text
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 442 passed

python -m py_compile scripts\run_domain_bootstrap_qa.py
-> pass

expanded fixture/source-language leakage grep over scripts/src:
-> no hits
```

Current next-blocker read:

Do not spend more time tuning non-English rows from this batch until we either:

1. run a fresh compile for `ja_regulator_001` under the current
   recommendation-chain profile guard, or
2. adjudicate/revise the oracle rows that require external translations,
   external legal practice, or abstraction not directly present in source
   display rows.

For product signal, the better next measurement is an English regression/N=2
or a fresh ugly batch rerun, because this non-English residue is now dominated
by source-package and oracle-scope decisions rather than clean generic
mechanism gaps.

## Count-Breakdown Support And English Guardrail

Date: 2026-05-28 UTC

Prompting concern:

After sustained multilingual work, keep an English regression / N=2 checkpoint
on the working roster so multilingual retrieval repairs do not quietly damage
English messy-official-document behavior. The current worksheet already contains
the first locked English N=2 and current-code English smoke; before a larger
multilingual claim, run another English current-code two-fixture mini-cycle or
native affected-set spotcheck if the next changes touch shared query/judge
surfaces.

`es_regulator_001:q010` adjudication:

The full-run residue looked like a compile gap because the primitive KB exposed
only the total affected count and a group label. Source-record ACH review showed
the answer-bearing row was already admitted as source display:

```text
src_line_0106:
source display contains a source-stated count split:
  287 + 160
```

Mechanism applied:

```text
source_record_count_breakdown_support
```

Properties:

```text
- query-only support surface
- activated by structured Semantic IR count/list/amount inventory intent
- no raw utterance parsing
- no durable fact writes
- no fixture/source-language literals
- requires a count/breakdown shape across Semantic IR target groups
- requires admitted source display with multiple non-year numeric values
```

The first probe recovered the row but over-delivered topical numeric clutter.
The accepted version tightened the surface so the Spanish probe emits one
answer-bearing support row rather than citation/date noise.

Final probe artifact:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q010_count_breakdown_split_intent_probe_20260528\domain_bootstrap_qa_20260528T084006219984Z_qa_qwen-qwen3-6-35b-a3b.json

q010: exact
support rows: 1
compatibility/runtime/write: 0 / 0 / 0
```

Affected-row replay:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_residue_after_count_breakdown_tight_20260528\domain_bootstrap_qa_20260528T085012866311Z_qa_qwen-qwen3-6-35b-a3b.json

rows: q010, q011, q019
result: 1 / 1 / 1
q010: exact
q011: partial
q019: miss
compatibility/runtime/write: 0 / 0 / 0
```

Churn sniff:

An intermediate affected-row replay showed over-activation on legal/article list
questions: `violation_category` had been treated as a count-breakdown trigger.
That was rejected. The accepted activation no longer fires on `q019`; it fires
on `q010` because the count/list intents jointly expose total-count plus
subgroup targets.

`q011` / `q019` read after affected replay:

```text
q011:
  partial
  source package itself uses placeholder ellipses for several requested
  security measures; do not tune the instrument to infer the missing labels.

q019:
  miss
  source supports the general Article 32 / appropriate measures rationale, but
  the reference names specific controls/double-verification details that are not
  visibly source-stated in the retained source text. Treat as source-support /
  oracle-scope adjudication before any compiler repair.
```

Read:

This is a real source-display retrieval repair, not a Spanish-language patch.
It should help count split rows where the compiler admitted source text but did
not normalize every component count into a durable predicate. It should not be
treated as a corpus score movement until an affected-set or full non-English
rerun checks churn.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 434 passed

fixture/source-language leakage grep over scripts/src:
-> no hits
```

Interpretation:

This stabilizes the q025 adjudicative-current-status blocker without adding
fixture vocabulary to the instrument. It also recovered q013 and q018 in the
same full-fixture replay, giving this French fixture a clean 25/0/0 under the
current code path. This is still an affected-fixture result, not a full
non-English corpus claim; the next higher-value measurement is an affected-set
or full non-English rerun to check whether the support surface introduces any
cross-fixture churn.

## Current-Best Non-English Full QA

Date: 2026-05-28 UTC

Compile root assembled for measurement:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_best_compile_20260528\compile
```

Assembly rule:

```text
base: fresh_non_english_wild_20260526_01_display_full_20260526\compile_display_full
overrides:
  de_regulator_001, es_regulator_001, fr_regulator_001, ja_regulator_001:
    regulatory_affected_compile_20260527
  fr_eu_official_001:
    fr_eu_disposition_compile_probe2_20260528
  ja_corporate_001:
    financial_report_probe_20260528_retry
```

Full QA artifact:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_best_full_qa_20260528\qa_batch_summary.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_best_full_qa_20260528\qa_batch_summary.md
```

Run conditions:

```text
provider: OpenRouter
model: qwen/qwen3.6-35b-a3b
lanes: 6
cache: disabled
questions: 200
```

Headline:

```text
exact / partial / miss: 175 / 11 / 14
exact rate: 87.5%
runtime_load_error_count: 0
write_proposal_rows: 0
compatibility rows: 0
```

Fixture scores:

```text
de_corporate_001:          21 / 0 / 4
de_regulator_001:          23 / 1 / 1
es_public_procurement_001: 19 / 3 / 3
es_regulator_001:          20 / 4 / 1
fr_eu_official_001:        24 / 0 / 1
fr_regulator_001:          25 / 0 / 0
ja_corporate_001:          22 / 2 / 1
ja_regulator_001:          21 / 1 / 3
```

Read:

The hygiene result remains strong: no runtime, write, or compatibility leakage.
The accuracy result is not a release claim. It is below the prior source-support
adjusted reading and below the desired multilingual threshold. The row residue
is clustered rather than random:

```text
source/oracle-package pressure:
  external legal bases, English translations, acronym expansions, later notices,
  ownership details, and legal-abbreviation facts not present in the source
  package.

multilingual abstraction/judge variance:
  rows where source-display evidence exists but the scorer must bridge a
  non-English source sentence to an English oracle abstraction.

true remaining compile/query pressure:
  count splits, obligation bundles, regulation measure lists, and authority-chain
  joins that need unlike-document confirmation before tuning.
```

Important French follow-up:

The full batch still marked `fr_eu_official_001:q025` miss even though
`current_adjudication_disposition_support` was present. Inspection showed the
answer-bearing `article_applied_to(..., basis_for_finality)` row landed beyond
the scorer's row sample. The repair was to keep the support generic but tighten
delivery:

```text
current adjudication support now caps duplicate procedural history
non-definition article_applied_to rows are delivered before plain cited_article rows
```

Probe after ordering:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q025_current_disposition_order_probe_20260528\domain_bootstrap_qa_20260528T074215666986Z_qa_qwen-qwen3-6-35b-a3b.json

q025: exact
current_adjudication_disposition_support rows delivered: 55
basis_for_finality row position: 30
```

Unicode target retrieval repair:

The later full French rerun moved `q018` to miss because one Semantic IR pass
collapsed the target into a multi-word Unicode phrase. The old semantic-target
matcher tried the full phrase and a concatenated non-ASCII-letter fallback, but
did not try language-agnostic Unicode word fragments. The repair adds
word-fragment variants for structured query-intent target terms only.

Probe:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q018_unicode_target_fragment_probe_20260528\domain_bootstrap_qa_20260528T080558482686Z_qa_qwen-qwen3-6-35b-a3b.json

q018: exact
matched source row: src_line_0074
```

Multilingual abstraction variance probe:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_fr_eu_q024_abstraction_variance_probe_20260528\domain_bootstrap_qa_20260528T080758522364Z_qa_qwen-qwen3-6-35b-a3b.json

q024: exact
```

Interpretation:

`q024` flips exact on single-row replay with the same compile, so it is not a
clean compiler repair target. It is scorer/abstraction variance: the source row
contains the relevant French legal sentence, while the oracle expresses the
answer in English summary form. Do not patch source-language phrases into the
instrument for this row.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 429 passed

fixture/source-language leakage grep over scripts/src:
-> no hits
```

Next read:

The immediate blocker is no longer the French current-disposition row. The next
useful work is to adjudicate the 25 non-exact rows from the full non-English run
into source-package/oracle limits, multilingual abstraction variance, and true
compile/query failures before applying any more mechanisms. The score drop is a
warning against tuning from the headline alone.

## Residue Adjudication And Semantic-Target Retrieval

Date: 2026-05-28 UTC

Residue adjudication:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_best_residue_adjudication_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_best_residue_adjudication_20260528.md

residue rows: 25
classifications:
  answer_rendering_gap: 1
  declared_source_or_oracle_limit: 2
  join_or_selection_gap: 1
  repairable_compile_gap: 6
  source_support_adjudication_needed: 15
```

Source-support score:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_best_source_support_score_20260528.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_current_best_source_support_score_20260528.md

reviewed rows: 0
excluded rows: 0
provisional source-contained score remains raw: 175 / 11 / 14
```

This is expected. The adjudicator classified row pressure, but no reviewed
source-support decisions were recorded for this specific run, so the scoring
tool correctly refused to subtract anything from the raw score.

Generic retrieval repairs applied while inspecting `es_regulator_001:q011`:

```text
1. Semantic-target windows now extend over following admitted list/continuation
   rows in the same source section, bounded to six lines.

2. Following list/continuation rows get list-continuation scoring so they are
   not pushed out of the 24-row support cap by unrelated same-target hits.

3. Structured phrase targets now have long-token fallback variants, but only
   after full-phrase and multi-token overlap fail. This prevents the fallback
   from preempting stronger established matches.
```

Probe artifacts:

```text
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q011_semantic_list_tail_probe_20260528\domain_bootstrap_qa_20260528T081259023829Z_qa_qwen-qwen3-6-35b-a3b.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q011_semantic_long_token_probe_20260528\domain_bootstrap_qa_20260528T081512012607Z_qa_qwen-qwen3-6-35b-a3b.json
C:\prethinker_tmp_archive\fresh_non_english_wild_20260526_01_es_reg_q011_list_continuation_probe_20260528\domain_bootstrap_qa_20260528T081717851948Z_qa_qwen-qwen3-6-35b-a3b.json
```

Outcome:

```text
q011 after retrieval repair: partial
all four circular source rows visible in query results:
  src_line_0183
  src_line_0184
  src_line_0185
  src_line_0186
```

Read:

The retrieval mechanism is now doing the right generic thing: it exposes the
complete list. The row remains partial because the oracle compresses those four
source rows into higher-level labels that are not literal source text. Do not
continue tuning this row without a product decision about cross-language
abstraction/paraphrase scoring.

Verification:

```text
python -m py_compile scripts\run_domain_bootstrap_qa.py
python -m pytest tests\test_domain_bootstrap_qa.py -q
-> 431 passed

fixture/source-language leakage grep over scripts/src:
-> no hits
```
