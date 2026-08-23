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
**corrections** are single-line changes that are wrong today and cheap to fix. The **rewrites** are
existing pages whose content is sound but whose shape or framing is not. The **new pages** are the
largest items and depend on the guides that specify them. Which of them to do first, and which depend on
which, is in [tasks.md](tasks.md) rather than here.

## Corrections — single lines, wrong today

These are the cheapest items on the list and several are actively misleading. None of them requires a
decision.

**The site tagline in the Docusaurus configuration still reads "Modular programming paradigm for
Rust."** This is the retired framing, and "modular" as a lead word is specifically retired by
[identity.md](../communication-strategy/identity.md). Replace with the settled line. *Website repo,
`docusaurus.config.ts`; see [site-structure.md](site-structure.md).*

**The announcement bar promotes the v0.7.0 release.** It is hardcoded rather than derived from the newest
post, so it goes stale silently with every release, and it is the site's most prominent single piece of
copy. *Website repo, `docusaurus.config.ts`.*

**The Hello World tutorial pins `cgp = "0.7.0"`.** The site's material is written against
[v0.8.0](../releases/v0-8-0.md), so `"0.8.0"` is the pin to carry. It does not resolve on crates.io until
the release ships, which ties this correction to the release rather than making it wrong: the tutorials
are correct the moment v0.8.0 is published, and until then a reader who wants to follow along needs a git
dependency on `main`, which is how every ecosystem repository tracks the library. *Website repo,
`docs/tutorials/hello.md`; see [tutorials/hello-world.md](tutorials/hello-world.md) and
[tasks.md](tasks.md).*

**The Resources page omits `cargo-cgp` entirely.** This is the most consequential single omission on the
site: the error toolchain is the direct answer to the most-cited obstacle to adopting CGP, and Resources
is where an evaluator looks for it. *Website repo, `docs/resources.md`.*

**The Resources crate list is incomplete and inconsistent.** It names `cgp-error-anyhow` but not
`cgp-error-eyre` or `cgp-error-std`, and lists `cgp-serde` by GitHub URL rather than its crates.io entry.
*Website repo, `docs/resources.md`.*

**The Introduction's status section is dated "As of 2025".** CGP is now at v0.8.0. This is resolved by
the *Project status* page below, but the year-stamp should go either way. *Website repo,
`docs/index.md`.*

**The Introduction routes newcomers to the blog as the most current material.** That was true before the
tutorials existed and is now the weaker answer, since the blog is the least current body of writing on
the site. Point at the tutorials first. *Website repo, `docs/index.md`; see
[blog/README.md](blog/README.md) for the drift that makes this urgent.*

**The Hermes SDK sits in a bare list at the bottom of Resources.** It is the real, non-trivial system CGP
was built for and the strongest social proof available to the evaluator profile, and it is presented as
one link among eight. *Website repo, `docs/resources.md`; see
[evidence.md](../communication-strategy/evidence.md).*

## Rewrites — pages whose shape or framing is wrong

**The front page needs rebuilding against its guide.** It diverges in six concrete ways: the hero
headline leads with "modular" and does not use the tag line; there is no reassurance line and no install
command; the feature grid has six entries, two leading with retired words, and disagrees with the
Overview's five; the code example does not show the implementation Rust rejects, so the reader never sees
the contrast — **and it does not compile**, since it writes `#[cgp_impl(HashWithDisplay)]` without `new`
and never declares the provider struct; the problem cards are generic and unanchored; and **there is no
cost section at all**, which on a page for this audience is the most consequential omission of the six.
The "Ready to Get Started?" block is template filler and should become the routing section. *Website
repo, `src/pages/index.tsx` and `src/components/HomepageFeatures/`; spec in
[writing-guides/homepage.md](writing-guides/homepage.md), and the snippet defect recorded in
[site-structure.md](site-structure.md).*

