# FDA Domain Transfer Work Order

Purpose: create an unlike FDA warning-letter micro fixture to test whether the
current `fda_warning_letter_v1` domain pack transfers beyond the Marigold
micro. This is not a score-polishing fixture. It should pressure the same
registered FDA carriers on a different public source.

## Package Name

Use this folder name:

```text
fda_warning_letter_domain_transfer_001
```

Package it as a zip containing exactly one top-level directory with that name.

## Source Selection

Select one real public FDA warning letter that is not already in this repo and
not derived from the Marigold micro. Prefer a CDER or drug CGMP warning letter
with:

- warning-letter issue date;
- issuing FDA office or center;
- recipient or firm;
- facility name/location and FEI if present;
- inspection date range;
- Form FDA 483 response date if present;
- at least two numbered CGMP violations;
- at least two CFR citations;
- preferably one sterility, aseptic-processing, contamination-control, or
  microbiological-control violation so the category boundary can be tested on a
  source other than the Marigold micro;
- response deadline or response instruction;
- consultant recommendation if present;
- concluding scope/responsibility language;
- signatory block if present, or clear absence if the excerpt does not include it.

Avoid synthetic or LLM-authored documents. Use a real FDA page/PDF/text source.

## Files

Create these files:

```text
fda_warning_letter_domain_transfer_001/
  manifest.json
  source.md
  expected_facts.pl
  forbidden_facts.pl
  source_notes.md
```

## manifest.json

Use:

```json
{
  "fixture_id": "fda_warning_letter_domain_transfer_001",
  "source": "source.md",
  "expected_facts": "expected_facts.pl",
  "forbidden_facts": "forbidden_facts.pl",
  "purpose": "Transfer-test the closed FDA warning-letter domain schema on an unlike real FDA warning letter without prose-shaped atom slots."
}
```

## source.md

Include a compact excerpt of the source, not the entire warning letter unless
the whole letter is short. Preserve enough context to support every expected
fact. Use plain markdown. Include a short source citation at the top:

```text
Source URL: ...
Source title: ...
Accessed: 2026-06-01
```

Do not add explanatory notes inside `source.md`; use `source_notes.md` for notes.

## expected_facts.pl

Use only registered FDA domain predicates from:

```text
datasets/domain_profiles/fda_warning_letter_v1/ontology_registry.json
```

Expected facts should cover 18-28 rows. Use Prolog variables for IDs and source
coordinates, as in the Marigold fixture:

```prolog
fda_warning_letter(Letter, IssuingOffice, Recipient, IssueDate, SrcLetter).
```

Required carrier pressure:

- `fda_warning_letter/5`
- `fda_facility_identity/5` if facility identity/FEI appears
- `fda_correspondence_party/5` for recipient and any signatory/contact present
- `fda_inspection_event/6`
- `fda_form483_response/4` if response date appears
- `fda_prior_warning_letter/5` only if a prior warning letter is source-stated
- `fda_regulatory_meeting/4` only if a meeting/teleconference is source-stated
- `fda_violation/5` for each numbered violation in the excerpt
  - choose the most compact governed category supported by the source;
  - if a sterility/microbiological-control violation could reasonably be
    categorized as either `contamination_control` or `aseptic_processing`, pick
    one and explain the rationale in `source_notes.md`;
- `fda_violation_citation/4` for each CFR/statutory citation
- `fda_violation_detail/5` for atomic details such as affected lot, affected
  product, process area, procedure scope, record-review subject, or response
  status
- `fda_adulteration_basis/5` if adulteration basis appears
- `fda_response_requirement/6` for response deadline/instructions
- `fda_consultant_recommendation/4` if source-stated
- `fda_conclusion_scope/4` for not-all-inclusive, responsibility, recurrence,
  ownership, or product-scope conclusion language
- `domain_omission/5` only for explicit source-stated absence, such as no
  signatory shown in the excerpt

Do not create new predicates. Do not use prose-shaped atom values.

## forbidden_facts.pl

Add 5-10 forbidden facts that catch obvious cheating:

- paragraph-shaped violation categories;
- full response instructions as one atom;
- full rule text as a citation value;
- source excerpt or summary atoms;
- inferred signatory/contact facts not present in the source;
- inferred recurrence/repeat-observation facts not source-stated.

## source_notes.md

Include:

- source URL and title;
- why this warning letter was selected;
- which expected facts were hard to represent;
- rationale for each `fda_violation/5` category choice, especially any
  contamination-control versus aseptic-processing boundary;
- any facts deliberately omitted because the source did not state them clearly;
- any uncertainty about atom choice.

## What This Pressures

This fixture pressures:

- transfer of the FDA closed predicate registry;
- stable wrapper/facility/recipient atom construction;
- second-layer violation details without source prose;
- response requirement decomposition;
- consultant citation scoping;
- conclusion-scope recurrence/responsibility rows;
- omission accountability for absent signatory/contact information.

## Acceptance Check Before Delivery

Before zipping, run a self-check by inspection:

- every expected fact uses a registered signature;
- no expected or forbidden fact contains full prose sentences;
- every expected fact is directly supported by `source.md`;
- source text is real public FDA material, not synthetic;
- the zip contains the top-level folder and the five required files.

## Codex Preflight After Delivery

Before any compile run, validate the unpacked package:

```powershell
python scripts\validate_domain_transfer_package.py `
  --package-dir datasets\compile_micro_fixtures\fda_warning_letter_domain_transfer_001 `
  --profile-registry datasets\domain_profiles\fda_warning_letter_v1\ontology_registry.json `
  --out-md C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_preflight.md `
  --out-json C:\prethinker_tmp_archive\fda_warning_letter_domain_transfer_001_preflight.json
```

If this preflight fails, fix the fixture package before compiling. Do not spend
inference budget on a package with missing source citation, out-of-registry
expected facts, or prose-shaped expected atoms.
