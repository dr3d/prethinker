#!/usr/bin/env python3
"""
Render persistent KB corpora from kb_store into HTML pages.

Each ontology directory with kb.pl becomes one page under hub/kb by default.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render kb_store corpora into HTML snapshot pages.")
    parser.add_argument("--kb-root", default="kb_store", help="Root directory containing ontology KB folders.")
    parser.add_argument("--output-dir", default="hub/kb", help="Output directory for rendered KB HTML pages.")
    parser.add_argument("--title-prefix", default="KB Snapshot", help="Title prefix for rendered pages.")
    return parser.parse_args()


def _resolve(path_text: str) -> Path:
    raw = Path(path_text)
    if raw.is_absolute():
        return raw.resolve()
    return (ROOT / raw).resolve()


def _normalize_clause(clause: str) -> str:
    text = clause.strip()
    if text and not text.endswith("."):
        text += "."
    return text


def _read_corpus(path: Path) -> list[str]:
    if not path.exists():
        return []
    clauses: list[str] = []
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("%") or line.startswith(":-"):
            continue
        if line.endswith("."):
            clauses.append(line)
    return clauses


def _count_top_level_args(args_text: str) -> int:
    if not args_text.strip():
        return 0
    depth = 0
    count = 1
    for ch in args_text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth > 0:
                depth -= 1
        elif ch == "," and depth == 0:
            count += 1
    return count


def _extract_goal_signatures(expr: str) -> list[str]:
    signatures: list[str] = []
    text = expr.strip()
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if not ch.isalpha() or not ch.islower():
            i += 1
            continue
        j = i + 1
        while j < n and (text[j].isalnum() or text[j] == "_"):
            j += 1
        name = text[i:j]
        k = j
        while k < n and text[k].isspace():
            k += 1
        if k >= n or text[k] != "(":
            i = j
            continue
        depth = 0
        p = k
        close_idx = -1
        while p < n:
            if text[p] == "(":
                depth += 1
            elif text[p] == ")":
                depth -= 1
                if depth == 0:
                    close_idx = p
                    break
            p += 1
        if close_idx < 0:
            i = j
            continue
        args = text[k + 1 : close_idx]
        arity = _count_top_level_args(args)
        signatures.append(f"{name}/{arity}")
        i = close_idx + 1
    return signatures


def _parse_kb(clauses: list[str]) -> dict[str, object]:
    facts: list[str] = []
    rules: list[str] = []
    signatures: set[str] = set()
    for raw in clauses:
        clause = _normalize_clause(raw)
        if ":-" in clause:
            rules.append(clause)
        else:
            facts.append(clause)
        expr = clause[:-1] if clause.endswith(".") else clause
        for sig in _extract_goal_signatures(expr):
            signatures.add(sig)
    return {
        "facts": facts,
        "rules": rules,
        "signatures": sorted(signatures),
    }


def _render_page(
    *,
    ontology_name: str,
    corpus_path: Path,
    profile_payload: dict[str, object] | None,
    parsed: dict[str, object],
    title_prefix: str,
) -> str:
    facts = parsed.get("facts", [])
    rules = parsed.get("rules", [])
    signatures = parsed.get("signatures", [])
    if not isinstance(facts, list):
        facts = []
    if not isinstance(rules, list):
        rules = []
    if not isinstance(signatures, list):
        signatures = []

    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    profile_json = json.dumps(profile_payload or {}, indent=2, ensure_ascii=False)

    signature_items = "".join(f"<li><code>{html.escape(str(sig))}</code></li>" for sig in signatures) or "<li>(none)</li>"
    fact_items = "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in facts) or "<li>(none)</li>"
    rule_items = "".join(f"<li><code>{html.escape(str(item))}</code></li>" for item in rules) or "<li>(none)</li>"

    return f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title_prefix)} - {html.escape(ontology_name)}</title>
  <style>
    :root {{
      --bg: #f6f8fb;
      --panel: #ffffff;
      --ink: #142033;
      --muted: #5c6b82;
      --border: #d8e0ea;
      --header: #f9fbfe;
      --code-bg: #eef4ff;
      --code-ink: #0f2c58;
    }}
    html[data-theme="dark"] {{
      --bg: #131920;
      --panel: #1d2530;
      --ink: #e8eef6;
      --muted: #a9b4c6;
      --border: #334257;
      --header: #212b38;
      --code-bg: #24344a;
      --code-ink: #cae3ff;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); font-family: "Segoe UI", Arial, sans-serif; }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 24px; }}
    .topbar {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }}
    h1 {{ margin: 0; font-size: 28px; }}
    .meta {{ color: var(--muted); font-size: 14px; margin: 8px 0 18px; }}
    .theme-btn {{
      border: 1px solid var(--border); background: var(--panel); color: var(--ink); border-radius: 999px;
      padding: 8px 12px; font-size: 12px; cursor: pointer;
    }}
    .panel {{ background: var(--panel); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 16px; overflow: hidden; }}
    .panel h2 {{ margin: 0; padding: 12px 14px; font-size: 16px; border-bottom: 1px solid var(--border); background: var(--header); }}
    .panel .body {{ padding: 12px 14px; }}
    ul {{ margin: 0; padding-left: 20px; }}
    li {{ margin: 4px 0; }}
    code {{
      background: var(--code-bg); color: var(--code-ink); border: 1px solid var(--border); border-radius: 6px;
      padding: 2px 5px; font-family: Consolas, "Courier New", monospace; font-size: 12px;
    }}
    pre {{
      margin: 0; white-space: pre-wrap; word-break: break-word; background: var(--header);
      border: 1px solid var(--border); border-radius: 8px; padding: 10px;
      font-family: Consolas, "Courier New", monospace; font-size: 12px;
    }}
    .stats {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }}
    .stat {{ border: 1px solid var(--border); border-radius: 8px; padding: 10px; background: var(--header); }}
    .stat .k {{ color: var(--muted); font-size: 12px; }}
    .stat .v {{ font-size: 18px; font-weight: 600; margin-top: 2px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <h1>{html.escape(title_prefix)}: {html.escape(ontology_name)}</h1>
      <button id="theme-toggle" class="theme-btn" aria-label="Toggle theme">theme</button>
    </div>
    <p class="meta">Generated {generated} | Corpus: {html.escape(str(corpus_path))}</p>

    <section class="panel">
      <h2>Summary</h2>
      <div class="body">
        <div class="stats">
          <div class="stat"><div class="k">Facts</div><div class="v">{len(facts)}</div></div>
          <div class="stat"><div class="k">Rules</div><div class="v">{len(rules)}</div></div>
          <div class="stat"><div class="k">Predicate Signatures</div><div class="v">{len(signatures)}</div></div>
        </div>
      </div>
    </section>

    <section class="panel">
      <h2>Predicate Signatures</h2>
      <div class="body"><ul>{signature_items}</ul></div>
    </section>

    <section class="panel">
      <h2>Facts</h2>
      <div class="body"><ul>{fact_items}</ul></div>
    </section>

    <section class="panel">
      <h2>Rules</h2>
      <div class="body"><ul>{rule_items}</ul></div>
    </section>

    <section class="panel">
      <h2>Ontology Profile JSON</h2>
      <div class="body"><pre>{html.escape(profile_json)}</pre></div>
    </section>
  </div>
  <script>
    (() => {{
      const root = document.documentElement;
      const toggle = document.getElementById("theme-toggle");
      const key = "kb_snapshot_theme_pref";
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


def main() -> int:
    args = parse_args()
    kb_root = _resolve(args.kb_root)
    output_dir = _resolve(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not kb_root.exists():
        raise FileNotFoundError(f"KB root not found: {kb_root}")

    count = 0
    for ontology_dir in sorted(p for p in kb_root.iterdir() if p.is_dir()):
        corpus_path = ontology_dir / "kb.pl"
        if not corpus_path.exists():
            continue
        profile_path = ontology_dir / "ontology_profile.json"
        profile_payload: dict[str, object] | None = None
        if profile_path.exists():
            try:
                loaded = json.loads(profile_path.read_text(encoding="utf-8-sig"))
                if isinstance(loaded, dict):
                    profile_payload = loaded
            except json.JSONDecodeError:
                profile_payload = None

        clauses = _read_corpus(corpus_path)
        parsed = _parse_kb(clauses)
        ontology_name = ontology_dir.name
        html_page = _render_page(
            ontology_name=ontology_name,
            corpus_path=corpus_path,
            profile_payload=profile_payload,
            parsed=parsed,
            title_prefix=args.title_prefix,
        )
        output_path = output_dir / f"{ontology_name}.html"
        output_path.write_text(html_page, encoding="utf-8")
        print(f"Wrote {output_path}")
        count += 1

    print(f"Rendered KB pages: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

