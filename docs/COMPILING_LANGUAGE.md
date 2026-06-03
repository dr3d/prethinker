# Compiling Language

Last updated: 2026-05-28

> Status: historical pre-reset public explainer. The core metaphor is still
> useful, but the measurement figures below are not current claims. Current
> phase-close status lives in
> [Closed Domain Predicate Packs Technical Note](https://github.com/dr3d/prethinker/blob/main/docs/CLOSED_DOMAIN_PREDICATE_PACKS_TECHNICAL_NOTE.md)
> and
> [Current Research Headline](https://github.com/dr3d/prethinker/blob/main/docs/CURRENT_RESEARCH_HEADLINE.md).

How Prethinker treats ordinary English as compilable input and turns it into a
queryable, auditable knowledge program.

This document is the visitor-friendly mental model. It explains the idea, not
every implementation detail. For the exact current artifact contract, read
[Compiled KB Artifact Package](https://github.com/dr3d/prethinker/blob/main/docs/COMPILED_KB_ARTIFACT_PACKAGE.md).
For QA measurement, read
[QA Instrument](https://github.com/dr3d/prethinker/blob/main/docs/QA_INSTRUMENT.md).

## The Strange Idea

Most software starts with a programming language. A person writes Python,
JavaScript, Rust, SQL, or Prolog, and a machine executes it.

Prethinker starts somewhere softer and more dangerous: ordinary source
language.

English is the rhetorical case in this explainer because the contrast with
Prolog is vivid. The architecture is not meant to be English-only.

A source document might say:

> On January 12, payment failed. The approval was superseded by hold notice H-2,
> and the file returned to pending payment status.

A human can read that sentence and answer many questions:

- What happened?
- When did it happen?
- What changed?
- What superseded the approval?
- What status came after the failure?
- Is the old approval still current?

Prethinker's job is to turn English source language into a compiled KB package
that can answer those questions later. The package is Prolog-like: facts and
rules, plus ledgers, epistemic state, and query policy.

For example, a good compile might contain facts like:

```prolog
payment_failed(pr_18, date_2026_01_12).
superseded_by(approval_pr_18, hold_notice_h_2).
status_after(pr_18, pending_payment, date_2026_01_12).
```

Now a later question can be asked as a logic query:

```prolog
superseded_by(approval_pr_18, What).
```

And the program can answer:

```prolog
What = hold_notice_h_2.
```

That is the core mental shift. Prethinker is not "asking an LLM to answer from
a document." It is asking an LLM to help compile a document into durable,
inspectable state. The answer should come from the compiled artifact package,
not from the model's memory, hidden retrieval, or sampling variance.

## Current Shape

The current instrument is a two-stage discipline:

```text
source document
  -> semantic compile passes
  -> deterministic mapper admission
  -> frozen KB artifact package
  -> governed QA over admitted state
  -> audited exact / partial / miss rows
```

The LLM is still important. It proposes semantic structure, candidate
predicates, query plans, evidence bundles, and answer judgments. But it does
not get to decide what becomes durable truth. Deterministic code owns schema
validation, predicate contracts, source ledgers, Prolog execution, write
blocking, and cleanliness counters.

The current public measurement anchor is no longer the old general QA
scoreboard. Later sign-clean audits showed that some older high exact-rate
measurements depended on paths that cannot carry the technical thesis. The
current claim-bearing result is narrower: closed, lens-scoped predicate domains
can stabilize recurring official-document skeleton anatomy under strict gates.

Those current numbers are summarized in the closed-domain technical note. This
document keeps the core mental model: "compiling language" is being measured as
an instrument, not merely described as an analogy.

## Why This Is Hard

English is not a programming language in the usual sense.

It is full of compression:

```text
The approval was superseded by hold notice H-2.
```

That short sentence hides several logical commitments:

- there was an approval;
- there was a hold notice;
- the hold notice has identifier H-2;
- the hold notice came after the approval;
- the hold notice changed the status or authority of the approval;
- the approval should not be treated as the final state.

English is also full of ambiguity:

```text
The sample was received by Niko on Monday and logged as received by Ada on
Tuesday.
```

Did Niko receive the physical sample in the field? Did Ada receive it at the lab
desk? Are these two receipt events or one event described twice? A useful logic
program must not crush those differences into one vague fact.

English also reports things without making them true:

```text
The copied notice said all members could borrow the key, but the notice was
noncontrolling because it omitted the final board vote.
```

The notice made a claim. The document also says the claim was not authoritative.
A careless compiler might write:

```prolog
may_borrow_key(all_members).
```

But that would be wrong. The source did not assert that all members really may
borrow the key. It asserted that a copied notice claimed this, and that the
notice was not controlling.

A better compile would preserve the source layer:

```prolog
document_type(notice_1, copied_notice).
document_status(notice_1, noncontrolling).
document_content(notice_1, all_members_may_borrow_key).
omitted_authority(notice_1, final_board_vote).
```

That distinction is the difference between compiling language and merely
summarizing it.

## The Target: A Logic Program

Prolog is a useful target because it is built around three simple ideas.

First, a fact:

```prolog
custody_holder(glaze_room_key, marco_bell).
```

This says that, in the compiled world, Marco Bell holds custody of the glaze
room key.

Second, a rule:

```prolog
may_access(Person, Key) :-
    custody_holder(Key, Person).
```

This says a person may access a key if they are its custody holder.

Third, a query:

```prolog
custody_holder(glaze_room_key, Who).
```

This asks the program to find values for `Who` that make the statement true.

This is radically different from a natural-language answer string. A sentence
like "Marco Bell held the key" is useful to a human, but it is not directly
joinable with other facts. A fact like `custody_holder(glaze_room_key,
marco_bell).` can be joined, counted, filtered, contradicted, superseded, and
explained.

The compiled program is not just an answer. It is a machine-readable world.

## The Source Is Not The World

One of the most important ideas in Prethinker is that the source document and
the world described by the source are not the same thing.

A source can say:

```text
The draft recommendation proposed weekend checkout for all advanced students.
```

That does not mean weekend checkout was approved. It means a draft proposed it.

A careful compile might say:

```prolog
document_type(dr_5, draft_recommendation).
document_status(dr_5, draft).
document_content(dr_5, weekend_checkout_for_all_advanced_students).
pending_condition(dr_5, facilities_legal_review).
```

The document's proposal is preserved, but it is not promoted into a final
permission.

This matters because many documents contain competing layers:

- draft recommendations;
- staff notes;
- official registers;
- board votes;
- court orders;
- copied notices;
- corrected records;
- superseded entries;
- final findings.

Humans naturally track those layers. A compiler must make them explicit.

If it does not, it creates false truth. It turns "someone said X" into "X is
true." In legal, medical, scientific, administrative, or historical records,
that is catastrophic.

## The Compiler Pipeline

Prethinker's compile process can be understood as a sequence of increasingly
strict gates.

### 1. Read The Source

The input is ordinary text. The compiler first has to understand the document's
genre and purpose:

- Is this a story?
- A roster?
- A policy?
- A legal contract?
- A correction log?
- A chain-of-custody record?
- A status timeline?
- A source-authority dispute?

This matters because different genres have different answer-bearing surfaces.
A school-trip roster needs membership and attendance surfaces. A custody packet
needs authority, source, access, and control surfaces. A status docket needs
initial/current/final status surfaces.

The genre is not the answer, but it tells the compiler what kinds of facts to
watch for.

### 2. Build Or Select A Predicate Palette

Before writing facts, the compiler needs a vocabulary. Some vocabulary comes
from stable profile contracts. Some is proposed by the model and then checked.
Some is preserved as residue until it earns its place.

For a custody document, useful predicates might include:

```prolog
custody_holder(Item, Person).
access_controlled_by(Item, Person).
document_type(Document, Type).
document_status(Document, Status).
document_content(Document, Content).
supersedes(NewSource, OldSource).
```

For an operational status docket, useful predicates might include:

```prolog
record_status_at(Record, Phase, Status, Date).
record_event(Record, EventType, Actor, Date).
record_alias(Record, Alias).
superseded_by_document(OldState, Document).
resulting_status_after(Event, Status).
```

This vocabulary is the "shape" of the resulting program. A bad palette can make
the source impossible to query even if the compiler noticed all the right
sentences. This is why current Prethinker work tracks palette stability,
profile-local registry priors, and direct compile-surface delivery rather than
only final answer scores.

For example, suppose the source says:

```text
The approval was superseded by hold notice H-2, and the file returned to
pending payment status.
```

A weak palette might only emit:

```prolog
status_superseded_by(approved_subject_to_payment, pending_payment).
```

That captures the resulting status, but it loses the thing that did the
superseding: hold notice H-2.

The problem is not that the compiler failed to see the sentence. The problem is
that the palette did not preserve the right distinction.

### 3. Emit Candidate Operations

The model proposes candidate facts and rules. These are not automatically
trusted.

An operation might be:

```json
{
  "operation": "assert",
  "predicate": "custody_holder",
  "args": ["glaze_room_key", "marco_bell"],
  "source": "direct",
  "safety": "safe"
}
```

This is a proposed write into the logic program.

The word "proposed" matters. The model is allowed to suggest structure, but the
system still has to decide whether the proposal is admissible.

### 4. Admit Only Grounded Facts

Prethinker has to reject facts that are not safe to commit.

Bad:

```prolog
approved(all_student_checkout).
```

If the source only said a draft proposed all-student checkout, this fact is
overcommitted.

Better:

```prolog
document_type(dr_5, draft_recommendation).
document_content(dr_5, all_student_checkout).
document_status(dr_5, draft).
```

The deterministic mapper tries to admit facts that are:

- grounded in the source;
- shaped according to the allowed predicate palette;
- not inferred beyond what the source states;
- not using unresolved placeholders;
- not collapsing source layers;
- not turning claims into findings;
- not turning proposals into approvals.

This admission step is one reason the system behaves like a compiler rather
than a chatbot. A chatbot can answer in fluent prose and move on. A compiler
must decide what goes into the program.

### 5. Preserve Source Addressability

Even when a fact is not cleanly compiled, the source text is still preserved in
a source-record ledger.

For example:

```prolog
source_record_text_atom(src_line_0017,
    copied_studio_memo_sm_5_is_noncontrolling_because_it_copied_dr_5_and_omitted_fd_5).
source_record_label(src_line_0017, sm_5).
```

This is not a substitute for a good semantic fact, but it is valuable. It lets
the system know where evidence came from. It also lets audits ask:

- Did the source contain the answer?
- Did the compiler miss a direct surface?
- Did the selector fail to query the right predicate?
- Is the answer only present as text, not as logic?

Source addressability is the compiler's receipt trail.

### 6. Freeze The Artifact Package

The product of compilation is not just one file of facts. Conceptually, it is a
package:

```text
world.pl          admitted source state
epistemic.pl      claims, findings, corrections, uncertainty
ledgers.pl        deterministic source addressability
query_policy.json what QA may use
manifest.json     reproducibility and instrument metadata
diagnostics.json  skipped, blocked, and coverage notes
```

The source remains available for audit and recompilation, but ordinary QA is
supposed to answer from the compiled package. Admitted source-record display
rows inside `ledgers.pl` are part of that package; hidden rereading of raw
source prose outside the artifact is not. If QA can only answer by going back
to raw source prose, that is evidence that the compile did not preserve the
right answer-bearing surface yet.

### 7. Run Governed QA

Questions are compiled too, but under a different authority boundary. During QA,
the model may propose query plans or judge answer quality, but it may not write
new source truth. The harness validates query predicates and arities, executes
the admitted queries, blocks writes, and records exact/partial/miss outcomes.

That is why the cleanliness counters matter. A good answer is not enough. The
run must also say whether it depended on retired compatibility rescue, runtime
load errors, or QA-time write proposals.

## Truth Is Layered

In ordinary programming, a fact is usually just true inside the program:

```prolog
open(door_1).
```

In natural-language compilation, truth is layered.

Consider:

```text
The staff note recommended opening the door. The board rejected the note. The
final order kept the door closed.
```

A poor compile:

```prolog
open(door).
```

A better compile:

```prolog
document_type(note_1, staff_note).
document_content(note_1, recommend_open_door).
document_status(note_1, rejected).

document_type(order_1, final_order).
document_content(order_1, keep_door_closed).
document_status(order_1, controlling).
```

Now the program can answer two different questions:

```prolog
document_content(note_1, What).
```

Answer:

```prolog
What = recommend_open_door.
```

And:

```prolog
document_content(order_1, What).
```

Answer:

```prolog
What = keep_door_closed.
```

The system can say what was recommended without confusing it with what became
true.

This is one of the central disciplines of the architecture:

Do not erase epistemic status.

Claims, drafts, findings, corrections, copied notices, disputed statements, and
official records are different kinds of truth-bearing objects.

## Uncertainty Is Not Failure

Uncertainty appears in several forms.

### Missing Surface

The source says something, but the compile does not emit a queryable coordinate.

Source:

```text
The initial status was pending lab receipt.
```

Weak compile:

```prolog
final_status(ws_12, completed_below_threshold).
```

The compiler preserved the final status but missed the initial status. That is
a compile-surface gap.

### Ambiguous Layer

The source uses the same word for two different event layers.

```text
Niko received the sample in the field. Ada logged the sample as received at the
lab desk.
```

If the compile emits only:

```prolog
sample_received(ada_voss, b_12, date_2026_04_11).
```

then a question like "Who received sample B-12?" can become unstable. The
source has field receipt and lab receipt. The program needs both layers:

```prolog
field_received(niko_shah, b_12, date_2026_04_10).
lab_logged_received(ada_voss, b_12, date_2026_04_11).
```

Or a more general event representation:

```prolog
record_event(ws_12, field_receipt, niko_shah, b_12, date_2026_04_10).
record_event(ws_12, lab_receipt_log, ada_voss, b_12, date_2026_04_11).
```

### Conflicting Identity

The same thing may be called by several names:

```text
Grant queue GQ-5 tracks proposal P-5.
```

A weak compile might create both `gq_5` and `queue_gq5` without linking them.
Then one status lands on one atom and another status lands on the other.

A better compile needs an alias relation:

```prolog
record_id(gq_5).
record_alias(gq_5, queue_gq5).
record_alias(gq_5, grant_queue_gq_5).
```

Without this, the program may technically contain the right answer but fail to
find it from the user's wording.

### Source-Only Evidence

Sometimes the answer is present only in source text:

```prolog
source_record_text_atom(src_line_0012, initial_status_was_pending_lab_receipt).
```

This is useful evidence, but it is not yet a proper semantic surface. The
compiler has preserved the sentence, but not compiled the fact.

The audit can identify this case. It is a signal for future compiler repair.

## Queries Are Programs Too

Once the source has been compiled, a question becomes a query plan.

Question:

```text
Who held custody of the glaze room key?
```

Possible query:

```prolog
custody_holder(glaze_room_key, Who).
```

Question:

```text
Why was the copied memo noncontrolling?
```

Possible queries:

```prolog
document_status(sm_5, noncontrolling).
copied_from(sm_5, dr_5).
omitted_authority(sm_5, fd_5).
omitted_authority(sm_5, cf_5).
```

The query planner is not supposed to invent answers. It searches the compiled
program. If the program has the right surfaces, the answer can be assembled
from facts. If the program only has source text, the system may still find
evidence, but that is weaker. If the program lacks both, the correct answer is
"not supported by the compiled KB."

This is another important distinction:

The LLM may help write the query, but the logic program supplies the evidence.

## The Result Is Inspectable

Because the output is a program, the system can be audited.

If an answer is wrong, we can ask where the failure happened:

### Did The Source Contain The Answer?

If not, this is not a compiler failure. The source simply does not support the
answer.

### Did The Compiler Preserve The Source Text?

If yes, the source-record ledger can prove the sentence was seen.

### Did The Compiler Emit A Direct Fact?

If no, this is a compile-surface gap.

### Did The Compiler Emit A Fact Under The Wrong Shape?

If yes, this is a palette problem.

For example:

```prolog
status_superseded_by(approval, pending_payment).
```

This may be less useful than:

```prolog
superseded_by_document(approval, hold_notice_h_2).
resulting_status_after(hold_notice_h_2, pending_payment).
```

### Did The Query Ask The Wrong Predicate?

If the fact exists but the query misses it, this is a query-planning failure.

### Did Identity Split Across Atoms?

If `gq_5` and `queue_gq5` are the same record but the program does not know
that, this is an alias failure.

This auditability is the heart of the research. A normal LLM answer can be
wrong in a foggy way. A compiled KB answer can be wrong in a locatable way.

## Why Not Just Use Embeddings?

Embeddings are useful for finding relevant text. They can tell us that a
paragraph about a hold notice is probably related to a question about
supersession.

But embeddings do not by themselves say:

```prolog
superseded_by(approval_pr_18, hold_notice_h_2).
```

They do not enforce:

- which source is controlling;
- which claim is only a draft;
- which date belongs to which event;
- which status is initial versus final;
- which person performed which role;
- which object was governed by which rule.

Prethinker can still use retrieval-like machinery around the edges, but the
compiled program is the thing that makes exact, inspectable answers possible.

## A Small End-To-End Example

Source:

```text
Official key register OK-5 was filed by studio clerk Talia Wynn on 2027-03-05.
OK-5 names kiln supervisor Marco Bell as custody holder for the glaze room key.

Draft recommendation DR-5 proposed weekend glaze room checkout for all advanced
students, but it remained draft pending facilities legal review.

Facilities decision FD-5 allowed weekend checkout only to two monitor-trained
students and rejected all-student checkout.

A copied studio memo SM-5 says all advanced students may check out the glaze
room key on weekends. SM-5 is noncontrolling because it copied DR-5 before legal
review and omitted FD-5 and CF-5.
```

Compiled facts:

```prolog
document_type(ok_5, official_key_register).
filed_by(ok_5, talia_wynn, date_2027_03_05).
custody_holder(glaze_room_key, marco_bell).

document_type(dr_5, draft_recommendation).
document_status(dr_5, draft).
document_content(dr_5, weekend_checkout_for_all_advanced_students).
pending_condition(dr_5, facilities_legal_review).

document_type(fd_5, facilities_decision).
document_status(fd_5, controlling).
document_content(fd_5, weekend_checkout_only_two_monitor_trained_students).
rejected_request(fd_5, all_student_checkout).

document_type(sm_5, copied_memo).
document_status(sm_5, noncontrolling).
document_content(sm_5, all_advanced_students_may_check_out_key).
copied_from(sm_5, dr_5).
omitted_authority(sm_5, fd_5).
omitted_authority(sm_5, cf_5).
```

Now questions can be answered by querying the program.

Question:

```text
Who held custody of the glaze room key?
```

Query:

```prolog
custody_holder(glaze_room_key, Who).
```

Answer:

```text
Marco Bell.
```

Question:

```text
Did the draft recommendation approve checkout for all advanced students?
```

The program can distinguish proposed from approved:

```prolog
document_content(dr_5, weekend_checkout_for_all_advanced_students).
document_status(dr_5, draft).
```

Answer:

```text
No. DR-5 proposed checkout for all advanced students, but it remained draft.
```

Question:

```text
Why was SM-5 noncontrolling?
```

Queries:

```prolog
document_status(sm_5, noncontrolling).
copied_from(sm_5, dr_5).
omitted_authority(sm_5, fd_5).
omitted_authority(sm_5, cf_5).
```

Answer:

```text
SM-5 was noncontrolling because it copied DR-5 and omitted FD-5 and CF-5.
```

The important thing is not that the final answer is prose. The important thing
is that the prose is backed by a logic trace.

## Compilation Is A Discipline

The compiler must constantly resist tempting shortcuts.

Do not turn:

```text
The draft proposed X.
```

into:

```prolog
x_is_allowed.
```

Do not turn:

```text
The copied notice said X, but the notice was noncontrolling.
```

into:

```prolog
x.
```

Do not turn:

```text
The approval was superseded by notice H-2 and returned to pending status.
```

into only:

```prolog
status(pending).
```

Do not turn:

```text
Niko received the sample in the field. Ada logged it as received at the lab.
```

into one undifferentiated receipt event.

These are not cosmetic details. They are the difference between a program that
can reason and a pile of plausible labels.

## What Makes This Feel Like A Compiler

The analogy to a compiler is not decorative. It is structural.

Traditional compiler:

```text
source code -> parser -> intermediate representation -> optimizer/checker -> executable program
```

Prethinker:

```text
source language -> semantic passes -> candidate operations -> admission checks -> compiled KB package
```

Traditional compiler errors:

- syntax error;
- type error;
- unresolved symbol;
- unsafe operation.

Prethinker compiler errors:

- missing answer-bearing surface;
- unresolved identity alias;
- overcommitted claim;
- collapsed source layer;
- ambiguous event role;
- status phase omitted;
- query cannot reach existing fact.

Traditional compiler output:

```text
machine-executable program
```

Prethinker output:

```text
query-executable knowledge artifact
```

The result is not a summary of the document. It is a program compiled from the
document.

## The Big Picture

Natural language is full of facts, but the facts are not already arranged as a
database. They are wrapped in grammar, time, authority, uncertainty, emphasis,
source status, and human assumptions.

Prethinker tries to unwrap them carefully.

It asks:

- What entities exist?
- What events happened?
- What states changed?
- Who said what?
- Which source is controlling?
- Which source is only a draft?
- Which value was corrected?
- Which record superseded which earlier record?
- Which status is initial, current, or final?
- What is directly stated, and what is merely implied?
- What should be queryable later?

Then it writes the best-supported pieces into a logic program.

That program can answer questions because the information has been converted
from prose into relations.

The compiler is not perfect. It can miss surfaces, split identities, choose
local predicate names, or preserve evidence only as source text. But those
failures are visible. They can be audited. They can be repaired. And each repair
can be tested against new documents to see whether it is real architecture or
just memorization.

That is the journey:

```text
source sentence
    -> source-grounded claim
    -> typed relation
    -> admitted fact
    -> queryable artifact
    -> evidence-backed answer
```

The magic is not that a model "understands English."

The magic is that understanding is forced to leave a trace.

