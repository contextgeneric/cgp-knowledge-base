# The error backends in the Projects section

The public section for `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`, the three crates
that each make one concrete type a CGP context's abstract error: one walkthrough per crate, the shared
design, the guides for choosing and debugging a backend, and one reference page per provider. The
smallest of the four sections, and the one a reader of the error-handling pages most likely needs next.

- **Planned URL** — `https://contextgeneric.dev/docs/projects/error-backends/`
- **Ports** — [projects/error/](../../projects/error/README.md)
- **Repository** — [`cgp`](https://github.com/contextgeneric/cgp), under `crates/standalone/error/`
  on `main`
- **Status** — planned; no page written

## What it covers

**The section answers what to wire for `anyhow::Error`, `eyre::Report`, or a boxed standard error as
the context's error**, which the site does not: the *Modular error handling* Concepts page makes the
error type a wiring decision, and the reference documents `HasErrorType`, `CanRaiseError`,
`CanWrapError`, and the generic error providers. So it is reached from those pages, not from the
sidebar alone.

Each crate's walkthrough is a short tutorial on one wiring: set the error type, route each source type
to a raising provider, wire the wrapper, then raise, wrap, and print an error. The wiring is on a
fieldless environmental context, `App`, which stands for the application's choices. The index states
that the crates are opt-in, that nothing in `cgp` depends on them, and that `cgp-error-anyhow` is the
one the ecosystem's projects use.

## The pages

Three walkthroughs, one architecture page, two guides, 15 reference pages, and the index: about 22.

- **Index** — from the [project README](../../projects/error/README.md): the table of the three
  crates, the four roles each fills, which to reach for first, and the route to the walkthroughs and
  guides.
- **Walkthroughs**, one per crate, as the crate's `index.md`:
  - `anyhow/index.md` — from
    [cgp-error-anyhow/README.md](../../projects/error/cgp-error-anyhow/README.md): the verified wiring
    and what `{}`, `{:#}`, and `downcast_ref` show afterwards. The pattern: a concrete error library
    chosen by one wiring entry, with each source type routed by the `open` statement.
  - `eyre/index.md` — from [cgp-error-eyre/README.md](../../projects/error/cgp-error-eyre/README.md):
    the same wiring, and the report handler that `auto-install` supplies.
  - `std/index.md` — from [cgp-error-std/README.md](../../projects/error/cgp-error-std/README.md): a
    boxed standard error, and how a reporter walks its chain.
- **Architecture** — `architecture.md`, from [architecture.md](../../projects/error/architecture.md):
  the four roles, what a backend adds over the generic providers, the `Send + Sync + 'static` bounds,
  the feature and `no_std` facts, and the namespace paths the components register under, which a
  reader wiring through a namespace needs. The one unverified claim, that `cgp-error-anyhow` and
  `cgp-error-std` build for a target without `std`, is stated as unverified.
- **Guides** — `guides/choosing-a-backend.md` and `guides/debugging.md`, from
  [guides/](../../projects/error/guides/README.md). The choosing guide drops its section on testing a
  downstream project against a local change to the crates, a contributor workflow. The debugging
  guide keeps each mistake's snippet and its `cargo cgp check` output.
- **Reference**, one page per construct under each crate's directory, from each crate's
  `reference.md`:
  - `anyhow/` — `UseAnyhowError`, `RaiseAnyhowError`, `DebugAnyhowError`, and `DisplayAnyhowError`.
  - `eyre/` — `UseEyreError`, `RaiseEyreError`, `DebugEyreError`, and `DisplayEyreError`.
  - `std/` — `UseBoxedStdError`, `RaiseBoxedStdError`, `DebugBoxedStdError`, `DisplayBoxedStdError`,
    and the types `Error`, `StringError`, and `WrapError`.

  `cgp_error_anyhow::Error` re-exports `anyhow::Error`, so the anyhow index mentions it and it gets no
  page.

**There is no limitations page**: the backends are small, and their limits fit in a sentence on the
index.

## Prerequisites

**Nothing in the code.** The crates use current idioms, and the `cgp` test suite compiles and runs
each crate README's example, which the walkthroughs quote.

**The eyre and std records need their own verified wiring first.** Only
[cgp-error-anyhow/README.md](../../projects/error/cgp-error-anyhow/README.md#what-it-provides) quotes a
wiring and its printed error. The [eyre](../../projects/error/cgp-error-eyre/README.md) and
[std](../../projects/error/cgp-error-std/README.md) records say only that the wiring is the same with
their names, so each needs its README's example quoted with the output its `readme_eyre.rs` or
`readme_std.rs` test produced: for eyre, the report with its `Location:` section, and for std, the
chain printed with `{}` and with `{:#}`. Those outputs distinguish the three walkthroughs.

**The release condition is the `cgp` release itself.** The crates ship from the `cgp` repository at the
same version, so the pages are written against the source and published once 0.8.0 is on crates.io.

## Links into the section

When the section publishes, the *Modular error handling* Concepts page, the reference pages for
`HasErrorType`, `CanRaiseError`, and `CanWrapError`, the error providers overview, and Resources each
link the section index or the matching walkthrough, per the
[project README](../../projects/error/README.md#public-material-derived-from-these-documents). There is
no source post.

## Maintaining it

The crates are near copies of one design, so a change to one usually reaches all three: revise the
three walkthroughs and their reference pages together, and keep the shared design on the one
architecture page.
