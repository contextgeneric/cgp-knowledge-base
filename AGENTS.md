# AGENTS.md: the CGP knowledge base

Follow this file for every task in this repository. Read [README.md](README.md) for what the base is,
and [summary.md](summary.md) for every document it contains.

## Orient before any task

- Invoke the `/cgp` skill before working with CGP constructs, and re-invoke it when you move into an
  unfamiliar construct.
- Load the `/point-first-writing` skill before writing or revising prose, which is nearly every task.
- Read [README.md](README.md), [summary.md](summary.md), the section `README.md`, and the section
  `AGENTS.md` of the section you are about to touch.
- Read the documents a task touches before changing them, and the documents they link to when a change
  crosses a boundary.

## The synchronization rule

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

## Verify against the source, not from memory

- Verify a claim about an expansion, a default, a syntax form, a module layout, or a compiler behavior
  against the source, a test, a snapshot, or a command before writing it.
- Use the Rust compiler and Clippy checkouts under `../external/` as read-only ground truth; cite them,
  never edit them, and never depend on them.
- Read the compiler source from the pinned nightly's `rustc-dev` component when `../external/rust` is
  absent.
- Treat a published crate's own documentation as the ground truth for its API.
- Prefer verifying against a source over reasoning about what it probably does.
- Read the expansion snapshot when you doubt what a macro emits, rather than guessing.

## Document the present, not the history

- Describe current behavior as though it had always worked that way.
- Do not record how the code reached its current state with changelog entries, version numbers attached
  to behavior, or "renamed from", "previously", "used to", or "no longer" traces.
- Rewrite a corrected discrepancy to state the current behavior and delete the old wording.
- Keep a current deviation only in a Known issues or limitations section.
- Exempt only [releases/](releases/README.md) and [website/blog/](website/blog/README.md); when you
  need to say what something used to be, link the release document that records it.

## Document official versions, never pre-releases

- Name `cgp` v0.8.0 and `cargo-cgp` v0.1.0 as the official versions the base describes.
- Update the version rule in every `AGENTS.md` that names them when the official versions change.
- Name official release versions only, never a pre-release.
- Write as though the official version has been published; quote command output with the official
  version.
- Do not name a pre-release, describe how it behaves, compare it with the source, or tell a reader how
  to move off it.
- Yield only to an explicit user instruction to document a particular pre-release.
- Do not apply the rule to a manifest or lockfile; they state what they must to build.

## This repository is public

- Write as though a member of the Rust community will find the document, because one may.
- Distil public discussion into what it amounts to; never link a thread or quote an identifiable
  person.
- Never disparage another project; assume its maintainers are reading.
- Keep speculation about individuals, private correspondence, and unpublished finances or plans out.
- Keep unfinished work and known defects in; they are the point of the base.

## Writing links

- Link inside this repository with a relative path.
- Prefer the local checkout when reading a cross-project link.
- Link a member project's tree with a GitHub URL on `main`.
- Link a project section's project at the branch [sibling-projects.md](sibling-projects.md) records, not
  `main`.
- Keep a bare checkout path and a read-only external source as a relative filesystem reference.
- Link a construct, error class, or example to the document that owns it rather than re-explaining it.
- Cross-link generously; prefer one explanation plus a link over two explanations that will disagree.

## Project facts and CGP patterns have separate owners

- Keep project facts in [projects/](projects/README.md); link there from elsewhere, because a fact
  stated outside the project's section goes stale.
- Keep CGP patterns in [cgp/](cgp/README.md) and [examples/](examples/README.md); a project links to
  them instead of restating them.
- Let a worked example stand alone, even when it develops the same scenario as a project, and never
  present it as a description of the project.
- Match a reproduced project's code to the branch [sibling-projects.md](sibling-projects.md) records.
- Let a concept page use simplified code when the reduction explains the concept better; the code is
  an illustration, not a reproduction, and still uses current idioms and compiles.
- Record a project's older idiom as a change in its `issues.md`, not by modernizing the example alone.

## Registering a document, and adding a section

- Register a new document in its section `README.md` and in [summary.md](summary.md) in the same
  change.
- Fix the catalog, the summary, and every cross-link when a document is moved, renamed, split, or
  deleted.
- Add a section by creating its directory with a `README.md`, an `AGENTS.md` if it needs rules, a base
  `README.md` entry, and `summary.md` lines.
- Add a new member project to [sibling-projects.md](sibling-projects.md) and the matching file in each
  member repository that carries one.
- Add a nested `AGENTS.md` only when its directory has significant rules of its own; otherwise extend the
  parent.

## Keeping summary.md honest

- Keep [summary.md](summary.md) one line per document, in the document's own vocabulary.
- Update it when a document is added, removed, renamed, or repurposed.
- Let the section catalogs carry the fuller framing; keep the summary an index.

## Prose mechanics

- Keep the opening and closing backticks of an inline code span on the same line; never break a link
  inside `](...)`.
- Put the fences of a code block on their own lines with a blank line before and after.
- Reflow only the paragraph being edited; leave the rest alone.
- Leave a line long when it cannot be wrapped without breaking a code span or link.

## Show the example behind an error message

- Show the code that triggers a diagnostic in the same document.
- Say what it wires or declares, then name the mistake the message is really about.
- Do not quote an error with no example behind it.

## Committing changes

- Commit only when the user explicitly asks for one commit of the changes then in the working tree.
- Never commit as a side effect of finishing a task.
- Never bring commits up yourself; answer plainly if asked.
- Treat a commit request as one-shot, never a standing mode.
- Always commit on the current branch.

## Ask when in doubt

- Surface a question whenever a behavior, a corner case, a document's home, or a decision is
  ambiguous.
- Do not bake a guess into a document, its catalog, the summary, and the skill.

## Where the section rules live

- [cgp/AGENTS.md](cgp/AGENTS.md) governs the CGP documentation, and defers to
  [cgp/implementation/AGENTS.md](cgp/implementation/AGENTS.md) and
  [cgp/errors/AGENTS.md](cgp/errors/AGENTS.md).
- [cargo-cgp/AGENTS.md](cargo-cgp/AGENTS.md) governs the tool documentation.
- [examples/AGENTS.md](examples/AGENTS.md), [related-work/AGENTS.md](related-work/AGENTS.md),
  [communication-strategy/AGENTS.md](communication-strategy/AGENTS.md),
  [website/AGENTS.md](website/AGENTS.md), and [projects/AGENTS.md](projects/AGENTS.md) govern their
  sections.
