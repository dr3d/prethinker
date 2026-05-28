# fixture_notes — legal_order_chronology_001

## Why this document is a good ACH stress test

A settled SEC cease-and-desist order is, on its face, one-sided (the respondent neither admits nor denies). But the analytic question it raises is genuinely contestable: among several actors and systems whose failures the order recites, where does responsibility for the misleading disclosures actually sit? The order itself supplies competing loci and then takes a position, which makes it a clean actor-responsibility ACH with a determinable winner and real — but not extreme — sensitivity. It also carries a long, forensically-gapped chronology that supports separate date/sequence reasoning.

## The competing loci of responsibility are all in the source

- **Disclosure controls / policy design (h1).** The order says the misleading statements "resulted in part from the company's failure to design controls," devotes a findings section to the absence of escalation controls, and notes the company's own disclosed material weakness in disclosure controls.
- **Cybersecurity personnel (h2).** Personnel repeatedly failed to escalate; during the 2022 event they misread alerts, assumed malware was quarantined, delayed investigating for almost a week, and operated a misconfigured detection pipeline.
- **Disclosure drafters / decision-makers (h3).** The 10-K risk factors framed actual, known intrusions as hypothetical and were carried forward substantially unchanged from the pre-breach 2019 language.

## How the document adjudicates

The order's causal chain places the root in the controls (h1): the pre-2022 policies did not require escalation, and "consequently" the personnel did not report (so h2 is framed as downstream of h1); decision-makers therefore could not assess materiality, producing the misleading disclosures (h3 conduct). The distinct Rule 13a-15(a) charge and the company's own material-weakness diagnosis reinforce h1 as the locus.

## Why sensitivity is medium

This fixture sits between the batch's two brackets:

- It is more robust than a single-row flip: h1 is anchored by three rows (the causal-bridge sentence, the dedicated controls findings, and the material-weakness disclosure), so removing any one does not cleanly flip the winner.
- It is more sensitive than the batch's low-sensitivity fixture: removing BOTH the causal-bridge sentence and the dedicated controls findings would foreground the negligent disclosure content and shift the best read to h3 (the drafting failure). And several rows are genuinely double-edged — the EDR/SIEM misconfiguration and the unchanged-since-2019 risk factors each support two hypotheses at once.
- h2 cannot win on this record: the order frames the personnel non-reporting as a consequence of the controls gap, and the clearest operational-only failures concern the 2022 extortion event rather than the 2020/2021 risk-factor disclosures at the heart of the charges.

A correct ACH read names h1 as the winner, marks sensitivity medium, identifies the causal-bridge row as load-bearing, and notes that the winner is stable to any single-row removal but flips under a plausible two-row removal.

## Contested-chronology dimension

The order repeatedly flags that Unisys could not establish the full timeline because of forensic gaps ("significant gaps in its ability to identify the full scope"; "unable to determine how long the misconfiguration persisted"; documents reviewed only in 2022 when "only half ... remained available"). The "when did Unisys know enough to require disclosure" question is itself contestable from the dates: it knew of intrusions by December 2020 yet filed hypothetical-framed risk factors in February 2021 and February 2022. The dates_sequence QA exercises this without requiring outside knowledge.

## Source-containment

Every fact needed is in source.md. The order defines its own technical vocabulary (threat actor, credential, exfiltration) in [DEFINITIONS], and the securities-law provisions are described in plain terms in the Violations section (e.g., Rule 13a-15(a) "requires issuers to maintain disclosure controls and procedures designed to ensure required information is recorded, processed, summarized, and reported within the specified time periods"). No outside knowledge of the SolarWinds attack, SEC procedure, or cybersecurity is required to answer the QA or run the ACH. Administrative payment and signature boilerplate is summarized because it carries no facts load-bearing for the analysis. No Prethinker internals are referenced anywhere.
