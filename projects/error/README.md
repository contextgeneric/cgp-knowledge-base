# The CGP error backends

The error backends are three small crates, `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`,
that each fix a CGP context's abstract error type to one concrete type and supply the providers that
raise errors into it and add detail to it. Generic code is written against `HasErrorType`,
`CanRaiseError`, and `CanWrapError`; a backend is what a context wires to make those traits concrete.

- **Repository** — <https://github.com/contextgeneric/cgp>, under
  [`crates/standalone/error/`](https://github.com/contextgeneric/cgp/tree/main/crates/standalone/error)
- **Local checkout** — `../cgp/crates/standalone/error`, per
  [sibling-projects.md](../../sibling-projects.md)
- **Branch documented** — `main`
- **Crates** — `cgp-error-anyhow`, `cgp-error-eyre`, and `cgp-error-std`, all at 0.8.0-alpha
- **Tracks** — `cgp` 0.8.0-alpha, through a path dependency on `cgp-core`
- **Status** — Small and complete for what they cover; tested by the `error_backends` target of
  `cgp-tests`

## What they are

The crates live in the `cgp` repository but are not part of the `cgp` crate: an application adds the
one it wants as a separate dependency, and nothing in `cgp` depends on them. So they are documented
here as a project of their own rather than under [cgp/](../../cgp/README.md), which documents the
traits they implement. The traits, the in-tree generic providers such as `RaiseFrom` and
`DebugError`, and the idea of treating the error type as a wiring decision all belong to
[modular error handling](../../cgp/concepts/modular-error-handling.md) and the
[error providers reference](../../cgp/reference/providers/error_providers.md); these documents cover
only what the three crates add.

The three crates share one design, set out in [architecture.md](architecture.md). Each exports a
provider that sets the error type, a provider that raises a standard error without formatting it,
and two providers that format any `Debug` or `Display` value into a message, where the last three
also wrap a detail onto an existing error:

| Crate | Error type | Type provider | Raise | Format with `{:?}` | Format with `{}` | `no_std` |
|---|---|---|---|---|---|---|
| [`cgp-error-anyhow`](cgp-error-anyhow/README.md) | `anyhow::Error` | `UseAnyhowError` | `RaiseAnyhowError` | `DebugAnyhowError` | `DisplayAnyhowError` | yes |
| [`cgp-error-eyre`](cgp-error-eyre/README.md) | `eyre::Report` | `UseEyreError` | `RaiseEyreError` | `DebugEyreError` | `DisplayEyreError` | no |
| [`cgp-error-std`](cgp-error-std/README.md) | `Box<dyn core::error::Error + Send + Sync>` | `UseBoxedStdError` | `RaiseBoxedStdError` | `DebugBoxedStdError` | `DisplayBoxedStdError` | yes |

`cgp-error-anyhow` is the one the ecosystem uses: [hypershell](../hypershell/README.md), the
[cgp-serde](../cgp-serde/README.md) tests, and the [cgp-examples](../cgp-examples/README.md) `builder`
crate all wire it, as do three worked examples. No project in the ecosystem wires `cgp-error-eyre` or
`cgp-error-std`, so their only users are the tests.

## Which revision these documents describe

These documents describe the crates on the `cgp` repository's `main` branch at version 0.8.0-alpha.
The 0.8.0-alpha crates on crates.io carry the same public items but differ from this source in four
ways that change behavior:

- **eyre panics.** The published `cgp-error-eyre` builds eyre with no features, so every report it
  builds panics unless the application has installed a hook with `eyre::set_hook`. This source
  enables `auto-install`.
- **eyre locations.** Where the application enables eyre's default features, the published crate's
  reports record a `Location:` inside the backend. In this source `raise_error` and `wrap_error` are
  `#[track_caller]` and the crate enables `track-caller`, so the location is the caller's line.
- **std wrapping.** The published `RaiseBoxedStdError` implements only `ErrorRaiser`, so it cannot be
  wired as a wrapper. This source gives it an `ErrorWrapper` impl.
- **std chains.** The published `WrapError` prints its source inside its own `Display` and also
  returns it from `source()`, so a reporter that walks the chain prints the source twice. This source
  prints the detail alone with `{}`.

The published crates also depend on anyhow 1.0.95 and eyre 0.6.12, where this source requires anyhow
1.0.104 and eyre 0.6.14, and they write their providers in the explicit provider-trait forms that
`#[cgp_impl]` with `#[use_type]` replaces here. Source links point at `main`, which is the branch
[sibling-projects.md](../../sibling-projects.md) records for this project.

## Building and testing

The crates are members of the `cgp` workspace, so they build with it: stable Rust 1.89 or later, the
2024 edition, and the toolchain pinned in the workspace's `rust-toolchain.toml`. Each depends on
`cgp-core` under the name `cgp`, because the CGP macros emit paths through `::cgp`. For the same
reason the example in each crate's README is marked `ignore` rather than run as a doctest: in the
crate's own doctests `cgp` names `cgp-core`, which has no `core` module, while the example imports
from the `cgp` facade the way an application does. The tests live in the `cgp-tests` crate's
`error_backends` target and run with the rest of the suite, which CI runs through
`cargo nextest`; each crate's `testing.md` says what they pin. So that the README examples are
still checked, the `cgp-tests` build script reads each README, turns its `ignore` block into a test
module, and the `readme_anyhow.rs`, `readme_eyre.rs`, and `readme_std.rs` files include it, which
keeps the README the only copy of its example.

These documents were verified against the `cgp` source on `main` at commit `adc616c`, with `rustc`
1.98.1, where `cargo test --workspace --all-features` and both clippy configurations pass. One claim
could not be checked by building: that `cgp-error-anyhow` and `cgp-error-std` compile for a target
without `std`, because no such target was installed. The `no_std` column above therefore rests on the crates'
source and on anyhow declaring itself `no_std`, and the `cgp` repository's CI does not build any
crate for a bare-metal target either.

## Confirmed gaps

The crates have no open defects. One repository-wide housekeeping item remains:

- **No bare-metal build.** Nothing builds `cgp-error-anyhow` or `cgp-error-std` for a target without
  `std`, so their `no_std` status is not checked in CI.

Each crate's own `issues.md` lists what is specific to it.

## The catalog

The section follows the [project shape](../AGENTS.md#the-shape-of-a-project-section), with one
subdirectory per crate. Because the three crates are near copies of each other, the design and the
guides are shared at the project level rather than repeated in each crate, and each crate carries a
single `reference.md` in place of a `reference/` directory.

- [architecture.md](architecture.md) — the shared design: the four roles, how each maps onto the
  error components, what a backend adds over the generic providers, the `Send + Sync + 'static`
  bounds, the namespace paths the components register under, and the feature and `no_std` facts.
- [guides/](guides/README.md) — choosing a backend and routing each source type, and debugging the
  wiring mistakes a backend invites.
- [cgp-error-anyhow/](cgp-error-anyhow/README.md) — `anyhow::Error` as the context's error.
- [cgp-error-eyre/](cgp-error-eyre/README.md) — `eyre::Report` as the context's error.
- [cgp-error-std/](cgp-error-std/README.md) — a boxed standard error, with the `StringError` and
  `WrapError` types.

## Public material derived from these documents

These documents feed the crates' own READMEs, which are also their rustdoc front pages on docs.rs,
the `/cgp` skill's
[error backends](https://github.com/contextgeneric/cgp-skills/blob/main/cgp/references/error-backends.md)
reference, and the website pages that name the backends: the Resources page, the modular-error-handling concept
page, and the reference pages for `CanRaiseError`, `CanWrapError`, `HasErrorType`, and the error
providers. The website records for those pages are in
[website/site-structure.md](../../website/site-structure.md).
