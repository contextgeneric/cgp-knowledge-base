# Quickstart

The Quickstart gets a reader to a running CGP program without teaching anything.

- **URL:** <https://contextgeneric.dev/docs/quickstart>
- **Source:** [docs/quickstart.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/quickstart.md)
- **Status:** Current
- **How it was made:** written by an agent from this base, level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md); its program is verified by
  compiling and running it, and its install path cannot be walked until the release (see below)

## What it covers

The page has four parts: the install, one complete program for `src/main.rs`, the exact output of
`cargo run`, and one link to the Hello World tutorial. It opens by naming Context-Generic Programming
with a short form of the tag line, because it may be a reader's first contact, and says the reader
can follow it without learning the concepts.

The install names Rust 1.89, the floor `cgp` declares, because on Rust 1.88 `cargo add cgp` selects
`cgp` 0.4.2 and the program fails with "cannot find attribute `cgp_fn`". It creates the project with
`cargo new` before `cargo add cgp`, and shows the version that writes.

The program is a `#[cgp_fn]` function with an `#[implicit]` argument reading a field of a
`#[derive(HasField)]` struct, the gentlest entry CGP has, per the
[comprehension barriers](../../communication-strategy/readers.md#the-comprehension-barriers): a
function and a struct, with no wiring, generics, or trait to understand. It is a **value context,
self-targeted**: `Person` is the thing being greeted.

**It stops before the second context, which is the whole boundary against
[Hello World](../tutorials/hello-world.md).** The tutorial's payoff is running `greet` unchanged on a
second context; the Quickstart only proves the program runs. The two show similar code on purpose,
so a reader arriving at the tutorial sees at once what is new.

## How it relates to the knowledge base

[writing-guides/orientation.md](../writing-guides/orientation.md) specifies the page type and owns the
ten-minute activation target that [evidence.md](../../communication-strategy/evidence.md) records as
the site's activation signal. The construct choices come from
[readers.md](../../communication-strategy/readers.md#the-comprehension-barriers), the opening
descriptor from [identity.md](../../communication-strategy/identity.md#the-tag-line), and the program's
shape from the [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md) and
[`#[implicit]`](../../cgp/reference/attributes/implicit.md) references.

The program is compiled in the [`example-code` crate](../site.md#the-example-code-crate) as the
standalone binary `tests/quickstart.rs`, where the page's `fn main` is a `#[test]`; a second test
compares the page's `src/main.rs` block with the compiled program.

## Maintaining it

- **Do not let it grow.** A second example, an explanation of `#[implicit]`, or a note on the
  expansion turns it into a worse copy of the tutorial. The guide's check is to run it on a clean
  machine and time it; over ten minutes means a step comes out.
- **Re-pin it with the release.** The install names a version, and re-pinning is on the
  [release checklist](../writing-guides/release-announcement.md#publishing-and-what-happens-afterwards)
  beside the tutorials.
- **Walk the install at the release.** `cgp = "0.8.0"` does not resolve on crates.io until the
  release is published, so the guide's real check, pasting the program into a fresh project on a
  clean machine and timing the walk, runs then, before the branch merges if the crate is published
  first.
