# Website redesign tasks

This document is the **work plan for the CGP website redesign**: every task that remains, what each one
depends on, and the order to do them in. It exists because the redesign spans four repositories and
roughly a hundred pages, and the question an agent or a maintainer actually arrives with is not "what is
wrong with the site" but "what should I start on now, and what will I break if I start there".

It is deliberately a plan rather than a diagnosis, and that division matters because two documents both
listing outstanding work would drift apart. [redesign-queue.md](redesign-queue.md) owns the **diagnosis**
— what is wrong with each page today, why it is wrong, and which document carries the detail.
[information-architecture.md](information-architecture.md) owns the **target**, and the
[writing guides](writing-guides/README.md) own the **specification** for each kind of page. This document
owns only the plan: one short entry per task naming where the change lands, what blocks it, and what
"done" means, with a link to whichever of those three documents carries the substance. When a task's
detail is needed, follow the link rather than restating it here.

## The shape of the campaign

Three decisions fix the shape of everything below, and reading them first is what makes the ordering
make sense.

**The redesign and the v0.8.0 release are one event.** The whole site is rewritten on the website
repository's `v0.8.0` branch and goes live when that branch merges, alongside the release. Nothing
publishes incrementally, every page is written as though v0.8.0 has already shipped, and the rules
around that — including never committing redesign work to `main`, which deploys on push — are in
[AGENTS.md](AGENTS.md#the-redesign-lands-on-a-release-branch-all-at-once).

**The release waits for the complete reference.** The site reference is
[canonical](writing-guides/reference.md), so it carries a completeness obligation, and that obligation
is met on day one rather than deferred. R2 is therefore not a background task that runs alongside the
release — it is the task that sets the release date, and it is the largest thing on this list by a wide
margin. Everything except the deep dives is release-blocking.

**The work runs across many sessions, and the scope of each is assigned rather than inferred.** An
agent picking up this document works on the tasks it has been given, not on whatever the ordering
suggests is next. What the ordering below is *for* is deciding what to assign, and checking that a task
handed over is actually startable.

## How to read a task

Every task has an ID so that dependencies can be stated without ambiguity, a **lands in** field naming
the repository and path, and a **done when** condition. The IDs group by kind — `C` corrections, `E`
explanation tier, `F` front page, `T` teaching, `R` reference, `D` deep dives, `B` the blog, `V` the
version release, `O` orientation, `A` the AI disclosure, `X` cross-cutting — and they are stable, so a
task removed on completion leaves its ID retired rather than renumbered.

Four obligations apply to **every** task that adds or moves a page, and they are stated once here rather
than repeated in each entry, per [AGENTS.md](AGENTS.md). Adding a page means **adding or updating its
internal document in the same change**, because a page with no document has no recorded provenance.
Landing a task means **removing its entry from [redesign-queue.md](redesign-queue.md)** rather than
marking it done, and deleting that document once it is empty. Landing a task means **clearing the
matching `new` or `moved` marker** in [information-architecture.md](information-architecture.md), since
the redesign is finished when that inventory and [site-structure.md](site-structure.md) agree. And a page
written with AI assistance carries **one provenance note at its foot**, linking the section of the
disclosure page that matches how it was made, with the level recorded in its internal document — the
mechanics are in [AGENTS.md](AGENTS.md#disclosing-ai-use-on-a-page), and this one applies from the moment
A1 lands and never retroactively.

Four further standing rules bind the content rather than the bookkeeping. Every page is public writing and
is governed by [communication-strategy/](../communication-strategy/README.md) through its writing guide.
Every snippet is bound by the [synchronization rule](../AGENTS.md#the-synchronization-rule): verify
against the `cgp` source and the `/cgp` skill, prefer code already verified in
[examples/](../examples/README.md), and **never** take current syntax from a blog post. Every page
that shows CGP code **says which of the three shapes its example is in** — a value context or an
environmental one, self-targeted or parameter-targeted — because the site's examples span all three and a
reader who generalizes from one and then meets another without being told has no way to say what a context
is; the qualifiers and the four misreadings they prevent are in
[vocabulary.md](../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target), and an
introductory page records the shape in its internal document without necessarily using the terms on the
page. And **the author reads the high-traffic surfaces before they publish** while the rest ships on its
guide plus a spot check. Which surfaces those are is listed authoritatively in
[AGENTS.md](AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes) rather than restated here,
because the disclosure page states the arrangement publicly and three copies of it would drift.

## Two threads that run through several tasks

Two decisions are not tasks of their own because they change several pages each, and they are recorded
here so that a page written without them has to be revisited.

**The application shape is taught second.** A reader's first contact is the front page's hero block,
which is a value context and stays that way — it earns its place by showing a real `E0119` with nothing
but the annotations changed. Everything after it should reach the shape most CGP code is actually in.
On the explanation path that is already handled: the homepage essay's section 2 marks the transition and
*Why CGP exists* builds the application-context idea out of plain Rust. On the teaching path it is not,
because both existing tutorials wire a value context and the checking tutorial continues that family. The
answer is **T3**, the applied tutorial, which is naturally environmental — so it is release-blocking and
sits second in the tutorial order rather than last. The reasoning is the comprehension barrier in
[readers.md](../communication-strategy/readers.md#the-comprehension-barriers).

**Agent support answers the cost objection, and appears nowhere else.** Three of CGP's loudest costs —
the learning curve, the generated-type cascade, and the volume of wiring — are mechanical work over a
written-down vocabulary, which is what CGP's published agent skill reduces. That belongs in the
homepage's cost section, in *When to use CGP*, in *Project status*, and on Resources, stated beside the
cost and framed as a smaller cost rather than a solved one. It does **not** belong in the tag line, the
feature set, a hook, or a blog post's opening. The wording rules are in
[message.md](../communication-strategy/message.md#the-one-mitigation-that-spans-three-of-these) and
[vocabulary.md](../communication-strategy/vocabulary.md#words-and-framings-to-avoid).

## C — Corrections

Eight single-line changes, all in the website repository, none blocked by anything. Because the whole
redesign lands with the release, these are corrections *on the branch* rather than fixes that reach
readers today — several of them are then overtaken by a larger task, and they are still worth doing first
because they are minutes each and they stop the branch carrying known-wrong copy. The detail for each is
in [redesign-queue.md](redesign-queue.md#corrections--single-lines-wrong-today).

- **C1 — the site tagline.** Replace "Modular programming paradigm for Rust." with the settled line from
  [identity.md](../communication-strategy/identity.md). *Lands in:* `docusaurus.config.ts`. *Done when:*
  the configuration, the front page hero, and the site's own copy all carry the same line.
- **C2 — the announcement bar.** It promotes v0.7.0 and is hardcoded, so it goes stale silently with
  every release. *Lands in:* `docusaurus.config.ts`. *Done when:* it points at the v0.8.0 post.
  **Completed by V1** in practice; setting it early on the branch just stops the redesign carrying a
  stale bar.
- **C3 — the tutorial version pin.** Set it to `cgp = "0.8.0"`. Because the branch merges with the
  release, this is simply correct rather than a promise about an unpublished version — which is the
  whole reason the two events are coupled. *Lands in:* `docs/tutorials/hello.md`, and every future
  tutorial. *Done when:* the pin names the version the code is written against and re-pinning is on the
  release checklist.
- **C4 — `cargo-cgp` on Resources.** The single most consequential omission on the site: the error
  toolchain is the direct answer to the most-cited obstacle to adopting CGP, and Resources is where an
  evaluator looks for it. *Lands in:* `docs/resources.md`. *Done when:* the tool, its install command,
  and its purpose appear. **Superseded in part by R3**, which gives the tool a real section; C4 is the
  index entry and stays valuable afterwards.
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

The tier is the **Concepts** section at `docs/concepts/`, one page per idea, mirroring the internal
[cgp/concepts/](../cgp/concepts/README.md) catalog — eighteen pages plus a hand-written index,
specified by [writing-guides/explanation.md](writing-guides/explanation.md). It is the tier the
homepage offloads to, so it unblocks the most downstream work, and none of it is blocked by anything.
Every page here is a surface the author reads before publication.

**The section is scaffolded**, on the pattern the reference port uses: the category, the index, and all
eighteen stubs exist, each carrying its one-line summary and a *Not written yet* notice, so no idea is
missing from the site even where the page behind it is unwritten. What remains per page is the prose.
One page is written and is the model for the rest —
[Consumer and provider traits](https://contextgeneric.dev/docs/concepts/consumer-and-provider-traits),
which covers what E3 was to cover of the trait split.

The four entries below are the pages the homepage offloads to, and they are the ones to write first;
the remaining fourteen follow, and a group of related pages is the natural unit for one session.

- **E1 — *Project status and adoption risk*.** Mostly a move: lift the "Current Status" section out of
  the Introduction so the homepage can link it from above the fold. Its frankness is the asset and must
  survive the move; what changes is the year-stamp, the absence of `cargo-cgp`, the missing
  incremental-adoption reassurance, and the agent-support note among the mitigations. **This page has no
  settled home** — it is project meta rather than a CGP idea, so it does not belong under Concepts, and
  under **Project** beside Contribute is the obvious alternative. Settle that before writing it.
  *Blocks:* F1's second call to action. *Done when:* the page stands alone, the Introduction links to
  it, and C7 is moot.
- **E2 — *Bypassing coherence*, the page that plays *Why CGP exists*.** The highest-value page still
  unwritten and the homepage's most frequent destination: coherence as a guarantee, what it costs, the
  workarounds developers hand-roll, and the `Self`-becomes-a-parameter move with local coherence
  restored. The guide carries the five-movement outline plus the sixth movement that builds the
  application-context shape. *Lands in:* `docs/concepts/coherence.md`. *Blocks:* F1 (better done after,
  since the rewritten homepage links here most), R2's concept-link destinations, and the deep dives'
  primer removal.
- **E3 — *Impl-side dependencies*, completing *How CGP works*.** The trait-split half is written; what
  remains of the site's answer to "macros are magic" is the dependency-injection half — how an
  implementation states what it needs without the interface carrying it. *Lands in:*
  `docs/concepts/impl-side-dependencies.md`. *Blocks:* R2's concept-link destinations, and the deep
  dives' primer removal.
- **E4 — *How much CGP to use*, the page that plays *When to use CGP, and when not*.** A decision guide
  rather than an essay, and the page the homepage's cost section hands a skeptic. It also carries the
  second of the two shape decisions — which of CGP's three shapes to reach for, posed as two questions
  rather than as a taxonomy — and the agent support note beside the costs. *Lands in:*
  `docs/concepts/modularity-hierarchy.md`. *Blocks:* F1's cost section, which currently has nowhere to
  hand off to.

## F — The front page

- **F1 — rebuild the front page against its guide.** The largest single-page change on the list, and the
  one that most needs its destinations to exist first: the hero and tag line, the reassurance line and
  install command, the settled before/after example and the copy that sells it, the six-section bounded
  essay including the cost section, and the routing section replacing the "Ready to Get Started?" filler.
  The hero block's own snippet must be **compiled, not eyeballed**, per the guide. *Lands in:*
  `src/pages/index.tsx` and `src/components/HomepageFeatures/`. *Spec:*
  [writing-guides/homepage.md](writing-guides/homepage.md). *Blocked by:* C1, E1, E2, E4, F2, and O2
  softly. *Done when:* the guide's five draft checks pass and the author has read it.
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
  `cargo-cgp` and the extensible-data work and understates what CGP now offers for enums. The page
  **stays where it is** rather than moving into a category, so the `slug: /overview` this task once
  carried is no longer needed. *Blocked by:* E2 and E4, which are what the depth pointers should point
  at instead.

## T — Teaching

- **T1 — the interim checking note.** Every tutorial that reaches `delegate_components!` should say that
  wiring is lazy, name `check_components!`, and name `cargo cgp check`. *Lands in:* `docs/tutorials/`.
  *Blocked by:* nothing. *Superseded by:* T2, after which each tutorial keeps only a pointer — so this is
  worth doing only if T2 is not being done in the same stretch.
- **T2 — the *Checking and debugging* tutorial.** First-principles register, the natural fourth part of
  the area-calculation family: lazy wiring, `check_components!`, and one deliberate failure shown both
  raw and through `cargo cgp check`, with the tool's youth conceded honestly. The highest-value teaching
  addition and the one that most directly answers the objection that has cost CGP the most readers.
  *Lands in:* `docs/tutorials/area-calculation/`. *Material:*
  [check traits](../cgp/concepts/check-traits.md), the
  [debugging guide](../cgp/guides/debugging.md), and
  [cargo-cgp/reference/usage.md](../cargo-cgp/reference/usage.md). *Blocked by:* nothing.
- **T3 — the applied-register tutorial.** Release-blocking, and **second in the tutorial order rather
  than last**, because it is where a reader meets an application context after a homepage and a Hello
  World that both wire a value one — the reasoning is in
  [the threads above](#two-threads-that-run-through-several-tasks). Draw the scenario from
  [examples/](../examples/README.md) rather than inventing one, and introduce the context as "a type
  that stands for this application, which is where its choices live" the first time it appears.
  *Blocked by:* nothing hard; it links out to the reference, so it reads better once R2 exists.
- **T4 — the area-calculation idiom note.** The series shows `impl<Context> AreaCalculator for Context`
  before simplifying to `impl AreaCalculator`, which is pedagogically deliberate and should stay — but
  the page must say plainly that the second form is the idiom, because a reader who stops early copies
  the first. *Lands in:* `docs/tutorials/area-calculation/static-dispatch.md`. *Blocked by:* nothing.

## R — The reference, the tooling section, and the error catalog

By far the largest item on the list, and the one that sets the release date, since the release waits for
it. It carries a completeness obligation from the moment it starts: a construct with no page is a hole a
reader falls into. The spec and the porting procedure are in
[writing-guides/reference.md](writing-guides/reference.md).

- **R1 — the reference index.** Written, at `docs/reference/index.md`: it names the six constructs a
  newcomer needs, then groups the remaining seventy-five by the job they do. It is one of the surfaces
  the author reads, so **that read is what remains**. It is also the section's completeness check —
  every construct has an entry here even where the page behind it is a stub — so a page added later is
  added to this index in the same change.
- **R2 — port the construct pages.** Seventy-five pages under `docs/reference/`, all **scaffolded** with
  a one-line description and a stub notice, and three written in full:
  [`#[cgp_component]`](https://contextgeneric.dev/docs/reference/macros/cgp_component),
  `#[cgp_impl]`, and `delegate_components!`. Those three are the model the rest are ported against, and
  the settled conventions — anchors from heading text, the collapsed formal grammar, the shared
  provenance note, compiled snippets — are recorded in
  [site-structure.md](site-structure.md). Each remaining page is ported from its internal document by
  the guide's four transformations: re-point every link, restructure into the layered descent, add
  *When to reach for it*, and convert the Source section. Two things ride on this beyond the pages
  themselves — the internal [guides](../cgp/guides/README.md) reach the public site **only** through
  the *When to reach for it* sections, and every new page owes a provenance note. This group ships on
  its guide plus a spot check rather than a full read, and a subdirectory is the natural unit for one
  session. *Blocked by:* E2 and E3 for the concept links the remaining pages need, R4 for what a
  *Gotchas* section may defer to. *Done when:* no stub notice remains.
- **R3 — the tooling section.** `cargo-cgp` gets its own top-level docs section beside the reference
  rather than inside it, since every other reference page answers "what does this construct mean".
  *Material:* [cargo-cgp/reference/](../cargo-cgp/reference/README.md). *Blocked by:* nothing, and it is
  small — worth doing early, since it is what C4, T2, and the homepage's cost section all point at.
- **R4 — the error catalog page.** Scaffolded at `docs/reference/errors.md` and still to be written: the
  compile errors CGP produces after codegen, so a reader who hits a wiring failure has somewhere on the
  site to look it up. The seventeen internal [error-class documents](../cgp/errors/README.md) are the
  material; the public page is one page rather than seventeen, organized by the catalog's own
  hidden-versus-surfaced axis, showing the small program behind each class and what `cargo cgp check`
  makes of it. Its existence is what lets every *Gotchas* section stay construct-specific instead of
  re-explaining the same failure, which is why it should be written **before** the bulk of R2 — the
  three pages written so far each inline a little of what it will own. *Blocked by:* nothing.

## D — The deep dives, and the code they quote

**Post-release.** All three deep dives are still wanted, and none of them holds up the v0.8.0 release —
they are the largest discretionary body of work on the list and they serve readers who are currently
served, if imperfectly, by the blog posts they grow out of. Each is planned in
[deep-dives/](deep-dives/README.md) and each is blocked by modernization work in the repository it
tracks. **The code tasks are genuine library work, not documentation housekeeping**, and they come first:
a deep dive written against the current code would show forms the guides tell readers not to write. They
are also independent of everything above, so they can start whenever there is capacity for them.

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

Two posts, both **post-release**, and both deliberately spaced rather than bundled. Publishing several
substantial pieces at once makes them compete for the same readers on the same day in channels whose
ranking is time-weighted, so the second mostly takes attention from the first — which wastes the smaller
piece and makes neither reception readable as evidence. Neither post blocks anything, and neither is a
redesign defect; the group exists so that writing which is neither a release note nor a deep dive has
somewhere to be tracked.

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
  [implicit parameters](../related-work/implicit-parameters.md).

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

  One decision remains open: whether to include the **`mtl` functional-dependency comparison** —
  `class MonadReader r m | m -> r` fixes the environment type *by* the monad, which is the same
  output-not-input move — since it is the strongest argument for the functional-programming reader,
  showing CGP reaching for a discipline they already trust rather than a novelty, but costs a paragraph
  most readers will skip; the suggestion is to include it late, after the payoff has landed.

- **B2 — the incoherent-Rust post.** A substantial draft already exists on the website repository's
  `incoherent-rust` branch, at `blog/2026-03-30-incoherent-rust-today.md`, and it is the only piece of
  CGP writing aimed squarely at the [language-design
  reader](../communication-strategy/readers.md#the-language-design-and-compiler-team-reader). It reads
  CGP against the dictionary-passing, incoherent-Rust, and context-and-capabilities discussion, and
  argues that CGP is a working implementation of a fragment of it on stable Rust today. *Lands in:*
  `blog/`, author voice. *Blocked by:* nothing technically; held until after the release so it does not
  compete with the announcement for attention. The internal record is
  [blog/incoherent-rust-today.md](blog/incoherent-rust-today.md).

  Three things it needs before publication. A **currency pass**: the draft is dated against posts from
  March, so the upstream discussion has to be re-read and the framing adjusted to where it now stands
  rather than where it stood. The **publication mechanics** the draft is missing — a `slug` and a `tags`
  entry, per the [conventions](blog/README.md). And a **check that the concessions are still the
  strongest part**, since what this reader values is the boundary: what CGP does not solve, which is the
  formalization goal and the migration of the existing trait ecosystem.

## V — The version release

- **V1 — finish the v0.8.0 release announcement, and merge the branch.** This is the campaign's last
  task rather than an interruption in it, because the release and the redesign publish together. The
  draft stops mid-argument, covers one feature of several, teaches an attribute name that changed twice
  during development, carries a placeholder date, and opens by claiming a release that has not happened.
  Its motivation section is the strongest part and needs no change. *Lands in:* `blog/`, then the branch
  merge. *Spec:* [writing-guides/release-announcement.md](writing-guides/release-announcement.md);
  material and the mechanical items in [blog/v0-8-0-release.md](blog/v0-8-0-release.md) and
  [releases/v0-8-0.md](../releases/v0-8-0.md). *Blocked by:* the `cgp` v0.8.0 release itself, and by
  every release-blocking task above. *Completes:* C2 and C3. *Note:* this is the first post written from
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

## A — The AI disclosure

- **A1 — the disclosure page.** Written and building at `docs/ai/disclaimer.md` on the release branch,
  and recorded in [site-structure.md](site-structure.md). What remains is **the author's read**, which
  is the task's real gate rather than a formality: this is the one page where a wrong sentence is a
  false public claim about the project rather than about CGP. Two things to check in particular — that
  the review claim still matches the
  [authorship rule](AGENTS.md#who-drafts-a-page-and-who-reads-it-before-it-publishes) rather than
  flattening it, and that the library section still separates the design from the macro implementation,
  since the `cgp` commit trailers make the blunter version disprovable. *Spec:*
  [ai-disclosure.md](../communication-strategy/ai-disclosure.md).

Disclosure for the **other repositories** — `cargo-cgp` above all, whose source sits wholly at level
three — is deliberately out of scope here and happens after the redesign is published. Do not add notes
to another project's README or documentation in the meantime.

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
- **X2 — the crate's own landing page.** `crates/main/cgp/README.md` is what crates.io and docs.rs
  display for the `cgp` crate, and it is a thirteen-line stub that says CGP's constructs are "still
  mostly undocumented within Rustdoc", routes readers to the book the site itself describes as not
  recently updated, and links the public into this knowledge base. Meanwhile the repository's own
  `README.md` already implements the settled tag line and the curated five features and is visible only
  on GitHub. This is a first-contact surface working against the project, and it is not a website task,
  which is the only reason nobody has owned it. *Lands in:* the `cgp` repository. *Done when:* the crate
  README carries the tag line, the reassurance line, and a short quick look; points at the site's
  reference rather than at the knowledge base; and the claim about rustdoc coverage is either true or
  gone. *Blocked by:* nothing, though it reads better once R1 and R2 give it a destination.

## What depends on what

The table below is the dependency graph in one view. Read it to check whether a task is startable; read
the [ordering](#the-ordering) for what to start on.

| Task | Blocked by | Blocks |
|---|---|---|
| C1–C8 | nothing | C1 → F1; C2 and C3 completed by V1 |
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
| R2 | R1, E2, E3, R4 (soft) | T3 (soft), X2 (soft) |
| R3 | nothing | nothing (C4, T2 point at it) |
| R4 | nothing | R2's *Gotchas* sections |
| DC1, DC2, DC3 | nothing | DD1, DD2, DD3 respectively |
| DD1, DD2, DD3 | their DC task, plus E2 and E3 | nothing |
| B1, B2 | nothing (both held until after V1) | nothing |
| V1 | the v0.8.0 release, and every release-blocking task | completes C2 and C3; unblocks B1 and B2 |
| O1 | nothing | O2, and the Introduction narrowing (soft) |
| O2 | O1 | F1's first call to action (soft) |
| A1 | the author's read | every page-adding task's provenance note |
| X1, X2 | nothing | nothing |

Four shapes in that graph are worth naming, because they are what make the ordering non-obvious. The
**explanation tier is the hub**: E2 and E3 are prerequisites for the front page, the reference, and all
three deep dives, which is why building them early converts into progress everywhere else. **R2 sets the
release date**, so it is the one task worth starting before it is strictly next and worth running in
parallel with everything else. The **deep dives are gated on code** rather than on writing, so their long
lead time starts with DC1–DC3 and those can run at any time. And **V1 is the terminus rather than an
interrupt**: nothing publishes until it lands, so a task deferred is a release deferred.

## The ordering

**First, the corrections (C1–C8), in a single pass on the branch.** They cost minutes each and they stop
every later task inheriting known-wrong copy.

**A1 is drafted already**, which matters for the ordering rather than merely for the tally: it is what
every subsequent page's provenance note links to, so no page added from here carries a dangling
obligation. Its remaining step is the author's read.

**Then R4, R3, and R1.** This is the change most worth noticing in the ordering: because the release
waits for the reference, the reference's *prerequisites* are the real critical path, and all three are
small. R4 fixes what a *Gotchas* section may defer to, R3 is what C4, T2, and the homepage's cost section
all point at, and R1 fixes the grouping that seventy pages then slot into.

**Then E1 and E2, then E4 and E3.** E1 is mostly a move of text that already exists, unblocks the
homepage's second call to action, and creates the category the rest of the tier and F3 need; E2 is the
page the rewritten homepage links to most. E4 is what the homepage's cost section needs, and E3 is what
the reference's concept links need.

**Then start R2, and keep it running.** It is long, mechanical, parallelizable, and it is the release
date. Split it by subdirectory across sessions and let everything below run alongside it.

**Then O1 and O2, then F2 and F3, then F1.** The orientation pages give the front page its first call to
action a real destination; F2 and F3 settle what the Overview is before the front page is rebuilt against
it; F1 is the largest single-page change and the one that most needs its destinations in place.

**Then T2, T3, and T4.** T2 is the highest-value teaching addition and the one that most directly answers
the objection that has cost CGP the most readers; T3 is where a reader finally meets an application
context; T4 is cheap enough to fold into the corrections pass. T1 is worth doing only if T2 is not.

**X1 and X2 fit anywhere and are worth doing early** — a stale published skill misteaches every agent
that reads it, and the crate's landing page is working against the project every day it stays as it is.

**DC1–DC3 whenever there is capacity**, since they are independent of everything above and are the long
lead time on the deep dives.

**Then V1, and the merge.** Everything above ships at once.

**Then, spaced out: DD1–DD3, B2, and B1.** Post-release work, published apart rather than together.

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
