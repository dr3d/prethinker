#!/usr/bin/env python3
"""
Render conversation JSON transcripts into themed HTML pages.

Supports:
- standard layout skin (default)
- telegram skin
- imessage skin
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
DEFAULT_TEMPLATE = ROOT / "scripts/templates/dialog-session-page.template.html"
DEFAULT_THEME_DIR = ROOT / "scripts/templates/dialog-themes"
THEME_FILES = {
    "standard": "standard.css",
    "telegram": "telegram.css",
    "imessage": "imessage.css",
}

SHARED_ANNOTATION_CSS = """

    .annotation-stack {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin: 8px 0 12px;
    }

    .annotation-card {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 10px 12px;
      margin-right: auto;
      max-width: 92%;
      background: color-mix(in srgb, var(--panel) 84%, var(--tool));
    }

    .annotation-card.annotation-score {
      background: color-mix(in srgb, var(--assistant) 72%, var(--panel));
    }

    .annotation-card.annotation-pass {
      background: color-mix(in srgb, var(--copy-done-bg) 58%, var(--panel));
      border-color: color-mix(in srgb, var(--copy-done-border) 70%, var(--border));
    }

    .annotation-card.annotation-fail {
      background: color-mix(in srgb, #ffd7d7 58%, var(--panel));
      border-color: color-mix(in srgb, #d66 65%, var(--border));
    }

    .annotation-card.annotation-warning {
      background: color-mix(in srgb, #ffe8b3 56%, var(--panel));
      border-color: color-mix(in srgb, #cc9a33 65%, var(--border));
    }

    html[data-theme="dark"] .annotation-card.annotation-fail {
      background: color-mix(in srgb, #4a2424 60%, var(--panel));
      border-color: color-mix(in srgb, #b77676 60%, var(--border));
    }

    html[data-theme="dark"] .annotation-card.annotation-warning {
      background: color-mix(in srgb, #4b3a20 60%, var(--panel));
      border-color: color-mix(in srgb, #b88f49 60%, var(--border));
    }

    .annotation-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 6px;
    }

    .annotation-kind {
      border: 1px solid var(--border);
      border-radius: 999px;
      padding: 1px 7px;
      font-size: 10px;
      letter-spacing: .05em;
      text-transform: uppercase;
      color: var(--muted);
      background: var(--panel);
      font-family: "Courier New", monospace;
    }

    .annotation-title {
      font-size: 12px;
      color: var(--ink);
      font-weight: 600;
      letter-spacing: .01em;
    }

"""


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False)
    return str(value)


def _humanize_stem(stem: str) -> str:
    parts = [part for part in stem.replace("_", "-").split("-") if part]
    if not parts:
        return "Session"
    # Preserve source casing so presentation-level capitalization is CSS-driven.
    return " ".join(parts)


def _compact_lower_label(text: str) -> str:
    normalized = text.replace("_", " ").replace("-", " ").strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def _scenario_short_id(scenario_id: str, fallback_index: int) -> str:
    match = re.match(r"^(s\d+)", scenario_id.strip(), flags=re.IGNORECASE)
    if match:
        return match.group(1).lower()
    return f"s{fallback_index:02d}"


def _decode_tool_output(payload: Any) -> Any:
    value = payload
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            return stripped

    if isinstance(value, list):
        # Common LM Studio MCP envelope: [{"type":"text","text":"{...json...}"}]
        if len(value) == 1 and isinstance(value[0], dict):
            text = value[0].get("text")
            if isinstance(text, str):
                text = text.strip()
                if not text:
                    return ""
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text
    return value


def _pretty_json(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, indent=2, ensure_ascii=False)


def _truncate_text(text: str, max_chars: int) -> str:
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n... [truncated]"


def _normalize_annotations(raw_value: Any) -> list[dict[str, str]]:
    if not isinstance(raw_value, list):
        return []
    annotations: list[dict[str, str]] = []
    for item in raw_value:
        if isinstance(item, str):
            text = _coerce_text(item)
            if text:
                annotations.append({"kind": "info", "title": "Annotation", "text": text})
            continue
        if not isinstance(item, dict):
            continue
        kind_raw = _coerce_text(item.get("kind")).strip().lower() or "info"
        kind = re.sub(r"[^a-z0-9_-]", "", kind_raw) or "info"
        title = _coerce_text(item.get("title")).strip() or "Annotation"
        text = _coerce_text(item.get("text") or item.get("message")).strip()
        if not text:
            continue
        annotations.append({"kind": kind, "title": title, "text": text})
    return annotations


def _normalize_steps(payload: dict[str, Any]) -> list[dict[str, Any]]:
    steps = payload.get("steps")
    if not isinstance(steps, list):
        return []

    turns: list[dict[str, Any]] = []
    for index, raw_step in enumerate(steps, start=1):
        if not isinstance(raw_step, dict):
            continue
        tool_calls = raw_step.get("tool_calls")
        if not isinstance(tool_calls, list):
            tool_calls = []
        turns.append(
            {
                "title": _coerce_text(raw_step.get("step")) or f"turn_{index}",
                "user_text": _coerce_text(raw_step.get("prompt") or raw_step.get("user_prompt")),
                "assistant_text": _coerce_text(raw_step.get("assistant_message") or raw_step.get("assistant_reply")),
                "tool_calls": tool_calls,
                "annotations": _normalize_annotations(raw_step.get("annotations")),
            }
        )
    return turns


def _normalize_messages(payload: dict[str, Any]) -> list[dict[str, Any]]:
    messages = payload.get("messages")
    if not isinstance(messages, list):
        return []

    turns: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    def ensure_current() -> dict[str, Any]:
        nonlocal current
        if current is None:
            current = {
                "title": f"turn_{len(turns) + 1}",
                "user_text": "",
                "assistant_text": "",
                "tool_calls": [],
                "annotations": [],
            }
        return current

    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", "")).strip().lower()
        text = _coerce_text(message.get("content") or message.get("text"))
        if role == "user":
            if current is not None and (current["user_text"] or current["assistant_text"] or current["tool_calls"]):
                turns.append(current)
            current = {
                "title": f"turn_{len(turns) + 1}",
                "user_text": text,
                "assistant_text": "",
                "tool_calls": [],
                "annotations": [],
            }
            continue

        if role == "assistant":
            active = ensure_current()
            if active["assistant_text"]:
                active["assistant_text"] += "\n\n" + text
            else:
                active["assistant_text"] = text
            continue

        if role == "tool":
            active = ensure_current()
            active["tool_calls"].append(
                {
                    "tool": message.get("name") or message.get("tool") or "tool",
                    "arguments": message.get("arguments", {}),
                    "output": message.get("output") or text,
                }
            )
            continue

        # Fallback: append unknown-role content to assistant transcript.
        active = ensure_current()
        if text:
            if active["assistant_text"]:
                active["assistant_text"] += "\n\n" + text
            else:
                active["assistant_text"] = text

    if current is not None and (current["user_text"] or current["assistant_text"] or current["tool_calls"]):
        turns.append(current)
    return turns


def _normalize_scenarios(payload: dict[str, Any]) -> list[dict[str, Any]]:
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list):
        return []

    turns: list[dict[str, Any]] = []
    for scenario_index, scenario in enumerate(scenarios, start=1):
        if not isinstance(scenario, dict):
            continue
        scenario_id = _coerce_text(scenario.get("scenario_id")) or f"scenario_{scenario_index}"
        scenario_short = _scenario_short_id(scenario_id, fallback_index=scenario_index)
        steps = scenario.get("steps")
        if not isinstance(steps, list):
            continue
        for step_index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                continue
            tool_calls = step.get("tool_calls")
            if not isinstance(tool_calls, list):
                tool_calls = []
            step_title_raw = _coerce_text(step.get("step")) or f"step_{step_index}"
            if ":" in step_title_raw:
                _, step_suffix = step_title_raw.split(":", 1)
            else:
                step_suffix = step_title_raw
            step_label = _compact_lower_label(step_suffix)
            turns.append(
                {
                    "title": f"{scenario_short} / {step_label}",
                    "user_text": _coerce_text(step.get("prompt") or step.get("user_prompt")),
                    "assistant_text": _coerce_text(step.get("assistant_message") or step.get("assistant_reply")),
                    "tool_calls": tool_calls,
                    "annotations": _normalize_annotations(step.get("annotations")),
                }
            )
    return turns


def _extract_response_text(raw_response: Any) -> str:
    if not isinstance(raw_response, dict):
        return ""
    output = raw_response.get("output")
    if not isinstance(output, list):
        return ""
    parts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = _coerce_text(item.get("content") or item.get("text"))
        if not content:
            continue
        kind = _coerce_text(item.get("type")).strip().lower()
        if kind:
            parts.append(f"[{kind}]\n{content}")
        else:
            parts.append(content)
    return "\n\n".join(parts).strip()


def _normalize_documents(payload: dict[str, Any]) -> list[dict[str, Any]]:
    documents = payload.get("documents")
    if not isinstance(documents, list):
        return []

    turns: list[dict[str, Any]] = []
    for index, document in enumerate(documents, start=1):
        if not isinstance(document, dict):
            continue
        document_id = _coerce_text(document.get("document_id")) or f"document_{index}"
        user_lines = [f"Extraction evaluation document: {document_id}"]
        prompt_set = _coerce_text(document.get("prompt_set"))
        if prompt_set:
            user_lines.append(f"Prompt set: {prompt_set}")
        user_text = "\n".join(user_lines)

        assistant_text = _coerce_text(document.get("response_text"))
        if not assistant_text:
            parsed_payload = document.get("parsed_payload")
            if parsed_payload is not None:
                assistant_text = _pretty_json(parsed_payload)
        if not assistant_text:
            assistant_text = _extract_response_text(document.get("raw_response"))
        if not assistant_text:
            assistant_text = "(no assistant response text captured)"

        parse_ok = document.get("parse_ok")
        tool_calls: list[dict[str, Any]] = []
        if parse_ok is not None:
            tool_calls.append(
                {
                    "tool": "parse_result",
                    "arguments": {"document_id": document_id},
                    "output": {
                        "parse_ok": parse_ok,
                        "doc_score": document.get("doc_score"),
                    },
                }
            )

        turns.append(
            {
                "title": f"document::{document_id}",
                "user_text": user_text,
                "assistant_text": assistant_text,
                "tool_calls": tool_calls,
                "annotations": _normalize_annotations(document.get("annotations")),
            }
        )
    return turns


def _normalize_turns(payload: dict[str, Any]) -> list[dict[str, Any]]:
    turns = _normalize_steps(payload)
    if turns:
        return turns
    turns = _normalize_scenarios(payload)
    if turns:
        return turns
    turns = _normalize_documents(payload)
    if turns:
        return turns
    return _normalize_messages(payload)


def _render_tool_call(call: dict[str, Any], *, max_output_chars: int) -> str:
    tool_name = html.escape(_coerce_text(call.get("tool")) or "tool")
    args_raw = call.get("arguments", {})
    args_text = _pretty_json(args_raw)
    args_html = html.escape(args_text)

    output_html = ""
    if "output" in call:
        decoded = _decode_tool_output(call.get("output"))
        pretty = _pretty_json(decoded)
        pretty = _truncate_text(pretty, max_chars=max_output_chars)
        output_html = (
            "<details class=\"tool-output\">"
            "<summary>output</summary>"
            f"<pre>{html.escape(pretty)}</pre>"
            "</details>"
        )

    return (
        "<li class=\"tool-item\">"
        f"<div class=\"tool-line\"><code>{tool_name}</code> <code>{args_html}</code></div>"
        f"{output_html}"
        "</li>"
    )


def _render_turn_card(
    turn: dict[str, Any],
    *,
    copy_label: str,
    copy_success_label: str,
    copy_failure_label: str,
    max_output_chars: int,
) -> str:
    title = html.escape(_coerce_text(turn.get("title")) or "turn")
    user_text = _coerce_text(turn.get("user_text")) or "(empty user prompt)"
    assistant_text = _coerce_text(turn.get("assistant_text")) or "(empty assistant reply)"

    user_text_escaped = html.escape(user_text)
    assistant_text_escaped = html.escape(assistant_text)

    user_copy_attr = html.escape(user_text, quote=True)
    assistant_copy_attr = html.escape(assistant_text, quote=True)
    copy_label_attr = html.escape(copy_label, quote=True)
    copy_success_attr = html.escape(copy_success_label, quote=True)
    copy_failure_attr = html.escape(copy_failure_label, quote=True)

    tool_calls = turn.get("tool_calls", [])
    if not isinstance(tool_calls, list):
        tool_calls = []

    if tool_calls:
        tool_items = "".join(
            _render_tool_call(call, max_output_chars=max_output_chars)
            for call in tool_calls
            if isinstance(call, dict)
        )
        tool_html = (
            "<details class=\"toolbox tool-expando\">"
            f"<summary><span>tool calls</span><span class=\"expando-count\">{len(tool_calls)}</span></summary>"
            f"<ul class=\"tool-list\">{tool_items}</ul>"
            "</details>"
        )
    else:
        tool_html = (
            "<details class=\"toolbox tool-expando\">"
            "<summary><span>tool calls</span><span class=\"expando-count\">0</span></summary>"
            "<p class=\"tool-list\">No tool calls captured.</p>"
            "</details>"
        )

    annotations = turn.get("annotations", [])
    if not isinstance(annotations, list):
        annotations = []
    annotation_items: list[str] = []
    for annotation in annotations:
        if not isinstance(annotation, dict):
            continue
        kind = re.sub(r"[^a-z0-9_-]", "", _coerce_text(annotation.get("kind")).strip().lower()) or "info"
        title_text = _coerce_text(annotation.get("title")).strip() or "Annotation"
        body_text = _coerce_text(annotation.get("text")).strip()
        if not body_text:
            continue
        annotation_items.append(
            "<div class=\"annotation-card annotation-"
            + html.escape(kind, quote=True)
            + "\">"
            + "<div class=\"annotation-head\">"
            + "<div class=\"annotation-title\">"
            + html.escape(title_text)
            + "</div>"
            + "<div class=\"annotation-kind\">"
            + html.escape(kind)
            + "</div>"
            + "</div>"
            + "<pre>"
            + html.escape(body_text)
            + "</pre>"
            + "</div>"
        )
    annotation_html = ""
    if annotation_items:
        annotation_html = "<div class=\"annotation-stack\">" + "".join(annotation_items) + "</div>"

    return (
        "<section class=\"step-card\">"
        f"<h2>{title}</h2>"
        "<div class=\"bubble user\">"
        "<div class=\"bubble-head\">"
        "<div class=\"label\">User</div>"
        f"<button class=\"copy-btn\" data-copy=\"{user_copy_attr}\" data-label=\"{copy_label_attr}\" "
        f"data-success-label=\"{copy_success_attr}\" data-failure-label=\"{copy_failure_attr}\">{html.escape(copy_label)}</button>"
        "</div>"
        f"<pre>{user_text_escaped}</pre>"
        "</div>"
        f"{tool_html}"
        "<div class=\"bubble assistant\">"
        "<div class=\"bubble-head\">"
        "<div class=\"label\">Assistant</div>"
        f"<button class=\"copy-btn\" data-copy=\"{assistant_copy_attr}\" data-label=\"{copy_label_attr}\" "
        f"data-success-label=\"{copy_success_attr}\" data-failure-label=\"{copy_failure_attr}\">{html.escape(copy_label)}</button>"
        "</div>"
        f"<pre>{assistant_text_escaped}</pre>"
        "</div>"
        f"{annotation_html}"
        "</section>"
    )


def _load_theme_css_map(theme_dir: Path) -> dict[str, str]:
    css_map: dict[str, str] = {}
    for theme_name, filename in THEME_FILES.items():
        theme_path = theme_dir / filename
        if not theme_path.exists():
            raise FileNotFoundError(f"Theme CSS missing: {theme_path}")
        css_map[theme_name] = theme_path.read_text(encoding="utf-8") + "\n" + SHARED_ANNOTATION_CSS
    return css_map


def _render_page(
    *,
    template_html: str,
    theme_css_map: dict[str, str],
    initial_skin: str,
    title: str,
    page_description: str,
    page_meta: str,
    content_html: str,
    docs_hub_link: str,
    repo_link: str,
    appearance_storage_key: str,
) -> str:
    if initial_skin not in theme_css_map:
        supported = ", ".join(sorted(theme_css_map))
        raise ValueError(f"Initial skin '{initial_skin}' not available. Supported skins: {supported}")

    initial_skin_css = theme_css_map[initial_skin]
    skin_css_map_json = json.dumps(theme_css_map, ensure_ascii=False).replace("</", "<\\/")
    skin_order_json = json.dumps(list(theme_css_map.keys()), ensure_ascii=False)

    replacements = {
        "{{PAGE_TITLE}}": html.escape(title),
        "{{PAGE_DESCRIPTION}}": html.escape(page_description),
        "{{PAGE_META}}": html.escape(page_meta),
        "{{CONTENT_HTML}}": content_html,
        "{{NAV_DOCS_HUB}}": html.escape(docs_hub_link, quote=True),
        "{{NAV_REPO}}": html.escape(repo_link, quote=True),
        "{{INITIAL_SKIN_NAME}}": html.escape(initial_skin, quote=True),
        "{{INITIAL_SKIN_CSS}}": initial_skin_css,
        "{{SKIN_CSS_MAP_JSON}}": skin_css_map_json,
        "{{APPEARANCE_STORAGE_KEY}}": html.escape(appearance_storage_key, quote=True),
        "{{SKIN_ORDER_JSON}}": skin_order_json,
    }

    output = template_html
    for token, value in replacements.items():
        output = output.replace(token, value)
    return output


def _render_one_file(
    *,
    source: Path,
    target: Path,
    template_html: str,
    theme_css_map: dict[str, str],
    args: argparse.Namespace,
) -> None:
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    turns = _normalize_turns(payload)
    if not turns:
        raise ValueError(f"No renderable turns found in {source}")

    title = args.title.strip() if args.title else _coerce_text(payload.get("title")).strip()
    if not title:
        title = _humanize_stem(source.stem)

    cards_html = "".join(
        _render_turn_card(
            turn,
            copy_label=args.copy_label,
            copy_success_label=args.copy_success_label,
            copy_failure_label=args.copy_failure_label,
            max_output_chars=args.max_tool_output_chars,
        )
        for turn in turns
    )

    captured_at = _coerce_text(payload.get("captured_at")) or "unknown"
    model = _coerce_text(payload.get("model")) or "unknown"
    integration = _coerce_text(payload.get("integration")) or "unknown"
    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    page_meta = (
        f"Captured: {captured_at} | Model: {model} | Integration: {integration} | "
        f"Initial skin: {args.theme} | Rendered: {generated}"
    )

    page = _render_page(
        template_html=template_html,
        theme_css_map=theme_css_map,
        initial_skin=args.theme,
        title=title,
        page_description=f"Themed session transcript rendered from {source.name}.",
        page_meta=page_meta,
        content_html=cards_html,
        docs_hub_link=args.docs_hub_link,
        repo_link=args.repo_link,
        appearance_storage_key=f"dialog_appearance_pref_{source.stem}",
    )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(page, encoding="utf-8")
    print(f"Wrote {target}")


def _collect_sources(source: Path, pattern: str, recursive: bool) -> list[Path]:
    if source.is_file():
        return [source]
    if not source.exists():
        raise FileNotFoundError(f"Input path does not exist: {source}")
    if not source.is_dir():
        raise ValueError(f"Input path must be a JSON file or directory: {source}")
    if recursive:
        return sorted(path for path in source.rglob(pattern) if path.is_file())
    return sorted(path for path in source.glob(pattern) if path.is_file())


def _resolve_target(source: Path, args: argparse.Namespace, source_root: Path | None) -> Path:
    if args.output:
        out = Path(args.output).resolve()
        if source_root is None and out.suffix.lower() == ".html":
            return out
        if source_root is not None:
            relative = source.relative_to(source_root)
            return out / relative.with_suffix(".html")
        return out / f"{source.stem}.html"
    if source_root is not None and not args.in_place:
        raise ValueError("Directory input requires --output <dir> or --in-place.")
    return source.with_suffix(".html")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render JSON transcript files into themed HTML pages.")
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file or directory containing JSON files.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Output HTML file path for single input, or output directory for directory input.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="When input is a directory, write .html files next to source .json files.",
    )
    parser.add_argument(
        "--pattern",
        default="*.json",
        help="Glob pattern when --input is a directory (default: *.json).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search recursively when --input is a directory.",
    )
    parser.add_argument(
        "--theme",
        default="standard",
        choices=sorted(THEME_FILES.keys()),
        help="Conversation skin.",
    )
    parser.add_argument(
        "--title",
        default="",
        help="Optional page title override (single-file input recommended).",
    )
    parser.add_argument(
        "--template",
        default=str(DEFAULT_TEMPLATE),
        help="HTML template path.",
    )
    parser.add_argument(
        "--theme-dir",
        default=str(DEFAULT_THEME_DIR),
        help="Directory holding theme CSS files.",
    )
    parser.add_argument(
        "--docs-hub-link",
        default="/docs",
        help="Top-nav docs hub link.",
    )
    parser.add_argument(
        "--repo-link",
        default="https://github.com/dr3d/prolog-reasoning",
        help="Top-nav repository link.",
    )
    parser.add_argument(
        "--copy-label",
        default="copy",
        help="Copy button default text.",
    )
    parser.add_argument(
        "--copy-success-label",
        default="copied",
        help="Copy button success text.",
    )
    parser.add_argument(
        "--copy-failure-label",
        default="copy-failed",
        help="Copy button failure text.",
    )
    parser.add_argument(
        "--max-tool-output-chars",
        type=int,
        default=10000,
        help="Maximum characters shown for each tool output block (0 disables truncation).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    template_path = Path(args.template).resolve()
    theme_dir = Path(args.theme_dir).resolve()

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    sources = _collect_sources(input_path, pattern=args.pattern, recursive=args.recursive)
    if not sources:
        raise FileNotFoundError(f"No JSON files matched pattern '{args.pattern}' under {input_path}")
    is_directory_input = input_path.is_dir()
    source_root = input_path if is_directory_input else None
    if is_directory_input and args.output and Path(args.output).suffix.lower() == ".html":
        raise ValueError("--output must be a directory when rendering multiple input files.")
    if len(sources) > 1 and args.title.strip():
        raise ValueError("--title can only be used for single-file rendering.")
    if is_directory_input and not args.output and not args.in_place:
        raise ValueError("Directory input requires --output <dir> or --in-place.")

    template_html = template_path.read_text(encoding="utf-8")
    theme_css_map = _load_theme_css_map(theme_dir=theme_dir)

    for source in sources:
        target = _resolve_target(source, args, source_root=source_root)
        _render_one_file(
            source=source,
            target=target,
            template_html=template_html,
            theme_css_map=theme_css_map,
            args=args,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
