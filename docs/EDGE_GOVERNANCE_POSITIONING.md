# Prethinker as Edge-Class Governance Architecture

*A strategic positioning document for Prethinker Labs*

Last updated: 2026-05-09
Audience: Architecture Codex, Benchmark Sr Dev, Scott, future collaborators
Status: Strategic positioning, not benchmark methodology specification

Read with:

- [Project Horizon](https://github.com/dr3d/prethinker/blob/main/docs/PROJECT_HORIZON.md)
- [Benchmark Publication Plan](https://github.com/dr3d/prethinker/blob/main/docs/BENCHMARK_PUBLICATION_PLAN.md)
- [Two-Axis Benchmark Frame](https://github.com/dr3d/prethinker/blob/main/docs/TWO_AXIS_BENCHMARK_FRAME.md)
- [Two-Axis Probe Discipline](https://github.com/dr3d/prethinker/blob/main/docs/TWO_AXIS_PROBE_DISCIPLINE.md)

---

## What this document is and is not

This is **strategic positioning** for Prethinker Labs. It articulates where Prethinker sits in the AI landscape, what category it occupies, and what claims should and should not be made about it.

It is not benchmark methodology. The methodology specification lives in
`BENCHMARK_PUBLICATION_PLAN.md`; the two-axis documents are the active research
frame and probe discipline for cheap Axis 2 feel-outs.

It is not a product roadmap. Specific products, timelines, and resource allocations are downstream decisions.

It is not a publication. The eventual benchmark publication will use this positioning as context, but the publication itself reports data, not strategic frame.

The document exists to align the team (Architecture Codex, Benchmark Sr Dev, Scott, and future collaborators) on what story Prethinker should be telling and what claims should be defensible.

---

## The core architectural claim

> **Governance comes from the architecture, not the model.**

That sentence is the cleanest bridge between Prethinker's research, product, and benchmark strategy. The mapper, compiled KB, selector, and helpers are what make the system governed. The underlying model proposes; the architecture decides what survives.

This single property has cascading implications: the architecture should be largely model-agnostic, the moat shouldn't depend on having the largest model available, and the differentiator at smaller scales should grow rather than shrink.

That last claim, graceful degradation across model sizes, is a hypothesis worth testing, not a result yet proven. Naming it explicitly as something we still need to measure is part of the discipline of this document.

---

## What today's data actually showed

The first frontier comparison pilot ran **10 fixtures, 370 rows, 3 runs per row** against three frontier models:

- `anthropic/claude-opus-4.7`
- `openai/gpt-5.5`
- `google/gemini-3.1-pro-preview`

Frontier models scored high on direct single-document QA. The architecture readout described it as *"frontier direct scores are very high on this pilot, especially Claude and GPT on the precision batch."*

This means **frontier models are very capable at direct single-document answer quality.** The original benchmark framing of "Prethinker beats frontier LLMs on hard documents" is contestable on these specific fixtures at this specific test condition.

What hasn't been measured yet:

- How frontier LLMs handle multi-document context (axis 2)
- Whether their answer quality survives interference, dilution, and reordering
- How they perform without their full context window available
- Whether they can produce durable, queryable provenance across a session

Those are the conditions where Prethinker's architecture is structurally different from frontier chat systems, and where the empirical work is still pending.

---

## The reframe

**Prethinker isn't competing with frontier models on capability. It's competing on a different axis where frontier chat systems do not natively provide the same properties.**

Frontier chat systems excel at single-document direct QA when given full attention. They could in principle support persistent governed memory if wrapped in application architecture, but they don't ship that property natively. Their default mode is stateless cloud inference with context windows that reset between sessions.

Prethinker's architectural commitments produce three properties that frontier chat systems don't natively offer:

1. **Persistent governed memory** - compiled KBs that live on disk, queryable across sessions, with structural provenance
2. **Edge-class hardware compatibility** - works with moderate models on consumer hardware
3. **Hypothesized graceful degradation across model sizes** - governance comes from the architecture, so the underlying model is replaceable. This is a research hypothesis to be tested, not a proven result.

These three together describe a product category that frontier chat systems don't currently occupy. Frontier-lab developers could build something like Prethinker as a layer over their models. They're not currently doing it because their incentives push toward cloud chat, not edge knowledge systems.

---

## What changes vs what stays the same

| Property | Frontier chat system | Prethinker |
|---|---|---|
| Per-document direct answer quality | Excellent | Good (depends on underlying model) |
| Persistent governed memory across sessions | Not natively provided | Permanent (compiled KBs) |
| Multi-document recall under stuffed context | Token-context decay expected | No token-context decay after compilation, but retrieval/helper/selector/KB-scale effects still need testing |
| Provenance | Generated per-answer, varies by session | Durable, queryable, structurally tracked |
| Cost per query | High (frontier inference per call) | Lower (KB lookup plus moderate inference) |
| Hardware requirement | Cloud or expensive GPU | Consumer-class hardware (5090, M-series Macs, eventually NPU laptops) |
| Privacy | Cloud round-trip | Fully local possible |
| Offline operation | Not supported | Default |
| Behavior at small model sizes | Quality degrades, hallucination grows | Hypothesis: governance preserved with reduced compile coverage; needs measurement |

This isn't "Prethinker beats frontier LLMs." It's "Prethinker and frontier chat systems are optimized for different use cases, with measurable architectural differences in what each is structurally suited for."

---

## What governs vs what proposes

The architectural insight Prethinker captures is that *governance and capability can be decoupled*.

The mapper does validation work. The compiled KB does durability work. The selector does routing work. The model does proposal work. The model just has to propose plausibly; the architecture decides what becomes truth.

This implies that as the underlying model shrinks, the architecture's role grows in importance. A 7B model might propose more flawed candidates than a 70B model, but the mapper rejects ungrounded proposals regardless of source. The output is governed either way; the proposal admission rate just decreases.

**Whether this graceful degradation actually holds is empirically open.** It's the central hypothesis of the edge-class positioning, and it needs explicit measurement. We name it as a hypothesis here rather than asserting it as fact.

---

## The hardware angle

The hardware story matters more than it looks at first glance.

**Today, on a 5090:** Qwen 35B running locally produces research-grade Prethinker outputs. The OpenRouter migration confirmed that cold-compile and operational portability hold for the same model on cloud infrastructure. Repair-stack and lens output can still drift by provider - the seismic test work this week showed lens output varies measurably across infrastructures even with the same model name. Operational portability is proven; bit-equivalent output is not.

**Today, on a 16GB consumer GPU:** 7-13B models can technically drive Prethinker. The architectural claim is that governance discipline holds regardless of underlying model size, but the actual quality and governance curve at 7-13B scale is unmeasured. This is a research question, not a current capability claim.

**Today, on Apple Silicon with unified memory:** M3/M4 Macs run 30B+ models efficiently. Not specialty hardware, consumer laptops.

**Coming over 2026-2027:** Intel and AMD NPUs in standard laptops; ARM-based mobile inference for moderate models. Edge inference for moderate-size models becomes default rather than specialty.

**The trajectory:** edge-class inference is becoming a commodity capability. The bottleneck for trustworthy edge knowledge work isn't inference; it's governance. Prethinker's architectural insight applies precisely at this moment: when raw inference is cheap and ubiquitous, the differentiator becomes whether the system preserves meaning rather than fabricating it.

---

## The persistent memory differentiator

Frontier chat systems have huge attention budgets per call but no persistent KB across sessions or documents by default. Prethinker on edge hardware has modest attention budget per call but persistent KBs through compiled state that lives on disk.

A user with Prethinker on their laptop could:

- Compile their document corpus once, over a few days
- Query it across sessions at query-time cost only
- Add new documents incrementally as they arrive
- Get governed answers with structural provenance
- Operate fully offline if desired
- Keep all data on their own machine

That's a personal knowledge system, not a chat session.

**The compiled KB has no token-context decay.** The meaning isn't sitting in attention. But the system still has potential decay points: query planning, selector choice, schema drift over time, conflicting KBs, large-KB scale effects on selector behavior. The 12-point gap between selector at 77.5% and available ceiling at 89.6% on today's data is precisely this kind of system-level degradation, even though the compiled state itself isn't decaying.

The honest claim: **token-attention decay disappears after compilation, but other system-level degradation remains and needs continued architectural work.**

---

## Product implications

The legal benchmark / consumer product story sharpens significantly under this positioning.

The original framing was "Prethinker beats ChatGPT/Claude/Gemini on legal documents."

The deeper version is **"Prethinker turns your laptop into a personal legal memory that frontier chat systems do not natively provide."**

That's not a feature comparison. It's a different product category.

### Use cases that snap into focus

**Personal document assistant.** Compile your contracts, leases, medical records, tax documents. Query across sessions with privacy. Frontier chat systems don't natively provide persistent governed KBs across sessions.

**Personal medical chart.** Track medications, allergies, conditions, procedures across decades in your own queryable KB. Add records as they arrive. Cross-reference everything with structural provenance.

**Lawyer's research assistant.** Compile case files, statutes, contracts. Query by structural relationships. Run entirely on the lawyer's machine, satisfying client confidentiality requirements.

**Researcher's knowledge base.** Compile papers, notes, drafts. Query across the corpus with provenance. Add new material incrementally.

**Field assistant for trades.** Plumber, electrician, contractor compiles reference material, code books, manufacturer specifications. Query at the job site, offline.

**Personal accountability partner.** Compile journal entries, emails, plans. Query later for accurate retrieval. Memory you can trust against your own selective recall.

**Compliance officer's contract review.** Compile internal contracts, regulatory documents. Local processing satisfies data residency requirements.

**Estate or inheritance management.** Compile wills, deeds, family records, financial documents. Stays on the family's machine.

Each of these requires *persistent governed memory* and is poorly served by stateless cloud chat. Each is a real category of work currently done badly with general-purpose tools or expensively with specialist software.

---

## Architectural identity

Prethinker is an **adapter pattern for turning capable LLMs (including small ones) into governed-memory knowledge systems**.

The lens, the mapper, the selector, the helpers all work whether the underlying model is Qwen 35B, Llama 13B, or a future small model. Today's OpenRouter migration proved cross-infrastructure portability for the same model at the cold-compile and operational layers. The next test is cross-model-size portability: does the architecture hold its value as the model shrinks?

The hypothesis: yes, with measurable reduction in compile coverage but preserved governance properties. **This is research lane work, not yet proven.** It belongs on the experimental roadmap as a named research direction.

If that hypothesis holds empirically, Prethinker becomes a piece of consumer infrastructure: a way to make any local LLM trustworthy enough for real knowledge work.

---

## Three-dimensional benchmark frame

The benchmark publication strategy works best as three dimensions, not two:

```
Axis 1: compile-time fidelity
  What structure gets admitted correctly from one document.

Axis 2: retention durability
  What structure remains recoverable when context is stuffed,
  reordered, interfered with, or diluted.

System class: frontier cloud / edge governed / edge ungoverned
  What category of system is being tested.
```

A complete benchmark publication reports all three classes against both axes. Each system class has different patterns:

- **Frontier cloud**: high axis 1 under optimal conditions, axis 2 expected to degrade under stuffed context
- **Edge governed (Prethinker)**: moderate axis 1 (depends on underlying model), strong axis 2 expected
- **Edge ungoverned**: variable axis 1 (depends on model), weak axis 2 expected

The publication framing becomes: **"Comparing three system classes on two axes of meaning preservation."** That's a paper, neutral about which class wins where because the data tells you. It positions Prethinker honestly: hypothesized to be strongest on retention durability, competitive on compile-time fidelity, optimized for edge deployment, not designed for frontier chat use cases.

---

## Evidence priorities for the framework

The four next experiments needed:

**1. Axis-2 stuffed-context probe.** Single fixture (`contradictory_evidence_packet`) standalone vs stuffed inside other fixtures. Measure per-category degradation. Cheap feel-outs are already running on the benchmark side; promote this into methodology only after the probe produces structured evidence. Low cost. High information value.

**2. Small-model Prethinker degradation curve.** Run Prethinker with progressively smaller underlying models (Qwen 35B to Llama 13B to Llama 7B). Measure compile coverage and admitted-fact governance properties. This tests the graceful-degradation hypothesis directly.

**3. Edge ungoverned baseline.** Run small models without Prethinker's governance layer on the same fixtures. Measures what governance actually adds at small model scales. This is the third leg of the comparison stool for the three-system-class benchmark.

**4. Persistent-memory demo.** Build a working artifact where someone can see what persistent governed memory feels like to use. Query cost visible. Provenance visible. Cross-session continuity visible. Not abstract claims, concrete artifact for product launch material.

Each experiment generates publishable data. Together they form the empirical foundation for the edge-class governance positioning.

---

## What this changes for current work

### For Architecture Codex

Today's direction toward "the part of Prethinker that does compiling into perfect memory" aligns with this strategic frame. Strengthening compile-time durability strengthens the moat that frontier chat systems don't currently occupy.

The new pre-compile ledger category (deterministic source addressability) is moat-strengthening: structural memory that needs no LLM interpretation. Every category of deterministic structure preserved at compile time is durable advantage.

The strategic priority shifts subtly: not just "improve scores," but "improve durable structural state." Both matter, but durable structural state is the part that defines Prethinker's category.

### For Benchmark Sr Dev

The benchmark publication strategy expands from two-axis to three-system-class.

The planned probe on `contradictory_evidence_packet` stuffed-context still applies. Add to the roadmap: at some point, run the same fixtures with smaller models driving Prethinker, to populate the system-class dimension. The minimum-viable-extension discipline still applies: same scorer, same oracle, same harness, just different context-assembly recipes and different underlying models.

### For product work

The legal benchmark and consumer product was already aligned with this direction. The strategic frame just makes the positioning sharper.

The product story isn't "Prethinker is better at legal documents than ChatGPT." That's contestable. The product story is **"Prethinker is the way to get trustworthy answers about your legal documents that stay on your machine, work offline, and remember everything you've shown them."** Frontier chat systems don't natively provide this, by architectural choice and product positioning, not by capability limit.

### For research direction

Small-model Prethinker is now a named research lane, not a vague aspiration. The experimental program described in evidence priority 2 belongs on the research roadmap as a real planned experiment.

This is publishable research independent of benchmark methodology. *"Edge-class governed reasoning vs cloud-class ungoverned reasoning"* is a real comparison nobody has measured systematically.

---

## Phrases worth preserving

> **"Governance comes from the architecture, not the model."**
> *(The keeper. The cleanest bridge between research, product, and benchmark strategy.)*

> **"Frontier models match capability. Prethinker provides governed memory. Different game."**

> **"Persistent governed memory for edge-class knowledge work."**

> **"Frontier chat systems do not natively provide [property X]."**
> *(Use this construction throughout instead of "frontier models can't" - it's accurate and defensible.)*

These compress real architectural properties into communicable form without overclaiming.

---

## What this document is not

It's not a product roadmap.

It's not a commitment to any specific publication timeline.

It's not a substitute for the original benchmark work. The precision fixtures still matter, the comparison work still matters.

It's not a retreat from frontier comparison. Prethinker should still be measured against frontier LLMs, both because the comparison is interesting and because patterns of difference reveal architectural properties.

It's not a claim of proven superiority on any axis. Several of its central claims (graceful degradation across model sizes, retention durability under stuffed context) are hypotheses awaiting measurement.

It's not benchmark methodology. The methodology specification lives in
`BENCHMARK_PUBLICATION_PLAN.md`; the two-axis documents describe the current
research frame and probe discipline.

---

## What this document is

A statement of where Prethinker Labs is positioned strategically, and where the real surface for product and research lives:

- Frontier capability is increasingly commoditized for direct single-document QA
- Frontier chat systems have structural defaults (cloud, stateless, no persistent KB) that don't fit edge-class knowledge work
- Edge-class hardware is becoming ubiquitous
- Edge-class governance is a real differentiator that requires architectural work, not scale
- Prethinker is positioned exactly at this intersection

The work continues unchanged. The positioning gets sharper. The product surface enlarges. Both the architecture work and the benchmark work serve this positioning.

The sentence that captures the direction:

> **Prethinker is what trustworthy knowledge work looks like on hardware that fits in your bag.**

Worth aiming there.

