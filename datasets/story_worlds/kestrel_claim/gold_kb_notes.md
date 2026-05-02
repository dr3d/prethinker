# The Kestrel Claim — Strategy Notes

## Why This Is Harder Than Iron Harbor and Blackthorn

### Iron Harbor was: rules + events + violations
### Blackthorn was: procedural state + deadlines + epistemic evolution
### Kestrel is: competing accounts + layered financial arithmetic + contractual interpretation + dual-role entities + regulatory multi-jurisdiction

The fundamental difficulty of Kestrel is that there is no single authoritative
account of what happened, what it costs, or what it means. Almost every fact
in the document has at least two versions, and the system must preserve both
without resolving the dispute.

### Specific harder-than-previous elements:

**1. Competing survey reports with irreconcilable measurements.**
The owner's surveyor says 3.2 meters of fracture. The underwriter's surveyor
says 2.8 meters. Both explain their methodology. Both are defensible. The
system MUST preserve both measurements attributed to their respective sources,
and MUST NOT pick one as "the" measurement. Additionally, the underwriter's
surveyor found No. 3 tank damage that the owner's surveyor did not report at
all. The system must track what each surveyor saw and did not see.

**2. Layered financial arithmetic with multiple calculation chains.**
The H&M claim has a claimant figure (USD 1,009,000), an underwriter-adjusted
figure (USD 720,000), a deductible (USD 250,000), two net figures (USD 759,000
and USD 470,000), a per-underwriter share calculation (45% × net), a
reinsurance attachment-point comparison, and items in dispute with specific
amounts and reasons. The system needs to handle these as queryable facts with
arithmetic relationships, not just as prose.

**3. Dual-role entity.**
Harbour Mutual is simultaneously an H&M following underwriter (25% line) AND
the P&I club insurer. These are separate contracts with separate terms,
separate notification requirements, and separate deductibles. The system must
track Harbour Mutual's position in both roles without confusing them. This is
not a person with two titles — it is one entity operating under two different
contractual frameworks on the same loss.

**4. Cover suspension with a precise window.**
The Classification Clause suspends cover from October 15 08:00 UTC to
October 28 16:00 UTC — exactly 13 days and 8 hours. Costs incurred during
this window have disputed coverage status. The system must track the
suspension window as temporal facts and reason about which costs fall inside
vs. outside it.

**5. Reinsurance layer arithmetic.**
The reinsurance structure has attachment points, limits, and share calculations
that determine whether a layer is triggered. The 72-hour notice provision
adds a temporal compliance check on top of the financial arithmetic. The
late-notification question is moot for this specific loss (Oceanic's share
is below the attachment point) but becomes relevant if additional claims push
the total above the threshold. The system must track both the current
arithmetic and the conditional future scenario.

**6. Salvage as a separate legal proceeding.**
The LOF 2020 salvage contract is a distinct legal instrument with its own
arbitration. The salvage security (USD 4,500,000) is a guarantee, not a
payment, and the actual award will be determined later. The system must
distinguish between posted security and actual liability.

**7. The sanctions non-breach.**
The Cotonou bunker call was planned, then canceled before it occurred, and
Oceanic has explicitly stated it will not raise the trading warranty defense.
But the system must preserve the entire chain: the original instruction, the
cancellation, the reason for cancellation (OFAC SDN list), Oceanic's decision
not to raise the defense, and Wavecrest's argument for why the defense would
fail even if raised. This is a resolved non-issue that nonetheless contains
real legal reasoning the system must not discard.

**8. Multi-jurisdiction regulatory correspondence.**
Togo (DAM), Panama (flag state), and Lloyd's (arbitration) are all involved,
each with different authority. Panama's preliminary finding is favorable to
the vessel. DAM adds a prospective recommendation that is explicitly not
retroactive. The system must track which body said what, with what authority,
and whether any finding is retroactive or prospective.

**9. Multilingual witness statements in four languages.**
Russian (Master), Greek (Chief Engineer), French (duty manager), plus English
for the surveyors and lawyers. Each statement carries substantive technical
content that must be extracted accurately.

**10. The navigation dispute is unresolved.**
Ashworth raises the depth-contour margin issue. The owner says navigation was
prudent. Panama says no fault. DAM says recommendation is not retroactive.
Oceanic reserves the defense without invoking it. The system must preserve
all five positions without resolving them.

**11. Loss of hire as a coverage interpretation question.**
The loss of hire claim is not about what happened — both sides agree on the
off-hire period. It is about whether loss of hire is covered under the
H&M policy absent a specific LOH clause. This is a legal interpretation
question, not a factual question, and the system must preserve both positions
(covered as consequential loss vs. excluded under Clause 23.4) without
deciding the issue.

