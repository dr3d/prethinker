# Dense Answer-Bearing Complement Ladder

This probe extends `answer_bearing_complement_ladder` with nearby distractor
facts. It tests whether compile keeps the requested complement distinct when
the source also contains adjacent names, categories, purposes, relations, and
exception clauses.

The target is density, not domain vocabulary:

- official name versus event name
- definition descriptor versus installation/location descriptor
- purpose clause versus adjacent measurement clause
- start label versus planning and closure labels
- relation target versus contrast target
- component list versus separate goals or sections
- generic category versus narrower subtype

No repair should be made from this probe unless the failure is phrased at this
general level.
