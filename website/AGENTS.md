# AGENTS.md: the CGP website

Read [README.md](README.md) for the section and the base-wide [../AGENTS.md](../AGENTS.md) rules.

## The one-way link rule

- Never link a published page into the knowledge base.
- The two hand-written exceptions are `docs/ai/disclaimer.md` and the pages under
  `docs/ai/knowledge-base/`, within the bounds below.
- The published skill pages under `docs/ai/skills/` may cite this base by deep GitHub URL; nobody
  hand-writes them, and another page must not link here.
- The disclaimer may link the base's front door and its issue tracker.
- The knowledge-base pages may also link the four top-level entry files (`README.md`, `summary.md`,
  `AGENTS.md`, and `sibling-projects.md`), never a document inside a section; name a section's
  directory in prose instead.
- Do not correct these links or extend the exception to another page.
- Link a published page by its live URL; link a source file by a GitHub URL on `main`, never a relative
  path.

## Leave legacy resources off public pages

- No public page links, lists, or recommends the CGP Patterns book or the Hermes SDK.
- Point a reader who wants a first-principles explanation or a real system at the site's Concepts and
  Projects pages.
- Do not direct a page to present either resource; the book's record, the project history, and the
  blog records that mention them stay as they are.
- Raise a page that already mentions one with the author.

## The agent skill is published as a snapshot

- Never edit a page under `docs/ai/skills/`; they are symlinks into the `cgp-skills` submodule.
- Never bump the submodule pointer; it is the author's decision.
- Assume the snapshot is current, and read the `../cgp-skills` checkout when you need what the skill
  says.
- Do not treat a lagging snapshot as a defect; it needs no issue, note, or fix.

## Consult communication-strategy before writing public prose

- Read the knowledge base's [communication-strategy](../communication-strategy/README.md) before
  outlining or drafting a page.
- Read the page's [writing guide](writing-guides/README.md) first, and read
  [information-architecture.md](information-architecture.md) before adding or moving a page.
- Read the page's own document for what it currently is.
- Read [author-personality.md](../communication-strategy/author-personality.md) and
  [voice-and-register.md](../communication-strategy/voice-and-register.md) before any prose.
- Read [formats.md](../communication-strategy/formats.md) for the artifact's playbook.
- Read [readers.md](../communication-strategy/readers.md) to name the single reader and the
  comprehension barriers.
- Read [vocabulary.md](../communication-strategy/vocabulary.md) for which term to use, and
  [identity.md](../communication-strategy/identity.md) for a one-sentence description and the
  headline feature set.
- Read [message.md](../communication-strategy/message.md) whenever a page makes a claim about what CGP
  is good for, and satisfy its pain, strength, objection, and boundary.
- Never publish an invented benchmark, adoption figure, or quotation.
- Never disparage another crate or language to elevate CGP.
- Concede a genuine cost beside the benefit wherever the audience will look for it.

## Layer the depth; do not omit the advanced material

- Cover everything the subject supports; the layers control the order a reader meets things, not what
  is left out.
- The site reference is canonical; a construct's page is the only public source, so it must cover
  every syntax form the macro accepts, every option, and every default.
- Say what replaced a legacy form and put an advanced form lower on the page, but keep it on the page.
- An explanation page carries the idea completely, including the hard parts.
- A tutorial may select its material, but defer what it leaves out to a linked page.
- Resolve the tension with structure rather than omission.
- Enumerate against the parser, not the previous draft, and say when forms combine.
- The knowledge base itself needs no such rule; its documents are written for agents.

## Verify code against current CGP, and never against a blog post

- Invoke the `/cgp` skill and verify every snippet against the `cgp` source or its tests.
- Prefer the idioms the guides teach, and draw on [examples/](../examples/README.md).
- A concept page may cut a project's scenario down to what the concept needs; the code still compiles
  and need not match the project.
- Put a page's code in the website repository's `example-code/` crate, one module per heading.
- Fill an elided body with a comment saying so, write a rejected snippet as a `compile_fail` doctest,
  and prefer duplication between files over a shared helper neither page shows.
- Treat a missing `example-code` file as an unvisited page, not an unverified one; it does not replace
  `cargo cgp expand` for generated code, and it is the website's alone.