**12. Temporal corrections that affect the incident narrative.**
Correction 1 changes the grounding time from 03:22 to 03:17 UTC. This
affects the notification timeline (how quickly was Meridian notified?) and
all downstream timing calculations. The system must retract the old time,
assert the new time, and propagate the change through temporal ordering.

**13. Measurement corrections that don't change the conclusion.**
Correction 2 changes a measurement from 15mm to 8mm and notes that 8mm is
within class tolerance. This means the correction changes the fact AND its
significance simultaneously. The system must track both the corrected
measurement and the interpretive note that the corrected value is within
tolerance.

**14. Case law citations as authority claims.**
Wavecrest cites *The Bamburi* and *The Star Sea*. These are legal authority
claims — the system must record them as citations supporting a party's
argument, not as facts about the case itself. A citation is not an
endorsement and not a finding.

## How The Reference KB Was Generated

### Step 1: Entity identification
Every entity was catalogued: vessel, persons, companies, syndicates,
committees, policies, clauses, reinsurance layers, survey reports, claims,
regulatory bodies, legal proceedings, case citations.

### Step 2: Predicate families with source attribution
Because almost every fact in this document has competing versions, many
predicate families need a source argument: `survey_finding(surveyor, item,
value)` rather than `finding(item, value)`. The source is not optional
metadata — it is part of the fact's identity, because the same item has
different values from different sources.

### Step 3: Financial predicates with calculation chains
Financial facts are stored as individual amounts with category and basis
labels. The calculation chain (gross claim → deductible → net → share →
reinsurance threshold) is stored as a series of related predicates that can
be queried and verified, not as a single computed result.

### Step 4: Temporal facts with correction provenance
Timestamps are ISO 8601. Corrections generate retract-old/assert-new pairs
with the corrected value clearly marked as superseding the original. Temporal
ordering facts feed the temporal kernel.

### Step 5: Disputed facts stored as parallel claims
Where surveyors disagree (fracture length, No. 3 tank damage, repair cost),
both versions are stored as source-attributed claims. The system does not
resolve the dispute. Where legal positions differ (loss of hire coverage,
navigation prudence, cost allocation during suspension), both positions are
stored as party claims with citation support where provided.

### Step 6: Policy rules as executable Prolog
The Classification Clause, Trading Warranty, deductible application,
reinsurance attachment-point calculation, and notification requirements are
encoded as Prolog rules that can be queried against the admitted facts.

### Step 7: Validation against the QA battery
Every question was checked against the reference KB to ensure the answer is
derivable from the stored facts and rules.

## Failure Modes Targeted

| Failure mode | Where it appears | Difficulty vs previous |
|---|---|---|
| Competing factual accounts | Survey reports (fracture length, No. 3 tank, repair cost) | NEW — neither previous fixture had irreconcilable measurements |
| Dual-role entity | Harbour Mutual as H&M insurer AND P&I club | NEW — entity tracking with role-context switching |
| Financial arithmetic chains | Claim → deductible → net → share → reinsurance threshold | HARDER — multi-layer calculation, not just single amounts |
| Cover suspension window | Oct 15 08:00 to Oct 28 16:00, 13 days 8 hours | HARDER — precise UTC timestamps, cost allocation disputes |
| Temporal correction propagation | Grounding time 03:22 → 03:17 | SIMILAR to Iron Harbor but affects more downstream facts |
| Measurement correction with interpretive note | No. 3 tank 15mm → 8mm (within tolerance) | NEW — correction changes both fact and significance |
| Non-breach with full reasoning chain | Cotonou sanctions issue, resolved but preserved | NEW — a decided non-issue with real legal reasoning |
| Multi-jurisdiction authority | Togo DAM, Panama flag state, Lloyd's arbitration, BV class | HARDER — four bodies with different scopes and powers |
| Legal citation as authority claim | *The Bamburi*, *The Star Sea*, Insurance Act 2015 | NEW — citations supporting arguments, not facts |
| Unresolved multi-party dispute | Navigation prudence — five competing positions | HARDER — more positions, no resolution |
| Coverage interpretation question | Loss of hire — legal question, not factual | NEW — the dispute is about contract meaning, not events |
| Security vs payment distinction | Salvage security USD 4.5M posted, not paid | NEW — financial status distinction |
| Multilingual technical content | Russian, Greek, French, English | SIMILAR difficulty, different languages |
| Reinsurance conditionality | Late notice moot now, relevant if future claims push total up | NEW — conditional future relevance |
| Claim/fact separation | Survey findings as expert opinions, not established facts | SIMILAR but with source-attributed competing versions |
