# The Projects section

This directory holds the blueprint for the website's **Projects** section, which publishes the
[projects/](../../projects/README.md) sections of this base as public documentation, one directory
per project, with the projects' example programs expanded into short tutorials. None of it is
written yet. It takes the place of three planned deep dives, for the reasons in [What the section
replaces](#what-the-section-replaces).

- **Planned location** — `https://contextgeneric.dev/docs/projects/`, a `Projects` category between
  Reference and `cargo-cgp` in the sidebar
- **Derived from** — [projects/](../../projects/README.md), which stays the source of truth
- **Page-type spec** — [../writing-guides/project.md](../writing-guides/project.md); read it first
- **Status** — in progress: the section index, 21 Hypershell pages, and 45 cgp-serde pages are
  written on the website's `v0.8.0` branch, per [hypershell.md](hypershell.md#what-is-written) and
  [cgp-serde.md](cgp-serde.md#what-is-written); the other two projects are planned. Post-release, per [Ordering](#ordering)

## What the section is

The section's job is to **show CGP's design patterns working in programs that do something real**,
and to give an evaluator evidence that CGP holds up past a toy. The Concepts pages explain each idea
with the smallest code that shows it, and the tutorials build ideas up from a greeting or a
rectangle; neither shows a namespace assembling a language or a wiring table choosing a JSON
encoding in a program someone would actually run. The project sections under
[projects/](../../projects/README.md) already document four such projects in depth, verified against
their source, so the section is a port of that material rather than new writing.

**The example pages carry it.** Each runnable program or test in a project gets one page, written as
a short tutorial in the applied register: a short introduction with links for a reader who does not
know CGP, the program run and its real output, a walkthrough whose headings name the ideas, the
pattern it demonstrates and what that costs, and a route onward. The architecture, guide, and
reference pages exist so that an example page can name a construct and link to its full account, and
so that a reader who adopts a library has somewhere to look things up. The page kinds and their
rules are in [the writing guide](../writing-guides/project.md).

**Every reference page documents one construct**, as the site reference does. The internal project
references group each family into one document, so the port splits them, and each project's plan
records which internal document feeds which pages.

## What the section replaces

**This blueprint supersedes the three planned deep dives** — Hypershell, extensible data types, and
cgp-serde — each a multi-page rewrite of a long blog post. The deep dives were planned when the only
detailed account of each project was its announcement post, so each plan had to rebuild the material
from the post and patch its drifted code. That is no longer the situation. The project sections now
carry the architecture, reference, guides, examples, and defects of each project, verified against
its current source, and porting them is both more complete and more reliable than converting a post.

Three things the deep dives got right carry over unchanged, and the [writing
guide](../writing-guides/project.md) states each as a rule: a Projects page teaches its own subject
and links to the Concepts tier instead of carrying a CGP primer; the candid account of costs
survives the conversion from the author's voice to the project's; and the post a section grew out of
gets a pointer to it at the top, the one sanctioned edit to a published post. The code prerequisites
the deep-dive plans found in `hypershell` and `cgp-serde` carry over too, as tasks DC1 and DC3 in
[tasks.md](../tasks.md), which keep their IDs.

Each deep-dive page has a home in the new section or in a section the site already publishes:

| Planned deep-dive page | Where its material now goes |
|---|---|
| Hypershell: what Hypershell is | the Hypershell index and the `hello` example |
| Hypershell: programs as types | Hypershell architecture: abstract syntax |
| Hypershell: interpreting a program | Hypershell architecture: interpretation |
| Hypershell: assembling the language with namespaces | Hypershell architecture: assembly |
| Hypershell: extending the language | the Hypershell guide on extending the language, and the extension examples |
| Hypershell: trade-offs and related work | the Hypershell limitations page, and a comparison with shell scripts |
| Extensible data types: why shape-generic code | the `builder` and `expression` indexes in cgp-examples |
| Extensible data types: building a record from independent providers | the five `builder` example pages |
| Extensible data types: under the hood, records | the published *Extensible records* Concepts page and the builder trait pages of the reference |
| Extensible data types: handling every variant | the four `expression` example pages |
| Extensible data types: under the hood, variants | the published *Extensible variants* Concepts page and the variant trait pages of the reference |
| Extensible data types: casting between shapes | the casting trait pages of the reference, and the upcasting in the `expression` examples |
| Extensible data types: when to reach for this | the cost sections of the two Concepts pages, and *Modularity Hierarchy* |
| cgp-serde: one type, two encodings | the cgp-serde index and the `messages` example |
| cgp-serde: serialization as a component | cgp-serde architecture: component design, and the Serde bridge |
| cgp-serde: writing serializers | the cgp-serde provider reference, re-entrant providers, and the guide on writing a provider |
| cgp-serde: wiring an application | the `basic` and `messages` examples, and the guide on wiring a context |
| cgp-serde: arena-allocating deserialization | the two arena examples, and cgp-serde architecture: context services |
| cgp-serde: what it does not do | the cgp-serde limitations page and the comparison with Serde |

The extensible data types deep dive is the one that disappears as a unit, because its material was
never a single project. Its patterns belong to two cgp-examples crates, and its internals were
already published by the Concepts and Reference sections after the plan was written.

## The public tree

The tree mirrors the internal sections, so a public page's source is visible from its path. Each
project is a subcategory whose `_category_.json` links its index, and within a project the order is
the order a reader needs: examples first, then architecture, guides, reference, and the limitations
page last.

```text
docs/projects/
├── index.md                   the section index: the projects, and a pattern-finding table
├── cgp-examples/
│   ├── index.md
│   ├── expression/            index, examples/, architecture/
│   ├── builder/               index, examples/, architecture.md
│   ├── transfer/              index, examples/, architecture/, guides/
│   ├── web-app/               index, examples/
│   └── greet/                 index, examples/
├── hypershell/
│   ├── index.md
│   ├── examples/              one page per runnable program
│   ├── architecture/          one page per idea, with an index
│   ├── guides/
│   ├── reference/             one page per construct, grouped by kind
│   ├── shell-scripts.md       the comparison
│   └── limitations.md
├── cgp-serde/
│   ├── index.md
│   ├── examples/              one page per test
│   ├── architecture/
│   ├── guides/
│   ├── reference/
│   ├── serde-comparison.md
│   └── limitations.md
└── error-backends/
    ├── index.md
    ├── architecture.md
    ├── guides/
    ├── anyhow/                the crate's walkthrough as its index, and one page per construct
    ├── eyre/
    └── std/
```

Example pages are named in kebab case after the program, as the internal documents are; reference
pages are named in snake case after the construct, as the site reference's pages are. Each project's
plan gives its full page list.

## How a page maps to its source

The mapping is one internal document to one public page, except where the writing guide says
otherwise. The exceptions are the reference, which splits, and the examples of three cgp-examples
crates, whose internal sections have no per-example document yet.

| Internal document | Public page |
|---|---|
| a project's or subproject's `README.md` | its `index.md` |
| `examples/README.md` | `examples/index.md`, the examples in teaching order |
| `examples/<program>.md` | `examples/<program>.md`, expanded into a short tutorial |
| `architecture/README.md` | `architecture/index.md`, the design on one page |
| `architecture/<idea>.md` | `architecture/<idea>.md` |
| `guides/<job>.md` | `guides/<job>.md` |
| `reference/<family>.md` | one page per construct in the family, under `reference/<kind>/` |
| `issues.md` | none; bugs and missing features stay internal |
| a comparison document | a page of the same name |
| the README and `architecture/`, for their limits | `limitations.md`, the high-level limits of the design and status |
| `testing.md` | none; the limitations page says only that the project is lightly tested |
| [cgp-examples/constructs.md](../../projects/cgp-examples/constructs.md) | the pattern-finding table on the section index |

**Where a project has no per-example document, it is written in this base first.** A public page
ports an internal record, which is where its probe results and run output are kept, so an example
page with no record would have nowhere to record what it was verified against. The three cases are
in [the cgp-examples plan](cgp-examples.md#knowledge-base-prerequisites).

## The section index

The section's own index, `docs/projects/index.md`, is hand-written and does two jobs. It introduces
the projects honestly, saying which are libraries a reader could depend on and which are
demonstrations, and that the two libraries are proofs of concept. And it carries a **pattern-finding
table**, the public form of [constructs.md](../../projects/cgp-examples/constructs.md) widened to
all four projects, which routes a reader who arrives knowing an idea to the example page that shows
it. Its first rows are these, each to be checked against the example pages as they are written:

| Pattern | Example pages that show it |
|---|---|
| Choosing a provider per type with the `open` statement | cgp-serde `messages`, expression `add-mult` |
| Dispatching on a later parameter, such as a handler's input | Hypershell `http-checksum-client`, expression `add-mult-code` |
| A library's defaults assembled into a namespace a context joins | Hypershell `hello`, transfer `query-balance`, web-app `namespaces` |
| Namespace defaults registered with `#[default_impl]` | web-app `default-impls`, transfer `query-balance` |
| Extending a namespace with new syntax | Hypershell `http-checksum-native`, `parallel-compare` |
| Wrapping a provider in a higher-order provider | transfer `transfer-funds`, web-app `fine-grained` |
| Bundling wiring into aggregate providers | web-app `fine-grained` |
| Abstract domain types chosen by the context | transfer `query-balance`, greet `greet-abstract-type` |
| Making a concrete library a context's error type | error backends `anyhow`, `eyre`, `std` |
| Reading configuration from context fields | builder `full-builder`, Hypershell `hello-name` |
| Assembling a context with the extensible builder pattern | the five `builder` examples |
| Handling every variant with the extensible visitor pattern | the four `expression` examples |
| Interpreting a program written as a type | every Hypershell example |
| Drawing a runtime service from the context | cgp-serde `arena` |
| Two applications encoding the same type differently | cgp-serde `messages` |
| Growing from coarse traits to fine-grained components | web-app `coarse-grained`, then `fine-grained` |

The index also routes by reader: the pattern learner to the table, the evaluator to the two library
indexes and their limitations pages, and a reader who wants the smallest possible program to the
greet examples and the Hello World tutorial.

## The catalog

Each project has a plan here, recording the page list, the internal document behind each page, what
must be true before the pages are written, and which posts get a pointer when they publish. The page
counts are estimates from the internal catalogs; each plan says how its count was reached.

- [cgp-examples.md](cgp-examples.md) — the five demonstration crates: about 18 example pages across
  `expression`, `builder`, `transfer`, `web-app`, and `greet`, with architecture pages for three of
  them and no reference. The recommended first section, because its code already uses current idioms
  and its patterns are the broadest.
- [hypershell.md](hypershell.md) — the type-level shell-scripting DSL: 13 example pages, the largest
  reference of the four at about 75 construct pages, and a comparison with shell scripts. Its
  reference and its extension pages wait on DC1.
- [cgp-serde.md](cgp-serde.md) — Serde as components: 4 example pages, about 30 construct pages, and
  the comparison with Serde. Its component pages wait on DC3.
- [error-backends.md](error-backends.md) — `cgp-error-anyhow`, `cgp-error-eyre`, and
  `cgp-error-std`: one walkthrough per crate, 15 construct pages, and the shared guides. The
  smallest, and the only one whose published crates change behavior at the release.

At these estimates the section is roughly two hundred pages, most of them reference pages, which is
why the ordering below writes the examples of every project before the bulk of any reference.

## What must be true before a project's pages are written

Four conditions gate each project, and each plan says which apply to it.

**The project's documented branch is on its default branch.** Every project section here documents a
`v0.8.0` branch or the `cgp` repository's `main`, and public source links point at the default
branch, because that is where a reader who clones the repository lands. Until the branch merges, a
page's source links would show code the page does not describe.

**The code uses current idioms.** A page that exists to teach patterns must not show a form the
[guides](../../cgp/guides/README.md) tell readers to replace, so where the project still uses one,
the change lands in the project first. These are DC1 for `hypershell` and DC3 for `cgp-serde`.

**The install instructions can name a release.** A page telling a reader to add a crate names a
version built against the `cgp` release the site describes. The Hypershell crates on crates.io are
built against `cgp` 0.4.1, so its section needs a new release, or it gives a git dependency and says
why. The cgp-examples crates are unpublished and are cloned and run instead.

**Each example page's internal record exists and is current.** The run output a page quotes comes
from the record, and a *Try a change* result is run and recorded there before it is published.

## Ordering

**The section lands after the v0.8.0 relaunch rather than with it.** It is the largest discretionary
body of work left, its readers are served in the meantime by the Concepts pages and the posts, and
three of its four projects need their own branches merged and, for the libraries, their own
releases, which follow the `cgp` release rather than precede it. The tasks are P1–P5 in
[tasks.md](../tasks.md#p--the-projects-section-and-the-code-it-quotes).

Within the section, the recommended order is:

1. **cgp-examples `expression`, as the pilot.** Four contexts, three passing tests, current idioms,
   and the extensible visitor pattern, which the framework-author reader is least served on today.
   It exercises the example page kind without the reference, so it tests the writing guide cheaply.
2. **The rest of cgp-examples**, with the section index and its pattern table, since those crates
   show the most patterns for the least reference.
3. **Hypershell, once DC1 lands.** It is the one project with measured search demand behind it, per
   [seo.md](../seo.md), so its index and examples come first and its reference follows.
4. **cgp-serde, once DC3 lands**, examples and comparison first.
5. **The error backends**, which can move earlier if capacity allows, since nothing blocks them past
   the release.

## Links into the section from the rest of the site

A section nobody links to is found only from the sidebar, so four kinds of onward link are part of
the work, and each is a task in [tasks.md](../tasks.md) rather than an afterthought.

- **Concepts pages** gain an entry labelled *In practice:* in their *Where to go next* list,
  pointing at the example page that shows the idea, in the way fourteen of them already carry a
  *Comparison:* entry.
- **Reference pages** for the constructs the examples use may add the example page to their
  *Related* list, where it adds something the page's own example does not.
- **The applied tutorial** (T3) ends by routing to the project example that develops its scenario,
  where one does.
- **Resources** lists each project's section rather than only its repository.

The blog posts the sections grow out of get their pointer when each section publishes; each plan
names which.

## The document shape for a plan

Each plan opens with a level-one heading and a one-sentence statement of the section, then a framed
list of identifying facts: the planned URL, the internal section it ports, the repository and the
revision the pages describe, and its status. It then develops, in prose:

- **What it covers**, and which reader it serves most.
- **The pages**, listed by kind with the internal document behind each, the pattern each example
  shows, and the context shape it wires.
- **Prerequisites**, separated into code changes in the project, documents to write in this base
  first, and release conditions.
- **The source posts**, and the pointer each gets.
- **Maintaining it** once written.

## Maintaining these documents

These documents lead the pages rather than following them, so they are plans until a project's pages
land and records afterwards. When a project's section is written, its plan becomes the record of
that section: the page list stays as the inventory, the prerequisites that were met are removed, and
the plan records the revision each page was verified against and how the pages were made, per
[AGENTS.md](../AGENTS.md#disclosing-ai-use-on-a-page). [site-structure.md](../site-structure.md)
then gains a short *Projects* entry pointing here, since the section is a ported catalog.

When a project's internal section changes, the synchronization rule reaches its public pages: a
change to a provider's behavior updates the internal reference entry and the public page for that
construct in the same change, and a change to an example updates its record and its page. Register a
new plan here and in [../../summary.md](../../summary.md) in the same change that adds it.
