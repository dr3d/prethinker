# Fixture notes — osha_incident_ugly_003

## What this document pressures

This fixture combines two OSHA documents — the underlying Citation and Notification of Penalty (PDF) and the announcing news release (HTML) — so the model under test has to navigate both citation-internal joins and citation-vs-news-release inconsistency probes.

### Date discrepancy between news release and citation (q021)
The news release lede places the incident "in June 2024" and the body says "on June 8, 2024," but Citation 1 Item 1 says "On or about July 8, 2024." This is a verbatim inconsistency in the official source. The inspection-opening date (07/09/2024) is consistent with a July 8, 2024 incident — supporting the citation's July 8 date as correct. q021 probes whether the model surfaces the inconsistency rather than picking one or silently averaging.

### Identifier recurrence (q022, q023)
The same penalty amount ($16,131 / $16,131.00) appears in five distinct locations across the news release and the citation packet; the same inspection number (1760606) appears in four distinct locations within the citation packet. Pipelines that deduplicate values aggressively will under-count; pipelines that don't track location will be unable to enumerate them in source order.

### Attribution stack (q024)
Condell Eastmond is attributed four times — once via a paraphrased quote in the news release, and three times as a signature/closer in the citation packet (cover letter, Citation 1 Item 1, Debt Collection Notice). q024 forces enumeration with provenance.

### Calendar-days vs working-days arithmetic (q025)
The 182 calendar days the inspection was open and the 15 working days the employer has to contest are explicitly different time units. The source defines working days as excluding weekends and Federal holidays. Pipelines that flatten "days" into a single unit will get the comparison wrong.

### Six-step enumeration in violation narrative (q011)
Citation 1 Item 1 lists six corrective methods. The methods are connected by "and" connectors and appear as a single semicolon-separated paragraph in the original PDF; the fixture preserves them as a bulleted list and tests source-order recovery.

### Blank fields as content (q015)
The "Notice to Employees of Informal Conference" contains literal blank fields for the conference date and time. These are not redactions or omissions — they are intentional blanks in the form. q015 probes whether the model recognizes blanks as a distinct kind of content.

### Negative finding probe (q017)
The source describes the citation as issued; it does not contain any follow-on contest, payment, or abatement-certification status. q017 tests whether the model correctly reports that the source is silent on later events, rather than inventing a status.

### Multi-document field union (q003, q004, q005)
OSHA office address appears in the cover letter and in the Citation header; the news release contributes media contacts; the news release also contributes the company description (workforce, counties served). Each of q003, q004, q005 forces a particular field-set across distinct sub-documents.

### Schedule of debt-collection charges (q014)
The Debt Collection Notice specifies a 1% interest rate, a 6% delinquent charge rate, and a separate "Administrative Costs" category, each with its own threshold (30 calendar days for interest, 90 calendar days for delinquent charges). q014 stresses preservation of all three rates and triggers.

### Penalty payment threshold (q018)
The $25,000 ACH-only threshold is buried in the Penalty Payment paragraph. q018 tests recovery of this specific numeric threshold and the associated Transaction-ID requirement.

### Section 5(a)(1) general-duty citation (q012)
The citation is under Section 5(a)(1) of the OSH Act — the "general duty" clause — rather than a specific 29 CFR standard. This is itself a distinguishing fact for the fixture (general-duty citations require a "recognized hazard" finding rather than a standards violation). The fixture preserves the language verbatim in Citation 1 Item 1's section header.
