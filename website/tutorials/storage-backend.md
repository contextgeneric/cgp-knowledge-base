# Storage backend tutorial

The site's applied-register tutorial: a single page that builds a profile-picture lookup on an
application context, then gives its tests their own storage backend with a component and two
providers, so a reader sees one operation run against two backends each context chose.

- **URL**: <https://contextgeneric.dev/docs/tutorials/storage-backend>
- **Source**: [docs/tutorials/storage-backend.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/tutorials/storage-backend.md),
  published with the v0.8.0 release
- **Pages**: one, at `sidebar_position: 3` in the tutorials category, after Hello World and before
  the area-calculation series
- **Status**: Current
- **How it was made**: written by an agent from the knowledge base; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md), with the provenance line that
  links the disclosure page's documentation section

## What it teaches

The page opens with the problem: a deployment reads its files from disk, and its tests would rather
not touch the disk. It sets up a binary project with `cgp`, `anyhow`, and `tokio`, then introduces
`App` as a type that stands for the application, with a `HashMap` standing in for the database and a
`local_dir` field naming the picture folder.

**Read the application's data with functions** writes `get_user` and `fetch_storage_object` as async
`#[cgp_fn]` functions whose `#[implicit]` arguments read `App`'s fields, and a `main` that writes a
picture and prints `Alice has a 16-byte picture`. **Combine the steps** adds
`get_user_profile_picture`, which declares both with `#[uses]`, and notes that a context lacking
`local_dir` cannot call it.

**Add a backend for tests** is where the page pays off. One `#[cgp_fn]` has one implementation, so
the storage step becomes the `CanFetchStorageObject` component with the `FetchLocalObject` provider.
`App` chooses it with `delegate_components!`, described as a lookup table resolved at compile time,
and a test module defines `TestApp`, the `FetchMemoryObject` provider, and its own table. The test
passes without the disk, and `get_user_profile_picture` is unchanged.

**Check the wiring** says wiring is lazy, adds `check_components!` for both contexts, deletes
`App`'s `local_dir` field, and shows a shortened raw error, then the `cargo cgp check` report
naming the missing field, with the canonical qualification. rustc reports the mistake at the
check and at the call in `main`, and the page says the tool keeps the check's report, the one it
quotes. **Where to go next** routes to the area-calculation
series, two Concepts pages, the Overview's abstract error type, and, for the
framework author, the extensible-data Concepts pages. The Overview's *Where to go next* and the
area-calculation series' Checking and Debugging page link it back.

## The teaching contract

**Objective.** A reader can give one operation of an application two implementations, choose one per
context in a checked wiring table, and test the operation against an in-memory backend.

**Prerequisites.** Rust, async functions, and adding a dependency. It assumes no CGP, and says that
Hello World is a shorter first look at the same starting point, but does not require it. It does not
assume blanket implementations, coherence, or the generated traits, and never names them.

**Register and shape.** Applied, so it has no desugaring section and links the area-calculation
series and the Concepts pages for the mechanism. Its running example is an **environmental context**
whose component targets `Self`: `App` and `TestApp` stand for the application and its test, and both
carry fields. It is the section's first environmental context, which is why it sits second, after
Hello World's value context, as the
[tutorial guide](../writing-guides/tutorial.md#say-which-shape-the-tutorials-example-is-in) sets out.

**Concept sequence.** Prelude → application context with `#[derive(HasField)]` → `#[cgp_fn]` with
`#[implicit]` → `#[uses]` → `#[cgp_component]` → `#[cgp_impl]` → `delegate_components!` → a second
context and provider → lazy wiring → `check_components!` → `cargo cgp check`. The component arrives
only when the test needs a second implementation, which is the guide's construct ladder.

**Payoff.** The test passing in *Add a backend for tests*, with the lookup unchanged. Earlier, the
component has no reason to exist; later, the checking section would carry the motivation instead.

**Level of explanation.** Shallow: each construct is named for the job it does, and the mechanism is
one sentence about the lookup table resolving at compile time. `IsProviderFor` and
`DelegateComponent` never appear; `CanUseComponent` and the `Chars` list appear only inside the
quoted raw error.

**Vocabulary.** "Context", "component", and "provider" in bold where each first becomes necessary;
"wiring table" and "lookup table" for `delegate_components!`; "consumer trait" and "provider trait"
are avoided, with `StorageObjectFetcher` described as "the trait each implementation targets",
consistent with [vocabulary.md](../../communication-strategy/vocabulary.md).

## How it relates to the knowledge base

The scenario is the [profile-picture example](../../examples/profile-picture.md), which the
[Overview](../pages/overview.md) and the `cgp` README also use, under the same names
(`CanFetchStorageObject`, `StorageObjectFetcher`, `App`) and the Overview's `FetchLocalObject` and
`local_dir`. The page departs from the example in three ways that keep it runnable without a server
or cloud account: a `HashMap` stands in for the database, the storage step reads a local folder and
memory rather than S3 and Google Cloud, and the lookup returns the picture's bytes rather than
decoding an image. No project ships the scenario, so the page routes to the Overview's S3 and Google
Cloud providers rather than to a Projects example page. The page keeps the async methods that the
Overview drops, so its two links to the Overview call that code a synchronous version of this
component.

The constructs are [`#[cgp_fn]`](../../cgp/reference/macros/cgp_fn.md),
[`#[implicit]`](../../cgp/reference/attributes/implicit.md),
[`#[uses]`](../../cgp/reference/attributes/uses.md),
[`#[async_trait]`](../../cgp/reference/macros/async_trait.md),
[`#[cgp_component]`](../../cgp/reference/macros/cgp_component.md),
[`#[cgp_impl]`](../../cgp/reference/macros/cgp_impl.md),
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md), and
[`check_components!`](../../cgp/reference/macros/check_components.md). The page follows the
[tutorial guide](../writing-guides/tutorial.md)'s applied register and its checking obligation.

## Where it diverges from CGP v0.8.0

**Nothing.** The code compiles against `cgp` 0.8.0, and the `Cargo.toml` pins `cgp = "0.8.0"`,
which resolves once the release is published.

## Maintaining it

- **The code compiles in the website's `example-code` crate.** Each step is a module of
  `tests/tutorials/storage_backend.rs`, assembled from the page's blocks in order. The deliberate
  mistake is `tests/compile_fail/tutorials/storage_backend_missing_field.rs`, the whole finished
  file with the field deleted, with its explanation at the end so its line numbers match a reader's
  `src/main.rs`.
- **The quoted output comes from that fixture.** The raw excerpt matches its blessed `.stderr`,
  whose `Chars` abbreviation depends on the pinned toolchain, and the `cargo cgp check` report was
  captured from it with `cargo-cgp`'s pinned driver. A change to the program captures both again
  rather than editing the text.
- **Keep the payoff in place.** The component must still arrive because the test needs a second
  backend; adding a component earlier, or an abstract error type, belongs in a new tutorial or on
  the Overview it links.
- **Keep the names the Overview uses**, so a reader moving between the two sees one scenario.
