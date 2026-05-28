# fixture_notes — public_order_low_001

## Why this source was chosen
A self-contained FTC complaint (the operative findings document behind the finalized consent Decision and Order) that allocates responsibility for a series of data breaches. The responsibility allocation is over-determined — it rests on a list of independent, separately sufficient security failures — which makes it an ideal low-sensitivity fixture, while the document also contains a genuinely tempting off-axis hypothesis (the external attackers). It is fresh public-record material and an agency-order domain that diversifies the batch beyond NTSB/SEC/OSHA/FDA.

## Why the ACH sensitivity target is low
The complaint locates responsibility in Respondents' failure to provide reasonable security (e1) and then enumerates seven independent failures in Paragraph 27 — password controls, patching, monitoring/logging, access controls, firewall controls, network segmentation, and multifactor authentication — each separately sufficient to support the unreasonable-security finding. The deception count (e9) is an additional independent basis, and the post-acquisition responsibility row (e6) plus the Third Breach on Marriott's own network (e7) independently fix responsibility on Marriott. Because the read is supported by so many independent rows, no single-row removal materially changes it. There are no sensitivity rows.

## The off-axis and wrong hypotheses
- Off-axis (h2): external malicious actors. The intrusions were unquestionably carried out by attackers (e8), and a reader could call that "the explanation." But the complaint locates responsibility in the firm's failure to defend against foreseeable intrusions, not in the existence of attackers. This is the batch's off-axis hypothesis for this fixture.
- Plausible but wrong (h3): the inherited-Starwood-legacy reading. Tempting because the First and Second Breaches originated in Starwood's systems before Marriott's acquisition. It is foreclosed by e6 (Marriott took control and became responsible for both companies' security) and e7 (the Third Breach occurred on Marriott's own network).

## Direct / partial / off-axis rows
- Direct to h1 (unreasonable security): e1 (umbrella), e2 (passwords), e3 (patching), e4 (monitoring/logging), e5 (MFA), e9 (deception count).
- Direct responsibility-allocation rows defeating h3: e6 (post-acquisition responsibility), e7 (Third Breach on Marriott's network).
- Off-axis to h2: e8 (external attackers exploited vulnerabilities).

## Double-edged rows
- e4 (failure to monitor/log) is double-edged in a useful way: it both supports h1 and undercuts h2, since the years-long failure to detect the Second Breach is attributable to the firm's own monitoring gap rather than to attacker sophistication.
- e8 (attackers exploited vulnerabilities) names the proximate cause of the intrusions (h2) but, in context, the "vulnerabilities" are the very failures enumerated in Paragraph 27, so the row ultimately reinforces h1.

## Extraction quirks
- The Paragraph 27 failures are a lettered sub-list (a-g); the text_anchors quote the lead clause of individual sub-items, which appear verbatim in source.md.
- The complaint quotes two privacy-policy passages with internal quotation marks ("firewalls," "guaranteed security"); anchors avoid spanning those embedded quotes.
- Three distinct breaches with overlapping date ranges (First: from June 2014; Second: from July 28, 2014, detected Sept 7, 2018; Third: Sept 2018-Dec 2018 and Jan-Feb 2020) are easy to conflate; section coordinates separate them.
- The document is the complaint that accompanies the finalized Decision and Order (Docket C-4807, Dec. 20, 2024); it is the findings-bearing instrument, which is why it is used here rather than the press release or the order's injunctive terms.
