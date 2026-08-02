# Writing a reference page

A reference page explains **one CGP construct completely** — what it is for, when to reach for it, how
to write it, what it generates, and where it bites. The reference is the place a reader goes when they
already know the name of the thing they need, and it is the largest and most mechanical body of writing
on the site.

- **Where they live** — `docs/reference/`, grouped into subdirectories by kind
- **Voice** — project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from** — the internal reference at `cgp/reference/`, which stays the source of truth
- **Scale** — roughly 70–85 pages, ported rather than written from scratch

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

## Granularity: close to one page per construct

The reference is organized **one page per construct**, because a reader arrives knowing a name and
wanting a URL, and because a page per construct is what makes deep links from the tutorials, the deep
dives, and compiler errors possible. The subdirectory layout mirrors what a construct *is* — `macros/`,
`attributes/`, `derives/`, `components/`, `providers/`, `traits/`, `types/` — the same split the internal
[reference index](../../cgp/reference/README.md) explains.

**Consolidate only where separate pages would serve nobody.** Four groups qualify, and they take the
count from 85 to roughly 70.

The **type-level spines** — `Cons`/`Nil`, `Either`/`Void`, `Chars`, and `PathCons` — are types a reader
needs to *recognize in an error message*, never to write, and each internal document is short. One
*Type-level spines* page covering all four serves that reader better than four pages. The sugar that
builds them — `Symbol!`, `Product!`, `Sum!`, `Path!` — keeps a page each, since those are written
constantly.

The **three getter providers** `UseField`, `UseFieldRef`, and `UseFields` differ by one axis each and are
chosen together; one page comparing them is more useful than three pages a reader must collate.

The **extensible-data derive family** `CgpData`, `CgpRecord`, and `CgpVariant` is an umbrella and its two
faces. One page, with the umbrella leading.

The **two low-level provider macros** `#[cgp_provider]` and `#[cgp_new_provider]` are forms a reader
meets rather than writes, and they differ only in whether the struct is declared. One page.

Resist consolidating anything else. In particular the four provider *catalogues* the internal reference
already groups — handler combinators, dispatch combinators, monad providers, error providers — are
already the consolidated form and should not be split, but neither should they absorb their neighbours.

Two pages are not constructs at all, and they go in opposite directions.
[`cargo-cgp`](../../cgp/reference/cargo-cgp.md) documents the toolchain, and it does not belong under
`reference/` on the public site, where every other page answers "what does this construct mean" — give
the tool its own top-level docs section, alongside the reference rather than inside it. The **error
catalog**, by contrast, belongs *inside* the reference, because a reader who hits a wiring failure is
doing exactly what the reference is for: looking one thing up by a name they already have, in this case
an error code or a message shape.

That page is a consolidation of a different kind from the four above. The internal
[errors catalog](../../cgp/errors/README.md) is seventeen documents organized by class, and seventeen
public pages would be a category no reader scans; one page, organized by the internal catalog's own
**hidden-versus-surfaced** axis, is what a reader can actually use. It shows the small program behind
each class, says what the compiler reports, and says what `cargo cgp check` makes of it — the last
being why it sits beside the tooling section conceptually even though it lives in the reference. Write
it **before** the bulk of the port, because its existence is what lets every *Gotchas* section stay
construct-specific instead of re-explaining the same failure.

## The layered page

Every reference page descends through the same six sections, in the same order, so that a reader learns
the shape once and can then skim any page by habit. **The descent is by reader level**: a beginner gets
what they need from *What it's for* and *Using it* and stops, a working developer reads to the end of the
examples and the *When to reach for it* judgement that follows them, and only an advanced reader
continues into the machinery. Nobody has to read past their level to find their answer.

**What it's for** — one or two paragraphs, readable by someone who has finished the first tutorial and
nothing else. State the problem the construct solves before naming any mechanism, and gloss or link every
term a newcomer will not have. This is the internal Purpose section rewritten for a reader who does not
have the `/cgp` skill loaded, and it is the section most often ported badly, because the internal version
assumes fluency the public reader has not got.

**Using it** — the accepted forms, each argument and option, and what defaults fill an omission. The
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
beginner still stops after *Using it* and *Examples*, and everything below *When to reach for it* is for
a reader going deeper.

**Under the hood** — the exact expansion, with before/after blocks. **This section stays**, and it is not
optional: CGP's central credibility problem is that its constructs are macros, and a Rust programmer will
not adopt what they cannot see through. It is the same commitment the
[tutorial guide](tutorial.md) makes for the desugaring appendix and the
[explanation guide](explanation.md) makes for *How CGP works*. Mark it clearly as the advanced section so
a beginner knows they may skip it, and keep it faithful to current macro output — this is the part most
likely to drift, and `cargo cgp expand` is how to check it rather than guess.

For a macro with custom syntax, the **formal grammar** belongs here too, in the Rust Reference's
[notation](https://doc.rust-lang.org/reference/notation.html), and it goes inside a collapsed
`<details>` block labelled "Formal grammar" so that a beginner never meets EBNF by accident while an
advanced reader or macro author gets the precise answer. The rules for what counts as custom syntax and
how the grammar is written are unchanged from the internal
[conventions](../../cgp/AGENTS.md#syntax-grammar-conventions).

**Gotchas** — corner cases, surprising behavior, and open bugs. The internal Known issues section, kept
whenever there is something to record and omitted entirely when there is not. Do not soften these; a
reader who hits an unlisted corner case trusts the rest of the page less.

The page then closes with two short lists rather than sections: **Related constructs**, each with a
phrase saying how it relates, and **Source**, linking the construct's implementation on GitHub.

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
[error catalog page](#granularity-close-to-one-page-per-construct) covering that class. This is the one
mapping that depends on a page being written rather than merely re-pointed, which is why the catalog
page comes early: until it exists, a *Gotchas* section has to inline whatever it needs, and every
section written that way has to be revisited afterwards.

A link to an **implementation document** is dropped. That material is for people maintaining CGP, and its
public substitute is the GitHub source link in the Source list.

## Placement, navigation, and completeness

The reference is a new top-level category under `docs/`, sitting after Tutorials in the sidebar, because a
reader reaches for it once they are writing code rather than while learning. It needs a directory with a
`_category_.json` per group, and the sidebar is autogenerated from the tree — see
[site-structure.md](../site-structure.md) for the mechanics and the stock-Docusaurus constraint.

The category needs a real **index page**, not an autogenerated list. Seventy pages is too many to scan,
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

**Read only *What it's for* and *Using it* and ask whether a reader who has finished one tutorial
understands what this is and how to write it.** That is the layered promise, and it is the thing porting
from an internal document most reliably breaks.

**Count the forms against the parser.** Open the construct's argument or body parser in
`cgp-macro-core` and check that every branch it takes has a place on the page. A page that covers most
of a grammar is the normal failure here, and it is invisible from the page itself — see the
[coverage rule](../AGENTS.md#layer-the-depth-do-not-omit-the-advanced-material).

**Grep the page for links into the knowledge base.** One surviving `../../cgp/` link is a broken public
page.

**Check the expansion against `cargo cgp expand`** rather than against the internal document, which may
itself have drifted.

**Check the descent is intact** — nothing from *Under the hood* has leaked upward, and nothing a beginner
needs has sunk below the examples.

**Check the page exists in the index** and that its *Related constructs* list points at real pages, since
a canonical reference with holes is worse than one that is honestly partial.
