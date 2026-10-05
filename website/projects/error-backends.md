# The error backends in the Projects section

The public section for `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`, the three crates
that each make one concrete type a CGP context's abstract error: one walkthrough per crate, the
shared design, the guides for choosing and debugging a backend, and one reference page per provider.
The smallest of the four sections, and the one a reader of the error-handling pages is most likely
to need next.

- **Planned URL** — `https://contextgeneric.dev/docs/projects/error-backends/`
- **Ports** — [projects/error/](../../projects/error/README.md)
- **Repository** — [`cgp`](https://github.com/contextgeneric/cgp), under `crates/standalone/error/`
  on `main`
- **Status** — planned; no page written

## What it covers

The site already explains the idea these crates implement. The *Modular error handling* Concepts
page makes the error type a wiring decision, and the reference documents `HasErrorType`,
`CanRaiseError`, `CanWrapError`, and the generic error providers such as `RaiseFrom` and
`DebugError`. What the site does not say is what to wire when a reader wants `anyhow::Error`,
`eyre::Report`, or a boxed standard error as the context's error. This section answers that, and so
it is linked from those pages rather than reached from the sidebar alone.

The section's example pages are the three crates' walkthroughs, each a short tutorial on one wiring:
set the error type, route each source type to a raising provider, wire the wrapper, then raise and
wrap an error and print it. The anyhow record's wiring is on a fieldless environmental context,
`App`, which stands for the application's choices, and the other two walkthroughs use the same
shape. The index states plainly that the crates are opt-in, that nothing in `cgp` depends on them,
and that `cgp-error-anyhow` is the one the ecosystem's projects use.

## The pages

Three walkthroughs, one architecture page, two guides, 15 reference pages, and the index: about 22
in all.

- **Index** — from the [project README](../../projects/error/README.md): the table of the three
  crates, the four roles each fills, which to reach for first, and the route to the walkthroughs and
  guides.
- **Walkthroughs**, one per crate, as the crate's `index.md`:
  - `anyhow/index.md` — from
    [cgp-error-anyhow/README.md](../../projects/error/cgp-error-anyhow/README.md): the verified
    wiring and what `{}`, `{:#}`, and `downcast_ref` show afterwards. The pattern: a concrete error
    library chosen by one wiring entry, with each source type routed by the `open` statement.
  - `eyre/index.md` — from
    [cgp-error-eyre/README.md](../../projects/error/cgp-error-eyre/README.md): the same wiring, and
    the report handler that `auto-install` supplies.
  - `std/index.md` — from [cgp-error-std/README.md](../../projects/error/cgp-error-std/README.md): a
    boxed standard error, and how a reporter walks its chain.
- **Architecture** — `architecture.md`, from
  [architecture.md](../../projects/error/architecture.md): the four roles, what a backend adds over
  the generic providers, the `Send + Sync + 'static` bounds, and the feature and `no_std` facts. The
  namespace paths the components register under are kept, since a reader wiring through a namespace
  needs them.
- **Guides** — `guides/choosing-a-backend.md` and `guides/debugging.md`, from
  [guides/](../../projects/error/guides/README.md). The choosing guide drops its section on testing
  a downstream project against a local change to the crates, which is a contributor workflow rather
  than a user's. The debugging guide keeps each mistake's snippet and its `cargo cgp check` output,
  with the canonical qualification.
- **Reference**, one page per construct under each crate's directory, from each crate's
  `reference.md`:
  - `anyhow/` — `UseAnyhowError`, `RaiseAnyhowError`, `DebugAnyhowError`, and `DisplayAnyhowError`.
  - `eyre/` — `UseEyreError`, `RaiseEyreError`, `DebugEyreError`, and `DisplayEyreError`.
  - `std/` — `UseBoxedStdError`, `RaiseBoxedStdError`, `DebugBoxedStdError`, `DisplayBoxedStdError`,
    and the types `Error`, `StringError`, and `WrapError`.

  `cgp_error_anyhow::Error` is a re-export of `anyhow::Error` rather than a construct, so it is
  mentioned on the anyhow index and gets no page.

There is **no limitations page**: the backends are small, and their limits fit in a sentence on the
index. The one unverified claim, that `cgp-error-anyhow` and `cgp-error-std` build for a target
without `std`, is stated as unverified on the architecture page rather than asserted.

## Prerequisites

**Nothing in the code.** The crates are written in current idioms, and each crate's README example
is compiled and run by the `cgp` test suite, which is what the walkthroughs quote.

**Two records need their own verified wiring first.** Only
[cgp-error-anyhow/README.md](../../projects/error/cgp-error-anyhow/README.md#what-it-provides)
quotes a wiring and what printing the error produces. The
[eyre](../../projects/error/cgp-error-eyre/README.md) and
[std](../../projects/error/cgp-error-std/README.md) records say only that the wiring is the same
with their names, so each needs its crate README's example quoted, with the output its
`readme_eyre.rs` or `readme_std.rs` test run produced: for eyre, the report with its `Location:`
section, and for std, the chain printed with `{}` and with `{:#}`. Those outputs are what
distinguish the three walkthroughs.

**The release conditions are the `cgp` release itself.** The crates ship from the `cgp` repository
at the same version, and the pages describe the 0.8.0 release, so they are written against the source
and published once that release is on crates.io.

## Links into the section

This section is the one whose inbound links matter more than its sidebar position. When it
publishes, the *Modular error handling* Concepts page, the reference pages for `HasErrorType`,
`CanRaiseError`, and `CanWrapError`, the error providers overview, and Resources each link the
section index or the matching walkthrough, per the [project
README](../../projects/error/README.md#public-material-derived-from-these-documents). There is no
source post.

## Maintaining it

The crates are near copies of one design, so a change to one usually reaches all three. Revise the
three walkthroughs and the matching reference pages together, and keep the shared design on the one
architecture page rather than repeating it per crate.
