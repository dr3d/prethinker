# Fixture notes — osha_incident_ugly_001

## Why this document was chosen

This is a current OSHA IMIS accident-and-inspection dossier with the full structural anatomy the task spec calls for: a named employer, an event date, a one-sentence narrative, a stated fatality outcome, an inspection number, an accident summary number, and a separate report ID — plus citations, penalties, abatement dates, and a contest record. It also presents three fatally injured workers in a single table, which forces correct row-by-row joins.

## Messy features

- **Three workers, three identifiers:** Employees #1, #2, #3 — ages 26, 48, 57 — all male, all construction laborers, all listed as "Fatality" in Degree of Injury, with no Nature of Injury value populated. Same occupation, different ages.
- **Three numbers that look interchangeable but are not:**
    - Inspection Nr `1814187.015`
    - Accident / Investigation Summary Nr `180500.015`
    - Report ID `0112600`
    plus a related Accident Activity Nr `2277281` and a related companion Inspection `1814197`. Conflating these is a classic OSHA-record mistake.
- **Two addresses for the same employer:** Site address `I91 North Exit 10a West Springfield, West Springfield, MA 01089` vs Mailing address `1010 Turnpike Street, Canton, MA 02021`. The accident happened at the site address, not the mailing address.
- **Multiple distinct dates:** Event Date 03/28/2025, Date Opened 03/28/2025 (same), Close Conference 09/10/2025, Citations Issuance Date 09/17/2025, Abatement Due Date 11/04/2025, Contest date 10/06/2025. Putting these in the correct sequence is the timeline pressure.
- **Two Serious citations to the same standard family but different subparts:** `19260200 G01` and `19260200 G02`. Both at $11,585. Both contested on 10/06/2025. The total penalty $23,170 = 2 × $11,585.
- **Case status conflict:** The case is OPEN, both citations have been issued, and both have been contested. Case status "OPEN" appears twice on the inspection detail page.
- **Lots of blank cells:** SIC value, Nature of Injury (three blanks), Emphasis, Case Closed, Project Cost, Stories. These should not be invented.
- **The employer is "Premier Fence, Llc"** — a fence contractor performing guardrail (not fence) repairs on a highway. Industry classification NAICS 238990 (All Other Specialty Trade Contractors). Identifying that the employer's *name* is "Premier Fence" while the *work* was guardrail maintenance is its own pressure.
- **Inspection Type "Fat/Cat"** — OSHA shorthand for Fatality/Catastrophe; preserved verbatim.

## Prethinker design pressure

- Three-identifier disambiguation: Inspection Nr vs Accident/Investigation Summary Nr vs Report ID. Easy to swap or conflate.
- Multi-row source-record join: three employees with overlapping attributes — questions about the eldest victim's age must pick the right row.
- Date order across at least five distinct dates that are all real events in the case life cycle.
- Blank-handling: cells with no value are not "unknown" by default; they should be reported as absent in the source rather than guessed.
- Penalty arithmetic: $11,585 × 2 = $23,170, both initial and current; FTA $0.
- Address disambiguation: site address vs mailing address for the same legal entity.

## Source caveats

The IMIS public interface is the authoritative source. The dossier is for an active (open) case; citations are issued but contested; values could change as the case progresses. The source.md captures the state as of retrieval on 2026-05-24.

## Local normalization note

The incoming `qa.md` contained both questions and authored reference answers using `q001`-style markers. It was preserved as `qa_authored_with_answers.md`; the canonical `qa.md` was regenerated from `qa_questions.jsonl` as numbered, questions-only Markdown for `scripts/run_domain_bootstrap_qa.py`. Reference answers remain isolated in `oracle.jsonl` for after-the-fact scoring only.
