# Narrative Transfer Datasets

This directory holds narrative and literary probes that do not belong in the
real-world transfer corpus.

Use these fixtures to test source-bounded narrative reasoning: aliases,
testimony, event order, causality, narrator limits, invented-in-document claims,
and retrospective explanation.

## Main Lens

The first research lens is source-bounded prior containment. Some prose is
famous, public, quoted, summarized, or otherwise likely to be partly present in
model training. That does not make it useless. It creates a different product
question:

```text
When the model may already know the text, does Prethinker still compile and
answer from the provided source, or does it leak remembered plot, entities,
locations, motives, or resolutions into the local knowledge base?
```

This matters for real product use too. Public lawsuits, regulations, incident
reports, annual reports, standards, clinical guidelines, and news-covered events
may all be partially known to an LLM before the user supplies the document.

Good narrative probes should therefore pressure:

- source-local aliases and identity resolution
- who knew what at each point in the text
- narrator limits and retrospective explanation
- invented-in-document entities and false claims
- chronology before the final explanation is revealed
- whether answers cite compiled source evidence rather than cultural memory

Do not mix these scores into native-corpus or real-world-transfer claims. Famous
public-domain works may be partially known to the model, so they are useful
mechanism probes rather than clean unseen evidence.
