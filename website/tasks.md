# Website redesign tasks

This document is the **work plan for finishing the CGP website redesign**: every task that remains, what
each one depends on, and the order to do them in. It exists because the redesign spans four repositories
and roughly a hundred pages, and the question an agent or a maintainer actually arrives with is not "what
is wrong with the site" but "what should I start on now, and what will I break if I start there".

It is deliberately a plan rather than a diagnosis, and that division matters because two documents both
listing outstanding work would drift apart. [redesign-queue.md](redesign-queue.md) owns the **diagnosis**
— what is wrong with each page today, why it is wrong, and which document carries the detail.
[information-architecture.md](information-architecture.md) owns the **target**, and the
[writing guides](writing-guides/README.md) own the **specification** for each kind of page. This document
owns only the plan: one short entry per task naming where the change lands, what blocks it, and what
"done" means, with a link to whichever of those three documents carries the substance. When a task's
detail is needed, follow the link rather than restating it here.

## How to read a task

Every task has an ID so that dependencies can be stated without ambiguity, a **lands in** field naming
the repository and path, and a **done when** condition. The IDs group by kind — `C` corrections, `E`
explanation tier, `F` front page, `T` teaching, `R` reference, `D` deep dives, `B` the blog, `V` the
version release, `O` orientation, `X` cross-cutting — and they are stable, so a task removed on completion
leaves its ID retired rather than renumbered.

Three obligations apply to **every** task that adds or moves a page, and they are stated once here rather
than repeated in each entry, per [AGENTS.md](AGENTS.md). Adding a page means **adding or updating its
internal document in the same change**, because a page with no document has no recorded provenance.
Landing a task means **removing its entry from [redesign-queue.md](redesign-queue.md)** rather than
marking it done, and deleting that document once it is empty. And landing a task means **clearing the
matching `new` or `moved` marker** in [information-architecture.md](information-architecture.md), since
the redesign is finished when that inventory and [site-structure.md](site-structure.md) agree.

