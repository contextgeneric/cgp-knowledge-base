# Website deep dives

This directory holds one internal document per **deep dive** — the multi-page, living documents that
develop one substantial CGP project or technique end to end. Each deep dive grows out of a blog post
whose material remains valuable and whose code has gone stale, and each document here records the same
four things: what the deep dive covers, how it is split into pages, what must change from the source
post, and **what must change in the tracked code base** for the deep dive to be written against
current CGP.

None of the three deep dives exists yet. These documents are the plan for writing them, and they are
written before the pages rather than after, per [../AGENTS.md](../AGENTS.md). The page-type
specification is [../writing-guides/deep-dive.md](../writing-guides/deep-dive.md); read it first.

## Why a deep dive rather than a revised blog post

CGP's three richest pieces of writing are blog posts, and blog posts are the wrong container for them.
A published post is a **dated artifact** the site's rules forbid rewriting, so as CGP moves the post
drifts — and all three have drifted badly, predating namespaces, `#[cgp_impl]`, `#[implicit]`, and the
`open` statement between them. A post is also a **single page of extraordinary length**: the Hypershell
announcement runs to roughly 16,500 words.

A deep dive is a different artifact rather than an edit to those. It lives under `docs/`, so
[document-the-present](../AGENTS.md#do-not-rewrite-history) applies and it is corrected in place
forever; and it is split into pages a reader can finish. **The source post stays exactly where it is**,
as the record of what was said at the time, with its own document recording its drift.

## The code bases are ahead of the posts

The most useful fact for anyone starting one of these is that **the tracked repositories have already
been partly modernized**, so a deep dive is not written by patching the post's snippets — it is written
from the live code, with the remaining gaps closed first. All four repositories track `cgp`
`0.8.0-alpha`, and none of them uses the removed preset system, `#[cgp_context]`, or the inside-out
provider form that every source post shows.

They are not equally far along, and the difference decides how much work each deep dive carries.
**Hypershell** is the most modernized: it has a real namespace with path-prefixed components and
contexts that join it in one line, and its remaining gaps are localized. **cgp-serde** is the most
idiomatic at the provider level — the heaviest user of `#[uses]` and `#[use_type]` of the four — and
its tests already wire with `open` and `@`-paths, but it publishes no namespace, so every context
spells out its whole table. The two **cgp-examples** crates are the least modernized: they still read
context fields through getter traits where an `#[implicit]` argument is now the default, and declare
dependencies as hand-written `where Self:` bounds.

Each document below carries the concrete list. Where a change is uncertain, it is marked as such rather
than asserted — one of them, the `UseInputDelegate` tables in the expression example, looks like an
`open` candidate and is not.

## The catalog

- [hypershell.md](hypershell.md) — the type-level shell-scripting DSL. The largest of the three, and
  the one whose source post most needs its embedded CGP primer removed now that the explanation tier
  can carry it. Tracks [`hypershell`](https://github.com/contextgeneric/hypershell).
- [extensible-datatypes.md](extensible-datatypes.md) — extensible records and variants, from the four
  blog posts and two example crates. The only deep dive drawn from a *series* rather than a single
  post, and the one whose tracked code needs the most modernization. Tracks
  [`cgp-examples`](https://github.com/contextgeneric/cgp-examples).
- [cgp-serde.md](cgp-serde.md) — Serde rebuilt as CGP components. The clearest demonstration of the
  coherence bypass on a trait every Rust developer knows. Tracks
  [`cgp-serde`](https://github.com/contextgeneric/cgp-serde).

## The document shape

Each document opens with a level-one heading and a one-sentence statement of what the deep dive is,
then a short framed list of identifying facts — the planned URL, the source post or posts, the code base
it tracks, and its status. It then develops, in prose:

- **What it covers**, and why the material is worth the format.
- **The page split**, with each page's job and roughly its length. This is the section that does not
  exist for any other page type, and it is the main design decision a deep dive makes.
- **What changes from the source post** — the CGP constructs whose treatment must be rewritten, the
  material that moves out to the explanation tier, and the voice conversion.
- **Source-code changes needed**, naming files and line-level constructs, separated into changes the
  deep dive *requires* and changes that would merely improve the code.
- **How it relates to the knowledge base** — the examples, concepts, and reference documents behind it.
- **Maintaining it**, once written.

Register a new document here and in [../../summary.md](../../summary.md) in the same change that adds
it, and record any code change that lands in the tracked repository so the list stays honest.
