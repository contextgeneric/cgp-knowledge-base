# cgp-examples

`cgp-examples` is a repository of five independent example crates, each a small program that shows
one area of CGP in use: an HTTP service, a modular interpreter, an application builder, a study of
wiring at scale, and a greeting program. The crates share a workspace and nothing else, so these
documents treat each one as its own subproject.

- **Repository** — <https://github.com/contextgeneric/cgp-examples>
- **Local checkout** — `../cgp-examples`, per [sibling-projects.md](../../sibling-projects.md)
- **Branch documented** — `v0.8.0`
- **Crates** — `cgp-example-transfer`, `cgp-example-expression`, `cgp-example-builder`,
  `cgp-example-web-app`, and `cgp-example-greet`, all at 0.1.0 and unpublished
- **Tracks** — `cgp` 0.8.0-alpha, through a git patch to the `cgp` repository's `main` branch
- **Status** — Demonstrations rather than libraries; see [Workspace gaps](#workspace-gaps)

## What it is

Each crate develops one scenario, and four of the five correspond to a worked example under
[examples/](../../examples/README.md) that teaches the same patterns on its own. The crates are the
code as it ships; the worked examples are where an agent learns the patterns, per
[../../AGENTS.md](../../AGENTS.md#project-facts-and-cgp-patterns-have-separate-owners). The table
records, for each crate, what kind of context it wires, which blog post presents its code, and whether
it runs. A post that links the repository is marked as linking; the v0.8.0 post shows `web-app`'s code
without linking it. Every crate uses current CGP idioms, so its code is safe to copy for the patterns
it shows, apart from `greet`'s hand-written expansion, which is not the macro's current output:

| Subproject | Scenario | Context shape | Worked example | Blog post | Runs |
|---|---|---|---|---|---|
| [`transfer`](transfer/README.md) | balance and transfer endpoints served over HTTP | environmental; self-targeted, with one handler dispatched per endpoint | [money-transfer API](../../examples/money-transfer-api.md) | [v0.5.0 release](../../website/blog/v0-5-0-release.md), linking | yes, a server binary |
| [`expression`](expression/README.md) | an arithmetic interpreter open to new variants and operations | environmental; parameter-targeted | [expression interpreter](../../examples/expression-interpreter.md) | [extensible data types, part 2](../../website/blog/extensible-datatypes-part-2.md), linking | three unit tests |
| [`builder`](builder/README.md) | an application context assembled from per-subsystem builders | environmental; self-targeted | [application builder](../../examples/application-builder.md) | [extensible data types, part 1](../../website/blog/extensible-datatypes-part-1.md), linking | no entry point |
| [`web-app`](web-app/README.md) | one social-media backend wired four ways, up to namespace defaults | environmental; self-targeted | [social media app](../../examples/social-media-app.md) | [v0.8.0 release](../../website/blog/v0-8-0-release.md) | compiles only |
| [`greet`](greet/README.md) | a greeting written as a function, a component, and over an abstract type | value context; self-targeted | none | none | yes, three binaries |

## Which revision these documents describe

These documents describe the `v0.8.0` branch, which tracks `cgp` 0.8.0-alpha. It is 13 commits ahead
of `main`, which builds against the published `cgp` 0.7.0 and has no `web-app` crate, no namespace
wiring in `transfer`, and no `transfer` README. None of the crates is published. Source links point at
the `v0.8.0` branch, per
[../AGENTS.md](../AGENTS.md#a-project-section-documents-its-project-in-depth).

The repository also carries an unmerged `profile-picture` branch, which adds a `profile-picture` crate
and drops `web-app`. Nothing on that branch is documented here; the published version of that
scenario is the separate
[cgp-example-profile-picture](https://github.com/contextgeneric/cgp-example-profile-picture)
repository, taught as the [profile picture](../../examples/profile-picture.md) worked example.

## Building

The workspace builds against unreleased `cgp` code: its `[patch.crates-io]` section overrides `cgp`
and `cgp-error-anyhow` with the `cgp` repository's `main` branch by git URL, and the lockfile pins the
commit. To test against a local change to `cgp`, switch the same entries to the commented-out paths
into `../cgp`. It needs stable Rust 1.90 or later and uses the 2024 edition, and the repository has no
toolchain file. These documents were verified against `cgp` `main` at commit `adc616c`
(2026-09-26), with `rustc` 1.98.1, where `cargo test --workspace` passes. The only tests in the workspace are three unit tests in `expression`;
the other crates check their wiring at compile time with `check_components!` blocks, so a successful
build is most of their verification.

## Workspace gaps

These gaps belong to the repository as a whole rather than to one crate, so they are recorded here
rather than in a subproject's `issues.md`:

- **Empty root README** — the repository's `README.md` is empty, so a visitor finds no index of the
  crates. Only `transfer` has a README of its own.
- **`main` lags `v0.8.0`** — a reader who clones the default branch gets the `cgp` 0.7.0 versions of
  four crates and no `web-app`.

## The documents

Each subproject has its own section, sized to its crate, with its own `testing.md` and `issues.md`,
per [../AGENTS.md](../AGENTS.md#the-shape-of-a-project-section). One document spans them:

- [constructs.md](constructs.md) — each CGP construct the crates use, mapped to the subproject
  documents that show it in running code.

- [transfer/](transfer/README.md) — the money-transfer HTTP service:
  - [architecture/](transfer/architecture/README.md) — the design on one page, and:
    - [module-layout.md](transfer/architecture/module-layout.md) — the five modules and which kind of
      item each holds.
    - [error-design.md](transfer/architecture/error-design.md) — status-code markers, one error
      type, and the per-detail dispatch of the error provider.
    - [namespace-organization.md](transfer/architecture/namespace-organization.md) — the prefix tree,
      the two tables the context draws on, and the one path it overrides.
    - [request-lifecycle.md](transfer/architecture/request-lifecycle.md) — one balance query traced
      through every layer, with the recorded responses.
  - [reference/](transfer/reference/README.md) — every public item, grouped by family.
  - [guides/](transfer/guides/README.md) — adding an endpoint, and swapping the backend.
  - [testing.md](transfer/testing.md) — what the checks pin, and what nothing tests.
  - [issues.md](transfer/issues.md) — defects, missing features, and housekeeping.
- [expression/](expression/README.md) — the modular arithmetic interpreter:
  - [architecture/](expression/architecture/README.md) — the design on one page, and
    [dispatch-layers.md](expression/architecture/dispatch-layers.md) on the two ways the contexts key
    their dispatch and the wrapper every context needs.
  - [reference/](expression/reference/README.md) — the types, abstract types, evaluation and
    conversion providers, and dispatchers.
  - [examples/](expression/examples/README.md) — one document per context, with its tests and checks.
  - [testing.md](expression/testing.md) — the three tests, the four check blocks, and what nothing
    tests.
  - [issues.md](expression/issues.md) — missing features and housekeeping.
- [builder/](builder/README.md) — the application builder:
  - [architecture/](builder/architecture/README.md) — the design on one page.
  - [reference/](builder/reference/README.md) — the subsystem providers, the application structs, and
    the builder contexts.
  - [testing.md](builder/testing.md) — what the checks catch, what a probe ran, and what nothing
    tests.
  - [issues.md](builder/issues.md) — missing features and housekeeping.
- [web-app/](web-app/README.md) — the social-media wiring study, one document per stage:
  - [coarse-grained.md](web-app/coarse-grained.md) — one manager trait per domain.
  - [fine-grained.md](web-app/fine-grained.md) — one trait per operation, filter wrappers, and
    bundles.
  - [namespaces.md](web-app/namespaces.md) — the prefix tree and the production and test contexts.
  - [default-impls.md](web-app/default-impls.md) — a custom namespace that supplies seven of the nine
    components.
  - [testing.md](web-app/testing.md) — what the checks pin and catch, and what nothing tests.
  - [issues.md](web-app/issues.md) — missing features and housekeeping.
- [greet/](greet/README.md) — the greeting program, with its three binaries:
  - [expansion.md](greet/expansion.md) — the hand-written expansion against the macro's output.
  - [testing.md](greet/testing.md) — what running the binaries shows, and what nothing tests.
  - [issues.md](greet/issues.md) — the missing check blocks and housekeeping.

## Public material derived from these documents

These documents are the verified source for the repository's own READMEs, above all the `transfer`
walkthrough, whose drift from the code is recorded in
[transfer/issues.md](transfer/issues.md). They also feed the planned
[extensible data types deep dive](../../website/deep-dives/extensible-datatypes.md), which uses
`builder` and `expression` as its running code, and the unfinished
[v0.8.0 release post](../../website/blog/v0-8-0-release.md), whose code follows `web-app`.

## How it relates to the rest of the base

The worked examples in the table are the teaching versions of these crates and stand alone; an agent
learning a pattern reads the worked example, and an agent changing a crate reads its section here.
The blog records in the table track how far each post has drifted from the current release, and link
here for the code as it stands. The CGP constructs the crates use are documented under
[cgp/](../../cgp/README.md) and linked from each subproject rather than re-explained.
