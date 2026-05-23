# NTSB Thermometer Pilot 2026-05

Real-world NTSB accident investigation documents for Prethinker transfer testing.

## Overview

Two complete NTSB investigation reports with curated QA: one aviation accident (preliminary report), one marine accident (final report). Both are unmodified public records with full source material preserved.

- **Aviation (ntsb_001):** Robinson R44 II crash, Bluestem, WA, June 19, 2024 (WPR24FA200)
- **Marine (ntsb_002):** Towing vessel capsizing, Gulf of America, May 13, 2024 (DCA24FM038 / MIR-25-21)

**Total:** 50 QA items (25 per document)

## Document Structure

Each document directory contains:

```
ntsb_00X/
  source_original.pdf          # Original PDF from NTSB (PDFs not yet included in archive)
  source.md                    # Faithful markdown conversion
  metadata.json                # Document metadata + known caveats
  qa.md                        # 25 questions (no answers)
  oracle.jsonl                 # 25 answers (one JSON object per line)
  provenance.md                # Source verification + data quality notes
```

Root files:

```
manifest.json                  # Dataset overview
README.md                      # This file
```

## QA Structure

### Questions (qa.md)
- One per line
- No answers embedded
- Format: `q001: What was the registration number...`
- 25 per document across 10 categories

### Answers (oracle.jsonl)
- One JSON object per line
- Format: `{"id":"q001","source_id":"ntsb_001","category":"direct_lookup","reference_answer":"...","supporting_source_spans":["page 3"],"difficulty":"medium"}`
- Categories: direct_lookup, timeline, actor_action, causal_chain, policy_rule, count_table, contradiction, unresolved_issue, as_of_date, source_limitation
- Difficulty: easy, medium, hard

## Question Mix

Both documents are deliberately designed to pressure different facets:

1. **Direct lookup** (5 each): Name, number, date, location, basic facts
2. **Timeline/date inference** (5 each): Elapsed time, event sequence, clock math
3. **Actor/action attribution** (2 each): Who did what, roles, responsibilities
4. **Causal chain** (2 each): Why/how things happened, mechanical causation
5. **Policy/rule/application** (2 each): Regulatory requirements, compliance
6. **Count/table extraction** (2 each): Numbers, measurements from structured data
7. **Contradiction or competing explanation** (0-2): Crew vs. instrument data, competing theories
8. **Unresolved/open issue** (1-2): Uncertainties, unknowns in the record
9. **"As of date" state** (1 each): What was known/unknown at report date
10. **Source limitation or evidence quality** (2 each): Data gaps, measurement errors, missing information

## Data Discipline

### No Invented Content
- Every document is an unmodified public NTSB record
- No scenario construction, no synthetic data mixing
- Source material is messy and incomplete intentionally

### Faithful Extraction
- PDFs converted to markdown preserving headings, tables, structure
- No paraphrasing or interpretive summarization
- Quotes, measurements, and factual claims reproduced exactly

### Answer Grounding
- Every answer references supporting source span(s)
- No external knowledge injected
- Answers derived solely from document text

### Real Messy Uncertainty
- Preliminary reports lack final conclusions
- Weather data collected far from accident site
- Crew observations differ from instrument readings
- Some phenomena (waterspout? straight-line winds?) unconfirmed
- Investigation limitations and data gaps preserved

## Known Caveats

### ntsb_001 (Aviation)
- Preliminary report only; probable cause TBD
- Investigation ongoing; limited narrative detail
- Fire destroyed most of fuselage
- No final report issued as of May 2026

### ntsb_002 (Marine)
- Final report with probable cause determined
- Weather stations 21–27 nm from casualty site
- Salvage operations (May 18–June 15) modified wreckage before examination
- Storm characteristics (possible waterspout) inferred from crew testimony, not confirmed
- Some crew communications not definitively verified

## Transfer Testing Guidance

This pilot is designed to test Prethinker's performance on:

1. **Complex structured/narrative mix:** Tables, timelines, prose narratives interleaved
2. **Incomplete information:** Some questions cannot be answered from document
3. **Source limitation awareness:** Detecting what is and isn't known
4. **Competing evidence:** Crew estimates vs. NWS data, crew observations vs. instruments
5. **Regulatory knowledge:** Part numbers, regulatory codes, compliance requirements
6. **Contradiction detection:** Multiple sources providing conflicting measurements
7. **Causal reasoning:** Wind → barge drift → towline force → heeling → capsizing

## Implementation Roadmap

Phase 1 (completed): 2-document NTSB pilot (aviation + marine)  
Phase 2 (planned): 7 additional NTSB documents (expand aviation; add rail/highway/pipeline)  
Phase 3 (planned): FDA warning letter batch (8–12 documents)  
Phase 4 (planned): SEC/EDGAR batches (financial/regulatory)  
Phase 5 (planned): OSHA incident investigation reports  

## Metadata

| Field | Value |
|-------|-------|
| Created | 2026-05-23 |
| Dataset ID | ntsb_pilot_2026_05 |
| Version | 1.0 |
| Documents | 2 |
| Total QA items | 50 |
| Total questions | 50 |
| Answer format | JSONL (one per line) |
| Source authenticity | Official NTSB public records |
| Invention | None |

## Files to Include

```
prethinker_ntsb_pilot_2026_05.zip
├── manifest.json
├── README.md
├── ntsb_001/
│   ├── source_original.pdf (NTSB WPR24FA200)
│   ├── source.md
│   ├── metadata.json
│   ├── qa.md
│   ├── oracle.jsonl
│   └── provenance.md
└── ntsb_002/
    ├── source_original.pdf (NTSB MIR2521)
    ├── source.md
    ├── metadata.json
    ├── qa.md
    ├── oracle.jsonl
    └── provenance.md
```

## License and Attribution

All NTSB documents are public records. Source PDFs retrieved from official NTSB distribution:
- Aviation: https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/194501/pdf
- Marine: https://www.ntsb.gov/investigations/AccidentReports/Reports/MIR2521.pdf

QA curation by Prethinker pilot team, 2026.
