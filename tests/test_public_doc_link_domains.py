import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
GITHUB_MARKDOWN_PREFIX = "https://github.com/dr3d/prethinker/blob/main/"
PAGES_HTML_PREFIX = "https://dr3d.github.io/prethinker/"

MARKDOWN_LINK_RE = re.compile(r"\]\(([^)]+)\)")
HREF_RE = re.compile(r'href="([^"]+)"')


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return [REPO_ROOT / line for line in result.stdout.splitlines() if line]


def _iter_link_targets(text: str):
    for match in MARKDOWN_LINK_RE.finditer(text):
        yield match.group(1)
    for match in HREF_RE.finditer(text):
        yield match.group(1)


def _path_part(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target.split("#", 1)[0]


def test_public_markdown_and_html_links_use_canonical_domains():
    failures: list[str] = []

    for path in _tracked_files():
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        rel_path = path.relative_to(REPO_ROOT).as_posix()
        for target in _iter_link_targets(text):
            target_path = _path_part(target)
            if not target_path:
                continue

            parsed = urlparse(target_path)
            if parsed.scheme and parsed.scheme not in {"http", "https"}:
                continue

            lower_path = target_path.lower()
            if lower_path.endswith(".md") and not target.startswith(GITHUB_MARKDOWN_PREFIX):
                failures.append(f"{rel_path}: markdown link should use {GITHUB_MARKDOWN_PREFIX}: {target}")
            if lower_path.endswith((".html", ".htm")) and not target.startswith(PAGES_HTML_PREFIX):
                failures.append(f"{rel_path}: html link should use {PAGES_HTML_PREFIX}: {target}")

    assert not failures, "\n".join(failures[:100])
