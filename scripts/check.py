#!/usr/bin/env python3
"""Check the rules `AGENTS.md` states for the Markdown in this repository.

Three rules are checked:

- Every relative link resolves, except a link into the read-only `external/`
  checkouts, which may be absent on a runner.
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

ROOT = pathlib.Path(__file__).resolve().parent.parent

FENCE = re.compile(r"^(\s*>?\s*)(```|~~~)")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def prose_lines(text):
    """Yield (line number, line) for the lines outside fenced code blocks."""
    in_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, line


def check_links(path, failures):
    for number, line in prose_lines(path.read_text()):
        if "](" in line and ")" not in line.split("](", 1)[1]:
            failures.append(f"{path.relative_to(ROOT)}:{number}: link broken across lines")
        for target in LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = (path.parent / target.split("#")[0]).resolve()
            if "external" in resolved.parts:
                continue
            if not resolved.exists():
                failures.append(f"{path.relative_to(ROOT)}:{number}: broken link {target}")


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
