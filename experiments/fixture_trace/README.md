# Fixture Trace Experiment

This experiment is a sidecar viewer for inspecting one fixture as it moves
through Prethinker-style stages: source packet, compile passes, admission,
package artifacts, QA replay, and judge outcome.

The current specimen uses the contrast `black_lantern_maze` artifact run:

- source words: `2153`
- source transcript sections: `18`
- QA rows shown: `40 / 40`
- model decisions include: `answer`, `clarify`, `mixed`, `quarantine`
- judge result: `27 exact / 7 partial / 6 miss`

Open:

```text
experiments/fixture_trace/index.html
```

Regenerate the self-contained HTML after editing `trace_events.json`:

```powershell
python experiments/fixture_trace/build_trace_from_artifacts.py
python experiments/fixture_trace/render_fixture_trace.py
```

The current viewer is artifact-backed, but still sidecar-rendered. It reads a
compile JSON and QA JSON, converts them into a progressive trace event log, then
embeds that event log into the HTML viewer.

Python surface area:

- `build_trace_from_artifacts.py` converts compile/QA JSON into
  `trace_events.json`.
- `render_fixture_trace.py` embeds `trace_events.json` into
  `index.template.html`.
- Neither script imports or mutates the harness.

Design rule:

```text
summary first -> decision evidence -> raw machinery only on request
```
