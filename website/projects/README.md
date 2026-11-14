# The Projects section

This directory holds the blueprint for the website's **Projects** section, which publishes the
[projects/](../../projects/README.md) sections of this base as public documentation, one directory per
project, with each project's example programs expanded into short tutorials. Part of it is written on
the website's `v0.8.0` branch; each project's plan below says which pages.

- **Location** — `https://contextgeneric.dev/docs/projects/` once the `v0.8.0` branch publishes, a
  `Projects` category between Reference and `cargo-cgp` in the sidebar
- **Derived from** — [projects/](../../projects/README.md), which stays the source of truth
- **Page-type spec** — [../writing-guides/project.md](../writing-guides/project.md), which holds the
  page kinds, the mapping from internal document to page, and the rules every page follows; read it
  first
- **Status** — in progress: the section index and parts of cgp-examples, Hypershell, and cgp-serde
  are written, each listed in its plan's *What is written*; the error backends are planned

## What the section replaces

The section supersedes three deep dives planned when each project's announcement post was its only
detailed account: Hypershell, extensible data types, and cgp-serde. The project sections now carry
each project's design, reference, guides, examples, and defects, verified against its source, so
porting them replaces converting the posts. The extensible data types material lives in the
`builder` and `expression` crates of cgp-examples and in the *Extensible records* and *Extensible
variants* Concepts pages.

## The section index

`docs/projects/index.md` is hand-written and does two jobs:

- **It introduces the projects honestly**: which are libraries a reader could depend on and which are
  demonstrations, and that the two libraries are proofs of concept.
- **It carries a pattern-finding table**, the public form of
  [constructs.md](../../projects/cgp-examples/constructs.md) widened to every project, which routes a
  reader who knows an idea to the example page that shows it. A row is added with each example page
  that shows a pattern.

It also routes by reader: the pattern learner to the table, the evaluator to the two library indexes
and their limitations pages, and a reader who wants the smallest program to the greet examples and
the Hello World tutorial.

## The plans

Each project has a plan here: the page list with the internal document behind each page, what must be
true before the pages are written, and the posts that get a pointer.

- [cgp-examples.md](cgp-examples.md) — the five demonstration crates, almost entirely example pages,
  with no reference.
- [hypershell.md](hypershell.md) — the type-level shell-scripting DSL, with the largest reference and
  a comparison with shell scripts.
- [cgp-serde.md](cgp-serde.md) — Serde as components, with the comparison with Serde.
- [error-backends.md](error-backends.md) — `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`,
  one walkthrough per crate; the only section that ships from the `cgp` repository.

## What must be true before a project's pages are written

Each plan says which of these gates apply to it:

- **The documented branch is the project's default branch**, since public source links point there;
  until the branch merges, a page's source links show code it does not describe.
- **The code uses current idioms**, with each change the project needs listed in the plan's *Code
  prerequisites*, per [the guide](../writing-guides/project.md#code-on-a-projects-page).
- **The install instructions can name a release** built against the `cgp` release the site
  describes, or the page gives a git dependency and says why.
- **Each example page's internal record exists and is current**, holding the run output and every
  *Try a change* result the page quotes.

## Ordering

**The written pages publish with the website's `v0.8.0` branch; the rest land after the release.**
The remaining work is the largest discretionary body left, and three of the four projects need their
own branches merged and, for the libraries, their own releases, which follow the `cgp` release. Its
order:

1. **The rest of cgp-examples**: `builder`, `transfer`, and `greet`.
2. **Hypershell's blocked pages, once its code prerequisites land.** It is the one project with
   measured search demand, per [seo.md](../seo.md).
3. **cgp-serde's blocked pages, once its code prerequisites land.**
4. **The error backends**, which can move earlier, since nothing blocks them past the release.

## Links into the section from the rest of the site

A section nobody links to is found only from the sidebar, so these onward links are part of the work:

- **Concepts pages** gain an *In practice:* entry in their *Where to go next* list, pointing at the
  example page that shows the idea, beside their *Comparison:* entries. None carries one yet.
- **Reference pages** for the constructs the examples use may add the example page to their *Related*
  list, where it adds something the page's own example does not.
- **The applied tutorial** ends by routing to the project example that develops its scenario, where
  one does.
- **Resources** lists each project's section beside its repository.
- **The posts that present a project** carry a notice pointing to its section, and the example pages
  link them back; each plan names the posts.

## The document shape for a plan

Each plan opens with a level-one heading and a one-sentence statement of the section, then the
identifying facts: the URL, the internal section it ports, the repository and the revision the pages
describe, the status, and how the pages were made. It then develops what is written and what a
revision must respect, what the section covers and which reader it serves, the pages still to write
with the internal document behind each, the prerequisites (code changes, documents to write in this
base first, and release conditions), the source posts, and what maintaining the section must defend.

## Maintaining these documents

**A plan leads its pages until they land, then records them.** As a project's pages are written, its
plan lists them as written, removes the prerequisites they met, and records the revision each page was
verified against and how the pages were made, per
[AGENTS.md](../AGENTS.md#disclosing-ai-use-on-a-page). The [page records' index](../pages/README.md)
points here, since the section is a ported catalog.

**The synchronization rule reaches the public pages**: a change to a provider's behavior updates its
internal reference entry and its public page in the same change, and a change to an example updates
its record and its page. Register a new plan here and in [../../summary.md](../../summary.md) in the
same change that adds it.
