#!/usr/bin/env python3
"""
Render human-readable ladder pages from kb_scenarios + latest kb_runs summaries.

Outputs:
- docs/rungs/index.html
- docs/rungs/<scenario_name>.html for each ladder scenario
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render human-readable test ladder pages.")
    parser.add_argument("--scenarios-dir", default="kb_scenarios", help="Directory containing scenario JSON files.")
    parser.add_argument("--runs-dir", default="kb_runs", help="Directory containing run JSON reports.")
    parser.add_argument("--output-dir", default="docs/rungs", help="Directory for rung HTML pages.")
    parser.add_argument("--title", default="Test Ladder", help="Top-level title for ladder index.")
    return parser.parse_args()


def _resolve(path_text: str) -> Path:
    raw = Path(path_text)
    if raw.is_absolute():
        return raw.resolve()
    return (ROOT / raw).resolve()


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    if isinstance(parsed, dict):
        return parsed
    return None


def _scenario_sort_key(path: Path) -> tuple[int, int, str]:
    stem = path.stem.lower()
    # acid_05_* should come before acid_04_*, then stage_03_*, stage_02_*, ...
    match = re.match(r"^(acid|stage)_(\d+)_", stem)
    if not match:
        return (2, 0, stem)
    family = match.group(1)
    rung = int(match.group(2))
    if family == "acid":
        return (0, -rung, stem)
    return (1, -rung, stem)


def _collect_ladder_scenarios(scenarios_dir: Path) -> list[Path]:
    candidates = [
        p
        for p in scenarios_dir.glob("*.json")
        if p.is_file() and (p.name.startswith("acid_") or p.name.startswith("stage_"))
    ]
    candidates.sort(key=_scenario_sort_key)
    return candidates


def _collect_latest_runs_by_scenario(runs_dir: Path) -> dict[str, Path]:
    latest: dict[str, Path] = {}
    if not runs_dir.exists():
        return latest
    for path in sorted(runs_dir.glob("*.json")):
        if not path.is_file() or path.name.endswith(".dialog.json"):
            continue
        payload = _read_json(path)
        if not payload:
            continue
        scenario = str(payload.get("scenario", "")).strip()
        if not scenario:
            continue
        current = latest.get(scenario)
        if current is None or path.stat().st_mtime > current.stat().st_mtime:
            latest[scenario] = path
    return latest


def _heuristic_route(text: str) -> str:
    lowered = text.strip().lower()
    if re.search(r"\b(retract|remove|delete|undo|correction|actually)\b", lowered):
        return "retract"
    if re.search(r"\b(if|whenever|then)\b", lowered):
        return "assert_rule"
    if lowered.endswith("?") or re.search(r"^\s*(who|what|where|when|why|how)\b", lowered):
        return "query"
    if re.search(r"\b(translate|summarize|rewrite|format|explain)\b", lowered):
        return "other"
    return "assert_fact"


def _render_rung_page(
    *,
    scenario_path: Path,
    scenario_payload: dict[str, Any],
    latest_run_path: Path | None,
    output_path: Path,
) -> None:
    scenario_name = str(scenario_payload.get("name", scenario_path.stem))
    ontology_name = str(scenario_payload.get("ontology_name", ""))
    utterances = scenario_payload.get("utterances", [])
    validations = scenario_payload.get("validations", [])
    if not isinstance(utterances, list):
        utterances = []
    if not isinstance(validations, list):
        validations = []

    latest_run = _read_json(latest_run_path) if latest_run_path else None
    run_summary_html = "<p class=\"muted\">No run report found yet for this scenario.</p>"
    if latest_run:
        status = str(latest_run.get("overall_status", "unknown"))
        validation_passed = latest_run.get("validation_passed", 0)
        validation_total = latest_run.get("validation_total", 0)
        parse_failures = latest_run.get("turn_parse_failures", 0)
        apply_failures = latest_run.get("turn_apply_failures", 0)
        run_file = latest_run_path.name if latest_run_path else ""
        run_file_link = f"../../kb_runs/{run_file}" if run_file else "#"
        report_html_name = latest_run_path.with_suffix(".html").name if latest_run_path else ""
        report_html_path = ROOT / "docs" / "reports" / report_html_name
        report_html_link = f"../reports/{report_html_name}" if report_html_path.exists() else ""
        kb_page_link = ""
        kb_name = str(latest_run.get("ontology_kb_name", "")).strip()
        if kb_name:
            kb_page = ROOT / "docs" / "kb" / f"{kb_name}.html"
            if kb_page.exists():
                kb_page_link = f"../kb/{kb_name}.html"

        links: list[str] = [f"<a href=\"{html.escape(run_file_link)}\">raw run json</a>"]
        if report_html_link:
            links.append(f"<a href=\"{html.escape(report_html_link)}\">rendered run transcript</a>")
        if kb_page_link:
            links.append(f"<a href=\"{html.escape(kb_page_link)}\">KB snapshot</a>")

        run_summary_html = (
            f"<div class=\"summary {html.escape(status)}\">"
            f"<p><strong>Status:</strong> {html.escape(status)}</p>"
            f"<p><strong>Validation:</strong> {validation_passed}/{validation_total} passed</p>"
            f"<p><strong>Parser failures:</strong> {parse_failures} | <strong>Apply failures:</strong> {apply_failures}</p>"
            f"<p><strong>Artifacts:</strong> {' | '.join(links)}</p>"
            "</div>"
        )

    utterance_items = []
    for idx, raw in enumerate(utterances, start=1):
        text = str(raw)
        route = _heuristic_route(text)
        utterance_items.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td><code>{html.escape(route)}</code></td>"
            f"<td>{html.escape(text)}</td>"
            "</tr>"
        )
    utterance_rows = "\n".join(utterance_items) if utterance_items else "<tr><td colspan=\"3\">No utterances</td></tr>"

    validation_items = []
    for idx, item in enumerate(validations, start=1):
        if not isinstance(item, dict):
            continue
        vid = str(item.get("id", f"validation_{idx:02d}"))
        query = str(item.get("query", ""))
        expect_status = str(item.get("expect_status", "success"))
        min_rows = item.get("min_rows", "")
        max_rows = item.get("max_rows", "")
        validation_items.append(
            "<tr>"
            f"<td>{html.escape(vid)}</td>"
            f"<td><code>{html.escape(query)}</code></td>"
            f"<td>{html.escape(expect_status)}</td>"
            f"<td>{html.escape(str(min_rows))}</td>"
            f"<td>{html.escape(str(max_rows))}</td>"
            "</tr>"
        )
    validation_rows = "\n".join(validation_items) if validation_items else "<tr><td colspan=\"5\">No validations</td></tr>"

    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    page = f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Rung: {html.escape(scenario_name)}</title>
  <style>
    :root {{
      --bg: #f6f8fb; --panel: #ffffff; --ink: #142033; --muted: #5c6b82; --border: #d8e0ea; --header: #f9fbfe;
      --ok-bg: #e7f6ea; --ok-ink: #1d5d2b; --fail-bg: #fdecee; --fail-ink: #7a1f2b;
    }}
    html[data-theme="dark"] {{
      --bg: #131920; --panel: #1d2530; --ink: #e8eef6; --muted: #a9b4c6; --border: #334257; --header: #212b38;
      --ok-bg: #1f3a28; --ok-ink: #b7efc5; --fail-bg: #47232c; --fail-ink: #f6c2cc;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: "Segoe UI", Arial, sans-serif; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; margin-bottom: 8px; }}
    h1 {{ margin: 0; font-size: 28px; }}
    .muted {{ color: var(--muted); font-size: 14px; }}
    .theme-btn {{ border: 1px solid var(--border); background: var(--panel); color: var(--ink); border-radius: 999px; padding: 8px 12px; font-size: 12px; cursor: pointer; }}
    .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; margin-top: 14px; overflow: hidden; }}
    .panel h2 {{ margin: 0; padding: 12px 14px; font-size: 16px; background: var(--header); border-bottom: 1px solid var(--border); }}
    .body {{ padding: 12px 14px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--border); padding: 10px 8px; font-size: 14px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); background: var(--header); }}
    tr:last-child td {{ border-bottom: none; }}
    code {{ background: var(--header); border: 1px solid var(--border); border-radius: 6px; padding: 2px 5px; font-family: Consolas, "Courier New", monospace; font-size: 12px; }}
    a {{ color: #0b66d0; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .summary {{ border: 1px solid var(--border); border-radius: 10px; padding: 10px; }}
    .summary.passed {{ background: var(--ok-bg); color: var(--ok-ink); }}
    .summary.failed {{ background: var(--fail-bg); color: var(--fail-ink); }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1>{html.escape(scenario_name)}</h1>
        <p class="muted">Ontology: {html.escape(ontology_name or "(none)")}</p>
        <p class="muted">Scenario file: {html.escape(str(scenario_path))}</p>
      </div>
      <button id="theme-toggle" class="theme-btn" aria-label="Toggle theme">theme</button>
    </div>
    <p class="muted">Generated {generated} | <a href="./index.html">Back to ladder index</a> | <a href="../index.html">Back to docs</a></p>

    <section class="panel">
      <h2>Latest Run Summary</h2>
      <div class="body">{run_summary_html}</div>
    </section>

    <section class="panel">
      <h2>Utterance Plan</h2>
      <div class="body">
        <table>
          <thead><tr><th>#</th><th>Expected Route</th><th>Utterance</th></tr></thead>
          <tbody>
{utterance_rows}
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <h2>Validation Contract</h2>
      <div class="body">
        <table>
          <thead><tr><th>ID</th><th>Query</th><th>Expect</th><th>Min Rows</th><th>Max Rows</th></tr></thead>
          <tbody>
{validation_rows}
          </tbody>
        </table>
      </div>
    </section>
  </div>
  <script>
    (() => {{
      const root = document.documentElement;
      const toggle = document.getElementById("theme-toggle");
      const key = "rung_theme_pref";
      const stored = window.localStorage.getItem(key);
      if (stored === "dark" || stored === "light") {{
        root.setAttribute("data-theme", stored);
      }} else {{
        const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        root.setAttribute("data-theme", prefersDark ? "dark" : "light");
      }}
      const sync = () => {{
        const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
        toggle.textContent = `theme: ${{current}}`;
      }};
      sync();
      toggle.addEventListener("click", () => {{
        const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
        const next = current === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        window.localStorage.setItem(key, next);
        sync();
      }});
    }})();
  </script>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")


def _render_index_page(
    *,
    title: str,
    rows_html: str,
    output_path: Path,
) -> None:
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    page = f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    :root {{ --bg:#f6f8fb; --panel:#ffffff; --ink:#142033; --muted:#5c6b82; --border:#d8e0ea; --header:#f9fbfe; }}
    html[data-theme="dark"] {{ --bg:#131920; --panel:#1d2530; --ink:#e8eef6; --muted:#a9b4c6; --border:#334257; --header:#212b38; }}
    body {{ margin:0; background:var(--bg); color:var(--ink); font-family:"Segoe UI", Arial, sans-serif; }}
    .wrap {{ max-width:1100px; margin:0 auto; padding:24px; }}
    .topbar {{ display:flex; justify-content:space-between; align-items:flex-start; gap:10px; margin-bottom:8px; }}
    h1 {{ margin:0; font-size:30px; }}
    .muted {{ color:var(--muted); font-size:14px; }}
    .theme-btn {{ border:1px solid var(--border); background:var(--panel); color:var(--ink); border-radius:999px; padding:8px 12px; font-size:12px; cursor:pointer; }}
    .panel {{ background:var(--panel); border:1px solid var(--border); border-radius:12px; overflow:hidden; margin-top:14px; }}
    table {{ width:100%; border-collapse:collapse; }}
    th, td {{ border-bottom:1px solid var(--border); padding:10px 8px; text-align:left; font-size:14px; vertical-align:top; }}
    th {{ color:var(--muted); background:var(--header); }}
    tr:last-child td {{ border-bottom:none; }}
    code {{ background:var(--header); border:1px solid var(--border); border-radius:6px; padding:2px 5px; font-family:Consolas, "Courier New", monospace; font-size:12px; }}
    a {{ color:#0b66d0; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    .status.passed {{ color:#1d7a36; font-weight:600; }}
    .status.failed {{ color:#a82633; font-weight:600; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1>{html.escape(title)}</h1>
        <p class="muted">Generated {generated} | <a href="../index.html">Back to docs</a></p>
      </div>
      <button id="theme-toggle" class="theme-btn" aria-label="Toggle theme">theme</button>
    </div>
    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>Rung</th>
            <th>Scenario</th>
            <th>Utterances</th>
            <th>Validations</th>
            <th>Latest Run</th>
          </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
      </table>
    </div>
  </div>
  <script>
    (() => {{
      const root = document.documentElement;
      const toggle = document.getElementById("theme-toggle");
      const key = "ladder_theme_pref";
      const stored = window.localStorage.getItem(key);
      if (stored === "dark" || stored === "light") {{
        root.setAttribute("data-theme", stored);
      }} else {{
        const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        root.setAttribute("data-theme", prefersDark ? "dark" : "light");
      }}
      const sync = () => {{
        const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
        toggle.textContent = `theme: ${{current}}`;
      }};
      sync();
      toggle.addEventListener("click", () => {{
        const current = root.getAttribute("data-theme") === "dark" ? "dark" : "light";
        const next = current === "dark" ? "light" : "dark";
        root.setAttribute("data-theme", next);
        window.localStorage.setItem(key, next);
        sync();
      }});
    }})();
  </script>
</body>
</html>
"""
    output_path.write_text(page, encoding="utf-8")


