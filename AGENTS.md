# AGENTS.md: the CGP knowledge base

Follow this file for every task in this repository. Read [README.md](README.md) for what the base is,
and [summary.md](summary.md) for every document it contains.

## Orient before any task

Learn CGP from the skill and this base, then read what a task touches before changing it:

- Learn CGP and its tools from the `/cgp` skill and this knowledge base; never restate them in an
  `AGENTS.md`.
- Invoke the `/cgp` skill before working with CGP constructs, and re-invoke it when you move into an
  unfamiliar construct.
- Load the `/point-first-writing` skill before writing or revising prose, which is nearly every task.
- Read [README.md](README.md), [summary.md](summary.md), the section `README.md`, and the
  [task guide](#task-guides) for the documents you are about to touch.
- Read the documents a task touches before changing them, and the documents they link to when a change
  crosses a boundary.

## Task guides

Each kind of document has a guide that holds the rules for writing it. Read the guide before writing
or revising such a document:

- **A `cgp/` reference, concept, or guide document:** [cgp/writing-guide.md](cgp/writing-guide.md).
- **An error class or code entry:** [cgp/errors/writing-guide.md](cgp/errors/writing-guide.md).
- **An implementation document:**
  [cgp/implementation/writing-guide.md](cgp/implementation/writing-guide.md), and for a macro review
  [cgp/implementation/review.md](cgp/implementation/review.md).
- **A `cargo-cgp/` document:** [cargo-cgp/writing-guide.md](cargo-cgp/writing-guide.md), and for an
  error-message improvement
  [cargo-cgp/implementation/improving-errors.md](cargo-cgp/implementation/improving-errors.md).
- **A worked example:** [examples/writing-guide.md](examples/writing-guide.md).
- **A related-work comparison:** [related-work/writing-guide.md](related-work/writing-guide.md).
- **A communication-strategy document:**
  [communication-strategy/writing-guide.md](communication-strategy/writing-guide.md).
- **A project section:** [projects/writing-guide.md](projects/writing-guide.md).
- **A website record or writing guide:** [website/README.md](website/README.md#rules-for-records)
  and [website/writing-guides/README.md](website/writing-guides/README.md).

## The synchronization rule

Every document stays in step with the code it describes, and the code wins any disagreement:

- Keep a document in sync with the code it describes, and keep that sync part of the change rather
  than a follow-up.
- Treat the source in the member projects as the single source of truth, above any document here and
  above the skill.
- Keep the implementation, the tests and snapshots, the reference document, the implementation
  document, and the skill in agreement; when they disagree, the code wins.
- Add a construct's document and catalog entry when the construct is added; remove or supersede both
  when it is removed; fix every cross-link when it is renamed.
- Make both the code change and its documentation change when the sibling checkout is present; when it
  is absent, state plainly what needs updating there.

## Keeping each section in step with its source

These changes make a section's documents stale, so each one carries the matching update:

- Update the matching `cgp/` reference document in the same change as a construct change to its
  syntax, its expansion, its defaults, its error behavior, or its relationships, and the
  implementation document with a parser, pipeline, generated-item, or error-path change.
- Revise the affected skill sub-skill, the routing guidance and reading cheat sheet in the skill's
  `SKILL.md`, and its front matter's `description` in the same change as a construct change.
- Revise the matching error class document in the same change as a fixture change, a new code, or a
  moved root cause.
- Revise the matching `cargo-cgp/` document in the same change as a change to the tool's behavior, its
  argument handling, its environment contract, its driver, or its crate structure.

## Verify against the source, not from memory

Check each claim against a source before writing it:

- Verify a claim about an expansion, a default, a syntax form, a module layout, or a compiler behavior
  against the source, a test, a snapshot, or a command before writing it.
- Use the Rust compiler and Clippy checkouts under `../external/` as read-only ground truth; cite them,
  never edit them, and never depend on them.
- Treat a published crate's own documentation as the ground truth for its API.
- Prefer verifying against a source over reasoning about what it probably does.
- Read the expansion snapshot when you doubt what a macro emits, rather than guessing.

## Document the present, not the history

Documents describe CGP as it is now; only the release documents and the blog records keep history:

- Describe current behavior as though it had always worked that way.
- Do not record how the code reached its current state with changelog entries, version numbers attached
  to behavior, or "renamed from", "previously", "used to", or "no longer" traces.
- Rewrite a corrected discrepancy to state the current behavior and delete the old wording.
- Keep a current deviation only in a Known issues or limitations section.
- Exempt only [releases/](releases/README.md) and [website/blog/](website/blog/README.md); when you
  need to say what something used to be, link the release document that records it.

## Document official versions, never pre-releases

The base names only official releases:

- Name official release versions only, never a pre-release.
- Do not name a pre-release, describe how it behaves, compare it with the source, or tell a reader how
  to move off it.
- Yield only to an explicit user instruction to document a particular pre-release.
- Do not apply the rule to a manifest or lockfile; they state what they must to build.

## This repository is public

Anyone can read this base, so write each document for a public reader:

- Write as though a member of the Rust community will find the document, because one may.
- Distil public discussion into what it amounts to; never link a thread or quote an identifiable
  person.
- Never disparage another project; assume its maintainers are reading.
- Keep speculation about individuals, private correspondence, and unpublished finances or plans out.
- Keep unfinished work and known defects in; they are the point of the base.
- Never fabricate evidence, such as a benchmark, an adoption figure, a quotation, or a
  version-specific claim.

## Writing links

Link each subject to the document that owns it, in the path form each kind of target needs:

- Link inside this repository with a relative path.
- Prefer the local checkout when reading a cross-project link.
- Link a member project's tree with a GitHub URL on `main`.
- Link a project section's project at the branch [sibling-projects.md](sibling-projects.md) records, not
  `main`.
- Keep a bare checkout path and a read-only external source as a relative filesystem reference.
- Link a construct, error class, or example to the document that owns it rather than re-explaining it.
- Cross-link generously; prefer one explanation plus a link over two explanations that will disagree.

## Project facts and CGP patterns have separate owners

Each fact has one owner, and other documents link to it instead of restating it:

- Keep project facts in [projects/](projects/README.md); link there from elsewhere, because a fact
  stated outside the project's section goes stale.
- Keep CGP patterns in [cgp/](cgp/README.md) and [examples/](examples/README.md); a project links to
  them instead of restating them.

## Registering a document, and adding a section

Every document is registered where readers look for it, in the same change that adds, moves, or
removes it:

- Register a new document in its section `README.md` and in [summary.md](summary.md) in the same
  change.
- Fix the catalog, the summary, and every cross-link when a document is moved, renamed, split, or
  deleted.
- Add a section by creating its directory with a `README.md`, a `writing-guide.md` if its documents
  need rules, a base `README.md` entry, and `summary.md` lines, and list the guide under
  [Task guides](#task-guides).
- Add a new member project to [sibling-projects.md](sibling-projects.md) and the matching file in each
  member repository that carries one.
- Keep this file the base's only `AGENTS.md`; put a section's rules for its documents in its writing
  guide.

## Keeping summary.md honest

`summary.md` indexes every document in one line each:

- Keep [summary.md](summary.md) one line per document, in the document's own vocabulary.
- Update it when a document is added, removed, renamed, or repurposed.
- Let the section catalogs carry the fuller framing; keep the summary an index.

## Prose mechanics

These mechanics keep each Markdown file rendering correctly and each diff small:

- Keep the opening and closing backticks of an inline code span on the same line; never break a link
  inside `](...)`.
- Put the fences of a code block on their own lines with a blank line before and after.
- Reflow only the paragraph being edited; leave the rest alone.
- Leave a line long when it cannot be wrapped without breaking a code span or link.

## Show the example behind an error message

An error message is quoted only beside the code that produces it:

- Show the code that triggers a diagnostic in the same document.
- Say what it wires or declares, then name the mistake the message is really about.
- Do not quote an error with no example behind it.

## Ask when in doubt

When a choice has more than one defensible answer, ask the user instead of guessing:

- Surface a question whenever a behavior, a corner case, a document's home, or a decision is
  ambiguous.
- Do not write a guess into a document, its catalog, the summary, or the skill.

## Committing changes

Commits happen only on the user's request:

- Commit only when the user explicitly asks for one commit of the changes then in the working tree.
- Never commit as a side effect of finishing a task.
- Never bring commits up yourself; answer plainly if asked.
- Treat a commit request as one-shot, never a standing mode.
- Always commit on the current branch.
