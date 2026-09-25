# Redesign queue

This document is the consolidated list of what is currently wrong with, or missing from, the CGP
website. Everything in it is recorded somewhere else already — in a page's own document, in a writing
guide, or in [information-architecture.md](information-architecture.md) — and gathering it here answers
a question none of those can: *what is the next thing to do, and how much does it cost?*

It exists because the redesign spans four kinds of change across several repositories, and a defect
recorded next to the page it affects is invisible to someone deciding where to start. Entries are
removed as they land rather than marked done, and **when the list is empty this document is deleted**,
per the base's [document-the-present rule](../AGENTS.md#document-the-present-not-the-history). The
detail behind each entry stays in its home document; what is here is the one-line statement, the cost,
and the pointer.

**This document is the diagnosis; [tasks.md](tasks.md) is the plan.** The two are kept apart because two
lists of outstanding work would drift: an entry here says what is wrong with a page and why, while a task
there names where the change lands, what blocks it, and what "done" means. Every entry below has a task,
and the dependency graph, the ordering, and the open decisions all live there.

## How to read the entries

Each entry names **where the change is made**, since not all of them are in the website repository. Most
are in [`contextgeneric.dev`](https://github.com/contextgeneric/contextgeneric.dev); one is in
[`cgp-skills`](https://github.com/contextgeneric/cgp-skills) and must never be fixed in the website copy;
and a few are knowledge-base documents that need updating in the same change.

Entries are grouped by cost rather than by page, because cost is what decides the order. The
**rewrites** are existing pages whose content is sound but whose shape or framing is not; the **new
pages** are the largest items and depend on the guides that specify them. Which of them to do first, and
which depend on which, is in [tasks.md](tasks.md) rather than here.

## Rewrites — pages whose shape or framing is wrong

**The front page needs rebuilding against its guide.** It diverges in six concrete ways: the hero
headline leads with "modular" and does not use the tag line; there is no reassurance line and no install
command; the feature grid has six entries, two leading with retired words, and disagrees with the
Overview's feature tour; the code example does not show the implementation Rust rejects, so the
reader never sees the contrast — **and it does not compile**, since it writes `#[cgp_impl(HashWithDisplay)]` without `new`
and never declares the provider struct; the problem cards are generic and unanchored; and **there is no
cost section at all**, which on a page for this audience is the most consequential omission of the six.
The "Ready to Get Started?" block is template filler and should become the routing section. *Website
repo, `src/pages/index.tsx` and `src/components/HomepageFeatures/`; spec in
[writing-guides/homepage.md](writing-guides/homepage.md), and the snippet defect recorded in
[site-structure.md](site-structure.md).*

**The front page's feature list needs the settled framing.** Its six-feature list should become the
five curated features in [identity.md](../communication-strategy/identity.md#the-headline-feature-set),
with links to the Overview for the broader tour. The Overview expands those features and covers
abstract types, extensible data, and handlers. *Website repo, front page.*

**The area-calculation series shows the non-idiomatic provider form first.** Presenting
`impl<Context> AreaCalculator for Context` before simplifying to `impl AreaCalculator` is pedagogically
deliberate and should stay, but a reader who stops early copies the wrong form — so the page must say
plainly that the second form is the idiom. *Website repo,
`docs/tutorials/area-calculation/static-dispatch.md`.*

**The v0.8.0 release post is an unfinished draft** that stops mid-argument, covers one feature of
several, teaches an attribute name that changed twice during development, carries a placeholder date, and
opens by claiming a release that has not happened. It must be finished before v0.8.0 ships. *Website
repo, `blog/2026-05-10-v0.8.0-release.md`; the material and the four mechanical items are listed in
[blog/v0-8-0-release.md](blog/v0-8-0-release.md), and the shape is now specified in
[writing-guides/release-announcement.md](writing-guides/release-announcement.md).*

## New pages

Each of these is specified but unwritten.

**Project status and adoption risk** — lifted out of the Introduction so it can be linked from above the
fold. Its frankness is the asset and must survive the move; what changes is the year-stamp, the absence
of `cargo-cgp`, and the missing incremental-adoption reassurance. **Its home is unsettled**: it is
project meta rather than a CGP idea, so it does not belong under Concepts, and under **Project** beside
Contribute is the obvious alternative.

**An applied-register tutorial** — building something real from an [example](../examples/README.md), for
the reader who evaluates a technology by seeing a realistic system rather than a rectangle. The site has
nothing in this register.

**Three deep dives** — Hypershell, extensible data types, and cgp-serde: multi-page living documents
replacing the usefulness of the three longest blog posts, whose code is uniformly stale. **These land
after the v0.8.0 relaunch rather than with it**, which is the one part of the target the relaunch does
not carry. Each is planned in [deep-dives/](deep-dives/README.md), and each carries a list of
source-code changes its tracked repository needs first. Two of those lists contain a substantial item:
**adopting `#[uses]` in `hypershell`, and `#[uses]` and `#[implicit]` in `cgp-examples/builder`**, and
**publishing a `CgpSerdeNamespace`**, which is a library improvement rather than a documentation
convenience.

**A blog post on implicit type arguments** — the framing that an abstract type is an implicit *type*
argument, so a type dependency stops being a parameter every layer threads. It is a `deepdive` rather
than a release note: abstract types date to v0.3.0 and `#[use_type]` to v0.7.0, so putting it in the
v0.8.0 announcement would present a reframing as new and set it competing with namespaces, against that
guide's one-change rule. Strictly this is new content rather than a redesign defect, and it is listed
here because it is the one piece of *writing* the queue would otherwise lose track of; its task, its
running example, and the two decisions it still carries are in [tasks.md](tasks.md).

## Also outstanding, outside the site

Four items are recorded here because the redesign depends on them or shares their surface, though the
work is elsewhere.

**The `cgp` crate's own landing page works against the project.** `crates/main/cgp/README.md` is what
crates.io and docs.rs display, and it is a thirteen-line stub telling readers that CGP's constructs are
"still mostly undocumented within Rustdoc", routing them to the book the site itself describes as not
recently updated, and linking the public into this knowledge base. The repository's own root `README.md`
already carries the settled tag line and the curated five features and is visible only on GitHub. This is
a first-contact surface, the fix is small, and it is not a website task — which is the only reason nobody
has owned it. *`cgp` repo.*

**The release-announcement guide is written but untested**, in the sense that no post has yet been
written from it; the v0.8.0 draft is the first opportunity and will show whether the spec holds.

**A substantial blog post sits unfinished on a branch.** The `incoherent-rust` draft is the only piece of
CGP writing aimed at the language-design reader, and it is the one whose value decays, since it answers a
conversation that will not stay live. It is not a redesign defect and is listed here so the queue does not
lose track of it; the record is [blog/incoherent-rust-today.md](blog/incoherent-rust-today.md) and the
task is B2 in [tasks.md](tasks.md).

**Four code bases need modernizing before their deep dives quote them.** The per-repository lists are in
[deep-dives/](deep-dives/README.md); the work is in `hypershell`, `cgp-serde`, and the `builder` and
`expression` crates of `cgp-examples`, and it is genuine library work rather than documentation
housekeeping. Because the deep dives land after the relaunch, so does this.

## Where the ordering lives

The order to do these in, the dependency graph behind that order, and which of them the v0.8.0 relaunch
waits for are all in [tasks.md](tasks.md), which is the redesign's plan. Keeping them there rather than
here is what stops the two documents disagreeing about what to do next. One item on this list waits on a
decision rather than on work: *Project status and adoption risk* has no settled home, and the front-page
rebuild cannot finish until it does.
