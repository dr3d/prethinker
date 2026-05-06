# Autolab Agent Skill Evolution

Last updated: 2026-05-06

## Principle

Autolab roles should evolve the same way Prethinker lenses evolve: a repeated
failure earns a name, the name earns a bounded job shape, and only then does it
become a reusable skill.

Do not pre-build a large agent org chart. The current useful frontier is two
skills:

- a source/domain hunter that brings back difficult material;
- a QA drafter that turns that material into sparse, hostile questions.

Everything else can wait until failure teaches us what role is missing.

## Why Sparse Wild Fixtures Matter

Curated fixtures are useful because they isolate a surface. Wild fixtures are
useful because they refuse to be polite.

Some harvested material should not be expected to reach 100%. It may be too
thin, contradictory, bureaucratic, partial, translated, table-heavy, missing
context, or full of stale/corrected claims. That is not bad data if the fixture
is labeled honestly. It teaches whether Prethinker can:

- compile enough epistemic state to say what is known;
- distinguish absence from contradiction;
- avoid zombie answering when evidence does not add up;
- ask for clarification when the compiled KB exposes ambiguity;
- preserve uncertainty rather than smoothing it into false confidence.

The score is not the only product. The failure shape is the product.

## Skill 1: Source/Domain Hunter

Purpose: find real-world source packets that stress semantic compilation.

The hunter should look for documents with at least two of these traits:

- named entities or roles;
- dates, intervals, amendments, corrections, or status changes;
- rules, requirements, thresholds, exceptions, or authority chains;
- claims made by one party and findings made by another;
- visible gaps, partial exhibits, unclear references, or conflicting surface
  language;
- enough source text to support 10-25 questions, but not so much that the first
  compile becomes a document-management problem.

Good hunting grounds:

- public enforcement letters;
- zoning, licensing, school-board, or city-committee minutes;
- procurement awards and protest decisions;
- grant guidelines plus amendment notices;
- recall, safety, audit, or inspection reports;
- museum, archive, accession, or deaccession records;
- policy pages with exceptions and effective-date notes.

Hunter output should be structured:

```json
{
  "schema_version": "autolab_source_candidate_v1",
  "candidate_id": "short_slug",
  "source_url": "https://...",
  "domain_label": "regulatory | governance | archive | safety | policy | other",
  "why_it_is_hard": ["temporal_status", "authority_chain"],
  "expected_sparse_score": "low | medium | high",
  "provenance_notes": "short human-readable note",
  "source_text_path": "tmp/hermes_mailbox/runs/.../source.md",
  "do_not_use_reason": ""
}
```

The hunter must not rewrite source facts into a cleaner story. It can clean
HTML/PDF clutter, preserve provenance, and label why the source looks useful.

Candidate source artifacts can be checked with:

```bash
python scripts/validate_autolab_candidate_artifacts.py --source-candidate path/to/source_candidate.json
```

Codex can queue the first bounded hunter/QA pilot with:

```powershell
python scripts/autolab_queue_wildbench_pilot.py --candidate-count 2 --qa-rows 12
```

That writes a markdown job packet for Hermes. The packet asks for public source
packets, cleaned source text, source-candidate JSON, QA-candidate JSON, a local
validator run, and a short summary. It explicitly forbids tracked code edits,
heavy compiles, and desktop-model calls.

For the small laptop control model, prefer staged pilots first:

```powershell
python scripts/autolab_queue_wildbench_pilot.py --source-only --candidate-count 1
```

Source-only hunting is intentionally humbler. It proves the web/provenance and
candidate-artifact path before asking the same small model to draft QA.

## Skill 2: QA Drafter

Purpose: draft questions that expose whether the compiled KB captured the
meaning surfaces that matter.

The QA drafter should create 10-25 candidate rows per source packet. It should
not assume every question has a crisp answer. It should include rows where the
correct response is "not established from the compiled artifact" or "requires
clarification" if the source itself supports that epistemic state.

Question families:

- direct fact: who, what, where, which item;
- temporal status: what was true on a date or after an amendment;
- authority: who can approve, deny, override, or interpret a rule;
- activation/exclusion: when a rule applies and when it does not;
- correction cascade: which later statement supersedes an earlier one;
- claim versus finding: who asserted something and whether it was established;
- absence: whether the source establishes a fact or leaves it unknown;
- rationale versus mechanism: why something happened versus what caused it.

QA output should be structured:

```json
{
  "schema_version": "autolab_candidate_qa_v1",
  "source_candidate_id": "short_slug",
  "rows": [
    {
      "qid": "q001",
      "question": "What status did X have after Y?",
      "surface_family": "temporal_status",
      "expected_answer_mode": "exact | uncertain | not_established | clarification",
      "source_anchor": "short quote or section label, not a long passage",
      "why_this_is_hard": "requires corrected status, not first mention"
    }
  ]
}
```

The QA drafter should not write oracle answers unless a later job explicitly
asks for answer-key drafting. In the wildbench path, source-faithful judging can
compare Prethinker answers to the source packet later.

Candidate QA artifacts can be checked with:

```bash
python scripts/validate_autolab_candidate_artifacts.py --qa-candidate path/to/qa_candidate.json
```

## Zombie-Inducing Content

Some content should be hunted specifically because it tempts a model to keep
talking after comprehension has failed. Useful zombie surfaces include:

- source packets with missing appendices;
- cross-references to documents not included in the packet;
- tables whose headings are separated from rows;
- amendment chains where the current rule is implied but not restated;
- testimony or minutes where proposals, objections, and final decisions are
  interleaved;
- contradictory claims where no adjudicator resolves the conflict;
- OCR or formatting damage that preserves some facts but not enough structure.

These samples should be labeled as stress fixtures, not normal score fixtures.
The target behavior may be graceful refusal, clarification, or low-confidence
compiled epistemic state, not a high exact score.

## Review Gate

Autolab can generate source candidates and QA drafts. Codex must still decide:

- whether the source becomes a real dataset fixture;
- whether sparse or zombie behavior is the intended target;
- whether a poor score is a harness failure or an honest evidence limit;
- whether a new hunter/drafter pattern deserves a named skill.

Failures beget creations. Creations earn their names. Names earn their slots.
