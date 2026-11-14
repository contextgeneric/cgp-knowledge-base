# cgp-examples in the Projects section

The public section for the five demonstration crates in `cgp-examples`, one subsection per crate and
almost entirely example pages: the extensible visitor and builder patterns, a namespace-organized web
service, a wiring study at four scales, and the smallest possible greeting.

- **URL** — <https://contextgeneric.dev/docs/projects/cgp-examples/>
- **Source** —
  [docs/projects/cgp-examples/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/projects/cgp-examples),
  written on the website's `v0.8.0` branch and not yet published
- **Ports** — [projects/cgp-examples/](../../projects/cgp-examples/README.md), one subproject per
  crate
- **Repository** — [`cgp-examples`](https://github.com/contextgeneric/cgp-examples), documented on
  its `v0.8.0` branch, which merges into `main` with the release; the pages describe `main` from
  then on
- **Verified against** — `cgp-examples` `v0.8.0` at commit `690911a`, with `cgp` `main` at `adc616c`
  through the workspace's patch, and `cargo-cgp` built from its source at commit `b6a6323`
- **Status** — Draft: the crate index and the `expression` and `web-app` subsections are written;
  `builder`, `transfer`, and `greet` wait on their records in this base and on its
  [code prerequisites](#code-prerequisites)
- **How it was made** — written by an agent from the project section; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What is written

Fourteen pages, all those nothing blocks, with cgp-examples in the section index's project list,
pattern table, and routes, and on Resources beside the repository. The site build passes with them.

- **Crate index** — `cgp-examples/index.md`, with a table of the five crates that links the two with
  pages and names the other three without a link.
- **`expression`** — the index; `examples/index.md` and `add-mult`, `add-mult-binary-op`,
  `add-mult-code`, and `add-mult-neg`; and `architecture/index.md` and `dispatch-layers.md`.
- **`web-app`** — the index and the four stage pages, `coarse-grained`, `fine-grained`, `namespaces`,
  and `default-impls`, under an unlinked `Stages` category, since the crate index lists the stages.
  The crate has no per-example records: each stage page ports its stage document,
  [coarse-grained.md](../../projects/cgp-examples/web-app/coarse-grained.md),
  [fine-grained.md](../../projects/cgp-examples/web-app/fine-grained.md),
  [namespaces.md](../../projects/cgp-examples/web-app/namespaces.md), and
  [default-impls.md](../../projects/cgp-examples/web-app/default-impls.md), which already have the
  example shape.

A revision must respect these facts:

- **Every run and diagnostic was reproduced.** `expression`'s three tests were run offline and passed,
  and `web-app` was checked with `cargo cgp check`. Each *Try a change* result, and each test the pages
  ask a reader to add, was run in a probe crate and is recorded in the internal document the page
  ports.
- **Two contexts have no test, so their pages give one.** The `add-mult-binary-op` and
  `add-mult-code` pages open *Run it* with an integration test the reader saves under
  `expression/tests/`, run as written in a copy of the repository. If the repository gains the tests,
  the pages switch to running them.
- **The dispatch wrapper's reason is stated as the likeliest explanation.** The base records the
  `where`-clause experiments as evidence rather than proof, and `dispatch-layers` keeps that
  uncertainty. Wiring the dispatcher directly reports `[CGP-E020]` through the context's check, as
  the [dispatch layers record](../../projects/cgp-examples/expression/architecture/dispatch-layers.md)
  states.
- **Source links point at `main`**, so until the `v0.8.0` branch merges they show the older `cgp`
  0.7.0 code, and the links into the `web-app` crate, which `main` lacks, fail.

## What it covers

**The crates are demonstrations, so they get no reference and no limitations pages**: each item is
explained where an example page first shows it, and each crate's status is a short section on its
index. They show more CGP patterns than the two libraries together, all in current idioms, and serve
the reader
[information-architecture.md](../information-architecture.md#how-each-reader-moves-through-the-site)
names as least served: the framework and library author who wants code generic over a struct's fields
or an enum's variants.

**Every crate but `greet` wires an environmental context**, so every example page outside `greet`
introduces its context as a type that stands for the application. `greet` is the one value context,
and its pages say so and link the Hello World tutorial, which teaches the same program.

## The pages still to write

The finished section is about 33 pages, estimated from the internal catalogs: about 18 examples, 7
architecture pages, 2 guides, and 6 indexes. The pages below wait on the
[prerequisites](#prerequisites).

### `builder`, the extensible builder pattern

Application contexts assembled from per-subsystem builder providers that never name the final struct.
Environmental and self-targeted: the builder contexts carry the configuration and the wiring.

- **Index** — from [builder/README.md](../../projects/cgp-examples/builder/README.md).
- **Examples**, one per builder context, from the sections of
  [builder-contexts.md](../../projects/cgp-examples/builder/reference/builder-contexts.md) once each
  has its own record:
  - `full-builder` — `FullAppBuilder` merging configurable SQLite, HTTP, and OpenAI builders into
    `App`. The pattern: independent outputs merged into one struct by field name, with configuration
    read as implicit arguments.
  - `default-builder` — `DefaultAppBuilder`, the same target from the default providers.
  - `postgres` — the database subsystem swapped for Postgres. The pattern: replacing one subsystem by
    changing one entry.
  - `anthropic` — a different struct, `AnthropicApp`, from a different AI provider. The pattern: the
    providers do not know the struct they build.
  - `anthropic-and-chatgpt` — one builder context producing three applications, chosen by a code with
    the `open` statement.
- **Architecture** — `architecture.md`, from
  [architecture/README.md](../../projects/cgp-examples/builder/architecture/README.md).

### `transfer`, a namespace-organized web service

A balance-and-transfer HTTP service in which every domain type, business operation, and cross-cutting
concern is a component, wired with prefixes, a namespace, and `#[default_impl]`. Environmental, mostly
self-targeted, with one handler dispatched per endpoint. Its scenario is also the
[money-transfer API](../../examples/money-transfer-api.md) worked example, which the applied tutorial
may draw on, so the two use the same vocabulary.

- **Index** — from [transfer/README.md](../../projects/cgp-examples/transfer/README.md), with the
  server command and `example.sh` as the way to run it.
- **Examples**, from the two traces in
  [request-lifecycle.md](../../projects/cgp-examples/transfer/architecture/request-lifecycle.md) once
  each has its own record:
  - `query-balance` — one authenticated query traced from the route to the in-memory store and back.
    The patterns: abstract domain types, a handler dispatched per endpoint marker, basic auth as a
    wrapper, and a context that joins a namespace.
  - `transfer-funds` — the transfer endpoint, with the self-transfer guard and every error status. The
    patterns: a higher-order provider guarding another, and errors raised with status-code markers.
- **Architecture** — `index.md`, `module-layout.md`, `error-design.md`, and
  `namespace-organization.md`, from
  [architecture/](../../projects/cgp-examples/transfer/architecture/README.md); the request lifecycle
  feeds the two examples rather than a page of its own.
- **Guides** — `adding-an-endpoint.md` and `swapping-the-backend.md`, from
  [guides/](../../projects/cgp-examples/transfer/guides/README.md). The second is where a reader meets
  the `[CGP-E011]` override conflict, and it shows the base-namespace design from the crate's
  [missing features](../../projects/cgp-examples/transfer/issues.md#missing-features) if the
  repository adopts it.

### `greet`, the smallest program

One greeting written as a CGP function, as a component with two providers, and over an abstract name
type; the repository's only **value context**.

- **Index** — from [greet/README.md](../../projects/cgp-examples/greet/README.md), stating that the
  Hello World tutorial teaches the first binary and linking it first.
- **Examples** — `greet-function`, `greet-component`, and `greet-abstract-type`, one per binary, from
  the README's sections once each has its own record. They use the Hello World tutorial's vocabulary
  and do not diverge from its code where the two show the same thing.
- `greet_expanded.rs` gets **no page** while it differs from the macro's output, per
  [expansion.md](../../projects/cgp-examples/greet/expansion.md).

## Prerequisites

### Knowledge-base prerequisites

**Three crates need per-example records before their pages**, per
[the guide](../writing-guides/project.md#the-page-kinds):

- **`builder`** — an `examples/` directory with one document per builder context, drawn from
  [builder-contexts.md](../../projects/cgp-examples/builder/reference/builder-contexts.md), each with a
  run once the crate has an entry point.
- **`transfer`** — `examples/query-balance.md` and `examples/transfer-funds.md`, drawn from
  [request-lifecycle.md](../../projects/cgp-examples/transfer/architecture/request-lifecycle.md) and
  the responses it records.
- **`greet`** — an `examples/` directory with one document per binary, drawn from the
  [README](../../projects/cgp-examples/greet/README.md#the-binaries).

### Code prerequisites

**These pages need changes in the repository first**, each recorded in the crate's `issues.md`:

- **Give `builder` an entry point**, a binary per builder or a test that builds each SQLite target
  against `sqlite::memory:`, so its pages show a run a reader can reproduce; see [builder's missing
  features](../../projects/cgp-examples/builder/issues.md#missing-features).
- **Add check blocks to `greet`'s two component binaries**, since a page that teaches wiring shows it
  checked; see [greet's missing features](../../projects/cgp-examples/greet/issues.md#missing-features).
- **Replace "capability" in `transfer`'s code comments**, since the pages quote that code; see
  [transfer's housekeeping](../../projects/cgp-examples/transfer/issues.md#housekeeping).
- **Worth doing, not blocking**: tests for `expression`'s two untested contexts, and the
  base-namespace refactor of `transfer`, which makes the backend guide show the better design.

### Release conditions

The crates are unpublished, so the pages clone the repository and run the crate, with no install
snippet. The `v0.8.0` branch must merge into `main` with the release, so a reader who clones the
default branch gets the code the pages describe; `main` lags it and has no `web-app` crate, per the
[workspace gaps](../../projects/cgp-examples/README.md#workspace-gaps).

## The source posts

Every part of the extensible data types series carries a notice at its top.
[Part 2](../blog/extensible-datatypes-part-2.md) links the `expression` pages, and each `expression`
example page links the post back at the section that develops it.
[Part 1](../blog/extensible-datatypes-part-1.md) links the *Extensible records* Concepts page and this
section, and gains a link to the `builder` index when those pages are written. Parts
[3](../blog/extensible-datatypes-part-3.md) and [4](../blog/extensible-datatypes-part-4.md) link the
Concepts pages and the reference, and part 4 the `expression` pages too. The
[v0.8.0 release post](../blog/v0-8-0-release.md) gets no notice, since it describes the current
design; the `web-app` pages link it at each stage's section, and the post can link the section back.

## Maintaining it

- **`expression`'s example pages, the Projects section's pilot, set the pattern for the whole
  section**, so a lesson from writing them revises [the guide](../writing-guides/project.md) rather
  than letting the next project drift.
- **Each crate stays a demonstration**: a page that begins to document every item of a crate has
  become a reference, which this section does not carry.
