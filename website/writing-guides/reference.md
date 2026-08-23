# Writing a reference page

A reference page explains **one CGP construct completely** — what it is for, when to reach for it, how
to write it, what it generates, and where it bites. The reference is the place a reader goes when they
already know the name of the thing they need, and it is the largest and most mechanical body of writing
on the site.

- **Where they live** — `docs/reference/`, grouped into subdirectories by kind
- **Voice** — project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from** — the internal reference at `cgp/reference/`, which stays the source of truth
- **Scale** — roughly 120 pages, ported rather than written from scratch

## The site reference is canonical

CGP's constructs are procedural macros, and a macro documents badly through rustdoc: what a reader needs
is the trait pair it generates, the wiring it participates in, and the code it desugars to, none of which
a signature shows. The crate's own [docs.rs](https://docs.rs/cgp) entry has also never been filled in —
documenting the `cgp` crate has been an open goal since the
[launch post](../blog/early-preview-announcement.md) — so pretending it carries the load would be a
fiction.

**So the site reference is the canonical place to look a construct up.** It is written to be complete
enough that a reader never needs docs.rs, and docs.rs is linked once from Resources rather than from
every page. Two consequences follow: a reference page may not defer to rustdoc for anything a reader
actually needs, and the reference carries a real completeness obligation — a construct that exists and
has no page is a hole a reader will fall into.

This is a change to the site's shape rather than an addition to it, and
[information-architecture.md](../information-architecture.md) records the new surface.

## Derived from the internal reference, and kept in step with it

The 85 documents under `cgp/reference/` already contain almost all of the *information* these pages
need. They are wrong for a public reader in four specific ways rather than in substance, so **a
reference page is ported, not rewritten**: take the internal document, apply the four transformations
below, and the result is most of the page.

