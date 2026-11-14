# AGENTS.md: the CGP website

Read [README.md](README.md) for the section and the base-wide [../AGENTS.md](../AGENTS.md) rules.

## The one-way link rule

- Never link a published page into the knowledge base.
- The two hand-written exceptions are `docs/ai/disclaimer.md` and the pages under
  `docs/ai/knowledge-base/`, within the bounds below.
- The disclaimer may link the base's front door and its issue tracker.
- The knowledge-base pages may also link the four top-level entry files (`README.md`, `summary.md`,
  `AGENTS.md`, and `sibling-projects.md`), never a document inside a section; name a section's
  directory in prose instead.
- The published skill pages under `docs/ai/skills/` may cite this base by deep GitHub URL, because
  nobody hand-writes them; no other page may link there.
- Do not correct these links or extend the exception to another page.
- Link a published page by its live URL, and a source file by a GitHub URL on `main`, never a relative
  path.

## Leave legacy resources off public pages

- Do not link, list, or recommend the CGP Patterns book or the Hermes SDK on a public page, or direct
  a page to present either.
- Point a reader who wants a first-principles explanation or a real system at the site's Concepts and
  Projects pages.
- Leave the book's record, the project history, and the blog records that mention them as they are.
- Raise a page that already mentions one with the author.

## The agent skill is published as a snapshot

- Never edit a page under `docs/ai/skills/`; they are symlinks into the `cgp-skills` submodule.
- Never bump the submodule pointer; it is the author's decision.
- Read the `../cgp-skills` checkout for what the skill says, and treat the published snapshot as
  current: a lagging snapshot needs no issue, note, or fix.

## Consult communication-strategy before writing public prose

- Read the shared set and the page kind's row of the
  [reading map](writing-guides/README.md#the-reading-map) before outlining or drafting a page, and a
  strategy document whole when the page makes a claim its row does not cover.
- Read the page's [writing guide](writing-guides/README.md) and the page's own record, and read
  [information-architecture.md](information-architecture.md) before adding or moving a page.
- Read [author-personality.md](../communication-strategy/author-personality.md) and
  [voice-and-register.md](../communication-strategy/voice-and-register.md) before any prose, and
  [message.md](../communication-strategy/message.md) whenever a page makes a claim about what CGP
  is good for, satisfying its pain, strength, objection, and boundary.
- Name Context-Generic Programming in each page's prose and relate a short form of the tag line to its
  content, following the
  [naming rule](../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page); the
  skill pages and the published blog posts are exempt.
- Write every public page in natural-writing's natural style unless its kind's writing guide names
  another; write this base's documents in point-first style.
- Never publish an invented benchmark, adoption figure, or quotation.
- Never disparage another crate or language to elevate CGP.
- Concede a genuine cost beside the benefit wherever the audience will look for it.

## Layer the depth; do not omit the advanced material

These rules govern public pages, not this base's documents.

- Cover everything the subject supports; let the layers set the order a reader meets things, and
  resolve the tension with structure rather than omission.
- Cover every syntax form, option, and default a construct accepts on its reference page, which is
  the only public source for it.
- Say what replaced a legacy form, and put an advanced form lower on the page rather than off it.
- Carry an idea completely on an explanation page, including the hard parts.
- Let a tutorial select its material, deferring what it leaves out to a linked page.
- Enumerate forms against the parser, not the previous draft, and say when forms combine.

## Verify code against current CGP, and never against a blog post

- Invoke the `/cgp` skill and verify every snippet against the `cgp` source or its tests.
- Prefer the idioms the guides teach, and draw on [examples/](../examples/README.md).
- Say which of CGP's three context shapes a page's code is in, using the qualifiers in
  [vocabulary.md](../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target); an
  introductory page may record the shape in its record instead.
- Let a concept page cut a project's scenario down to what the concept needs; its code must still
  compile, and need not match the project.
- Put a page's code in the website repository's `example-code/` crate, one module per heading, and run
  its tests after changing a page's code; do not mirror this base's own snippets there.
- Fill an elided body with a comment saying so, write a rejected snippet as a compile-fail fixture, and
  prefer duplication between files over a shared helper neither page shows.
- Treat a page without an `example-code` file as unvisited, not unverified, and check generated code
  with `cargo cgp expand`, which the crate does not replace.
- Verify a Projects page against the project's repository at the revision its plan records, by
  comparing each snippet and running each program; give it no `example-code` file.
- Never take current syntax from an existing blog post; read the post's divergence section first, and
  use the [removal ledger](../releases/README.md) when a construct's age is the question.

## Do not rewrite history

- Never edit a published blog post into agreement with current CGP; edit one only when its record says
  it was published unfinished.
- Annotate a misleading post, supersede it, or record the drift in its record, as the author chooses;
  record the drift by default for release notes.
- Never change a published post's `slug`, and never rewrite a snippet in it.
- Add a `:::note` notice to each post that presents a project or a feature its pages document, once
  that section is written: the post the section grew out of, the series posts that explain the
  feature's internals, and a talk that used the project as its demonstration.
- Place the notice directly under the front matter, or under the post's title where it has one, so the
  blog's excerpt shows it.
- Write the notice in the project voice, say where the code predates the current design, and link the
  project section and its Concepts page.
- Correct a page under `docs/` in place, without a changelog note.

## The redesign lands on a release branch, all at once

- Commit redesign work to the website repository's `v0.8.0` branch, never to `main`, where a push
  deploys the site.
- Write every page as though `cgp` v0.8.0 and `cargo-cgp` v0.1.0 have shipped; name `0.8.0` and
  `0.1.0`, and never a pre-release.
- Raise with the author a correction that must reach readers before the release, rather than deciding
  alone; it is the one change that also goes to `main`.

## Who drafts a page, and who reads it before it publishes

- Let agents draft the pages.
- Have the author read, in full, before publication: the front page, every Concepts page, the
  reference index, the AI disclosure page, the knowledge-base documentation page, every blog post, and
  the two comparison sections *What each approach costs* and *Where the other tool is the better
  choice*.
- Ship everything else on the guides plus a spot check.
- Flag a judgement call for the author's reading rather than deciding alone.
- Change this list and [ai-disclosure.md](../communication-strategy/ai-disclosure.md), which states it
  publicly, in the same edit.

## Disclosing AI use on a page

- Add one provenance line at the foot of each page written or substantially rewritten, linking the
  section of the AI disclosure that matches how it was made, and record the level in the page's record.
- Leave the front page without a provenance line, as the disclosure page states.
- Add no note to an existing page unless the author asks, and do not sweep retroactively.
- Add no note to a scaffolded stub; add it when the page is written.
- Keep the disclosure to the website; other repositories get theirs after the redesign.

## Records and their status

- Write a page's record to [the document template](README.md#the-document-template), and a writing
  guide to the guide shape the same section gives.
- Give a record's status as exactly one of the [status words](README.md#status-words).

## Registering a document

- Register every new document in its immediate index and in [../summary.md](../summary.md) in the same
  change.
- Add a page's record in the same change as the page.
- Record a ported catalog as one record under [pages/](pages/README.md), not one per page, and the
  Projects section one level down, one plan per project.
- Add a writing guide before adding a page of a kind the site has not published.
- Update [information-architecture.md](information-architecture.md) and the page's record as work
  lands; remove a completed entry rather than marking it done.
