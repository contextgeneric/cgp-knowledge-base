# AGENTS.md — the CGP knowledge base

This file governs how to write and maintain every document in this repository. Read
[README.md](README.md) first for what the knowledge base is and how it is organized, and
[summary.md](summary.md) to see what already exists. The rules here apply to the whole base; a
section adds its own rules in its own `AGENTS.md`, and those build on these rather than replacing
them.

The sections with rules of their own are the two member directories and the outward-facing sections:
[cgp/AGENTS.md](cgp/AGENTS.md) for the CGP library's documentation (and, nested under it,
[cgp/implementation/AGENTS.md](cgp/implementation/AGENTS.md) and [cgp/errors/AGENTS.md](cgp/errors/AGENTS.md)),
[cargo-cgp/AGENTS.md](cargo-cgp/AGENTS.md) for the toolchain's (with
[cargo-cgp/implementation/AGENTS.md](cargo-cgp/implementation/AGENTS.md)),
[examples/AGENTS.md](examples/AGENTS.md) for the worked examples,
[related-work/AGENTS.md](related-work/AGENTS.md) for the outward comparisons,
[communication-strategy/AGENTS.md](communication-strategy/AGENTS.md) for public-facing writing, and
[website/AGENTS.md](website/AGENTS.md) for the public site and the documents that track it. Read the
one that owns what you are about to touch, after this file.

Two sections have no rules of their own and are governed by this file alone:
[projects/](projects/README.md), whose only addition is that its documents stay brief, and
[releases/](releases/README.md), which is the single exception to the document-the-present rule below
and is otherwise bound by this file unchanged.

## Orient before any task