**Re-point every link.** This is the largest edit and the one that cannot be skipped, because the site
[may never link into the knowledge base](../AGENTS.md#the-one-way-link-rule). Every internal document is
dense with links to `concepts/`, `guides/`, `examples/`, `errors/`, and `implementation/`; the
[section below](#where-the-internal-links-go) says what each becomes.

**Restructure into the layered descent**, so a beginner and an expert can use the same page.

**Add the two sections the internal template lacks** — *When to reach for it* and, where the construct
has one, a plain-language gloss of any vocabulary a newcomer will not have. Internal documents assume the
`/cgp` skill and use "provider trait" and "impl-side dependency" as known words.

**Convert the Source section** from pointers into `cgp-macro-core` and the internal implementation
documents into links to the construct's source on GitHub.

The internal document remains the **source of truth**, and this is the arrangement's real cost: a
construct now has a public page as well as an internal document, and the base's
[synchronization rule](../../AGENTS.md#the-synchronization-rule) binds both. A change to a macro updates
the code, the internal document, *and* the public page, in that order and in the same change. A public
page that disagrees with its internal document is a defect in the public page.

## Granularity: one page per named construct

The reference is organized **one page per construct**, because a reader arrives knowing a name and
wanting a URL, and because a page per construct is what makes deep links from the tutorials, the deep
dives, and compiler errors possible. The subdirectory layout mirrors what a construct *is* — `macros/`,
`attributes/`, `derives/`, `components/`, `providers/`, `traits/`, `types/` — the same split the internal
[reference index](../../cgp/reference/README.md) explains.

**The rule is literal: every publicly nameable macro, attribute, derive, and trait gets its own page**,
and no page's title is a list of names. That includes a trait that exists only as the mutable, borrowed,
or provider-side mirror of another, and it includes the interlocking members of a family — the seven
builder traits get seven pages, not one. A page whose title reads *`X`, `Y` & `Z`* is a defect, however
closely the three are related.

Two consequences follow and both are load-bearing. **Cross-link instead of repeating**: where two pages
would say the same thing, one says it and the other links, so the shared explanation has exactly one
home. And **the mapping to the internal reference is no longer one to one** — one internal document now
feeds several public pages, which each internal document records so a later synchronization knows where
to look.

**Markers are the one thing that stays with its trait.** `IsPresent`, `IsNothing`, `IsVoid`,
`IsOptional`, `IsRef`, `IsMut`, and `IsOwned` are *types* implementing
[`MapType`](../../cgp/reference/traits/map_type.md) or `MapTypeRef` rather than constructs of their own,
so they are documented as their trait's impls. The reference index's *Looking for a name you don't see?*
table is what routes a reader who arrives holding one of those names.

**Two consolidations survive, and both are of things that are not separately nameable constructs.** The
**type-level spines** — `Cons`/`Nil`, `Either`/`Void`, `Chars`, and `PathCons` — are types a reader needs
to *recognize in an error message*, never to write, and one page covering all four serves that reader
better than four; the sugar that builds them, `Symbol!`, `Product!`, `Sum!`, and `Path!`, keeps a page
each. And the **two low-level provider macros** `#[cgp_provider]` and `#[cgp_new_provider]` differ only
in whether the struct is declared, and are forms a reader meets rather than writes.

**The rule reaches the groups scaffolded before it existed, and applying it there is part of porting
them.** `providers/` and `components/` have since been ported and only `types/` remains scaffolded,
carrying the internal reference's groupings; a page count taken off the current `types/` tree understates
what it becomes. The splits already applied are the model for it:

- **The four provider catalogues** — handler combinators, dispatch combinators, monad providers, error
  providers — became one page per provider. They were the largest expansion: the error catalogue alone
  holds `RaiseFrom`, `ReturnError`, `RaiseInfallible`, `DebugError`, `DisplayError`, `DiscardDetail`, and
  `PanicOnError`.
- **`use_field.md`** became three, for `UseField`, `UseFieldRef`, and `UseFields`. The internal guide
  kept them together because they are chosen together; a reader choosing between them is served by each
  page's *When to reach for it* and by the index.
- **The component docs that bundle more than one component** split by component: `can_raise_error.md`
  into `CanRaiseError` and `CanWrapError`, `runner.md` into `CanRun` and `CanSendRun`, and
  `has_runtime.md` into `HasRuntimeType` and `HasRuntime`. A *component* is one construct even though it
  generates a consumer trait, a provider trait, and a marker; two components are two pages. **A
  by-reference or async variant is itself a distinct component** — its own consumer trait, provider
  trait, and marker — so it gets its own page too: `computer.md` fed `Computer`, `ComputerRef`,
  `AsyncComputer`, and `AsyncComputerRef`; `try_computer.md` fed `TryComputer` and `TryComputerRef`; and
  `handler.md` fed `Handler` and `HandlerRef`, all grouped under a `handler/` subsection for the
  computation family.

Enumerate each group against the source when you port it rather than trusting the stub's title, and
update the counts in [site-structure.md](../site-structure.md),
[information-architecture.md](../information-architecture.md), and [tasks.md](../tasks.md) in the same
change.

**Splitting a page that already exists means re-pointing every link into it, and that is the step most
easily half-done.** Pages that are already written link to the stubs — `use_field.md` in particular is
cited from across `traits/` — so a split leaves dangling links in files you were not editing. Three
habits make it survivable. Search for the *old* file name across all of `docs/`, not just the group you
are porting, since the concepts tier links into the reference too. Search for **both link forms** — the
relative one ending in `.md`, written between reference pages, and the absolute one rooted at
`/docs/reference/` with no extension, which is what a concepts page uses — because a check that knows
only the first will pass while the build still fails on the second. And decide per
link which of the new pages it meant — a link labelled `CanUpcast` and a link labelled `build_from` came
from one page and belong on two different ones, so a blanket rename is wrong.

**A marker is documented on its trait's page rather than getting one, because it is not a separately
nameable *construct*.** A marker is a type implementing a trait, such as `IsPresent` or `IsRef`, and
belongs with that trait; the index's *Looking for a name you don't see?* table routes a reader who
arrives holding the name, and adding the row is part of the change.

**A provider alias, by contrast, gets its own page.** An alias such as `WithType`, `WithField`, or
`WithContext` is a spelling of `WithProvider<Inner>`, and though it is not a distinct type, a reader who
reaches for it by name needs a page to land on rather than an index row. Each alias page states what it
expands to, carries the wiring form and a worked example, and links to `WithProvider` for the adapter
mechanism and to its inner provider for the underlying behavior, so it repeats neither. The five `With…`
aliases — `WithContext`, `WithType`, `WithField`, `WithFieldRef`, and `WithDelegatedType` — each have a
page for this reason, and for the two whose inner provider is foundational and has no directly-wireable
form (`WithFieldRef`, `WithDelegatedType`), the alias page is where the wiring form and example live
while the inner provider's page keeps the mechanism.

Two pages are not constructs at all, and they go in opposite directions.
[`cargo-cgp`](../../cgp/reference/cargo-cgp.md) documents the toolchain, and it does not belong under
`reference/` on the public site, where every other page answers "what does this construct mean" — give
the tool its own top-level docs section, alongside the reference rather than inside it. The **error
catalog**, by contrast, belongs *inside* the reference, because a reader who hits a wiring failure is
doing exactly what the reference is for: looking one thing up by a name they already have, in this case
an error code or a message shape.

That page is a consolidation of a different kind from the two above. The internal
[errors catalog](../../cgp/errors/README.md) is seventeen documents organized by class, and seventeen
public pages would be a category no reader scans; one page, organized by the internal catalog's own
**hidden-versus-surfaced** axis, is what a reader can actually use. It shows the small program behind
each class, says what the compiler reports, and says what `cargo cgp check` makes of it — the last
being why it sits beside the tooling section conceptually even though it lives in the reference. Write
it **before** the bulk of the port, because its existence is what lets every *Common Mistakes* section stay
construct-specific instead of re-explaining the same failure.

## The layered page

Every reference page descends through the same six sections, in the same order, so that a reader learns
the shape once and can then skim any page by habit. **The descent is by reader level**: a beginner gets
what they need from *Overview* and *Usage* and stops, a working developer reads to the end of the
examples and the *When to reach for it* judgement that follows them, and only an advanced reader
continues into the machinery. Nobody has to read past their level to find their answer.

**Built-in component pages use a variant of this descent.** A page for one of the components CGP ships —
[`HasErrorType`](../../cgp/reference/components/has_error_type.md), the handler family, the runner and
runtime pairs, and the rest under `components/` — documents a high-level construct rather than a macro a
reader invokes, so it replaces *Under the hood* with a **Definition** section placed right after
*Overview*. Definition shows the component's trait definition and then explains each attribute on it in a
bullet linking the attribute's own page: `#[cgp_component]`, `#[cgp_type]`, `#[cgp_getter]`,
`#[async_trait]`, `#[prefix]`, `#[derive_delegate]`, and `#[use_type]`. Two rules keep the bullets
readable: **the key is the bare attribute name** — `#[prefix]`, not
`#[prefix(@cgp.core.error in DefaultNamespace)]` — with the argument's meaning carried in the
explanation, and **an attribute used more than once gets a single grouped bullet** (a component with a
`UseDelegate<Code>` and a `UseInputDelegate<Input>` derive gets one `#[derive_delegate]` bullet covering
both). These pages carry **no *Under the hood***, because the generated machinery is the ordinary
component expansion that the attribute links and the [concepts tier](explanation.md) already explain, and
re-deriving it per component would only repeat them. The other sections are unchanged.

**Overview** — one or two paragraphs, readable by someone who has finished the first tutorial and
nothing else. State the problem the construct solves before naming any mechanism, and gloss or link every
term a newcomer will not have. This is the internal Purpose section rewritten for a reader who does not
have the `/cgp` skill loaded, and it is the section most often ported badly, because the internal version
assumes fluency the public reader has not got.

**Usage** — the accepted forms, each argument and option, and what defaults fill an omission. The
internal Syntax section, largely unchanged.

**This section is where the [coverage rule](../AGENTS.md#layer-the-depth-do-not-omit-the-advanced-material)
bites hardest, and it is exhaustive by obligation rather than by ambition.** Every form the macro's
parser accepts belongs here — including the ones an author judges rare, advanced, or legacy — because
the site reference is canonical and a form that is absent reads as a form that does not exist. Three
habits make that achievable without the section becoming a wall. **Enumerate against the parser**, not
against the internal document, which may itself cover only the forms someone happened to write about.
**Give the forms a spine** rather than a flat list: where a grammar has independent axes — an operator,
a key form, a value form — name the axes and take them in turn, so a reader can find the one they are
asking about. And **say when the forms combine**, with one example that combines them, since a section
that treats each form in its own subsection otherwise implies they are alternatives.

Ordering carries the beginner, not selection. Lead with the form nearly everyone writes, put the
advanced and legacy forms after it, and mark a legacy form as legacy with its replacement named.

A construct whose accepted grammar is large (several operators, several key forms, several statements)
stays a long section even after that ordering, and that length is the coverage rule working as
intended, not a page to trim. Judge a Usage section by whether a beginner can stop at the common form
and an advanced reader can still find every other one, not by its word count.

**Examples** — at least one realistic, self-contained example, and more where forms differ meaningfully.
Prefer code already verified in [examples/](../../examples/README.md) over new snippets.

**When to reach for it, and when not** — the section with no internal counterpart, and often the most
useful on the page. Name the situations the construct is for, the alternative to prefer when it is not,
and the neighbouring construct a reader may actually have wanted. Most of this material already exists in
the internal [guides](../../cgp/guides/README.md), which are prescriptive where the reference is
descriptive; folding each guide's recommendation into the relevant page's *When* section is how that
material reaches the public site, since the guides have no public home of their own.

**It sits after the examples rather than before them, which is a deliberate departure from a
strict level-by-level descent.** Choosing between two constructs is a judgement, and a reader makes it
better having just seen what the construct looks like in use than having only been told what it is for —
so the page shows the thing, then argues about when to reach for it. The descent is otherwise intact: a
beginner still stops after *Usage* and *Examples*, and everything below *When to reach for it* is for
a reader going deeper.

**Under the hood** — the exact expansion, with before/after blocks. **This section stays** on a macro,
attribute, derive, or trait page, and is not optional there: CGP's central credibility problem is that
its constructs are macros, and a Rust programmer will not adopt what they cannot see through. The one
exception is a built-in component page, which omits it and carries a *Definition* section instead, per
the [component variant](#the-layered-page) above. It is the same commitment the
[tutorial guide](tutorial.md) makes for the desugaring appendix and the
[explanation guide](explanation.md) makes for *How CGP works*. The heading itself marks the section as
internals a beginner may skip, so it carries no separate admonition note. Keep it faithful to current
macro output, since this is the part most likely to drift, and `cargo cgp expand` is how to check it
rather than guess.

For a macro or attribute with custom syntax, the **formal grammar** is its own `## Formal grammar`
section, in the Rust Reference's
[notation](https://doc.rust-lang.org/reference/notation.html), placed after *Under the hood* so a
beginner never meets EBNF before the examples while an advanced reader or macro author gets the precise
answer. The rules for what counts as custom syntax and how the grammar is written are unchanged from the
internal [conventions](../../cgp/AGENTS.md#syntax-grammar-conventions).

**Common Mistakes** — corner cases, surprising behavior, and open bugs. The internal Known issues section,
kept whenever there is something to record and omitted entirely when there is not. Do not soften these; a
reader who hits an unlisted corner case trusts the rest of the page less.

The page then closes with two short lists rather than sections: **Related constructs**, each with a
phrase saying how it relates, and **Source**, linking the construct's implementation on GitHub.

## Say when a construct is machinery the macros generate

**Many of the constructs with a page are ones a user never writes.** The macros generate their impls, the
library's own recursions consume them, and a reader meets the name in an expansion or an error message
rather than in code they typed. A page that documents such a construct the same way it documents
`#[cgp_impl]` misleads by omission: it reads as an instruction, and a reader who takes it as one goes
looking for where to put something that was never theirs to put anywhere.

**So a page for a generated construct opens with a notice saying so**, in an `:::info` block headed
*Generated machinery*, placed after the one-line summary and before *Overview* — the same position
and shape the *Legacy — read, don't write* notice uses on
[`#[derive_delegate]`](../../cgp/reference/attributes/derive_delegate.md). The two notices are distinct
and a page carries at most one: legacy means *superseded, prefer the replacement*, while this one means
*current and correct, but not yours to write*.

The block says three things and stops.

**That the reader is not expected to use it**, stated in bold as the first sentence, because that is the
sentence a scanner needs. **Which macro or provider produces or consumes it**, linked — the derive that
emits the impls, the wiring macro that emits the table, the provider that bounds on it. And **what the
page is therefore for**: explaining what that macro produces, so an expansion or a diagnostic naming the
construct is legible. Where there is a narrow case in which the reader *does* name it — defining a monad
of their own, writing a getter provider by hand — say so in the same breath rather than overclaiming.

Two failure modes are worth naming. **Do not let the notice contradict the page**: if *Usage* gives an
import path and a bound, the notice cannot say the construct is unreachable — say instead that it is
rarely reached, and why. And **do not apply it to a construct whose methods a reader calls**. The test is
whether the name appears in ordinary application or generic code: `HasBuilder` and `ExtractField` are
generated too, but a reader calls `builder()` and `extract_field` by name, so they get no notice.

## Linking: three destinations, and one prohibition

The prohibition first: **a reference page may never link into the knowledge base**. That is the
[one-way rule](../AGENTS.md#the-one-way-link-rule), and it is the single easiest thing to get wrong when
porting, because the internal documents are built out of exactly those links.

Links go to three places instead.

**Elsewhere on the site**, which is where most re-pointed links land. Link to the
[tutorial](tutorial.md) that teaches the construct in use, the
[deep dive](deep-dive.md) that develops it at length, the
[explanation page](explanation.md) that carries the idea behind it, and other reference pages. Prefer a
tutorial link over an explanation link when a reader would rather see the construct working than
understand why it exists.

**External Rust documentation**, for any concept a reader may not have. This is what lets the reference
stay readable by a beginner without re-teaching Rust, and the destinations should be consistent across
pages rather than chosen per author. Prefer the **Rust Reference** for precision and the **Rust Book**
for teaching, and note that Book chapter *numbers* shift between editions, so a Book link is worth
re-checking when a page is revised.

| Concept a page may assume | Link to |
|---|---|
| Traits and trait bounds | [Rust Book: Traits](https://doc.rust-lang.org/book/ch10-02-traits.html) |
| Generic parameters | [Rust Book: Generic data types](https://doc.rust-lang.org/book/ch10-01-syntax.html) |
| Lifetimes | [Rust Book: Lifetime syntax](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) |
| Trait implementations, coherence, the orphan rule | [Rust Reference: Implementations](https://doc.rust-lang.org/reference/items/implementations.html) |
| Associated types and constants | [Rust Reference: Associated items](https://doc.rust-lang.org/reference/items/associated-items.html) |
| Procedural macros | [Rust Reference: Procedural macros](https://doc.rust-lang.org/reference/procedural-macros.html) |
| `PhantomData` | [std: `PhantomData`](https://doc.rust-lang.org/std/marker/struct.PhantomData.html) |
| The grammar notation used in a formal grammar | [Rust Reference: Notation](https://doc.rust-lang.org/reference/notation.html) |

A blanket implementation deserves special mention because CGP rests on it and the Rust Book covers it
only in passing; the [Hello World tutorial](../tutorials/hello-world.md) already links an external
explanation for exactly this reason, and a reference page should link the same one rather than pick a
different source.

**The source on GitHub**, in the Source list, so a reader can drop from the prose into the code.

### Where the internal links go

Each internal link target has a defined replacement, and knowing them turns the re-pointing edit from a
judgement call into a mechanical one.

A link to a **concept** becomes a link to the [explanation tier](explanation.md) page that covers the
idea — usually *Why CGP exists* or *How CGP works* — or, where no explanation page covers it, the
material is summarized in a sentence on the reference page itself rather than left dangling.

A link to a **guide** has no public destination, because the guides have no public counterpart. Fold the
guide's recommendation into the page's *When to reach for it* section, which is what that section is for.

A link to an **example** becomes a link to the tutorial or deep dive that carries the same scenario, or
the example code is inlined.

A link to an **error class** becomes a link to the section of the reference's
[error catalog page](#granularity-one-page-per-named-construct) covering that class. This is the one
mapping that depends on a page being written rather than merely re-pointed, which is why the catalog
page comes early: until it exists, a *Common Mistakes* section has to inline whatever it needs, and every
section written that way has to be revisited afterwards.

A link to an **implementation document** is dropped. That material is for people maintaining CGP, and its
public substitute is the GitHub source link in the Source list.

## Placement, navigation, and completeness

The reference is a new top-level category under `docs/`, sitting after Tutorials in the sidebar, because a
reader reaches for it once they are writing code rather than while learning. It needs a directory with a
`_category_.json` per group, and the sidebar is autogenerated from the tree — see
[site-structure.md](../site-structure.md) for the mechanics and the stock-Docusaurus constraint.

The category needs a real **index page**, not an autogenerated list. A hundred and twenty pages is far too many to scan,
and the index is where the layered-audience promise is kept at the section level: it should open by
naming the handful of constructs a newcomer actually needs, then group the rest by the job they do, in
the shape the internal [reference index](../../cgp/reference/README.md) already uses. A reader who does
not yet know which construct they want should be able to find it from this page.

Because the site reference is canonical, **completeness is an obligation**, and it is met when the
section first publishes rather than approached over time. Every construct the `cgp` crate exports needs
a page or a named place inside a consolidated one, and a construct added to the library gets its public
page in the same change as its internal document. That obligation is what makes this section the item
setting the relaunch's date, per [tasks.md](../tasks.md).

## What must not be on a reference page

**No knowledge-base links**, per the rule above.

**No teaching sequence.** A reference page is read in fragments by someone who already knows what they
are looking for. If a page starts walking a reader through building something, that material belongs in a
[tutorial](tutorial.md).

**No unmarked machinery in the top sections.** `DelegateComponent`, `IsProviderFor`, and the
`Symbol<…>` spine may appear under *Under the hood*, and should not appear above it.

**No internal vocabulary without a gloss.** "Impl-side dependency", "provider trait", and "context" are
knowledge-base words before they are public ones; introduce each with a plain definition on first use,
per [vocabulary.md](../../communication-strategy/vocabulary.md).

**No deferral to docs.rs** for anything a reader needs, since the site reference is the canonical place.

**No legacy form presented as current.** Where a construct has been superseded — `#[derive_delegate]` and
`UseDelegate` by the `open` statement, for instance — the page says so plainly in *When to reach for it*
and explains that the older form is what a reader will meet in existing code.

## Checking a draft

**Read only *Overview* and *Usage* and ask whether a reader who has finished one tutorial
understands what this is and how to write it.** That is the layered promise, and it is the thing porting
from an internal document most reliably breaks.

**Count the forms against the parser.** Open the construct's argument or body parser in
`cgp-macro-core` and check that every branch it takes has a place on the page. A page that covers most
of a grammar is the normal failure here, and it is invisible from the page itself — see the
[coverage rule](../AGENTS.md#layer-the-depth-do-not-omit-the-advanced-material).

**Ask whether a reader would ever type this construct's name.** If not, the page needs the
[*Generated machinery* notice](#say-when-a-construct-is-machinery-the-macros-generate), and if it has one,
check that nothing further down contradicts it.

**Grep the page for links into the knowledge base.** One surviving `../../cgp/` link is a broken public
page.

**Check the expansion against `cargo cgp expand`** rather than against the internal document, which may
itself have drifted.

**Check the descent is intact** — nothing from *Under the hood* has leaked upward, and nothing a beginner
needs has sunk below the examples.

**Check the page exists in the index** and that its *Related constructs* list points at real pages, since
a canonical reference with holes is worse than one that is honestly partial.
