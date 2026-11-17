# Releases

This document records, for each official Hypershell release, the facts behind its website
release-notes page and every finding of the diff review that the page leaves out. The page serves
an upgrader; this record serves an agent that needs the finer detail, as the website's
[release-notes guide](../../website/writing-guides/release-notes.md#two-layers-two-readers) divides
the two. Like [releases/](../../releases/README.md) for `cgp`, it records history, so it is exempt
from the base's rule on documenting the present.

## v0.2.0

- **Page:** <https://contextgeneric.dev/docs/release-notes/hypershell/v0.2.0>, written before the
  release; its date and links are set on release day.
- **Commits:** 69 from v0.1.0, through pull requests #1 to #5; #5 carries the move to `cgp` 0.8.0
  and the fixes.
- **Old notes:** none yet; the release's GitHub Release is a one-sentence pointer to the page.

The page leaves these findings out:

- **The path through `cgp`'s releases:** the repository moved through `cgp` 0.4.2, 0.5.0, 0.6.0,
  and 0.7.0 before 0.8.0; none of those states was published, so the page gives one move.
- **The changes on that path:** `#[cgp_context]` was dropped, the async `Send` bounds removed, and
  `#[cgp_provider]` replaced by `#[cgp_impl]`, each inside `cgp`'s own upgrade steps.
- **The probe that could not run:** `hypershell` 0.1.0 from crates.io fails to build on Rust 1.98.1,
  with `E0364` re-export errors in its own preset modules.
- **How the fixes were checked instead:** in the source at both tags. No v0.1.0 preset wires
  `PutMethod` or `DeleteMethod`, `ConvertTo` is wired as `Promote<HandleConvert>`, the streaming
  exec never waits for the child, and the WebSocket handler unwraps the connection result.
- **The examples:** the unpublished crate holds 13 programs, and `compare_and_branch` and
  `parallel_compare` define their `Compare` and `If` syntax in its `dsl` module.
- **The toolchain:** the repository moved from stable Rust 1.87 to a pinned nightly with
  `-Z next-solver=globally` in `.cargo/config.toml`.
- **Stable builds:** a crate outside the workspace builds the library and the `hello` program on
  stable Rust 1.98.1.
- **`StreamToLines`** is still wired by no namespace, as in v0.1.0; [issues.md](issues.md) records
  it.

## v0.1.0

- **Page:** <https://contextgeneric.dev/docs/release-notes/hypershell/v0.1.0>.
- **Dates:** published on crates.io on 2025-06-13, the day of its tag; the post followed on
  2025-06-14.
- **Commits:** 127 on the first-parent line up to the tag.
- **Old notes:** the [release post](../../website/blog/hypershell-release.md) alone; the repository
  has no GitHub Release and no changelog.

The page leaves these findings out:

- **The post's teaching:** its CGP introduction, the prototypal-inheritance comparison, the
  implementation walk-through, and its discussion of costs and future DSLs, which explain the
  release rather than change it.
- **The toolchain at the tag:** the toolchain file names stable Rust 1.87, the same as
  `rust-version`, and the repository has no `.cargo/config.toml`.
- **The patch table:** the manifest's `[patch.crates-io]` points Hypershell's own crates at their
  paths, beside commented-out `cgp` git entries; a published crate carries neither.
- **Package metadata at the tag:** every crate's `repository` names the `cgp` repository, the only
  keyword is `cgp`, and all crates share the description "Modular DSL for shellscripting in Rust".
- **The examples:** the unpublished `hypershell-examples` crate holds 11 programs, and
  `http_checksum_native` and `bluesky_websocket` build their own presets, `MyAppPreset` among them.
- **`StreamToLines`:** its handler, `HandleStreamToLines` in `hypershell-tokio-components`, is
  wired by no preset, so neither context runs the step; the page says so in one sentence.

## Public material derived from this

The website's `docs/release-notes/hypershell/` pages, recorded in
[website/pages/release-notes.md](../../website/pages/release-notes.md).
