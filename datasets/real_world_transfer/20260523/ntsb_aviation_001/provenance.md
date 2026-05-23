# Provenance: ntsb_aviation_001

## Source Information

**Source URL**: https://data.ntsb.gov/carol-repgen/api/Aviation/ReportMain/GenerateNewestReport/195085/pdf

**Retrieved**: 2026-05-23 at 14:32 UTC

**Original Format**: PDF, 5 pages

**Document Date**: August 30, 2024 (accident date)

**Published Date**: April 22, 2025 (original publication date)

**Investigation Docket**: https://data.ntsb.gov/Docket?ProjectID=195085

---

## Extraction Process

**Method**: PDF to text via pdftotext utility, verified by hand

**Conversions Applied**:
- Tables preserved as markdown tables for readability
- Hyperlinks converted to markdown links
- Page breaks marked as `---` for reference
- All structured data (pilot hours, aircraft specs) converted to markdown tables
- Narrative prose preserved exactly

**Artifacts Preserved**:
- Original acronym usage (AAIP, VMC, KOVE, CFR, etc.) without expansion
- Original spacing and formatting where possible
- Technical references to FAA regulations verbatim
- Probable cause language exactly as stated

---

## Known Issues & Caveats

1. **Some spacing approximated**: Original PDF formatting is approximate in markdown
2. **No OCR errors**: PDF was well-scanned, no OCR artifacts
3. **Acronyms unexpanded**: Document uses regulatory and aviation acronyms without full expansion. Context in original document.
4. **Incomplete inspector information**: Last inspection date and time since last inspection not specified in source
5. **Toxicology result**: Field marked as blank in original
6. **Medical limitations**: Reported as "without waivers/limitations" but full details not in summary

---

## Why This Document Pressures Prethinker

### Dense Structured Data Mixed with Narrative

The document mixes tabular pilot/aircraft specifications with open narrative description of the accident sequence and analysis. Prethinker must handle both:
- **Structured**: Tables of pilot flight time, aircraft certification, meteorological readings
- **Narrative**: Pilot's account of events, operator's claim, NTSB's causal analysis

### Causal Reasoning

The accident involves a **causal chain** requiring reasoning across multiple references:
1. Pilot error → failure to set collective friction
2. Collective friction inadequate → collective bounce activated
3. Collective bounce → vertical oscillation (3 cycles/second)
4. Oscillation → loss of control
5. Loss of control → terrain impact

Prethinker must thread together the initial condition (friction not set), the mechanism (collective bounce), and the outcome (crash).

### Source Authority and Credibility

The document explicitly **states a limitation**: "The NTSB did not travel to the scene of this accident."

This is a Class 4 investigation (lowest class), which constrains what the NTSB can definitively determine. Prethinker should recognize this as reducing evidentiary strength compared to investigations where the NTSB attended the scene.

### Contradiction: Operator Claim vs NTSB Finding

**Operator's Report** (from pilot/operator interview):
> "There were no preaccident mechanical malfunctions or failures that would have precluded normal operations."

**NTSB Probable Cause** (from investigation):
> "The pilot's failure to set collective friction which resulted in collective bounce and subsequent loss of control."

These don't directly contradict (one says no *mechanical* failures, the other says *pilot error*), but they frame the problem differently. Prethinker should recognize the framing difference.

### Regulatory Knowledge Required

Several questions require understanding of aviation regulations:
- Part 137 (agricultural flight operations)
- FAA medical certificates and their limitations
- Airworthiness certificates (Restricted vs Standard)
- Flight review requirements

### Timeline and Date Inference

Multiple dates appear throughout:
- Accident date: August 30, 2024
- Medical exam: February 6, 2024 (6 months prior)
- Last flight review: October 11, 2023 (9 months prior)
- Last 24 hours flight time: 1 hour (minimal recent experience)

Prethinker must infer temporal relationships and note that medical certification was recent while flight review was older.

### Specific Pressure Points

1. **Table extraction**: Can Prethinker extract and understand pilot hour breakdowns?
2. **Contradiction handling**: Can it recognize the difference between "no mechanical failures" and "pilot error in operation"?
3. **Acronym resolution**: Can it handle aviation-specific terminology (VMC, AAIP, UH-1H)?
4. **Source limitation awareness**: Can it note the significance of "NTSB did not travel to the scene"?
5. **Causal chain reasoning**: Can it thread together friction → bounce → oscillation → loss of control → crash?
6. **Regulatory context**: Can it understand Part 137 and FAA medical requirements?

---

## Access & Licensing

**Public Domain**: NTSB documents are U.S. government work products and are in the public domain. No access restrictions or licensing limitations.

**Citation**: 
> National Transportation Safety Board. (2025). Aviation Investigation Final Report - WPR24LA299, Colusa, California. Retrieved from https://data.ntsb.gov/Docket?ProjectID=195085

---

## Related Documents

- **NTSB Accident Report List**: https://www.ntsb.gov/investigations/AccidentReports/Pages/Reports.aspx
- **NTSB Safety Recommendations**: https://www.ntsb.gov/safety/recsearch/
- **Federal Register (Aviation Regulations)**: https://www.faa.gov/regulations_policies/