- Verify a Projects page against the project's repository at the revision its plan records, by
  comparing each snippet and running each program; it gets no `example-code` file.
- Never take current syntax from an existing blog post; read the post's divergence section first, and
  use the [removal ledger](../releases/README.md) when a construct's age is the question.

## Do not rewrite history

- Treat a published blog post as a dated artifact; do not edit it into agreement with current CGP.
- Annotate a misleading post, supersede it, or record the drift in its internal document; the choice
  between them is the author's, and recording the drift is the default for release notes.
- Edit a post only when its document says it was published unfinished.
- Add a `:::note` notice at the top of each post that presents a project or a feature its pages
  document when its section is written.
- Place the notice directly under the front matter, or under the post's title where it has one, so it
  also shows in the blog's excerpt.
- Scope the notice to the post the section grew out of, the series posts that explain the feature's
  internals, and a talk that used the project as its demonstration.
- Write the notice in the project voice, say where the code predates the current design, and link the
  project section and its Concepts page.
- Never change a published post's `slug`, and never rewrite a snippet in it.
- Correct a page under `docs/` in place, without a changelog note.

## The redesign lands on a release branch, all at once

- Write the redesign on the website repository's `v0.8.0` branch, and publish it when that branch
  merges with the release.
- Treat the branch as carrying both `cgp` v0.8.0 and `cargo-cgp` v0.1.0; it merges only after both are
  published.
- Never commit redesign work to `main`; a push to `main` deploys the site.
- Write every page as though the two releases have shipped; name `0.8.0` and `0.1.0`, and never a
  pre-release.
- Raise a correction that must reach readers before the release rather than deciding alone; it is the
  one change that goes to `main` too.

## Who drafts a page, and who reads it before it publishes

- Let agents draft the pages.
- Have the author read, in full, before publication: the front page, every Concepts page, the
  reference index, the AI disclosure page, the knowledge-base documentation page, every blog post, and
  the two comparison sections *What each approach costs* and *Where the other tool is the better
  choice*.
- Ship everything else on the guides plus a spot check.
- Flag a judgement call for reading rather than deciding alone.
- Change this list in [tasks.md](tasks.md) and
  [ai-disclosure.md](../communication-strategy/ai-disclosure.md) in the same edit.

## Disclosing AI use on a page

- Add one provenance line at the foot of a page written or substantially rewritten from now on,
  linking the specific section of the AI disclosure that matches how it was made.
- Do not add a note to an existing page unless the author asks, and do not sweep retroactively.
- Record which level applies in the page's internal document.
- Do not add a note to a scaffolded stub; add it when the page is written.
- Keep this to the website for now; other repositories get their disclosure after the redesign.

## The document template

- Open with a level-one heading and a one-sentence summary of what the page is and where it stands.
- Add the identifying facts: live URL, source file, publication date and tags, and status.
- Add how the page was made for a page written or substantially rewritten from now on, not for an
  older page.
- Develop **What it covers**, **How it relates to the knowledge base**, **Where it diverges from
  current CGP**, and **Maintaining it**.
- Replace the divergence section in a tutorial document with its teaching contract.
- Do not force this template on a writing guide; a guide states the job, the structure, what must never
  appear, how a draft is checked, and the gaps.

## Status vocabulary

- Use exactly one of these five words for a page's status.
- **Current** means the page describes CGP as it is now and its code compiles against v0.8.0.
- **Historical** means the page is a dated record that is correct about its own moment and does not
  track the library.
- **Outdated** means the page presents itself as current guidance but is not; raise it with the author.
- **Draft** means the page is published but unfinished.
- **Superseded** means a later page has replaced it and it is kept for the record.

## Registering a document

- Register every new document in its immediate index and in [../summary.md](../summary.md) in the same
  change.
- Add a page's document in the same change as the page.
- Record a ported catalog as one entry in [site-structure.md](site-structure.md), not one per page.
- Record the Projects section one level down, one plan per project.
- Add a writing guide before adding a page of a kind the site has not published.
- Update [information-architecture.md](information-architecture.md), [redesign-queue.md](redesign-queue.md),
  and [tasks.md](tasks.md) as work lands; remove a completed entry rather than marking it done, and
  delete a document once it is empty.
