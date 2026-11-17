# Releases

This document is the companion of Hypershell's release-notes pages on the website. Each page lists
the user-visible changes of one official release and the steps to upgrade; this document records,
per version, the facts behind the page and every finding of the diff review the page leaves out, as
the website's [release-notes guide](../../website/writing-guides/release-notes.md#two-layers-two-readers)
requires. Like [releases/](../../releases/README.md) for `cgp`, it records history, so it is exempt
from the base's rule on documenting the present.

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
- **The build at the tag:** the toolchain file names stable Rust 1.87, the same as `rust-version`,
  and the repository has no `.cargo/config.toml`; the manifest's `[patch.crates-io]` table points
  Hypershell's own crates at their paths, with commented-out `cgp` git entries, none of which a
  published crate carries.
- **Package metadata at the tag:** every crate's `repository` names the `cgp` repository, the only
  keyword is `cgp`, and all crates share the description "Modular DSL for shellscripting in Rust".
- **The examples:** the unpublished `hypershell-examples` crate holds 11 programs; two of them,
  `http_checksum_native` and `bluesky_websocket`, build their own presets, `MyAppPreset` among them.
- **`StreamToLines`:** its handler, `HandleStreamToLines` in `hypershell-tokio-components`, is
  wired by no preset, so neither context runs the step; the page says so in one sentence.

## Public material derived from this

The website's `docs/release-notes/hypershell/` pages, recorded in
[website/pages/release-notes.md](../../website/pages/release-notes.md).
