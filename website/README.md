# The CGP Website

This section is the knowledge base's record of the public CGP website, the Docusaurus site at
<https://contextgeneric.dev> built from the
[`contextgeneric.dev`](https://github.com/contextgeneric/contextgeneric.dev) repository. It
documents nothing about CGP itself: for each page the site publishes, it records what the page says,
how current it is, and which knowledge-base documents an agent reads before touching it. The rules
for its records are [below](#rules-for-records), and the rules for the pages are in the website
repository's [AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md).

## Why the section exists

The website is public and the knowledge base is internal, so a published page cannot link into the
base, apart from the pages that explain the base, within the bounds of
[the one-way link rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links).
The agent maintaining a page still needs the background and current-version facts only the base
holds, so each record here links outward to the page and inward to the reference, concepts,
examples, and communication-strategy documents the page rests on.

The records also track drift. Almost every blog post predates v0.8.0, and several teach syntax the
library no longer accepts, such as `#[cgp_context]`, `cgp_preset!`, the `Async` trait, `ProvideType`,
and `symbol!`. Each blog record names what is stale, so an agent can quote a post's ideas without
copying its dead code or rewriting the post.

## Records and specifications

The section holds two kinds of document:

- **Records** describe a page that exists: what it says, which documents own its material, how far it
  has drifted, and what a revision must keep. Everything under [pages/](pages/README.md),
  [blog/](blog/README.md), [tutorials/](tutorials/README.md), and [projects/](projects/README.md) is a
  record, apart from the Projects plans for pages not yet written.
- **Specifications** describe what the site should be:
  [information-architecture.md](information-architecture.md), [seo.md](seo.md),
  [visual-design.md](visual-design.md), and the [writing guides](writing-guides/README.md).

A guide and a record may disagree during the redesign: the guide states the intent, and the record
names the gap. Read the guide for the page's kind first, then the page's record, then the documents
the record links.

## The document template

A page's record follows this shape:

- A level-one heading and a one-sentence summary of what the page is and where it stands.
- The identifying facts: live URL, source file, publication date and tags, and status.
- How the page was made, for a page that carries a provenance line, not for an older page.
- **What it covers**, **How it relates to the knowledge base**, **Where it diverges from current
  CGP**, and **Maintaining it**.

A tutorial's record replaces the divergence section with its teaching contract. A writing guide does
not follow the template: it states the job, the structure, what must never appear, how a draft is
checked, and the gaps.

## Status words

A record gives its page's status as one of these words:

- **Current:** the page describes CGP as it is now, and its code compiles against v0.8.0.
- **Historical:** the page is a dated record, correct about its own moment, that does not track the
  library.
- **Outdated:** the page presents itself as current guidance but is not; raise it with the author.
- **Draft:** the page is unfinished, either unpublished or published with parts still to write.
- **Superseded:** a later page has replaced it, and it is kept for the record.

## Rules for records

These rules govern the section's own documents; the rules for the published pages are in the website
repository's [AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md).

- Write a page's record to [the document template](#the-document-template), and a writing guide to
  the guide shape the same section gives.
- Give a record's status as exactly one of the [status words](#status-words).
- Link a published page by its live URL, and a source file by a GitHub URL on `main`, never a
  relative path.
- Add a page's record in the same change as the page.
- Record a ported catalog as one record under [pages/](pages/README.md), not one per page, and the
  Projects section one level down, one plan per project.
- Update [information-architecture.md](information-architecture.md) and the page's record as work
  lands; remove a completed entry rather than marking it done.

## The catalog

- [site.md](site.md): the facts every page shares: the build and deployment, the `v0.8.0` release
  branch, the `example-code` crate, and the navigation.
- [information-architecture.md](information-architecture.md): the site as intended: what each surface
  is for, the target page inventory, the sidebar and navigation, and each reader profile's path.
- [seo.md](seo.md): the search and agent-discoverability strategy, from a twelve-month Search Console
  export: the low click-through rate as the measured problem, the terms the site can win, the tag
  line's job, and how the material reaches coding agents.
- [visual-design.md](visual-design.md): the theme: the palette, the tokens, the code themes, the
  fonts, images in both themes, the frame of the site, Docusaurus's layout constraints, and the
  contrast check and screenshots.
- [patterns-book.md](patterns-book.md): the CGP Patterns book, a legacy resource the site's pages leave
  out: which chapters are current, why its CI pin rules out a gradual update, the map from each
  chapter to the page that now owns its material, and the changes left in its repository.
- [writing-guides/](writing-guides/README.md): one guide per kind of page, with the
  [reading map](writing-guides/README.md#the-reading-map) of the strategy and SEO sections each kind
  draws on.
- [pages/](pages/README.md): one record per standalone page and per docs section, from the front page
  to the AI disclaimer.
- [blog/](blog/README.md): one record per blog post, including drafts on branches, with the catalog
  and a drift summary.
- [tutorials/](tutorials/README.md): one record per tutorial series, with its teaching contract.
- [projects/](projects/README.md): the blueprint for the Projects section and one plan per project;
  the Hypershell, cgp-serde, and cgp-examples sections are partly written, and the error-backend
  pages are planned.
