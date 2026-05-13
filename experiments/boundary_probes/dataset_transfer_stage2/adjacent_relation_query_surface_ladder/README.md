# Adjacent Relation Query Surface Ladder

Purpose: isolate query-surface misses where the compiled KB contains the
answer-bearing fact, but the question wording tempts the planner to retrieve a
nearby relation such as possession, return context, or membership instead.

Forbidden fix: do not add selectors, helpers, predicates, or prompts for this
packet's names, teams, offices, objects, or answer strings. A useful repair must
be a generic query-planning principle for complementary phrasing:

- in addition to;
- besides;
- along with;
- not only but also;
- neighboring relation versus answer-bearing relation.

