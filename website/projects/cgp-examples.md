# cgp-examples in the Projects section

The public section for the five demonstration crates in `cgp-examples`, one subsection per crate,
made almost entirely of example pages: the extensible visitor and builder patterns, a
namespace-organized web service, a wiring study at four scales, and the smallest possible greeting.
The recommended first project section to write, with `expression` as its pilot.

- **URL** — <https://contextgeneric.dev/docs/projects/cgp-examples/>
- **Source** —
  [docs/projects/cgp-examples/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/projects/cgp-examples),
  written on the website's `v0.8.0` branch and not yet published
- **Ports** — [projects/cgp-examples/](../../projects/cgp-examples/README.md), one subproject per
  crate
- **Repository** — [`cgp-examples`](https://github.com/contextgeneric/cgp-examples), documented on
  its `v0.8.0` branch; the pages describe it once that branch is the default
- **Verified against** — `cgp-examples` `v0.8.0` at commit `0c633ad`, with `cgp` `main` at `adc616c`
  through the workspace's patch, and `cargo-cgp` built from its source at commit `b6a6323`
- **Status** — Draft: 14 pages written, the section index and the `expression` and `web-app`
  subsections, listed in [What is written](#what-is-written); `builder`, `transfer`, and `greet`
  wait on their records in this base and on DC4
- **How it was made** — written by an agent from the project section; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What is written

**Fourteen pages are written, all the pages that nothing blocks**, and the Projects section index
gained cgp-examples in its project list, eight rows in its pattern table, and a line in its routes.
Resources links the section beside the repository. `yarn build` passes with them. They are:

- **Section** — `cgp-examples/index.md`, with a table of all five crates, linking the two that have
  pages and naming the other three without a link.
- **`expression`, the pilot** — the index; `examples/index.md` and the four example pages
  `add-mult`, `add-mult-binary-op`, `add-mult-code`, and `add-mult-neg`; and
  `architecture/index.md` and `architecture/dispatch-layers.md`.
- **`web-app`** — the index and the four stage pages, `coarse-grained`, `fine-grained`,
  `namespaces`, and `default-impls`, under an unlinked `Stages` category rather than an examples
  index, since the crate index already lists the stages.

**The pages not yet written** wait on this base or on DC4, and none is scaffolded as a stub:

- `builder`, `transfer`, and `greet` need their per-example records first, per [Knowledge-base
  prerequisites](#knowledge-base-prerequisites), and `builder` and `greet` also need DC4's entry
  point and check blocks. `transfer`'s pages quote code whose comments DC4 changes.

The writing turned up several facts a later revision must respect:

- **Every run and diagnostic was re-produced.** `expression`'s three tests were run offline and
  passed; `web-app` was checked with `cargo cgp check`. Each *Try a change* result, and each test
  the pages ask a reader to add, was run in a probe crate with a path dependency on the crate, with
  sources kept under `reports/probes/cgp-examples-pages/` in the workspace. The results are recorded
  in each example's record.
- **Two contexts have no test, so their pages give one.** The `add_mult_binary_op` and
  `add_mult_code` pages open their *Run it* with an integration test the reader saves under
  `expression/tests/`, and its output; both files were run as integration tests in a copy of the
repository, and match the pages. The pages say the repository has no test for the context;
  they do not call it a gap. If DC4 adds the tests, the pages switch to running them.
- **`web-app`'s pages check rather than run.** Each says on its first screen that every provider
  body is `todo!()`, and its *Check it* step is `cargo check`. Each *Try a change* removes or adds
  one entry and quotes `cargo cgp check`; the coarse and fine-grained pages make the same change so
  the reader sees the coarse manager lose every method where the fine-grained stage loses one.
- **The dispatch wrapper's reason is stated as the likeliest explanation.** The knowledge base
  records the `where`-clause experiments as evidence rather than proof, and `dispatch-layers` keeps
  that uncertainty. Wiring the dispatcher directly now reports `[CGP-E010]` through the context's
  check, which the [dispatch layers
  record](../../projects/cgp-examples/expression/architecture/dispatch-layers.md) is corrected to.
- **Source links point at `main`**, per the writing guide, so until the `v0.8.0` branch merges they
  show the older code, and `web-app` does not exist there.
- **The writing guide was revised from the pilot**, as this plan asks: a program with no runner gets
  a test to save, a wiring-only crate opens with *Check it*, and neighbouring designs make the same
  *Try a change*; see [the example page](../writing-guides/project.md#then-it-runs-the-program).
- **Every example page has a *The problem* section before its code**, per [the writing
  guide](../writing-guides/project.md#then-it-states-the-problem): the task, what makes it hard, and
  a *Without CGP* part that concedes where a shell script, plain Rust, or Serde's derive is simpler
  and names the requirement that tips the balance. A revision keeps it fair to the alternative.
- **No public page lists the crates' defects or housekeeping.** The unwired
  `EvalSubtractWithNegate`, the unread type binding, and `web-app`'s commented-out tables stay in
  the crates' `issues.md`.

## What it covers

The crates are demonstrations rather than libraries, and that decides the section's shape. Nobody
adds them as a dependency, so they get **no reference pages and no limitations pages**: each item is
explained where an example page first shows it, and each crate's status is a short section on its
index, per [the writing guide](../writing-guides/project.md#the-page-kinds). What they offer in
return is breadth. Between them they show more CGP patterns than the two libraries together, all in
current idioms, and they serve the reader
[information-architecture.md](../information-architecture.md#how-each-reader-moves-through-the-site)
names as least served: the framework and library author who wants to see code that is generic over a
struct's fields or an enum's variants.

Every crate but `greet` wires an **environmental context**, so every example page outside `greet`
introduces its context as a type that stands for the application. `greet` is the one value context,
and its pages say so and link the Hello World tutorial, which teaches the same program.

## The pages

The section has an index, `cgp-examples/index.md`, ported from the [project
README](../../projects/cgp-examples/README.md). It introduces the repository as five independent
demonstrations, carries the table of what each crate shows and whether it runs, explains that the
crates are cloned and run rather than added as dependencies, and links each crate's subsection.
About 18 example pages, 7 architecture pages, 2 guides, and 6 indexes make roughly 33 pages.

### `expression` — the extensible visitor pattern

A modular interpreter for a small arithmetic language, where each operator is its own type and each
operation is a set of per-operator providers. **The pilot**: four contexts, three passing tests, and
a pattern no other page on the site shows in a running program. Its context shape is environmental
and parameter-targeted, since the expression is the handler's input.

- **Index** — from [expression/README.md](../../projects/cgp-examples/expression/README.md), opening
  with the closed `enum` and `match` of the `classic` module as the starting point the crate
  improves on.
- **Examples**, in the teaching order of
  [expression/examples/](../../projects/cgp-examples/expression/examples/README.md):
  - `add-mult` — evaluation and conversion to Lisp, each keyed by the input type with the `open`
    statement. The pattern: one provider per variant, dispatched without a hand-written `match`.
  - `add-mult-binary-op` — one generic provider converting both binary operators. The pattern: a
    provider generic over the operator, reading its operands through a getter on the input.
  - `add-mult-code` — both operations in one component, keyed by operation code and input together.
    The pattern: dispatching on two parameters at once.
  - `add-mult-neg` — the language extended with subtraction and negation without editing the
    existing providers. The pattern: the expression problem, solved.
- **Architecture** — `architecture/index.md` from
  [architecture/README.md](../../projects/cgp-examples/expression/architecture/README.md), and
  `dispatch-layers.md`, which carries the wrapper every context needs to avoid the `E0275` overflow.

### `builder` — the extensible builder pattern

Application contexts assembled from per-subsystem builder providers that never name the final
struct. Environmental and self-targeted: the builder contexts carry the configuration and the
wiring.

- **Index** — from [builder/README.md](../../projects/cgp-examples/builder/README.md).
- **Examples**, one per builder context, from the sections of
  [builder-contexts.md](../../projects/cgp-examples/builder/reference/builder-contexts.md) once each
  has its own record:
  - `full-builder` — `FullAppBuilder`, configurable SQLite, HTTP, and OpenAI builders merged into
    `App`. The pattern: independent outputs merged into one struct by field name, with configuration
    read as implicit arguments.
  - `default-builder` — `DefaultAppBuilder`, the same target from the default providers.
  - `postgres` — the same application with the database subsystem swapped for Postgres. The pattern:
    replacing one subsystem by changing one entry.
  - `anthropic` — a different application struct, `AnthropicApp`, from a different AI provider. The
    pattern: the providers do not know the struct they build.
  - `anthropic-and-chatgpt` — one builder context producing three applications, chosen by a code
    with the `open` statement.
- **Architecture** — one page, `architecture.md`, from
  [architecture/README.md](../../projects/cgp-examples/builder/architecture/README.md).

### `transfer` — a namespace-organized web service

A balance-and-transfer HTTP service in which every domain type, business operation, and
cross-cutting concern is a component, and the wiring is organized with prefixes, a namespace, and
`#[default_impl]`. Environmental, mostly self-targeted, with one handler dispatched per endpoint.
The crate's scenario is also the [money-transfer API](../../examples/money-transfer-api.md) worked
example, which the applied tutorial (T3) may draw on; the two must use the same vocabulary.

- **Index** — from [transfer/README.md](../../projects/cgp-examples/transfer/README.md), with the
  server command and `example.sh` as the way to run it.
- **Examples**, from the two traces in
  [request-lifecycle.md](../../projects/cgp-examples/transfer/architecture/request-lifecycle.md)
  once each has its own record:
  - `query-balance` — one authenticated query traced from the route to the in-memory store and back.
    The patterns: abstract domain types, a handler dispatched per endpoint marker, basic auth as a
    wrapper, and a context that joins a namespace.
  - `transfer-funds` — the transfer endpoint, with the self-transfer guard and every error status.
    The patterns: a higher-order provider guarding another, and errors raised with status-code
    markers.
- **Architecture** — `index.md`, `module-layout.md`, `error-design.md`, and
  `namespace-organization.md`, from
  [architecture/](../../projects/cgp-examples/transfer/architecture/README.md). The request
  lifecycle document feeds the two examples rather than a page of its own.
- **Guides** — `adding-an-endpoint.md` and `swapping-the-backend.md`, from
  [guides/](../../projects/cgp-examples/transfer/guides/README.md). The second is where a reader
  meets the `[CGP-E005]` override conflict, and it should show the base-namespace design from the
  crate's [missing features](../../projects/cgp-examples/transfer/issues.md#missing-features) if DC4
  adopts it.

### `web-app` — wiring at four scales

One social-media backend wired four times, from coarse manager traits to namespace defaults.
Environmental and self-targeted throughout. **Nothing in it runs**: every provider body is
`todo!()`, so its pages are wiring studies whose "run it" step is `cargo cgp check`, and they say so
on the first screen.

- **Index** — from [web-app/README.md](../../projects/cgp-examples/web-app/README.md), with its
  table of the four stages.
- **Examples**, from the stage documents:
  - `coarse-grained` — one manager trait per domain, from
    [coarse-grained.md](../../projects/cgp-examples/web-app/coarse-grained.md). The pattern, and its
    cost: a coarse component carries every dependency of every method.
  - `fine-grained` — one component per operation, filter wrappers, and three bundles, from
    [fine-grained.md](../../projects/cgp-examples/web-app/fine-grained.md). The patterns: sizing a
    component by provider choice, higher-order filters, and aggregate providers.
  - `namespaces` — the same nine components under a prefix tree, with a production and a test
    context, from [namespaces.md](../../projects/cgp-examples/web-app/namespaces.md).
  - `default-impls` — a custom namespace supplying seven of the nine components, and the conflict an
    override meets, from [default-impls.md](../../projects/cgp-examples/web-app/default-impls.md).

### `greet` — the smallest program

One greeting written as a CGP function, as a component with two providers, and over an abstract name
type. The only **value context** in the repository.

- **Index** — from [greet/README.md](../../projects/cgp-examples/greet/README.md), stating that the
  Hello World tutorial teaches the first binary and linking it first.
- **Examples** — `greet-function`, `greet-component`, and `greet-abstract-type`, one per binary,
  from the README's sections once each has its own record. These pages must use the Hello World
  tutorial's vocabulary and must not diverge from its code where the two show the same thing.
- The hand-written expansion in `greet_expanded.rs` gets **no page** while it differs from the
  macro's output, per [expansion.md](../../projects/cgp-examples/greet/expansion.md).

## Prerequisites

### Knowledge-base prerequisites

**Three crates need per-example records before their pages can be written**, because a public
example page ports an internal record, per [the blueprint](README.md#how-a-page-maps-to-its-source):

- **`builder`** — an `examples/` directory with one document per builder context, drawn from
  [builder-contexts.md](../../projects/cgp-examples/builder/reference/builder-contexts.md), each
  with a run once the crate has an entry point.
- **`transfer`** — an `examples/` directory with `query-balance.md` and `transfer-funds.md`, drawn
  from
  [request-lifecycle.md](../../projects/cgp-examples/transfer/architecture/request-lifecycle.md) and
  the responses it records.
- **`greet`** — an `examples/` directory with one document per binary, drawn from the
  [README](../../projects/cgp-examples/greet/README.md#the-binaries).

`web-app` needs none: its four stage documents already have the example shape, and the public pages
map to them one to one.

### Code prerequisites

**DC4 in [tasks.md](../tasks.md) collects the changes these pages need in the repository.** Each is
recorded in the crate's `issues.md`:

- **Give `builder` an entry point**, a binary per builder or a test that builds each SQLite target
  against `sqlite::memory:`, so its example pages can show a run; see [builder's missing
  features](../../projects/cgp-examples/builder/issues.md#missing-features). Without it, the pages
  can only show a probe's result, which a reader cannot reproduce.
- **Add check blocks to `greet`'s two component binaries**, since a page that teaches wiring must
  show it checked; see [greet's missing
  features](../../projects/cgp-examples/greet/issues.md#missing-features).
- **Replace "capability" in `transfer`'s code comments**, since the pages quote that code; see
  [transfer's housekeeping](../../projects/cgp-examples/transfer/issues.md#housekeeping).
- **Worth doing, not blocking**: tests for `expression`'s two untested contexts, so every example
  page can show a test run; and the base-namespace refactor of `transfer`, which makes the backend
  guide show the better design.

### Release conditions

The crates are unpublished, so the pages give no install snippet: they clone the repository and run
the crate. The one condition is that the `v0.8.0` branch is the repository's default, so that a
reader who clones it gets the code the pages describe; today `main` lags it and has no `web-app`
crate, per the [workspace gaps](../../projects/cgp-examples/README.md#workspace-gaps).

## The source posts

Every part of the extensible data types series carries a notice at its top, as the author settled.
[Part 2](../blog/extensible-datatypes-part-2.md) links the `expression` pages, and each `expression`
example page links the post back at the section that develops it.
[Part 1](../blog/extensible-datatypes-part-1.md) links the *Extensible records* Concepts page and
this section, and gains a link to the `builder` index when those pages are written. Parts
[3](../blog/extensible-datatypes-part-3.md) and [4](../blog/extensible-datatypes-part-4.md), which
explain the internals, link the Concepts pages and the reference, and part 4 the `expression` pages
too. The unfinished [v0.8.0 release post](../blog/v0-8-0-release.md) gets no notice, since it
describes the current design; the `web-app` pages link it at the section for each stage, and the
post can link the section back when it is finished.


## Maintaining it

Two properties are worth defending. **The pilot's example pages set the pattern for the whole
Projects section**, so revise the writing guide from what writing them teaches rather than letting
the next project drift from it. And **each crate stays a demonstration on the site**: a page that
begins to document every item of a crate has become a reference, which this section deliberately
does not carry.
