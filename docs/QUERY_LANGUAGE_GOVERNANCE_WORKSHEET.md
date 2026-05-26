# Query Language Governance Worksheet

Date: 2026-05-26

Purpose:

Keep Prethinker aligned with the intended language boundary:

```text
LLM/router/SIR owns language understanding.
Python owns structure, admission, validation, deterministic ledgers, and proof.
Python should not become an English keyword interpreter for messy human queries.
```

## Trigger

A sidechat note in `tmp/SIDECHAT_LANGUAGE_REGEX_CONCERN_20260526.md` raised two
concerns:

1. Prethinker may be drifting into an English-only query bubble.
2. The project used to treat raw-utterance regex as forbidden, but the current
   QA/source-record layer uses many regex triggers over question text.

This is a road-alignment issue, not a random cleanup issue.

## Current Read

Do not panic-delete working query routes.

Do treat the current shape as architectural debt:

- The core router/Semantic IR lane still appears language-capable.
- The QA/source-record companion layer is the hotspot.
- Many deterministic companions use English regex gates over `utterance`,
  `question`, or `query` text to decide when to activate.
- That can improve English transfer batches while narrowing the real product
  front door.

The intended destination is:

```text
current: question text -> English regex trigger -> deterministic source-record support
better: question text -> governed semantic query lens -> structured query intent -> deterministic source-record support
```

Companions can remain deterministic. The switchboard should become structured
intent, not raw English keywords.

## Audit Added

New informational audit:

```text
scripts/audit_utterance_regex_governance.py
```

Properties:

- Scans active Python runtime files.
- Finds regex calls in query/utterance/question-adjacent functions.
- Classifies hits as:
  - `allowed_structural`
  - `allowed_syntax`
  - `legacy_tolerated`
  - `semantic_trigger`
  - `forbidden_or_needs_review`
- Does not fail CI.
- Emits JSON and Markdown for lab review.

Tests:

```text
tests/test_audit_utterance_regex_governance.py
```

## First Audit Run

Command:

```powershell
python scripts\audit_utterance_regex_governance.py `
  --out-json C:\prethinker_tmp_archive\utterance_regex_governance_20260526.json `
  --out-md C:\prethinker_tmp_archive\utterance_regex_governance_20260526.md
```

Result:

```text
schema: utterance_regex_governance_audit_v1
status: informational
files scanned: 23
regex hits: 556
parse errors: 0

allowed_structural: 149
allowed_syntax: 143
legacy_tolerated: 112
semantic_trigger: 152
```

Hotspot:

```text
scripts\run_domain_bootstrap_qa.py: 449 hits
```

Important direct confirmation:

The source-record routes recently added for Batch 04 are classified as semantic
triggers:

- `_source_record_note_marker_companion`
- `_source_record_under_heading_companion`
- `_source_record_ordered_labeled_entry_companion`

This does not make them wrong. It does mean they should eventually consume
structured query intent rather than raw English trigger regex.

## Multilingual Probe Re-Run

Command:

```powershell
$env:PRETHINKER_BASE_URL='http://127.0.0.1:1234'
$env:PRETHINKER_API_KEY='lm-studio-local'
python scripts\run_multilingual_semantic_ir_probe.py `
  --backend lmstudio `
  --base-url http://127.0.0.1:1234 `
  --model qwen/qwen3.6-35b-a3b `
  --timeout 420 `
  --out C:\prethinker_tmp_archive\multilingual_semantic_ir_20260526.jsonl
```

Result:

```text
router_ok: 10/10
router_score_avg: 1.000
compiler_parsed_ok: 10/10
```

Profiles selected:

```text
legal_courtlistener@v0: 2
medical@v0: 3
probate@v0: 1
sec_contracts@v0: 3
story_world@v0: 1
```

Languages covered:

```text
Spanish: 2
French: 2
German: 2
Italian: 1
Japanese: 1
Portuguese: 1
mixed English/Spanish: 1
```

Read:

- Today's local router/SIR path still handles the existing multilingual probe.
- This does not prove multilingual document compile+QA works.
- This does not prove non-English messy questions activate the source-record
  companion layer correctly.
- The immediate risk remains answer-routing drift, not total loss of language
  capability.

## Governance Rule

Allowed regex:

- source-format parsing
- source-row structural extraction
- Prolog syntax parsing
- JSON/schema/identifier validation
- quoted-span or token extraction that does not decide semantic intent

Dangerous regex:

- decides what a messy human question means
- activates an answer path based on English words
- encodes fixture, batch, document, or local-domain wording
- bypasses the semantic query lens by inspecting raw question text directly

## Structured Query Intent Target

The migration target is a small structured intent object produced by the
governed query lens/router/SIR path and consumed by deterministic query code.

Candidate fields:

```text
intent_type:
  list | count | date | source_location | heading_scope |
  note_marker | signatory | comparison | duration | status

target_terms:
  source-language-preserving target atoms/spans

answer_constraints:
  exact_text | count | normalized_date | cite_source_row

uncertainty_policy:
  answer | clarify | abstain

language:
  diagnostic only; not a trigger vocabulary table
```

## Near-Term Work

1. Keep `audit_utterance_regex_governance.py` informational and rerun it after
   query-side changes.
2. Pick one narrow companion family, probably note-marker or heading-scope, and
   move activation to structured intent without an English regex fallback.
3. Add a tiny multilingual compile+QA probe, not just router/SIR:
   - non-English source with same-language questions
   - English questions over non-English source
   - non-English questions over English/mixed source
   - translation/source-status trap
4. Track whether deterministic source-record support activated because of:
   - structured query intent
   - missing structured intent
   - no support path
5. Do not add Spanish/French/German keyword regex as the fix.

## Current Decision

The Batch 04 source-record repairs can remain because they are deterministic,
source-generic, tested, and leakage-clean.

The immediate course correction has started. Semantic IR now has an optional
`query_intents[]` field for query-shape metadata. The first migrated source
record routes are:

- `_source_record_note_marker_companion`
- `_source_record_under_heading_companion`
- `_source_record_ordered_labeled_entry_companion`
- `_source_record_role_transition_companion`
- `_source_record_board_nominee_path_companion`
- `_source_record_named_role_roster_companion`

These routes no longer activate from raw English regex over the question. They
require structured query intent, either emitted by Semantic IR or inferred from
structured Prolog query templates / evidence-bundle templates. The deterministic
code still parses artifact structure and source-record rows; it does not decide
that English words like "asterisk", "under", "list", "resign", "board path", or
"named individual" mean those routes should fire.

Latest audit deltas:

```text
initial audit:       556 regex hits / 152 semantic_trigger
after first patch:   549 regex hits / 147 semantic_trigger
after role patch:    526 regex hits / 127 semantic_trigger
```

The role-transition source parsers still use regex over normalized admitted
source-record atoms. That is source artifact parsing, not raw-question
interpretation.

Remaining work:

1. Keep migrating older query-side routes from raw `utterance` triggers to
   `query_intents[]`.
2. Rerun the governance audit after each migration batch.
3. Treat any score drop from missing intent as an honest lens/route gap, not as
   permission to restore English keyword fallbacks.
