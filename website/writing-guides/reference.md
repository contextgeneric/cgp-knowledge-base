# Writing a reference page

A reference page explains **one CGP construct completely**: what it is for, when to reach for it, how
to write it, what it generates, and where it bites. A reader comes here already knowing the name of
the thing they need.

- **Where they live**: `docs/reference/`, grouped into subdirectories by kind
- **Voice**: project voice, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from**: the internal reference at `cgp/reference/`, which stays the source of truth
- **Scale**: about 200 pages, ported rather than written from scratch
- **Record**: [pages/reference.md](../pages/reference.md), with
  [compile-errors.md](../pages/compile-errors.md) and [glossary.md](../pages/glossary.md)
- **Reading**: the shared set and
  [the reference pages' row](README.md#reference-pages-the-glossary-and-the-error-catalog) of the
  reading map

## The site reference is canonical

**The site reference is the canonical place to look a construct up, complete enough that a reader
never needs docs.rs.** CGP's constructs are procedural macros, and rustdoc cannot show what a reader
needs: the trait pair a macro generates, the wiring it joins, and the code it desugars to. The
crate's [docs.rs](https://docs.rs/cgp) entry has also never been filled in. So docs.rs is linked once,
from Resources; a page never defers to rustdoc for anything a reader needs; and a construct that
exists without a page is a defect. [information-architecture.md](../information-architecture.md)
records the surface.

## Derived from the internal reference, and kept in step with it

**A reference page is ported, not rewritten.** The 90 documents under `cgp/reference/` hold almost
all the information, and differ from a public page in four ways, which the port changes:

- **Re-point every link,** because the site
  [never links into the knowledge base](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links);
  [Where the internal links go](#where-the-internal-links-go) gives each replacement. This is the
  largest edit.
- **Restructure into the [layered descent](#the-layered-page),** so a beginner and an expert can use
  the same page.
- **Add *When to use it*,** and a plain gloss of every word a newcomer lacks; internal documents
  assume the `/cgp` skill and use "provider trait" and "impl-side dependency" as known words.
- **Convert the Source section** from pointers into `cgp-macro-core` and the implementation documents
  into links to the construct's source on GitHub.

**The internal document stays the source of truth, and the sync runs both ways.** A change to a macro
updates the code, the internal document, and the public page, in that order and in the same change,
per the [synchronization rule](../../AGENTS.md#the-synchronization-rule); a page that disagrees with
its document is the defect. A detail only the page carries (a form, a default, an error message, a
corner case, an expansion rule, a *When to use it* judgement from a guide) is checked against the
source and added to the internal document in the same change. A page may simplify or reorder its
document but never knows more.

## Granularity: one page per named construct

**Every publicly nameable macro, attribute, derive, trait, component, provider, and type gets its own
page, and no page's title is a list of names.** A reader arrives knowing a name and wanting a URL, and
one page per construct is what makes deep links from tutorials, project pages, and compiler errors
possible. The rule covers a trait that only mirrors another (mutable, borrowed, or provider-side) and
each member of a family: the seven builder traits get seven pages. The subdirectories mirror what a
construct *is* (`macros/`, `attributes/`, `derives/`, `components/`, `providers/`, `traits/`,
`types/`), as the internal [reference index](../../cgp/reference/README.md) explains.

Two consequences follow:

- **Cross-link instead of repeating:** where two pages would say the same thing, one says it and the
  other links.
- **The mapping to the internal reference is not one to one:** one internal document feeds several
  pages, and each internal document names them in a note under its Source section.

The rule's edges:

- **Components:** a component is one construct even though it generates a consumer trait, a provider
  trait, and a marker; two components are two pages. A by-reference or async variant is its own
  component and page, as `computer.md` fed `Computer`, `ComputerRef`, `AsyncComputer`, and
  `AsyncComputerRef`.
- **Providers:** each provider in an internal catalogue gets a page, as the error catalogue's
  `RaiseFrom`, `ReturnError`, `RaiseInfallible`, `DebugError`, `DisplayError`, `DiscardDetail`, and
  `PanicOnError` did.
- **Provider aliases get their own page.** An alias such as `WithType` or `WithContext` is a spelling
  of `WithProvider<Inner>`, and a reader who reaches for it by name needs a page. Each alias page
  states what it expands to, carries the wiring form and an example, and links `WithProvider` for the
  adapter and its inner provider for the behavior. Where the inner provider has no directly wireable
  form (`WithFieldRef`, `WithDelegatedType`), the alias page holds the wiring form and the inner
  page the mechanism.
- **Markers stay with their trait.** `IsPresent`, `IsNothing`, `IsVoid`, `IsOptional`, `IsRef`,
  `IsMut`, and `IsOwned` are types implementing [`MapType`](../../cgp/reference/traits/map_type.md) or
  `MapTypeRef`, documented as their trait's impls; add a row to the index's *Looking for a name you
  don't see?* table for each.
- **One consolidation survives:** `#[cgp_provider]` and `#[cgp_new_provider]`, which differ only in
  whether the struct is declared, share a page. The type-level lists get a page each (`Cons`, `Nil`,
  `Either`, `Void`, `Chars`, `PathCons`), with the family explanation on the head cells (`Cons`,
  `Either`, `Chars`, `PathCons`), and the sugar that builds them (`Symbol!`, `Product!`, `Sum!`,
  `Path!`, `Struct!`, `Enum!`) keeps a page each too.
- **A construct documented inside another page moves to its own page** in the directory its kind
  belongs to.

**Enumerate each group against the source when you port it,** rather than trusting a stub's title, and
update the counts in [pages/reference.md](../pages/reference.md) and
[information-architecture.md](../information-architecture.md) in the same change.

**Splitting a written page means re-pointing every link into it, the step most easily half-done:**

- Search for the old file name across all of `docs/`, since the Concepts tier links the reference too.
- Search for both link forms: the relative one ending in `.md`, used between reference pages, and the
  absolute one rooted at `/docs/reference/` without an extension, used by a Concepts page.
- Decide per link which new page it meant: a link labelled `CanUpcast` and one labelled `build_from`
  came from one page and belong on two.
- Split the `example-code` mirror with the page, since a mirror file naming a page that no longer
  exists is worse than none.

**Three pages are not constructs.** [`cargo-cgp`](../../cgp/reference/cargo-cgp.md) documents the
toolchain, so it gets its own top-level docs section beside the reference. The **error catalog**
belongs inside the reference, because a reader with a wiring failure is looking something up by a
name they have, an error code or a message shape. It consolidates the twenty-one class documents of
the internal [errors catalog](../../cgp/errors/README.md) into one page, organized by its
**hidden-versus-surfaced** axis, showing each class's program, what the compiler reports, and what
`cargo cgp check` makes of it. Write it before the bulk of a port, so every *Common Mistakes* section
can link a class instead of re-explaining it. The **glossary** belongs inside for the same reason, as
[The glossary page](#the-glossary-page) specifies.

## The layered page

**Every reference page descends through the same six sections, in the same order, by reader level.**
A beginner stops after *Overview* and *Usage*, a working developer reads to *When to use it*, and only
an advanced reader continues into the machinery.

- **Overview:** one or two paragraphs readable after the first tutorial. State the problem before
  naming any mechanism, and gloss or link every term a newcomer lacks. The first paragraph names
  Context-Generic Programming once and links the Introduction, because a reader who searched for the
  construct may land here first. Where the construct concerns choosing an implementation (a
  component, a provider, a wiring macro), relate a short form of the tag line to its job, as in "CGP
  enables pluggable trait implementations in Rust, and `delegate_components!` is where a context picks
  them"; a type-level building block leaves it out, per the
  [naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page). This
  is the internal Purpose section rewritten for a reader without the skill, and the section most often
  ported badly.
- **Usage:** every accepted form, each argument and option, and the defaults, from the internal Syntax
  section. The [coverage rule](README.md#layer-the-depth-do-not-omit-the-advanced-material) makes it
  exhaustive: every form the parser accepts is here, rare, advanced, and legacy ones included.
  **Enumerate against the parser,** not the internal document; **give the forms a spine,** naming
  independent axes (an operator, a key form, a value form) and taking them in turn; and **say when the
  forms combine,** with one example combining them. Order carries the beginner: the common form first,
  then advanced and legacy forms, each legacy form marked with its replacement. A large grammar stays a
  long section; judge it by whether a beginner can stop early and an advanced reader can find every
  form.
- **Examples:** at least one realistic, self-contained example, more where forms differ meaningfully,
  preferring code verified in [examples/](../../examples/README.md).
- **When to use it:** the situations the construct is for, the alternative when it is not, and the
  neighbour a reader may have wanted. It folds in the internal [guides](../../cgp/guides/README.md),
  which have no public home. It sits after the examples on purpose, because a reader judges between
  constructs better having just seen one in use.
- **Under the hood:** the exact expansion, with before/after blocks, required on a macro, attribute,
  derive, or trait page, because a Rust programmer will not adopt macros they cannot see through. The
  heading marks it as internals, so it needs no admonition. Check it with `cargo cgp expand`, since it
  drifts most. For a macro or attribute with custom syntax, a **`## Formal grammar`** section follows
  it, in the Rust Reference's [notation](https://doc.rust-lang.org/reference/notation.html), under the
  internal [conventions](../../cgp/writing-guide.md#syntax-grammar-conventions). The argument-free macros
  (`#[async_trait]`, `#[cgp_auto_dispatch]`, `#[cgp_auto_getter]`) have no grammar section.
- **Common Mistakes:** corner cases, surprising behavior, and open bugs, from the internal Known
  issues, omitted when there are none and never softened.

The page closes with three short lists: **Related constructs**, each with a phrase saying how it
relates; **The ideas behind it**, two or three Concepts pages and never more, each with a phrase saying
what it adds, as a route rather than a substitute for the page's own summary; and **Source**, linking
the implementation on GitHub.

Two groups vary the descent:

- **Built-in component pages** (`components/`) replace *Under the hood* with a **Definition** section
  right after *Overview*, because the generated machinery is the ordinary component expansion the
  attributes' pages and the [Concepts tier](explanation.md) explain. Definition shows the component's
  trait and explains each attribute on it (`#[cgp_component]`, `#[cgp_type]`, `#[cgp_getter]`,
  `#[async_trait]`, `#[prefix]`, `#[derive_delegate]`, `#[use_type]`) in a bullet linking the
  attribute's page. Key each bullet by the bare attribute name (`#[prefix]`, not its arguments), and
  group an attribute used twice into one bullet.
- **Trait pages** (`traits/`) add a **Definition** right after *Overview* and keep *Under the hood*.
  Definition shows the trait's own item (`pub trait`, `pub struct`, associated const, or function),
  taken from the internal Definition section, and explains its generic parameters, associated types,
  receivers, supertraits, defaults, and attributes; move the definition out of *Overview* or *Usage* so
  it appears once. *Under the hood* shows how the macros generate and consume it. Each trait page
  states where its traits are imported from, since about half are outside the prelude.

The macro, attribute, and derive groups have no *Definition* section.

## Conventions the port must follow

These mechanics are settled; copy them rather than rediscover them.

**Front matter:**

- **Every page carries a written `description`;** without one, Docusaurus takes the first line, which
  on a construct page is mostly punctuation. Write it from the page's own summary line, within about
  155 characters.
- **A page whose heading is a construct name also carries a search-facing `title`,** while its `h1`
  stays the name, such as `` # `#[cgp_component]` ``, and the `sidebar_label` is untouched. Put the
  construct name first, then its job, under about 45 characters, so the site name truncates first. A
  page covering two constructs names both and drops the job phrase. A page whose heading is already
  what a reader searches, as on Concepts and Comparisons, carries only a `description`.
- **Do not name CGP in a page's own title,** because every page renders as
  `{Page} | CGP — Context-Generic Programming`; the exception is a page whose subject is CGP, such as
  the disclosure page or the skill. [seo.md](../seo.md#titles-and-descriptions-are-the-per-page-levers-and-docusaurus-separates-them)
  holds the reasoning.
- **Escape apostrophes in single-quoted YAML** (`'a context''s wiring table'`); an unescaped one fails
  the build with an error naming the wrong line.
- **Sidebar labels carry no backticks,** because a `sidebar_label` is plain text; keep them in the
  `#` heading.

**Headings and admonitions:**

- **Anchors come from heading text,** because the MDX setup rejects `{#custom-id}`, so a linked heading
  cannot be reworded freely.
- **An admonition's title is a heading on its own line:** `:::info`, a blank line, then
  `### Still being written`. On this installation `:::info Still being written` is not a directive and
  renders as three plain paragraphs without a build error. The bracket form
  `:::info[Still being written]` also renders, but the heading form was chosen because it makes the
  title a link target and a table-of-contents entry.

**Glossing "context":** introduce the word with a gloss on first use, on every page, above the
advanced line, because a reference page is read on its own. Use the canonical clause from
[vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each),
"the type the method runs on, which supplies the values it needs as its fields", or a variant it
permits: "the type the implementation runs against", "the type the code runs against", "the type it
runs against", or, on abstract-type pages, "the type that implements the trait". Add a new variant to
vocabulary.md first, and never say "capability", per
[vocabulary.md](../../communication-strategy/vocabulary.md#words-and-framings-to-avoid). The full
account is on the Concepts page, reached through the sidebar. This is the convention most easily
dropped. `Product!`, `Sum!`, `Struct!`, `Enum!`, `Path!`, and `#[async_trait]` are exempt, because they
never use the word above the advanced line; `Symbol!` is not.

**Provenance note:** every reference page, a written index included, closes with "An AI agent wrote
this page using the CGP knowledge base. Its content was verified against the library's source. See How
AI is used in this project.", the last phrase linking the disclosure's documentation section, per
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page). Other footers follow its sentence structure:
"revised" for a revision alone, "wrote and revised" for both; tooling pages keep their claims about
verification against the tool; a footer never attributes verification to a person or agent the record
does not name. Pages without a note and the skill snapshot are outside this convention.

**Verification:**

- **Compile every snippet** against `cgp` 0.8.0 in the
  [`example-code` crate](../site.md#the-example-code-crate), with a `check_components!` assertion per
  wired context, and a rejected snippet as a compile-fail fixture. A page documenting a failure quotes
  the message the compiler actually produced.
- **Check every expansion with `cargo cgp expand --lib --item`** on each item the page shows (for a
  component: the consumer trait, the provider trait, the wired context, and the provider; for a
  `#[cgp_fn]`: the generated trait), never against the internal document. Treat a remembered path
  expansion as suspect: an `@`-path key's tail is a generic parameter, not `Nil`, and `expand` resugars
  unevenly, returning an `open` header's redirect target as `Path!(@Component)` while each entry's key
  stays a raw `PathCons` list, so a page showing both says so.

## Say when a construct is machinery the macros generate

**A page for a construct a user never writes opens with a *Generated machinery* notice.** The macros
generate such a construct's impls and the library's recursions consume it, so a reader meets the name
in an expansion or an error, and a page written like `#[cgp_impl]`'s reads as an instruction.

The notice is an `:::info` block after the one-line summary and before *Overview*, the position and
shape of the *Legacy — read, don't write* notice on
[`#[derive_delegate]`](../../cgp/reference/attributes/derive_delegate.md). A page carries at most one:
legacy means *superseded, prefer the replacement*; this one means *current, but not yours to write*.
The block says three things:

- **That the reader is not expected to use it,** in bold, first.
- **Which macro or provider produces or consumes it,** linked.
- **What the page is therefore for:** making an expansion or a diagnostic that names it legible. Name
  the narrow case where a reader does write it (their own monad, a hand-written getter provider).

**Do not let the notice contradict the page:** if *Usage* gives an import path and a bound, say the
construct is rarely reached, and why. **Do not apply it to a construct whose methods a reader calls**:
`HasBuilder` and `ExtractField` are generated, but a reader calls `builder()` and `extract_field`.
**A section that is entirely machinery says so once, in its overview:** the `types/` pages carry no
notice, while `traits/`, where generated constructs sit among written ones, uses the per-page notice.

## Linking: three destinations, and one prohibition

**A reference page never links into the knowledge base,** per the
[one-way rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links); it is the easiest thing to get wrong in a port.
Links go to three places instead:

- **Elsewhere on the site:** the [tutorial](tutorial.md) that teaches the construct, the
  [Projects example page](project.md#the-example-page) that shows it in a program, the
  [explanation page](explanation.md) behind it, and other reference pages. Prefer a tutorial when a
  reader would rather see it working. A mention of `cargo cgp check` links
  <https://contextgeneric.dev/docs/cargo-cgp/check>, not the tool's repository.
- **External Rust documentation,** from the table below, so every page links one place per concept:
  the Rust Reference for precision, the Rust Book for teaching. Book chapter numbers shift between
  editions, so recheck a Book link when revising.
- **The source on GitHub,** in the Source list.

| Concept a page may assume | Link to |
|---|---|
| Traits and trait bounds | [Rust Book: Traits](https://doc.rust-lang.org/book/ch10-02-traits.html) |
| Generic parameters | [Rust Book: Generic data types](https://doc.rust-lang.org/book/ch10-01-syntax.html) |
| Lifetimes | [Rust Book: Lifetime syntax](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) |
| Trait implementations, coherence, the orphan rule | [Rust Reference: Implementations](https://doc.rust-lang.org/reference/items/implementations.html) |
| Associated types and constants | [Rust Reference: Associated items](https://doc.rust-lang.org/reference/items/associated-items.html) |
| Procedural macros | [Rust Reference: Procedural macros](https://doc.rust-lang.org/reference/procedural-macros.html) |
| Supertraits | [Rust Reference: Traits](https://doc.rust-lang.org/reference/items/traits.html) |
| Trait objects and dynamic dispatch | [Rust Reference: Trait objects](https://doc.rust-lang.org/reference/types/trait-object.html) |
| `PhantomData` | [std: `PhantomData`](https://doc.rust-lang.org/std/marker/struct.PhantomData.html) |
| The grammar notation used in a formal grammar | [Rust Reference: Notation](https://doc.rust-lang.org/reference/notation.html) |

For a blanket implementation, which the Rust Book covers only in passing, link the external
explanation the [Hello World tutorial](../tutorials/hello-world.md) uses.

### Where the internal links go

Each internal link target has a fixed replacement:

- **A concept** becomes the [explanation tier](explanation.md) page that covers it, usually the
  Concepts page of the same name, or a sentence on the page where none does.
- **A guide** has no public counterpart; fold its recommendation into *When to use it*.
- **An example** becomes the tutorial or Projects example page with the same scenario, or the code is
  inlined.
- **An error class** becomes the section of the error catalog page covering that class.
- **An implementation document** is dropped; the GitHub source link replaces it.

## The glossary page

**The glossary is term lookup, where the index is construct lookup.** The index's *Looking for a name
you don't see?* table routes a construct's name (`IsPresent`, `#[cgp_new_provider]`) to its page; the
glossary routes a word (environmental context, blanket implementation, type class) to the page that
explains the idea. It exists because the site's vocabulary is glossed inline everywhere but defined
at length in few places, and the glossary is that destination.

**Placement:** `docs/reference/glossary.md`, labelled **Glossary**, at `sidebar_position: 91`, beside
the compile-errors page at 90. The reference index links it in prose as it links the error catalog.
The Concepts index, the Introduction, and the [Comparisons index](related-work.md#the-index-page) also
link it, because a newcomer meeting an unfamiliar word is not browsing the reference; dropping those
links loses the reader who needs it most. The layered descent does not apply.

**Structure:**

- **Every term is an `###` directly under its section's `##`, with no thematic grouping,** because
  Docusaurus anchors `h2` and `h3` only and a term without an anchor cannot be linked.
- **Sections are alphabetical,** because the page is looked up.
- **`toc_max_heading_level: 2`** keeps the table of contents to the three sections; the anchors are
  unaffected.

**Each entry is a definition and a route, never an explanation:** its heading, one or two sentences,
then a line of links, two as the norm and three at most. An entry that explains *why* becomes a worse
copy of a Concepts page and drifts from it. The three sections owe different things:

- **CGP terms:** [vocabulary.md](../../communication-strategy/vocabulary.md) is the source of truth;
  copy its canonical gloss rather than paraphrasing. Link the Concepts page that argues the idea and
  the reference page of the construct that expresses it.
- **Rust terms:** one sentence, linking the destination the
  [external documentation table](#linking-three-destinations-and-one-prohibition) fixes. A
  CGP-specific consequence is a clause and a link, never a paragraph.
- **Related concepts:** one or two sentences in the term's own community's vocabulary, linking the
  [comparison page](related-work.md) that places CGP against it and the term's canonical page, taken
  from that comparison page's Sources section. CGP's relationship to it is a clause at most. A term
  gets an entry only where a comparison page's *In your terms* table covers it. Never let a definition
  read as disparagement. `capability` gets an ordinary entry saying what the word means to those who
  use it, routing to the comparison page; the prohibition on calling CGP constructs capabilities binds
  the site's prose, not this entry.

**What the page does not do:** it does not retire the per-page gloss, which serves a reader arriving
from search; it shows no code, so it needs no `example-code` mirror; and it lists no constructs,
naming one only as a link where a term is embodied by it.

**Linking a term to it:**

- Link the first use on a page, in the body, and leave the inline gloss beside it; later uses stay
  unlinked.
- Never link from a closing routing list (*Related constructs*, *Where to go next*, *Sources*); a term
  that appears only there gets no link.
- A page that owns a term does not link it: *Bypassing coherence* does not link *coherence*.
- A compound use is not the general term: *consumer blanket impl* stays unlinked, and only *blanket
  implementation* links.
- The basic vocabulary is not linked: *context*, *component*, *provider*, *wiring*, and the two trait
  names are glossed or are the section's working words.
- A term already linked to its Concepts page stays pointed there.
- Because `onBrokenLinks` is `throw`, a new term and the links into it land in one change.

**Checking a glossary draft:**

- An entry longer than two sentences, or one that answers "why", belongs on the page it should link.
- Every Rust entry links the table's destination and teaches nothing.
- Read the related-concepts entries as a practitioner of each tool; cut or re-source one its community
  would not accept, and move any claim of CGP's advantage to the comparison page.
- Build the inventory by reading the pages, not by transcribing vocabulary.md, so every term the site
  uses without defining is covered.

## Placement, navigation, and completeness

**The reference is a top-level category under `docs/`, after Tutorials, Concepts, and Comparisons,**
because a reader reaches for it once they write code. Each group needs a `_category_.json`, and the
sidebar is autogenerated, per [site.md](../site.md#how-the-site-is-built).

**The category needs a written index page, not a generated list.** It opens with the handful of
constructs a newcomer needs, then groups the rest by job, in the shape of the internal
[reference index](../../cgp/reference/README.md), so a reader who does not yet know the construct's
name can find it.

**Completeness is an obligation:** every construct the `cgp` crate exports has a page or a named place
in a consolidated one, and a construct added to the library gets its page and its entry in the
reference index in the same change as its internal document.

## What must not be on a reference page

- **Knowledge-base links,** per the one-way rule.
- **A teaching sequence;** a walk through building something belongs in a [tutorial](tutorial.md).
- **Unmarked machinery above *Under the hood*,** such as `DelegateComponent`, `IsProviderFor`, or the
  `Symbol<…>` list.
- **Internal vocabulary without a gloss:** "impl-side dependency", "provider trait", and "context" get
  a plain definition on first use, per [vocabulary.md](../../communication-strategy/vocabulary.md).
- **Deferral to docs.rs.**
- **A legacy form presented as current:** where a construct is superseded (`#[derive_delegate]` and
  `UseDelegate` by the `open` statement), *When to use it* says so and that the old form appears in
  existing code.

## Checking a draft

- **Read only *Overview* and *Usage*** and ask whether a reader who has finished one tutorial knows what
  the construct is and how to write it; porting breaks this most reliably.
- **Count the forms against the parser** in `cgp-macro-core`: every branch has a place on the page. A
  page covering most of a grammar is the normal, invisible failure.
- **Ask whether a reader would ever type the construct's name;** if not, the page needs the
  *Generated machinery* notice (outside `types/`), and nothing below may contradict it.
- **Grep for links into the knowledge base;** one surviving `../../cgp/` link breaks a public page.
- **Check the expansion with `cargo cgp expand`,** not the internal document.
- **Check the descent:** nothing from *Under the hood* above it, nothing a beginner needs below the
  examples.
- **Check the "context" gloss mechanically,** allowing for the phrase wrapping across lines and for
  its permitted variants, and ignoring `MyContext` inside code blocks.
- **Check the page is in the index** and that its *Related constructs* point at real pages.