Load the CGP mental model before reasoning about any document here, because every section assumes it.
**Invoke the `/cgp` skill** — it is the authoritative orientation on consumer and provider traits,
`#[cgp_component]`/`#[cgp_impl]`/`#[cgp_fn]`, `delegate_components!`, `HasField`, `UseDelegate`,
check traits, and the vocabulary the whole base is written in. Re-invoke it whenever you move into an
unfamiliar construct. The skill lives in [`cgp-skills`](https://github.com/contextgeneric/cgp-skills)
and is built from this base, so the two must always use the same words for the same ideas.

**Load the `/dual-reader-prose` skill whenever you write or revise prose here**, which is nearly
every task, and follow its convention. A document in this base is read both by an agent scanning for
one fact and by an agent reading a subsystem end to end, and the style serves both: open every
section and every paragraph with a self-contained topic sentence that states its point, then
elaborate. Frame every list with a sentence before it and, where it helps, one after — an orphaned
bullet list serves the scanner and abandons the reader who needs the reasoning. Prefer prose to
bullets unless the content is genuinely a list.

Then read your way in from the top: [summary.md](summary.md) for what exists, the section's
`README.md` for how its documents are cataloged, and the section's `AGENTS.md` for its own rules.
Read the documents a task touches before changing them, and the documents they link to when a change
crosses a boundary.

## The synchronization rule

**A document must stay in sync with the code it describes, and keeping it in sync is part of the
change, not a follow-up.** The source in the member projects is the single source of truth, above any
document here and above the skill. When a change alters a construct's syntax, its expansion, its
defaults, its error behavior, or the way a tool is structured or behaves, revise the matching
document in the same change. A document that describes behavior the code no longer has is worse than
no document, because the next agent will trust it and be misled. Treat a stale document as a bug in
the change that made it stale.

The rule runs in both directions and reaches every view of the same truth. Adding a construct means
adding its document and registering it in the section's catalog; removing one means removing or
superseding its document and updating the catalog; renaming one means fixing every cross-link. The
implementation source, the tests and expansion snapshots that pin it, the reference document, the
implementation document, and the `/cgp` skill are five views of one truth — when they disagree, the
disagreement is a defect, and the code wins. The snapshots are the most mechanical check on whether
a document's expansion is honest: when you doubt what a macro emits, read the snapshot rather than
guessing.

Because this base and the code now live in separate repositories, a code change and its
documentation change land in two working trees. Make both when the sibling checkout is present, per
[sibling-projects.md](sibling-projects.md); when it is absent, state plainly what needs updating
where, so nothing is silently left to drift.

## Verify against the source, not from memory

Read the code before you write about it. A claim about an expansion, a default identifier, an
accepted syntax form, a module layout, or a compiler behavior is a claim about something you can
check, so check it — in the member project's source, in its tests, or by running the tool — rather
than transcribing another document or trusting a recollection. The documents most likely to be wrong
are the ones written from an earlier draft of themselves.

Two kinds of read-only source sit outside the member projects and are worth naming. The Rust
compiler and Clippy checkouts (`../external/rust`, `../external/rust-clippy`) are the ground truth
for how `rustc_driver` and a cargo-wrapping tool actually behave, since those internals shift between
nightlies; cite them, never edit them, and never create a dependency on them. A published crate's
own documentation is the ground truth for its API. Prefer verifying against a source over reasoning
about what it probably does.

## Document the present, not the history

Describe how the code works now, written as though it had always worked that way. Do not record how
it reached its current state: no changelog entries, no version numbers attached to behavior, and no
"renamed from", "previously", "used to", or "no longer" traces. These artifacts accumulate into noise
that ages badly — a reader cannot tell which "recently" is which, and a comparison against a former
state describes something that no longer exists. When you correct a discrepancy, rewrite the prose to
state the current behavior and delete the old wording outright. Git history is where the evolution
lives. The one place a document describes a deviation is a Known issues or limitations section, and
even there the deviation is a current one.

Two sections are exempt, and the exemption is narrow. [releases/](releases/README.md) exists to record
the history this rule keeps out of everywhere else — when a construct arrived, what it was called at
each point, and where it went — because a reader meeting `#[cgp_context]` in old code has nowhere else
to look. [website/blog/](website/blog/README.md) records how far each published post has drifted from
the current release, for the same reason. Neither exemption travels: a reference, concept, guide, or
implementation document still describes only the present, and a construct that no longer exists is
deleted from it rather than annotated. When you need to say what something *used* to be, link to the
release document that says it.

## This repository is public

**This knowledge base is written for an internal audience but published in a public repository, and
those are different things.** "Internal" here means the documents assume the `/cgp` skill, record
unfinished work, and are never linked from the website — not that they are unread by anyone outside
the project. Anyone can read them, and some already do: the `cgp` crate's own documentation links
here. Write every document as though a member of the Rust community will find it, because one may.

Three consequences bind every section, and the first is the one an agent is most likely to breach
without noticing. **Distil public discussion rather than pointing at it.** Community reaction to CGP
is legitimate input to the [communication strategy](communication-strategy/README.md), and the
conclusions drawn from it belong here — but a document records what the reaction *amounts to*, never a
link to the thread it came from and never a quotation attributable to the person who wrote it.
Summarizing a recurring objection is analysis; naming the comment that raised it is finger-pointing,
and it reads that way to the person named. Citations to *published work* that is not itself a reaction
to CGP — a survey, an article, a repository of design notes — are unaffected and remain the way an
audience claim is grounded.

**Never disparage another project, and assume its maintainers are reading.** The rule already governs
public writing; it governs these documents too, for the same reason and now also because they are
visible. A criticism of another crate is fair only where it would be fair said to its author's face.

**Keep material out that would harm someone if read.** Unfinished work and known defects belong here
and are the point of the base. Speculation about individuals, private correspondence, and anything
about the project's finances or plans that has not been said publicly do not.

## Writing links

Where a link points decides how it is written, and the three cases are worth keeping straight.

A link **inside this repository** is a relative path: a sibling document in the same directory is
`name.md`, a document in another directory is `../that-dir/name.md`, and a section index is
`../that-dir/README.md`. Cross-link generously — when a document mentions a construct, an error
class, or an example that another document owns, link it rather than re-explaining it, and prefer one
explanation plus a link over two explanations that will eventually disagree.

A link to **a member project's own tree** — its source, its tests, its manifests, its root
`AGENTS.md` — is always a GitHub URL on the `main` branch
(`https://github.com/contextgeneric/<project>/blob/main/<path>`, or `/tree/main/` for a directory),
never a relative `../../cgp/...` path, so the link resolves for a reader who has only this repository
checked out. When you *read* such a link yourself, prefer the local sibling checkout and fetch the
URL only when it is absent, per [sibling-projects.md](sibling-projects.md).

A **bare mention of a checkout's location** — the path `../cgp`, or a link into the read-only
`../external/rust` compiler source — is a filesystem reference rather than a published link, and it
stays relative. These are directions for an agent working in a local environment, not URLs for a
reader.

## Registering a document, and adding a section

Every document registers itself in its section's `README.md` catalog in the same change that creates
it, so a catalog is never behind its tree, and it registers a one-line summary in
[summary.md](summary.md) in that same change. When you move, rename, split, or delete a document, fix
the catalog, the summary, and every cross-link to it — the change that leaves a dangling link is the
change that broke it.

Adding a whole section means creating its directory with a `README.md` that catalogs it, giving it an
`AGENTS.md` if it needs rules of its own, registering it in the base [README.md](README.md), and
adding its files to [summary.md](summary.md). When the new section documents a new **member project**,
also add that project to [sibling-projects.md](sibling-projects.md) — and to the matching file in
every other member repository, which is what lets each project find the others.

## Keeping summary.md honest

[summary.md](summary.md) exists so an agent can learn, in one read, every file this base contains and
what each one holds. That makes it the file most easily left behind, so treat it as part of the tree
rather than a description of it: a document that is added, removed, renamed, or repurposed is
reflected there in the same change. Keep each entry to one line that says what the document covers,
in the same vocabulary the document itself uses, and let the section catalogs carry the fuller
framing — the summary is an index, not a second set of introductions.

## Prose mechanics

Two mechanical habits keep these documents rendering and reading correctly, and both are easy to
break while editing.

**Keep backticks well formed, and re-check them after every edit.** Keep the opening and closing
backticks of an inline code span on the **same line** — never let a line break fall between them,
which breaks the span. When a sentence with inline code would wrap awkwardly, wrap it elsewhere or
let the line run long; do not split the span. Put the fences of a code block on their own lines with
a blank line before the opening fence and after the closing one, so the block is recognized rather
than folded into the surrounding paragraph. The same applies to a markdown link: never break a line
inside its `](...)` destination. After editing any document, read the text back and confirm every
backtick and every link is intact.

**Reflow long lines lazily, as you edit.** Prose in this base is wrapped at roughly 100 columns, but
the wrapping is a convention rather than an invariant, and some lines run over — most often where a
long GitHub URL replaced a short relative path, or where a single unbreakable URL exceeds the width
on its own. Do not sweep the base to reflow them: re-wrap the paragraph you are already editing, and
leave the rest alone. A line that cannot be wrapped without breaking a code span or a link stays
long, per the rule above.

## Show the example behind an error message

When a document mentions a diagnostic tied to a specific example, include that example's code and
explain both what it does and what root cause produces the message. A reader who meets a rewritten
`[CGP-Exxx]` headline or a raw compiler error should be able to see, in the same document, the small
program that triggers it — the `delegate_components!` block, the provider impl, the `check_components!`
entry — rather than reconstruct it from the message. Show the snippet, say what it wires or declares,
then name the mistake the message is really about: the field the context never derives, the component
it omits, the redirect that resolves to nothing. An error quoted with no example behind it cannot be
checked or understood, and the point of this base is to explain *why* an error reads the way it does.

## Committing changes

Git commits are made **only when the user explicitly asks for one**, and each such request authorizes
exactly one commit of the changes then in the working tree. This rule is absolute and overrides any
general default.

- **Never commit unless explicitly asked.** Do not commit as a side effect of finishing a task or
  "wrapping up". If the work is done and the user has not asked, leave the changes uncommitted.
- **Never bring commits up yourself.** Uncommitted work is the normal, expected state, so it is not
  news: do not report commit status, do not ask whether to commit, and do not hint that committing is
  the next step. Answer plainly if the user asks — the rule is against volunteering it.
- **A commit request is one-shot, never a standing mode.** "Commit the changes" means commit the
  current changes, this once; it does not turn on automatic committing.
- **Always commit on the current branch.** Do not create or switch branches, even when the current
  branch is the default one.

## Ask when in doubt

Surface a question rather than guessing whenever something should be settled before the next step is
taken — an ambiguous intended behavior, a corner case whose correct outcome is unclear, a design
choice with more than one defensible answer, or a document whose right home is genuinely unclear. A
wrong assumption baked into a document, its catalog, the summary, and the skill is expensive to
unwind.
