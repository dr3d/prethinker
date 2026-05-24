# Fixture notes — sec_material_event_ugly_004

## What this document pressures

This fixture uses an SEC Form 8-K/A corrective amendment as a vehicle for probes about copy authority, error attribution, date-stack disambiguation, and form-type-specific signatory norms.

### Form type and amendment number (q001, q014)
"8-K/A" (form type with amendment suffix) and "(Amendment No. 1)" (cover-page amendment number) are distinct identifiers. Pipelines that drop the "/A" suffix or omit the amendment number lose key fixture identifiers.

### Single error, large impact (q021)
The single corrected figure is a $100 million understatement ($280.1M → $380.1M) — a leading-digit error (2 → 3) for a specific segment ("Private Equity"), a specific reporting period ("the quarter ended September 30, 2025"), and a specific line item ("Net Realizations") on a specific page ("page 11"). All four scope qualifiers must be recovered to answer q021 correctly. Pipelines that report only "the figure was wrong" or that misidentify segment/period/line will fail.

### Date stacking on October 23, 2025 (q009, q010, q022)
At least six distinct events anchor to October 23, 2025: (i) Amendment Date of Report, (ii) Original 8-K filing date, (iii) website Earnings Presentation posting, (iv) press release issuance, (v) press release date stamp, (vi) Amendment signature date. Pipelines that report only one or two will under-count. q009 and q010 force explicit enumeration of all event-anchors at this date.

### Date of Report vs filing transmission date (q008, q022)
The source provides "Date of Report" and "signature date" but does NOT explicitly state when the Amendment was transmitted to EDGAR. The accession sequence implies a later transmission, but the source itself only commits to October 23, 2025 as Date of Report/signature. Fixture probes whether the model recognizes that "Date of Report" is the date of the underlying event, not necessarily the transmission date.

### Copy-authority hierarchy (q024)
Two copies of the Q3 2025 earnings presentation exist per the source:
- EDGAR Copy (Exhibit 99.1 to Original 8-K) — contained the error.
- Earnings Presentation (Company's website, Shareholders page, Overview + Events sections) — contained the correct figure.

The Explanatory Note establishes the website Earnings Presentation as the canonical authority by referring to it as "the actual earnings presentation" and saying the EDGAR Copy "did not conform" to it. Pipelines that treat EDGAR as default authoritative will get the chain backward.

### "Furnished but not filed" (q018)
A small but important Exchange Act distinction. Item 2.02 expressly classifies the press release information as "furnished but not filed" — a status that limits Section 18 liability and excludes the material from automatic Securities Act incorporation. The source uses this verbatim language and the fixture probes recovery.

### Negative-finding probes on Amendment scope (q019, q020, q023)
Three independent negative-finding probes:
- q019: no other changes beyond the corrected figure
- q020: corrected Earnings Presentation not attached to this Amendment
- q023: no other content changes between Original 8-K and Amendment (Item 2.02 and Item 9.01 unchanged)

All three force recognition of what the source does NOT contain.

### CFO-as-signatory (q025)
Michael S. Chae signs as Chief Financial Officer. In contrast, the ServiceNow 8-K (sec_material_event_ugly_003) is signed by the General Counsel. The reason for the difference is the subject matter: Item 2.02 (financial reporting accuracy) → CFO; Item 5.02 (executive employment agreement) → GC. The source itself does not articulate this norm, so q025 limits the answer to what the source establishes vs what is implicit corporate-governance practice.

### Two website section names with intact quotation marks (q015)
"Overview" and "Events" — both must be reproduced with their quotation marks. q015 probes verbatim preservation.

### Case preservation: "NOT APPLICABLE" (q017)
The former-name field's value is in all caps in the source. Compare to ServiceNow's "Not Applicable" in title case. q017 probes whether the model preserves case fidelity rather than normalizing.

### Identifier formats and table reproduction (q012, q013)
- Three-cell identifier table (state / Commission File Number / IRS EIN) with column headings.
- Securities table with three column headings ("Title of each class" / "Trading Symbol(s)" — note the plural with parenthetical s — / "Name of each exchange on which registered").

The plural "Symbol(s)" is a small but distinctive marker; pipelines that normalize to "Trading Symbol" lose verbatim fidelity.

### Q3 reporting-period arithmetic (q007)
September 30, 2025 → October 23, 2025 = 23 calendar days. This is the typical lag for a 13-business-day quarterly earnings release cycle.

### Item 2.02 plus Item 9.01 — two-item filing (q014)
The filing reports under two Items in source order: 2.02 (Results of Operations) and 9.01 (Financial Statements and Exhibits). Pipelines that report only one Item miss the structural pattern of a "results announcement + supporting exhibits" 8-K.