Three further standing rules bind the content rather than the bookkeeping. Every page is public writing and
is governed by [communication-strategy/](../communication-strategy/README.md) through its writing guide.
Every snippet is bound by the [synchronization rule](../AGENTS.md#the-synchronization-rule): verify
against the `cgp` source and the `/cgp` skill, prefer code already verified in
[examples/](../examples/README.md), and **never** take current syntax from a blog post. And every page
that shows CGP code **says which of the three shapes its example is in** — a value context or an
environmental one, self-targeted or parameter-targeted — because the site's examples span all three and a
reader who generalizes from one and then meets another without being told has no way to say what a context
is. The qualifiers and the four misreadings they prevent are in
[vocabulary.md](../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target); an
introductory page records the shape in its internal document without necessarily using the terms on the
page.

## C — Corrections

Eight single-line changes, all in the website repository, none blocked by anything, and several actively
costing readers today. They are one pass rather than eight tasks in practice, and the detail for each is
in [redesign-queue.md](redesign-queue.md#corrections--single-lines-wrong-today).

- **C1 — the site tagline.** Replace "Modular programming paradigm for Rust." with the settled line from
  [identity.md](../communication-strategy/identity.md). *Lands in:* `docusaurus.config.ts`. *Done when:*
  the configuration, the front page hero, and the README all carry the same line.
- **C2 — the announcement bar.** It promotes v0.7.0 and is hardcoded, so it goes stale silently with
  every release. *Lands in:* `docusaurus.config.ts`. *Done when:* it points at something current.
  **Re-touched by V1**, which repoints it at the v0.8.0 post; fixing it now is still worth it, because V1
  is on a different clock.
- **C3 — the tutorial version pin.** Set it to `cgp = "0.8.0"`, the version the site's material is
  written against. Note that it resolves only once v0.8.0 is published, which couples this to **V1**
  rather than making it wrong; until then a reader following along needs a git dependency on `main`, and
  whether that goes on the page as a one-line note is a presentation call. *Lands in:*
  `docs/tutorials/hello.md`, and every future tutorial. *Done when:* the pin names the version the code
  is written against and re-pinning is on the release checklist.
- **C4 — `cargo-cgp` on Resources.** The single most consequential omission on the site: the error
  toolchain is the direct answer to the most-cited obstacle to adopting CGP, and Resources is where an
  evaluator looks for it. *Lands in:* `docs/resources.md`. *Done when:* the tool, its install command,
  and its purpose appear. **Superseded in part by R3**, which gives the tool a real section; C4 is the
  stopgap and stays valuable as an index entry afterwards.
- **C5 — the crate list.** Add `cgp-error-eyre` and `cgp-error-std`; list `cgp-serde` by its crates.io
  entry. *Lands in:* `docs/resources.md`.
- **C6 — Hermes SDK.** Promote it out of the bare list at the bottom; it is the real non-trivial system
  CGP was built for and the strongest social proof available to the evaluator, per
  [evidence.md](../communication-strategy/evidence.md). *Lands in:* `docs/resources.md`.
- **C7 — the Introduction's year-stamp.** Drop "As of 2025". *Lands in:* `docs/index.md`. **Subsumed by
  E1** if E1 lands first, since the whole status section moves.
- **C8 — the Introduction's routing.** It sends newcomers to the blog as the most current material, which
  was true before the tutorials existed and is now the weakest answer on the site. Point at the tutorials
  first. *Lands in:* `docs/index.md`.

## E — The explanation tier

Four new pages under a new `Understanding CGP` category, specified in full by
[writing-guides/explanation.md](writing-guides/explanation.md). This is the tier the homepage offloads
to, so it is the group that unblocks the most downstream work, and none of it is blocked by anything.

- **E1 — *Project status and adoption risk*.** Mostly a move: lift the "Current Status" section out of
  the Introduction so the homepage can link it from above the fold. Its frankness is the asset and must
  survive the move; what changes is the year-stamp, the absence of `cargo-cgp`, and the missing
  incremental-adoption reassurance. **This task also creates the category** — the directory, its
  `_category_.json`, and the `sidebar_position` front matter — since it is the first page in it.
  *Lands in:* `docs/understanding/` (name per the guide's naming rule) plus `docs/index.md`. *Blocks:*
  F1's second call to action. *Done when:* the page stands alone, the Introduction links to it, and C7 is
  moot.
- **E2 — *Why CGP exists*.** The highest-value page missing from the site and the homepage's most
  frequent destination: coherence as a guarantee, what it costs, the workarounds developers hand-roll,
  and the `Self`-becomes-a-parameter move with local coherence restored. The guide carries the
  five-movement outline. *Blocks:* F1 (better done after, since the rewritten homepage links here most),
  R2's concept-link destinations, and the deep dives' primer removal.
- **E3 — *How CGP works*.** The site's answer to "macros are magic": the two traits, the wiring table,
  what a call resolves to, the plain Rust an expansion produces, and why none of it costs anything at
  runtime. *Blocks:* R2's concept-link destinations, and the deep dives' primer removal.
- **E4 — *When to use CGP, and when not*.** A decision guide rather than an essay, and the page the
  homepage's cost section hands a skeptic. *Blocks:* F1's cost section, which currently has nowhere to
  hand off to.

## F — The front page

- **F1 — rebuild the front page against its guide.** The largest single-page change on the list, and the
  one that most needs its destinations to exist first: the hero and tag line, the reassurance line and
  install command, the settled before/after example and the copy that sells it, the six-section bounded
  essay including the cost section, and the routing section replacing the "Ready to Get Started?" filler.
  *Lands in:* `src/pages/index.tsx` and `src/components/HomepageFeatures/`. *Spec:*
  [writing-guides/homepage.md](writing-guides/homepage.md). *Blocked by:* C1, E1, E2, E4, F2. *Done
  when:* the guide's five draft checks pass.
- **F2 — reconcile the three feature lists.** The front page names six capabilities, the Overview names
  five, and [identity.md](../communication-strategy/identity.md#the-headline-feature-set) curates a
  different five. The reconciliation is not a merge: the **front page** carries the curated five as prose
  beats, and the **Overview** expands each of them and adds the breadth capabilities, so the two lists
  stop competing rather than being made identical. *Lands in:* the front page and the Overview.
- **F3 — repurpose and repair the Overview.** Its job is the **feature tour**: every high-level CGP
  capability walked through in more detail than any other surface carries, which makes it the destination
  for both section 3 and section 4 of the homepage essay. Five changes: state that job and drop the
  five-feature cap, since the cap belongs to the front page; **add the two abstract-types entries the page
  is missing** — a Key Features capability whose payoff is that a type the application chooses *stops
  being a parameter every layer carries*, and a Problems Solved entry for the threading pain itself, kept
  separate because a capability and the pain it removes reach different readers (the copy for both is in
  [message.md](../communication-strategy/message.md), and the gap is recorded in
  [site-structure.md](site-structure.md)); repoint the depth pointers, which all
  currently lead to the [CGP Patterns book](https://patterns.contextgeneric.dev/) that the Introduction
  itself describes as not recently updated; refresh the "Dynamic Dispatch" section, which predates
  `cargo-cgp` and the extensible-data work and understates what CGP now offers for enums; and move the
  file into the `Understanding CGP` category, **carrying `slug: /overview` so `/docs/overview` keeps
  serving** — the [no-plugin policy](site-structure.md) rules out a redirect, so without the slug every
  inbound link 404s. *Blocked by:* E2 and E4, which are what the depth pointers should point at instead,
  and E1, which creates the category.

## T — Teaching

- **T1 — the interim checking note.** Every tutorial that reaches `delegate_components!` should say that
  wiring is lazy, name `check_components!`, and name `cargo cgp check`. This is the cheap stopgap for the
  largest gap in the teaching material. *Lands in:* `docs/tutorials/`. *Blocked by:* nothing. *Superseded
  by:* T2, after which each tutorial keeps only a pointer.
- **T2 — the *Checking and debugging* tutorial.** First-principles register, the natural fourth part of
  the area-calculation family: lazy wiring, `check_components!`, and one deliberate failure shown both
  raw and through `cargo cgp check`, with the tool's youth conceded honestly. The highest-value teaching
  addition and the one that most directly answers the objection that has cost CGP the most readers.
  *Lands in:* `docs/tutorials/area-calculation/`. *Material:*
  [check traits](../cgp/concepts/check-traits.md), the
  [debugging guide](../cgp/guides/debugging.md), and
  [cargo-cgp/reference/usage.md](../cargo-cgp/reference/usage.md). *Blocked by:* nothing.
- **T3 — an applied-register tutorial.** The site has nothing in this register, so the reader who
  evaluates a technology by seeing a realistic system has nowhere to go. Draw the scenario from
  [examples/](../examples/README.md) rather than inventing one. *Blocked by:* nothing hard; it wants R2
  for its link-out targets, so it reads better after the reference exists than before.
- **T4 — the area-calculation idiom note.** The series shows `impl<Context> AreaCalculator for Context`
  before simplifying to `impl AreaCalculator`, which is pedagogically deliberate and should stay — but
  the page must say plainly that the second form is the idiom, because a reader who stops early copies
  the first. *Lands in:* `docs/tutorials/area-calculation/static-dispatch.md`. *Blocked by:* nothing.

## R — The reference and the tooling section

By far the largest item on the list, and the one with a standing completeness obligation once started: a
construct with no page is a hole a reader falls into. The spec and the porting procedure are in
[writing-guides/reference.md](writing-guides/reference.md).

- **R1 — the reference index.** Hand-written, not autogenerated: it opens by naming the handful of
  constructs a newcomer needs, then groups the rest by the job they do. Seventy pages are too many to
  scan, so this page is where the layered-audience promise is kept at the section level. *Lands in:*
  `docs/reference/index.md`. *Blocked by:* nothing, and worth writing **first**, because it fixes the
  grouping every ported page then slots into.
- **R2 — port the construct pages.** Roughly seventy pages under `docs/reference/`, grouped as `macros/`,
  `attributes/`, `derives/`, `components/`, `providers/`, `traits/`, `types/`, each ported from its
  internal document by the guide's four transformations — re-point every link, restructure into the
  layered descent, add *When to reach for it*, and convert the Source section. Two things ride on this
  task beyond the pages themselves: the internal [guides](../cgp/guides/README.md) reach the public site
  **only** through the *When to reach for it* sections, and the internal
  [errors catalog](../cgp/errors/README.md) has no public destination at all (see **R4**). *Blocked by:*
  R1 for grouping, E2 and E3 for the concept links to point at. *Done when:* every construct the `cgp`
  crate exports has a page or a named place inside a consolidated one.
- **R3 — the tooling section.** `cargo-cgp` gets its own top-level docs section beside the reference
  rather than inside it, since every other reference page answers "what does this construct mean".
  *Material:* [cargo-cgp/reference/](../cargo-cgp/reference/README.md). *Blocked by:* nothing, and it is
  small — worth doing early, since it is what C4, T2, and the homepage's cost section all point at.
- **R4 — design a public home for the error catalog.** Currently unowned work rather than a task with a
  spec: seventeen internal error-class documents have no public counterpart, so a reference page's
  *Gotchas* section inlines what it needs and a reader who hits a wiring failure has nowhere on the site
  to look it up. Decide the page type before R2 finishes, so the *Gotchas* sections do not all have to be
  revisited. *Blocked by:* nothing. *Precedes:* a writing guide for the page type, per
  [AGENTS.md](AGENTS.md).

## D — The deep dives, and the code they quote

Three multi-page living documents, each planned in [deep-dives/](deep-dives/README.md) and each blocked
by modernization work in the repository it tracks. **The code tasks are genuine library work, not
documentation housekeeping**, and they come first: a deep dive written against the current code would
show forms the guides tell readers not to write.

- **DC1 — modernize `hypershell`.** Adopt `#[uses(...)]` for its eight hand-written `Self:` bounds and
  `#[implicit]` for its context-field reads, replace the one live `UseDelegate` table in
  `providers/pipe.rs` — verifying first whether `open` accepts a bounded generic key — drop the six
  `#[derive_delegate(UseDelegate<Arg>)]` attributes, whose removal is breaking for downstream users and is
  accepted, and fix the two example comments describing the removed `#[cgp_inherit]`. *Lands in:* the
  `hypershell` repository.
- **DC2 — modernize the two `cgp-examples` crates.** The least modernized of the four: convert
  `builder`'s six getter traits to `#[implicit]` arguments, adopt `#[uses]` across both crates, and
  replace the `Code`-keyed `UseDelegate` tables with `open`. **Leave the `UseInputDelegate` tables and
  the `#[derive_delegate]` attribute they resolve through alone** — they key on `Input` and have no `open`
  equivalent, so they are the correct current form, and this is the one exception to the
  `#[derive_delegate]` removals in DC1 and DC3. *Lands in:* the `cgp-examples` repository.
- **DC3 — publish a `CgpSerdeNamespace`, and drop the three `#[derive_delegate]` attributes.** The
  namespace is a design decision about what the defaults should be rather than a mechanical conversion,
  and a genuine library improvement: without it every context spells out a dozen wiring entries, and the
  deep dive's payoff — two applications differing by a handful of lines — is far weaker. The attribute
  removals are breaking for downstream users and are accepted. *Lands in:* the `cgp-serde` repository.
- **DD1 — the Hypershell deep dive.** Six pages. *Blocked by:* DC1, and by E2/E3, which is where the
  post's embedded CGP primer goes instead of being re-taught. **This task also creates the `Deep dives`
  category.**
- **DD2 — the extensible data types deep dive.** Seven pages, from four blog posts and two example
  crates. *Blocked by:* DC2, E2/E3. Note that this is the deep dive serving the
  [least well-served reader](information-architecture.md) — the framework and library author.
- **DD3 — the cgp-serde deep dive.** Five pages. *Blocked by:* DC3, E2/E3.

Each of DD1–DD3 finishes the same way: **a pointer to the deep dive is added at the top of the blog post
it grew out of** — four posts in DD2's case. That is the one sanctioned edit to a published post, since it
adds a link and changes no claim; the post's slug and its snippets are untouched.

## B — The blog

One planned post, and the group exists so that a piece of writing which is neither a release note nor a
multi-page deep dive has somewhere to be tracked. Everything here is **new content rather than a redesign
defect**, so it is startable at any time and blocks nothing.

- **B1 — the implicit-type-arguments post.** The framing that an abstract type is an implicit *type*
  argument: a generic parameter is an input the caller supplies and so propagates through every
  intermediate signature, while an abstract type is determined by the context and propagates nowhere, so a
  codebase can accumulate type dependencies without its signatures growing. *Lands in:* `blog/`, tagged
  `deepdive`, author voice, with an explicit `slug` and a `{/* truncate */}` marker per the
  [publication conventions](blog/README.md). *Spec:* the deep-dive playbook in
  [formats.md](../communication-strategy/formats.md); the pain, the capability, and the audience-tuned
  one-liner are in [message.md](../communication-strategy/message.md), the mechanism in
  [impl-side dependencies](../cgp/concepts/impl-side-dependencies.md#type-dependencies-and-why-they-need-no-parameter)
  and [abstract types](../cgp/concepts/abstract-types.md), the prescriptive decision in
  [naming a type dependency](../cgp/guides/naming-a-type-dependency.md), and the related-work comparison in
  [implicit parameters](../related-work/implicit-parameters.md). *Blocked by:* nothing. *Blocks:* nothing.

  Four things about its shape are already settled. **Not a release note**, for the reason in
  [redesign-queue.md](redesign-queue.md): the capabilities are old, so a release framing would misreport
  them as new and compete with namespaces for v0.8.0's one change. **Title in the concrete-capability
  register** with no paradigm name, per [vocabulary.md](../communication-strategy/vocabulary.md).
  **One running example the whole way through**, and the database-and-transaction scenario is the one to
  use: it is already verified as compiling code, it is the environmental/self-targeted shape most CGP code
  is in, and `Db` → `Transaction` is a two-step climb that motivates the *second* forcing condition — two
  types that must agree — rather than only the first. And **reuse the v0.7.0 post's "Isn't this just Scala
  implicits?" section** rather than reinventing it, which [formats.md](../communication-strategy/formats.md)
  already names as the model of concede-then-distinguish.

  Two decisions remain open. Whether to include the **`mtl` functional-dependency comparison** —
  `class MonadReader r m | m -> r` fixes the environment type *by* the monad, which is the same
  output-not-input move — since it is the strongest argument for the functional-programming reader,
  showing CGP reaching for a discipline they already trust rather than a novelty, but costs a paragraph
  most readers will skip; the suggestion is to include it late, after the payoff has landed. And whether
  the post ships **before or after v0.8.0**: it is independent of the release, so the only argument for
  waiting is not competing with the announcement for attention.

## V — The version release

- **V1 — finish the v0.8.0 release announcement.** On its own clock and independent of everything above,
  because shipping a release with an unfinished announcement is worse than any item on this list. The
  draft stops mid-argument, covers one feature of several, teaches an attribute name that changed twice
  during development, carries a placeholder date, and opens by claiming a release that has not happened.
  Its motivation section is the strongest part and needs no change. *Lands in:* `blog/`. *Spec:*
  [writing-guides/release-announcement.md](writing-guides/release-announcement.md); material and the
  mechanical items in [blog/v0-8-0-release.md](blog/v0-8-0-release.md) and
  [releases/v0-8-0.md](../releases/v0-8-0.md). *Blocked by:* the release shipping. *Re-touches:* C2 (the
  announcement bar) and C3 (every tutorial's version pin). *Note:* this is the first post written from
  the release-announcement guide, so it is also the guide's first test — record what the spec got wrong.

## O — Orientation

- **O1 — write the orientation-page writing guide.** The site has no spec for the pages whose job is
  routing rather than teaching, and [writing-guides/README.md](writing-guides/README.md) defers it until
  the need arises. The need has arisen twice over: the Introduction and Resources are both being rewritten
  by C4–C8 and E1, and O2 adds a page of a kind the site has not published, which
  [AGENTS.md](AGENTS.md) requires a guide for **before** the page rather than after. It should cover the
  Introduction, Resources, and the Quickstart. *Blocked by:* nothing. *Blocks:* O2.
- **O2 — the Quickstart page.** Install and one working program, with no concepts and nothing to
  understand: the low-commitment landing the front page's first call to action and every launch post ask
  for. It is deliberately smaller than the [Hello World tutorial](tutorials/hello-world.md), which teaches
  one durable idea — this page only proves the thing runs, which is why it is orientation rather than a
  third tutorial. *Lands in:* `docs/`, second in the sidebar after the Introduction. *Blocked by:* O1.
  *Blocks:* F1's first call to action, which points at Hello World until this exists.

## X — Cross-cutting

- **X1 — update the agent skill and re-inline it.** The published copy states v0.7.0, teaches
  `#[use_type]` with `::` where current syntax uses `.`, presents `#[derive_delegate]` and nested
  `UseDelegate` tables where the idiom is `open`, never mentions
  [namespaces](../cgp/concepts/namespaces.md), and omits `cargo-cgp`. It should also carry two
  clarifications settled since: that [`#[uses]`](../cgp/reference/attributes/uses.md) applies to ordinary
  Rust traits and not only to CGP capabilities, and the
  [context and target qualifiers](../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target),
  since the skill's own examples span a value context (`Person: CanGreet`) and an environmental one
  without distinguishing them. **Fix it in `cgp-skills` and re-inline the result; never edit the website
  copy**, which would create a fourth version of the truth. *Lands in:* the `cgp-skills` repository, then
  the website repository. *Blocked by:* nothing.

## What depends on what

The table below is the dependency graph in one view. Read it to check whether a task is startable; read
the [ordering](#the-ordering) for what to start on.

| Task | Blocked by | Blocks |
|---|---|---|
| C1–C8 | nothing | C1 → F1; C3 completed by V1 |
| E1 | nothing | F1, F3 (it creates the category) |
| E2, E3 | nothing | F1 (E2), F3 (E2), R2, DD1–DD3 |
| E4 | nothing | F1, F3 |
| F2 | nothing | F1 |
| F3 | E1, E2, E4 | nothing |
| F1 | C1, E1, E2, E4, F2, O2 (soft) | nothing |
| T1 | nothing | nothing (superseded by T2) |
| T2, T4 | nothing | nothing |
| T3 | nothing hard; reads better after R2 | nothing |
| R1 | nothing | R2 |
| R2 | R1, E2, E3 | T3 (soft), R4 (soft) |
| R3 | nothing | nothing (C4, T2 point at it) |
| R4 | nothing | R2's *Gotchas* sections (soft) |
| DC1, DC2, DC3 | nothing | DD1, DD2, DD3 respectively |
| DD1, DD2, DD3 | their DC task, plus E2 and E3 | nothing |
| B1 | nothing | nothing |
| V1 | the v0.8.0 release shipping | completes C3; re-touches C2 |
| O1 | nothing | O2, and the Introduction narrowing (soft) |
| O2 | O1 | F1's first call to action (soft) |
| X1 | nothing | nothing |

Three shapes in that graph are worth naming, because they are what make the ordering non-obvious. The
**explanation tier is the hub**: E2 and E3 are prerequisites for the front page, the reference, and all
three deep dives, which is why building them early converts into progress everywhere else. The **deep
dives are gated on code** rather than on writing, so their long lead time starts with DC1–DC3 and those
can run in parallel with anything. And **V1 is on a separate clock**, so it interrupts the sequence
whenever the release ships rather than waiting for a slot. **B1 sits outside the graph entirely** — it is
new content rather than a redesign defect, so it neither waits for anything nor holds anything up, and it
can fill a slot whenever the writing appetite is there rather than the editing appetite.

## The ordering

**First, the corrections (C1–C8), in a single pass.** They are wrong today, they cost minutes, and two of
them — the missing `cargo-cgp` entry and the stale tagline — are actively costing the project readers.

**Then E1 and E2, in that order.** E1 is mostly a move of text that already exists, unblocks the homepage's
second call to action, and creates the category the rest of the tier and F3 need; E2 is the page the
rewritten homepage links to most, so the homepage rewrite goes better after it exists than before. Then E4,
which the homepage's cost section needs, and E3, which nothing above the fold needs but the reference does.

**Then O1 and O2**, which are small and give the front page its first call to action a real destination.

**Then F2 and F3, then F1.** F2 and F3 settle what the Overview is before the front page is rebuilt against
it, and F1 is the largest single-page change and the one that most needs its destinations in place.

**Then T2, the checking tutorial** — the highest-value teaching addition, and the one that most directly
answers the objection that has cost CGP the most readers. T1 and T4 are cheap enough to fold into the
corrections pass if convenient.

**Then R3 and R1, then R2.** R3 is small and is what several earlier tasks point at, so it is worth
pulling forward; R1 fixes the grouping before seventy pages are ported into it. R2 is then a long,
mechanical, parallelizable stretch with a completeness obligation, and it is the right work to run
alongside anything else.

**Start DC1–DC3 whenever there is capacity**, since they are independent of everything above and are the
long lead time on the deep dives. Then DD1–DD3 as each one's code and E2/E3 are ready.

**Interrupt for V1 whenever the release ships.**

X1 fits anywhere and is worth doing early, since a stale published skill misteaches every agent that
reads it.

## The one residual risk

Everything above is startable, and no task is waiting on a decision. One coupling is worth watching rather
than resolving: **C3 pins `cgp = "0.8.0"` against a release that has not shipped**, so a tutorial that goes
live before V1 does not resolve for a reader who copies its `Cargo.toml`. The clean answer is for the
release to precede or accompany the tutorial pass; the fallback is a one-line note giving the git
dependency on `main`, which is how the ecosystem repositories track the library. Either way this is a
sequencing question rather than a defect, and it disappears the moment V1 lands.

## Keeping this document current

This document leads the work rather than recording it, so it goes stale in one specific way: when a task
lands and its entry is left behind. **Remove a completed task's entry rather than marking it done**, per
[document-the-present](../AGENTS.md#document-the-present-not-the-history), and remove its row from the
dependency table and its mention in the ordering in the same change. When a decision has to be taken along
the way, record its consequence in the task and in the document that owns the affected page rather than
keeping a list of answers here.

Two documents are updated alongside every landing rather than after it, and both are named in the
[standing obligations](#how-to-read-a-task) above: [redesign-queue.md](redesign-queue.md), whose matching
entry is removed, and [information-architecture.md](information-architecture.md), whose `new` and `moved`
markers are cleared. **When this document is empty the redesign is finished, and it is deleted** — as is
redesign-queue.md, and at that point the inventory in `information-architecture.md` matches
[site-structure.md](site-structure.md).

When a task turns out to be larger than its entry suggests, or splits, record that here rather than in the
queue: the queue says what is wrong, and how the fix decomposes is a property of the plan.