**The site carries three disagreeing feature lists.** The front page names six capabilities, the Overview
names five, and [identity.md](../communication-strategy/identity.md#the-headline-feature-set) curates a
different five. The fix is not to make all three identical: the **front page** carries the curated five,
and the **Overview** — whose job is the detailed feature tour, per
[information-architecture.md](information-architecture.md#the-target-page-inventory) — expands each of
them and adds the breadth capabilities, so it is not capped at five and stops competing with the front
page rather than matching it. *Website repo, front page and `docs/overview.md`.*

**The Overview's depth pointers all lead to the book,** which the Introduction itself describes as not
recently updated — the error-handling section in particular links to a book chapter rather than to
anything maintained. Repoint at the explanation pages once they exist. *Website repo,
`docs/overview.md`.*

**The Overview predates `cargo-cgp` and the extensible-data work,** so its "Dynamic Dispatch" section
understates what CGP now offers for enums. *Website repo, `docs/overview.md`.*

**The Overview names no abstract-types capability and no generic-parameter-threading pain.** These are
absences rather than staleness, and the first is a gap in the page's *job*: it is where the front page's
breadth section offloads, so a capability the breadth line advertises has to appear here, and abstract
types do not. The second is the pain a reader with a deep call graph feels — a signature carrying an error
type, a runtime, and a storage handle through layers that touch none of them — which no entry on the site
currently names. The two are separate additions, one to each half of the page, because a capability and
the pain it removes reach different readers. *Website repo, `docs/overview.md`; the capability payoff and
the before/after are in [message.md](../communication-strategy/message.md), and the record of the gap in
[site-structure.md](site-structure.md).*

**Neither tutorial teaches that wiring is lazy,** mentions
[`check_components!`](../cgp/reference/macros/check_components.md), or mentions
[`cargo-cgp`](../cgp/reference/cargo-cgp.md) — so a reader who mis-wires a context meets a wall of
generated types at a call site with no idea that either mitigation exists. The full fix is the new
tutorial below; the interim fix is the short version in each tutorial that reaches
`delegate_components!`. *Website repo, `docs/tutorials/`; obligation stated in
[writing-guides/tutorial.md](writing-guides/tutorial.md).*

**The area-calculation series shows the non-idiomatic provider form first.** Presenting
`impl<Context> AreaCalculator for Context` before simplifying to `impl AreaCalculator` is pedagogically
deliberate and should stay, but a reader who stops early copies the wrong form — so the page must say
plainly that the second form is the idiom. *Website repo,
`docs/tutorials/area-calculation/static-dispatch.md`.*

**The inlined agent skill is a version behind.** It states v0.7.0 while the library is at v0.8.0, teaches
`#[use_type]` with `::` where current syntax uses `.`, presents `#[derive_delegate]` and nested
`UseDelegate` tables where the current idiom is the `open` statement, does not mention
[namespaces](../cgp/concepts/namespaces.md) at all, and omits `cargo-cgp`. **Fix this in `cgp-skills` and
re-inline the result — never edit the website copy**, which would create a fourth version of the truth.
*`cgp-skills` repo, then website repo; see [site-structure.md](site-structure.md).*

**The v0.8.0 release post is an unfinished draft** that stops mid-argument, covers one feature of
several, teaches an attribute name that changed twice during development, carries a placeholder date, and
opens by claiming a release that has not happened. It must be finished before v0.8.0 ships. *Website
repo, `blog/2026-05-10-v0.8.0-release.md`; the material and the four mechanical items are listed in
[blog/v0-8-0-release.md](blog/v0-8-0-release.md), and the shape is now specified in
[writing-guides/release-announcement.md](writing-guides/release-announcement.md).*

## New pages

Each of these is specified but unwritten. The explanation tier the homepage offloads to is no longer
among them: the **Concepts** section is complete, eighteen pages plus its index, with every page that
shows code backed by the website repository's `example-code/` crate.

**Project status and adoption risk** — lifted out of the Introduction so it can be linked from above the
fold. Its frankness is the asset and must survive the move; what changes is the year-stamp, the absence
of `cargo-cgp`, and the missing incremental-adoption reassurance. **Its home is unsettled**: it is
project meta rather than a CGP idea, so it does not belong under Concepts, and under **Project** beside
Contribute is the obvious alternative.

**A checking and debugging tutorial** — lazy wiring, `check_components!`, and `cargo cgp check`, with one
deliberate failure shown both raw and through the tool. The largest gap in the teaching material and the
natural next part of the area-calculation family. *Spec in
[writing-guides/tutorial.md](writing-guides/tutorial.md); material in
[check traits](../cgp/concepts/check-traits.md) and the [debugging guide](../cgp/guides/debugging.md).*

**An applied-register tutorial** — building something real from an [example](../examples/README.md), for
the reader who evaluates a technology by seeing a realistic system rather than a rectangle. The site has
nothing in this register.

**The construct reference is scaffolded and nearly written** — the pages under `docs/reference/`, of
which 160 are written (`macros/`, `attributes/`, `derives/`, `traits/`, `providers/`, and `components/`
complete) and only the `types/` (5) group carries a one-line description and a stub notice. The
`components/` group split its bundled titles into 17 pages under a `handler/` subsection when ported.
This is still by far the largest item on the list and the one that sets the release date, since the
relaunch waits for it. What the scaffold already buys is that the *index* is complete, so no construct is missing from the
site and no later page has to be retrofitted into the grouping; what remains is the prose, one
subdirectory at a time. Spec and porting procedure in
[writing-guides/reference.md](writing-guides/reference.md); the settled conventions and the current
state are in [site-structure.md](site-structure.md). One dependency is worth repeating: the reference's
*When to use it* sections are where the internal [guides](../cgp/guides/README.md) reach the
public site, since they have no public home of their own.

**Three deep dives** — Hypershell, extensible data types, and cgp-serde: multi-page living documents
replacing the usefulness of the three longest blog posts, whose code is uniformly stale. **These land
after the v0.8.0 relaunch rather than with it**, which is the one part of the target the relaunch does
not carry. Each is planned in [deep-dives/](deep-dives/README.md), and each carries a list of
source-code changes its tracked repository needs first. Two of those lists contain a substantial item:
**adopting `#[uses]` and `#[implicit]` in `hypershell` and `cgp-examples/builder`**, and **publishing a
`CgpSerdeNamespace`**, which is a library improvement rather than a documentation convenience.

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
here is what stops the two documents disagreeing about what to do next. Nothing on this list is waiting
on a decision.
