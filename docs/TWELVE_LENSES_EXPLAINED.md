# The Twelve Lenses

*What each meaning facet of Prethinker reads, and how it differs from the others.*

Prethinker reads a document through multiple semantic lenses. Each lens is an
LLM-driven reading strategy focused on one layer of meaning. The same document
can be read several ways, and each reading proposes predicates that the mapper
either admits to the knowledge base or rejects.

This page is the plain-language explainer for the twelve reader/control lenses.
The deeper lab roster also tracks **archival row ledger** as a thirteenth
addressability facet: it preserves exact row labels, docket IDs, exhibit IDs,
table rows, source names, and other document coordinates. That ledger is
architecturally important, but it is closer to a durable addressability
substrate than to a general reading strategy, so this explainer keeps it
separate.

## 1. Source Surface

Reads the document for the raw substance: entities, dates, quantities, rules,
corrections, exceptions, and claims. This is the "what is in this document"
lens. If a contract names a party, sets a date, or specifies a quantity, source
surface proposes a predicate for it.

What makes it distinct: every other reader lens reads about a document layer.
This one reads the document's basic content.

## 2. Operational Record

Reads for lifecycle states: permit applications moving through review, dockets
opening and closing, orders being issued and reversed, applications submitted
then accepted, decisions made and rescinded. Operational record proposes
predicates about what happened, in what order, and to which artifact.

What makes it distinct: source surface captures what entities and claims exist.
Operational record captures what happened to them over time.

## 3. Rule Composition

Reads for rules and their interactions: thresholds, eligibility criteria,
exception clauses, precedence between rules, activation conditions, and what
disables what. If a policy says applicants over 65 qualify except where
household income exceeds a threshold, rule composition proposes the rule, the
exception, and the threshold structure.

What makes it distinct: rule composition cares about how rules compose, not
what status any specific entity currently has.

## 4. Temporal Status

Reads for what was true when: status-at-date, deadline arithmetic, effective
dates, expiration, intervals, and supersession by time. It asks: given this
document, what was the state of X on date Y?

What makes it distinct: operational record sequences events. Temporal status
answers snapshot questions.

## 5. Authority

Reads for who controls the answer when sources disagree. If three documents
make conflicting claims about who holds title to a property, authority is the
lens that decides which document, speaker, office, correction, rule, or finding
the architecture should treat as governing.

What makes it distinct: other lenses read claims. Authority reads whose claims
win.

## 6. Evidence Provenance

Reads for the chain of custody around claims: who prepared a document, who
presented it, when, in what context, whether it was dated or admitted into the
record, and where it is physically or procedurally located. It tracks metadata
about evidence, not merely the content that evidence asserts.

What makes it distinct: authority decides which claims govern. Evidence
provenance tracks where each claim came from.

## 7. Epistemic Uncertainty

Reads for the confidence shape of claims: unknown, pending, disputed,
retracted, superseded, alleged, hedged, unsupported, provisional, and resolved
negative. If a witness says "I believe but cannot confirm," epistemic
uncertainty captures the hedge instead of collapsing it into a flat assertion.

What makes it distinct: this lens protects "X is alleged" from becoming "X."
Other lenses propose facts or claims. This one proposes the modal envelope
around them.

## 8. Entity And Role

Reads for identity and role transitions: aliases, custody chains, ownership
transfers, role changes, membership changes, and identification of the same
entity under different names.

What makes it distinct: source surface captures entities. Entity and role
tracks how those entities relate, change names, move roles, or pass between
holders.

## 9. Query Surface

Reads what kind of question the architecture is being asked. This runs at query
time. If a question asks who held title on March 15, query surface routes toward
authority and temporal predicates rather than free-form prose retrieval.

What makes it distinct: document lenses propose what is in the document. Query
surface proposes what to ask of the compiled state.

## 10. Selector Surface

Reads which compile artifact or evidence surface answers a question best. When
multiple lenses have produced different views of the same document, the selector
decides which view's predicates the planner should trust for this row.

What makes it distinct: query surface decides what predicate to ask for.
Selector surface decides which admitted evidence surface should answer.

## 11. Answer Surface

Reads how the answer should be presented: concise, hedged, refused, or marked
as insufficiently supported. If the KB has the relevant predicates, answer
surface proposes the direct answer. If support is incomplete, it proposes a
hedged answer or refusal with the reason.

What makes it distinct: selector surface routes the query. Answer surface
formats what comes back.

## 12. Struggle Detection

Reads whether further compile passes would add unique surface or just repeat
existing work. It tracks saturation, redundancy, and diminishing returns so the
architecture can stop or continue with a named expected contribution.

What makes it distinct: this is the lens that watches the other lenses. It
produces a meta-signal about when to keep reading and when to stop.

## How The Lenses Work Together

A document compile typically runs several reader lenses in sequence:

- **Source surface** captures the raw material.
- **Operational record** sequences the events.
- **Rule composition** captures the rule logic.
- **Temporal status** captures snapshot states.
- **Authority** captures who governs.
- **Evidence provenance** captures who said it and where it came from.
- **Epistemic uncertainty** captures the modal envelope.
- **Entity and role** captures identity, membership, custody, and role changes.

Each lens proposes predicates. The mapper admits what fits. The KB ends up with
a multi-layered representation where the same entity can have facts about its
operational state, authority, evidence, and uncertainty.

The remaining four lenses - **query surface**, **selector surface**, **answer
surface**, and **struggle detection** - operate at query time or as
meta-controls. They shape how the compiled KB gets used and how the compile
cycle decides when to stop.

The key architectural commitment: no single lens has to do everything. Each
lens has a narrow job. The mapper enforces contracts. The resulting KB is
durable, inspectable, and queryable in ways no single reading pass could produce
alone.

For the deeper calibration roster, including archival row ledger, see
[Semantic Lens Roster](https://github.com/dr3d/prethinker/blob/main/docs/SEMANTIC_LENS_ROSTER.md).
