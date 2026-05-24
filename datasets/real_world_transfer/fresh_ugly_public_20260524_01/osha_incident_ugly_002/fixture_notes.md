# Fixture notes — osha_incident_ugly_002

## Why this document was chosen

This is a complete OSHA IMIS dossier — Accident Report Detail plus matched Inspection Detail — for a *closed* fatality case, deliberately contrasted with osha_incident_ugly_001 (still-open, multi-victim, struck-by). It exercises a different industry (roofing contractors, NAICS 238160 vs all-other specialty trade 238990), a different fatal mechanism (fall through a deteriorated metal roof deck vs struck by a vehicle), a different case life cycle (Informal Settlement reducing penalty 50% vs both citations contested and unresolved), and a single victim rather than three. It also contains a real internal discrepancy in the original record (fall height 22.8 ft in narrative vs 23 ft in three other fields) — exactly the kind of ugly real-world inconsistency that benchmark data scrubs out.

## Messy features

- **Discrepant fall height** within the same document: narrative says 22.8 feet; Accident Details Non-building Height says 23; Employee Details Distance of Fall and Worker Height Above Ground/Floor each say 23 feet. All four values are preserved verbatim.
- **Same Investigation Summary text duplicated** between the Accident Report Detail page and the Inspection Detail page (a known IMIS oddity).
- **Settlement reduces penalty:** Initial Penalty $13,494, Current Penalty $6,747, FTA $0 — an exact halving. The "Latest Event" column shows "I — Informal Settlement"; the "Contest" column is blank. A reasoner that conflates "current" and "initial" penalty will give the wrong total.
- **Two states involved:** Site Address Plant City, FL 33563 vs Mailing Address Franklin, OH 45005. The accident occurred at the site address (Florida), not at the corporate mailing address (Ohio).
- **Several distinct dates** that must be ordered: Event Date 01/13/2020, Date Opened 01/13/2020 (same day), Close Conference 06/24/2020, Citation Issuance 06/25/2020, Abatement Due 07/08/2020, Case Closed 08/18/2020. The close conference *precedes* citation issuance by one day; both *precede* the abatement deadline; the case is then closed about six weeks after the abatement deadline.
- **Three numeric identifiers that look interchangeable but are not:** Inspection Nr `1455758.015`, Accident Summary / Investigation Nr `123160.015`, Report ID `0420600`. Plus a Related Activity Accident Activity Nr `1533489`. Conflating these is the same OSHA-record mistake exposed in fixture 001 but on a different numeric range.
- **Specific time of day** is given: 8:31 a.m. Most timeline questions in OSHA records lack a time component; this one does not.
- **Blank cells preserved:** SIC value, "Nature of Injury" for the employee, "Fatality Cause" sub-field, "Project Cost," and "Contest" — none of which should be invented.
- **"Cause: Roofing"** appears in the Construction sub-column of the Employee Details row — a short tag, not a sentence. Preserved verbatim.
- **NAICS 238160 / Roofing Contractors** is the establishment's classification — and the abstract explicitly names a "roofing company" — yet the citation 19260760 A01 is in 29 CFR 1926 Subpart R (Steel Erection). Identifying that an employer in the roofing trade was cited under a steel-erection standard is a join across what would otherwise be two separate facts.

## Prethinker design pressure

- Numeric reconciliation across fields: 22.8 vs 23 feet — neither is "the" answer; both must be reported as recorded.
- Settlement arithmetic: current is exactly half of initial. Easy to lose track of which is which.
- Three-identifier disambiguation: Inspection Nr vs Accident/Investigation Nr vs Report ID.
- Address disambiguation: site (FL) vs mailing (OH) for the same legal entity.
- Date ordering and inter-date intervals: six events in a single case life cycle, with one one-day gap (close conference → citation issuance) that is easy to flip.
- Standard-vs-industry mismatch: roofing contractor cited under a steel-erection-subpart standard.
- Blank-handling: nature of injury and contest cells are both blank, but for different reasons (one is unrecorded, one means "not contested").

## Source caveats

The IMIS public interface is the authoritative source. This case is closed; the record as captured here reflects the final, post-settlement state. The numeric inconsistency between the abstract (22.8 ft) and the structured fields (23 ft) is a feature of the original OSHA record and was not introduced in transcription.

## Local normalization note

The incoming `qa.md` contained both questions and authored reference answers using `q001`-style markers. It was preserved as `qa_authored_with_answers.md`; the canonical `qa.md` was regenerated from `qa_questions.jsonl` as numbered, questions-only Markdown for `scripts/run_domain_bootstrap_qa.py`. Reference answers remain isolated in `oracle.jsonl` for after-the-fact scoring only.