def main() -> int:
    args = parse_args()
    scenarios_dir = _resolve(args.scenarios_dir)
    runs_dir = _resolve(args.runs_dir)
    output_dir = _resolve(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scenario_files = _collect_ladder_scenarios(scenarios_dir)
    latest_runs = _collect_latest_runs_by_scenario(runs_dir)

    index_rows: list[str] = []
    for rank, scenario_path in enumerate(scenario_files, start=1):
        payload = _read_json(scenario_path)
        if not payload:
            continue
        scenario_name = str(payload.get("name", scenario_path.stem))
        utterances = payload.get("utterances", [])
        validations = payload.get("validations", [])
        if not isinstance(utterances, list):
            utterances = []
        if not isinstance(validations, list):
            validations = []

        latest_run_path = latest_runs.get(scenario_name)
        run_cell = "<span class=\"muted\">not run</span>"
        if latest_run_path:
            run_payload = _read_json(latest_run_path) or {}
            status = str(run_payload.get("overall_status", "unknown"))
            run_cell = (
                f"<span class=\"status {html.escape(status)}\">{html.escape(status)}</span> "
                f"(<a href=\"../../kb_runs/{html.escape(latest_run_path.name)}\">json</a>)"
            )

        page_name = f"{scenario_name}.html"
        output_path = output_dir / page_name
        _render_rung_page(
            scenario_path=scenario_path,
            scenario_payload=payload,
            latest_run_path=latest_run_path,
            output_path=output_path,
        )

        index_rows.append(
            "<tr>"
            f"<td>{rank}</td>"
            f"<td><a href=\"{html.escape(page_name)}\">{html.escape(scenario_name)}</a></td>"
            f"<td>{len(utterances)}</td>"
            f"<td>{len(validations)}</td>"
            f"<td>{run_cell}</td>"
            "</tr>"
        )

    rows_html = "\n".join(index_rows) if index_rows else "<tr><td colspan=\"5\">No ladder scenarios found.</td></tr>"
    _render_index_page(
        title=args.title,
        rows_html=rows_html,
        output_path=output_dir / "index.html",
    )

    print(f"Wrote {output_dir / 'index.html'}")
    print(f"Rendered rung pages: {len(index_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
