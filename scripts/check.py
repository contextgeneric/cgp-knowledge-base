#!/usr/bin/env python3
"""Check the rules `AGENTS.md` states for the Markdown in this repository.

Four rules are checked:

- Every relative link resolves, except a link into the read-only `external/`
  checkouts, which may be absent on a runner.
- Every link to a `#fragment` in a Markdown document names a heading in it,
  using the anchors GitHub derives from heading text, or an explicit `{#id}`
  or HTML `id` or `name`.
- Every document is registered in the `README.md` of its section and in
  `summary.md`.
- A link is never broken across lines, so `](` closes on the same line.

The script uses only the Python standard library, so a runner needs no install.
It skips fenced code blocks, so a link shown inside an example is not checked.
The `AGENTS.md` rule about an inline code span's backticks is not checked here,
because telling a broken span from a literal backtick needs a Markdown parser.

Usage: python3 scripts/check.py
"""

import pathlib
import re
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent

FENCE = re.compile(r"^\s*>?\s*(`{3,}|~{3,})(.*)$")
# Link text may hold one level of brackets, as in [`#[cgp_fn]`](cgp_fn.md).
LINK = re.compile(r"\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(([^)\s]+)\)")
HEADING = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
EXPLICIT_ID = re.compile(r"""\{#([^}\s]+)\}|<[^>]*\b(?:id|name)=["']([^"']+)["']""")
CODE_SPAN = re.compile(r"(`+)(.+?)\1")


def prose_lines(text):
    """Yield (line number, line) for the lines outside fenced code blocks.

    A fence follows CommonMark: a backtick fence's info string holds no
    backtick, so a line that opens with a code span is prose, and a closing
    fence repeats the opening character at least as many times, alone.
    """
    fence = None
    for number, line in enumerate(text.splitlines(), start=1):
        marker = FENCE.match(line)
        if fence is None:
            if marker and not (marker[1][0] == "`" and "`" in marker[2]):
                fence = marker[1]
                continue
            yield number, line
        elif (
            marker
            and marker[1][0] == fence[0]
            and len(marker[1]) >= len(fence)
            and not marker[2].strip()
        ):
            fence = None


def heading_text(raw):
    """The text GitHub renders for a heading's Markdown source."""
    raw = re.sub(r"\s*\{#[^}\s]*\}\s*$", "", raw)
    raw = re.sub(r"!?\[((?:[^\[\]]|\[[^\[\]]*\])*)\]\([^)]*\)", r"\1", raw)
    raw = re.sub(r"<[^>]+>", "", raw)
    pieces = []
    last = 0
    for span in CODE_SPAN.finditer(raw):
        pieces.append(plain_text(raw[last:span.start()]))
        pieces.append(span.group(2).strip())
        last = span.end()
    pieces.append(plain_text(raw[last:]))
    return "".join(pieces)


def plain_text(markdown):
    """Drop emphasis markers and backslash escapes outside code spans."""
    markdown = markdown.replace("*", "")
    markdown = re.sub(r"(?<![\w\\])_+|(?<!\\)_+(?!\w)", "", markdown)
    return re.sub(r"\\(.)", r"\1", markdown)


def slug(text):
    """GitHub's anchor for a heading, before duplicates are numbered."""
    return re.sub(r"[^\w\- ]", "", text.lower()).replace(" ", "-")


ANCHORS = {}


def anchors(path):
    """Every fragment a link to `path` may name."""
    if path not in ANCHORS:
        found = set()
        seen = {}
        for _, line in prose_lines(path.read_text()):
            found.update(a or b for a, b in EXPLICIT_ID.findall(line))
            heading = HEADING.match(line)
            if not heading:
                continue
            base = slug(heading_text(heading.group(1)))
            anchor = base
            while anchor in seen:
                seen[base] += 1
                anchor = f"{base}-{seen[base]}"
            seen[anchor] = 0
            found.add(anchor)
        ANCHORS[path] = found
    return ANCHORS[path]


def check_links(path, failures):
    for number, line in prose_lines(path.read_text()):
        where = f"{path.relative_to(ROOT)}:{number}"
        if "](" in line and ")" not in line.split("](", 1)[1]:
            failures.append(f"{where}: link broken across lines")
        for target in LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            file_part, _, fragment = target.partition("#")
            resolved = (path.parent / file_part).resolve() if file_part else path
            if "external" in resolved.parts:
                continue
            if not resolved.exists():
                failures.append(f"{where}: broken link {target}")
            elif fragment and resolved.suffix == ".md" and resolved.is_file():
                if urllib.parse.unquote(fragment) not in anchors(resolved):
                    failures.append(f"{where}: broken anchor {target}")


def section_catalog(path):
    """The nearest ancestor `README.md` that can register `path`, or None."""
    directory = path.parent
    while True:
        candidate = directory / "README.md"
        if candidate.exists() and candidate != path:
            return candidate
        if directory == ROOT:
            return None
        directory = directory.parent


def check_registration(path, failures):
    if path.name == "summary.md":
        return
    where = path.relative_to(ROOT)
    # The root `README.md` is the base's front door, not a section document.
    if path != ROOT / "README.md":
        catalog = section_catalog(path)
        if catalog is None:
            failures.append(f"{where}: no section `README.md` to register it in")
        else:
            text = catalog.read_text()
            relative = str(path.relative_to(catalog.parent))
            if path.name not in text and relative not in text:
                failures.append(f"{where}: not registered in {catalog.relative_to(ROOT)}")
    if str(where) not in (ROOT / "summary.md").read_text():
        failures.append(f"{where}: not named in summary.md")


def main():
    failures = []
    files = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    for path in files:
        check_links(path, failures)
        check_registration(path, failures)
    for failure in failures:
        print(failure)
    print(f"{len(files)} files checked, {len(failures)} problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
