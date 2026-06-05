# Current Domain Atom-Library Query Packet

This query micro-fixture measures atom-library query planning over retained
typed single-run compile artifacts from the current standing domain-pack
manifest.

It is not a compile-recall score and it is not messy human QA. The packet asks
carrier-shaped questions over atoms present in the named single-run artifact.
It should not use support>=2 multi-run oracle rows as reference answers unless
those rows are also present in the specific run JSON. Query planning may see the
compiled atom inventory and the question, but not source prose.

Claim boundary:

- planner proposes typed queries over emitted atoms;
- deterministic execution answers or fails;
- source-display questions are out of scope unless a typed display carrier is
  declared in the manifest;
- unsupported compile rows should not be counted as query failures for this
  packet.
