# Ecosystem projects

This directory documents the projects that **use** CGP without being part of it. Where
[cgp/](../cgp/README.md) and [cargo-cgp/](../cargo-cgp/README.md) document the language extension
and its toolchain, the projects here are libraries built *on top of* CGP: they demonstrate what the
paradigm makes possible, they exercise it at a scale the test suite cannot, and they are the closest
thing the ecosystem has to public evidence that CGP works on real problems.

## What belongs here

A project earns a directory here when it is developed under the
[contextgeneric](https://github.com/contextgeneric) organization, built with CGP rather than being
part of CGP, and public enough that the website or a blog post points at it. Most such projects are
**libraries**. A **repository of runnable demonstrations** qualifies too, once agents work on its
code directly and published material cites its programs. The conditions narrow the set, and two
near-misses are worth naming so the boundary stays clear.

[Hermes SDK](https://github.com/informalsystems/hermes-sdk/), CGP's first real-world adopter and the
codebase the paradigm grew out of, is a library built with CGP. It lives outside the organization
and is not developed alongside it, so it is an external reference recorded in
[sibling-projects.md](../sibling-projects.md) rather than a project here. The
[`cgp-example-profile-picture`](https://github.com/contextgeneric/cgp-example-profile-picture)
repository is inside the organization, but it is one tutorial program documented as the
[profile picture](../examples/profile-picture.md) worked example, so it too is recorded only in
[sibling-projects.md](../sibling-projects.md).
[`cgp-examples`](https://github.com/contextgeneric/cgp-examples) does have a section here: its
crates are cited by the blog, and agents work on them directly.

A project need not have a repository of its own. The [error backends](error/README.md) live in the
`cgp` repository, but they are separate crates that an application adds on its own, and nothing in
the `cgp` crate depends on them, so to a user they are a project built on CGP rather than part of
it. They are documented here for that reason, while the traits they implement stay under
[cgp/](../cgp/README.md). The worked examples that teach the same scenarios stay in
[examples/](../examples/README.md), because an agent learning CGP should not need a project section
to learn a pattern.

The distinction from a **member project** is about what the project is, not how carefully it is
documented. A member builds CGP itself; a project here is built with it. Both are verified against
their own source, and a project section grows from a single orienting `README.md` into the
[section shape](#section-shape) (architecture, reference, guides, tests, and open issues, plus a
document per example where the project ships runnable examples) as it is documented. A project made
of independent subprojects gets one subdirectory per subproject, each with that shape at its own
scale. A project section is the primary source for its project's facts, so other documents link to
it instead of restating them. A project document explains the project's own design and links to
[cgp/](../cgp/README.md) for the CGP constructs it uses rather than re-explaining them.

## The catalog

Four projects are documented so far. All four track the CGP release in preparation, 0.8.0, and
most are cited by public posts whose code has since gone stale, which is a recurring pattern worth
expecting: the project moves with the library while the post that announced it does not.

- [hypershell/](hypershell/README.md): a modular, type-level DSL for shell-script-like programs
  written as Rust types and interpreted at compile time. The project that drove the handler family
  into existence, and the reference implementation of the type-level DSL technique. Documented in
  the full project shape, with one document per runnable example, against its `v0.8.0` branch.
- [cgp-serde/](cgp-serde/README.md): Serde's `Serialize` and `Deserialize` rebuilt as CGP
  components, so that how each value type is encoded becomes a per-context wiring choice. The
  clearest demonstration of CGP's coherence workaround on a library every Rust developer already
  knows. Documented in the full project shape, with one document per runnable example in its
  `cgp-serde-examples` crate, against its `v0.8.0` branch.
- [cgp-examples/](cgp-examples/README.md): a repository of five independent example crates, each
  documented as its own subproject: an HTTP money-transfer service, a modular interpreter, an
  application builder, a web-app wiring study, and a greeting program. Documented against its
  `v0.8.0` branch, with all five subprojects written.
- [error/](error/README.md): the error backends `cgp-error-anyhow`, `cgp-error-eyre`, and
  `cgp-error-std`, which each make one concrete type a context's abstract error. Documented with one
  subdirectory per crate and a shared architecture and guides, against the `cgp` repository's `main`
  branch, where they live under `crates/standalone/error/`.
- [writing-guide.md](writing-guide.md): this section's rules, on verifying a section against its
  project's source, probing a runtime claim, and the shape each project document follows.

## How these relate to the rest of the base

Each project connects outward in three directions, and the documents make all three explicit. It has
a **worked example** in [examples/](../examples/README.md) that develops its scenario in verified
current syntax, building on the project's crates where it can: the
[shell-scripting DSL](../examples/shell-scripting-dsl.md) for Hypershell, and
[modular serialization](../examples/modular-serialization.md) for cgp-serde, and for cgp-examples
the worked example each subproject names in its own README, such as the
[money-transfer API](../examples/money-transfer-api.md) for `transfer`. That example and the
project's own section, not the project's announcement post, are what other documents quote. It has
an **announcement post** with an internal document under [website/blog/](../website/blog/README.md)
recording how far that post has drifted. And it exercises a set of **CGP constructs and concepts**,
linked per project so an agent can find the semantics behind anything it meets in the source.

Each project section also has a public counterpart: the website's **Projects** section ports these
documents to the site, with each project's example programs written as short tutorials. The
Hypershell, cgp-serde, and cgp-examples sections are written on the website's `v0.8.0` branch, and
the error backends' is planned. [website/projects/](../website/projects/README.md) holds one plan
per project naming the public page each document feeds. A project document's *Public material
derived from this* line points there.

For the communication strategy these projects are the ecosystem's most concrete social proof, which
[evidence.md](../communication-strategy/evidence.md) argues is what the evaluator profile actually
wants: a real system built with CGP rather than another argument. That value depends on them staying
current, so a project that falls behind the library stops being evidence and starts being a
liability.

## Section shape

A project starts as a single `README.md` and grows into the shape below as it is documented. The
shape is a guide rather than a template to fill: omit what a project does not need, and raise an
addition outside it before making it. The directories and files keep these names, so an agent moving
between projects finds the same kind of material in the same place.

- **`README.md`**: the front door. It records the repository, local checkout, documented branch,
  crates, tracked `cgp` version, and status; what the project is; a present-tense paragraph on which
  revision the documents describe; a short list of confirmed gaps linking `issues.md`; the catalog of
  every document; and the map to the public material they feed.
- **`architecture/`**: the project's own design, one idea per document. Its `README.md` states the
  whole design on one page and catalogs the rest.
- **`reference/`**: what each public item does, grouped by family rather than one document per item.
  Its `README.md` carries a table of every public item and the catalog.
- **`guides/`**: prescriptive documents for using the project: writing a provider, wiring a context,
  recognizing and fixing the common mistakes.
- **`examples/`**: for a project that ships runnable programs, one document per program named for it
  in kebab case, with a `README.md` cataloging them in teaching order. Each document opens with what
  the program demonstrates and a header list of **Source**, **Run**, **Needs**, and **Result**, then
  walks the program, its context and wiring, What it demonstrates, and any Known issues. **Result**
  says what running it produced, or why it was not run. Each example document is also the record its
  public page is written from, so a program the site will show needs its own document.
- **A comparison document**, named for what it compares against, when the project replaces or extends
  a well-known library.
- **`testing.md`**: what the project's tests pin, which checks they assert, and what is untested.
- **`issues.md`**: the open defects, missing features, and housekeeping items, grouped in that order.

A project made of several independent subprojects gives each one its own subdirectory, named for the
subproject's directory in the repository; each subproject follows this shape at its own scale.

## Adding a project

Create a directory named for the project with a `README.md` following the front-door shape in
[Section shape](#section-shape): what it is, which revision is documented, how
it is organized, what CGP it uses, how it relates to the rest of the base, and its current status.
Register it in the catalog above and in [../summary.md](../summary.md) in the same change, add it to
[../sibling-projects.md](../sibling-projects.md) so its checkout and repository are findable, and
check whether the website's Resources page should list it. The section then follows [Section shape](#section-shape), with [cgp-serde/](cgp-serde/README.md) as
the worked instance.
