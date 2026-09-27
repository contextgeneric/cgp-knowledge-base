# Hypershell in the Projects section

The public section for Hypershell, the type-level DSL whose programs are Rust types interpreted at
compile time through CGP wiring: thirteen example programs, the design that makes a program a type,
the guides for writing and extending the language, one reference page per construct, and a candid
account of what the proof of concept does not do. The project with measured search demand behind it.

- **URL** — <https://contextgeneric.dev/docs/projects/hypershell/>
- **Source** —
  [docs/projects/hypershell/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/projects/hypershell),
  written on the website's `v0.8.0` branch and not yet published
- **Ports** — [projects/hypershell/](../../projects/hypershell/README.md)
- **Repository** — [`hypershell`](https://github.com/contextgeneric/hypershell), documented on its
  `v0.8.0` branch, which is the only branch built on `HypershellNamespace`
- **Verified against** — `hypershell` `v0.8.0` at commit `7f7e943`, and `cargo-cgp` built from its
  source at commit `b6a6323`
- **Status** — Draft: 21 Hypershell pages and the section index written, listed in [What is
  written](#what-is-written); the reference, the comparison, and the pages that quote providers wait
  on DC1 or a knowledge-base document
- **How it was made** — written by an agent from the project section; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What is written

**Twenty-one Hypershell pages and the section index are written**, all the pages that nothing
blocks. `yarn build` passes with them, so every link they carry resolves. They are:

- **Section and project** — `docs/projects/index.md`, the section index, with Hypershell as its only
  project and a pattern-finding table of Hypershell rows; and `hypershell/index.md`.
- **Examples** — the index and eleven pages: `hello`, `hello-name`, `http-checksum-cli`,
  `http-checksum-client`, `http-checksum-native`, `nix-manual`, `save-webpage`, `github-issues`,
  `rust-playground`, `bluesky`, and `bluesky-websocket`.
- **Architecture** — the index, `abstract-syntax`, `assembly`, `streams-and-input-dispatch`, and
  `crate-layout`.
- **Guides** — `writing-a-program` and `debugging`, under a generated category index.
- **Limitations** — `limitations.md`.

**The pages not yet written** are the ones this plan says must wait, and none is scaffolded as a
stub. Pages that would link them instead describe the idea in place, or say the page is still being
written, so no link points at a placeholder:

- `examples/parallel-compare` and `examples/compare-and-branch`, `architecture/interpretation`,
  `architecture/error-handling`, and `guides/extending-the-language` quote providers in the explicit
  form, and wait on DC1. `compare-and-branch` also needs a confirmed run.
- The whole `reference/` group waits on DC1. The example pages name each Hypershell construct and
  link the architecture page that explains it, and gain links to construct pages when those exist.
- `shell-scripts.md` waits on its knowledge-base document.

The writing turned up several facts a later revision must respect:

- **Every run and diagnostic was re-produced.** `hello` and `hello_name` were built and run offline
  and printed what the records say. Every diagnostic the pages quote, and every fix they recommend,
  was re-run in a probe crate against the local checkout, with `cargo-cgp` built from source. The
  network examples were not re-run; their pages describe what they print, from the records, without
  quoting output that was not captured.
- **The diagnostics come from the unreleased `cargo-cgp`.** The published v0.1.0-alpha reports the
  missing dispatcher entry as `[CGP-E107]` where the source reports `[CGP-E110]`, and the site's
  [compile errors page](https://contextgeneric.dev/docs/reference/errors) already documents
  `[CGP-E110]`, so the pages follow the source. Re-check them when `cargo-cgp` next releases.
- **Source links point at `main`**, per the writing guide, so until the `v0.8.0` branch merges they
  show the older preset-based code.
- **The pages are on the website's release branch**, so they publish when that branch merges, with
  v0.8.0, unless they are moved off it first. The section was planned as post-release work;
  publishing it with the release instead is a decision for the author, and it depends on
  Hypershell's own `v0.8.0` branch merging by then.
- **The install instructions assume the merge too.** The index tells a reader to clone the
  repository, and to depend on it by git with its toolchain files copied, rather than naming a
  crates.io version.
- **Two knowledge-base corrections came out of it**: the namespace's route table listed only two of
  the four method markers, and the writing guide's advice about `Vec::<u8>::new()` overstated its
  effect. Both are fixed in the project section.
- **The architecture pages are written for an outside reader, not ported line for line.** Each opens
  with a question such a reader would ask, introduces bundles, namespaces, and input dispatchers one
  at a time, and leaves out the registration paths, the lookup internals, and the `[CGP-E104]` walk
  the internal documents carry. Their cost sections state trade-offs; the project's open issues stay
  on the limitations page. A revision should keep them that way, per the [writing
  guide](../writing-guides/project.md#architecture-pages).
- **No public page lists Hypershell's bugs or missing features.** The limitations page states only
  the high-level limits of the design, and the example pages carry no known-issues sections; the
  redirect, `StreamToLines`, WebSocket, and macro defects stay in the project's
  [issues](../../projects/hypershell/issues.md), per the [writing
  guide](../writing-guides/project.md#the-limitations-page).
- **Every example page has a *The problem* section before its code**, per [the writing
  guide](../writing-guides/project.md#then-it-states-the-problem): the task, what makes it hard, and
  a *Without CGP* part that concedes where a shell script, plain Rust, or Serde's derive is simpler
  and names the requirement that tips the balance. A revision keeps it fair to the alternative.
- **The `Try a change` results** are recorded in the example records for `hello_name`,
  `http_checksum_native`, and `bluesky_websocket` before the pages quote them.

## What it covers

Hypershell shows that CGP's wiring is a general mechanism rather than a dependency-injection device:
a pipeline such as `curl | sha256sum | cut` is written as a Rust type, each piece of syntax is an
empty struct, and the context that runs the program is its interpreter. Its examples are the site's
best material on **type-level DSLs**, **namespaces that assemble a library**, **dispatch on a
handler's input**, and **extending a language without touching its crates**, which is why it is the
second project in the [recommended order](README.md#ordering) and the first library.

The section serves the type-system reader and the evaluator most. It also answers the one query
cluster in
[seo.md](../seo.md#adding-a-page-is-almost-never-the-answer-and-the-data-says-which-three-cases-to-consider)
that has a page planned: *rust dsl*, which the announcement post wins today, and the *shell
scripting vs rust* comparisons it serves badly. The index is written to be the page that query lands
on, and the comparison with shell scripts is written for the second.

**The index must say on its first screen that Hypershell is an experimental proof of concept, not a
shell replacement**, as the project says of itself, and that it builds on nightly Rust with the new
trait solver. Every context in the project is environmental: `HypershellCli` is a type that stands
for one set of language choices. The interpreting component is parameter-targeted, with the program
as a `Code` selector and the stage's input as the target, and the example pages say so where the
first input dispatch appears.

## The pages

About 13 example pages, 7 architecture pages, 3 guides, roughly 75 reference pages, a comparison,
and the limitations page: close to a hundred in all, most of them reference.

### Index

From the [project README](../../projects/hypershell/README.md): the `hello` program and what it
prints, the one-line context

```rust
delegate_components! {
    HypershellCli {
        namespace HypershellNamespace;
    }
}
```

shown early because it is the section's strongest single demonstration, the proof-of-concept status,
the toolchain, and the route into the examples. Personal history, such as the project's name, stays
on the blog and is linked.

### Examples

One page per program in [examples/](../../projects/hypershell/examples/README.md), in its teaching
order, with `examples/index.md` from that README. The examples library's `Compare` and `If`, its two
extension namespaces, and the checksum bundle they route are explained on the example pages that use
them rather than in the reference, since they live in the unpublished examples crate rather than in
a library a reader depends on.

- `hello` — `echo hello world!` on the empty `HypershellCli`. The pattern: a program is a type, and
  a context joins the whole language in one line.
- `hello-name` — a runtime argument read from a custom context's field with `FieldArg`. The pattern:
  a context supplies the values a type-level program needs.
- `http-checksum-cli` — `curl | sha256sum | cut` as three streaming stages. The pattern: stage types
  line up through the next stage's input dispatch.
- `http-checksum-client` — the same with a native streaming request. The pattern: dispatch on the
  handler's input converts between stream kinds without the program saying so.
- `http-checksum-native` — the same with the checksum extension, joined by changing the namespace.
  The pattern: extending a language through an inheriting namespace.
- `nix-manual` — a native request feeding `tr` and `grep`, with a mixed argument list.
- `save-webpage` — a streaming request written to a file.
- `github-issues` — a URL joined and encoded from fields, a header, and JSON decoded into a Rust
  type.
- `rust-playground` — JSON in both directions on `HypershellHttp`. The page must say it was not run,
  since running it publishes a public gist, unless a run is recorded first.
- `bluesky` — an endless stream from a command provisioned by `nix-shell`.
- `bluesky-websocket` — the same with the WebSocket extension wired on the context. The pattern:
  extending through context entries rather than a namespace, and the trade between the two.
- `parallel-compare` — two sub-pipelines run concurrently and compared. The pattern: control syntax
  whose provider calls back into the context to run its operands.
- `compare-and-branch` — a comparison driving `If`. **It has no confirmed run**, so its record needs
  one before the page is written.

### Architecture

One page per document in [architecture/](../../projects/hypershell/architecture/README.md), with the
one-page design as the index: `abstract-syntax`, `interpretation`, `assembly`,
`streams-and-input-dispatch`, `error-handling`, and `crate-layout`. `interpretation` quotes a
provider in full and waits on DC1.

### Guides

`writing-a-program`, `extending-the-language`, and `debugging`, from
[guides/](../../projects/hypershell/guides/README.md). `extending-the-language` quotes providers and
waits on DC1. `debugging` quotes `cargo cgp check` output and carries the canonical qualification.

### Reference

One page per construct, split from the nine family documents in
[reference/](../../projects/hypershell/reference/README.md) and grouped by kind. A syntax type and
the provider that interprets it share the syntax type's page, as the internal reference already
pairs them; the method markers are documented on the `CanExtractMethodArg` page; and each error or
detail type is documented on the page of the syntax that raises it. The reference index carries the
lookup table for every folded name. Enumerate against the source when porting; the groups and their
approximate sizes are:

- **`reference/syntax/`, about 33 pages** — the execution syntax (`SimpleExec`, `StreamingExec`,
  `CoreExec`, `WithArgs`, `WithStaticArgs`, `FieldArgs`), the argument syntax (`StaticArg`,
  `FieldArg`, `JoinArgs`, `UrlEncodeArg`), the HTTP syntax (`SimpleHttpRequest`,
  `StreamingHttpRequest`, `CoreHttpRequest`, `WithHeaders`, `Header`), the conversions
  (`StreamToBytes`, `StreamToString`, `StreamToStdout`, `BytesToStream`, `BytesToString`,
  `StreamToLines`, `ToTokioAsyncRead`), files (`ReadFile`, `WriteFile`), JSON (`EncodeJson`,
  `DecodeJson`), control (`Pipe`, `Use`, `ConvertTo`, and `Box` as syntax), and the extensions
  (`Checksum`, `BytesToHex`, `WebSocket`).
- **`reference/components/`, 10 pages** — the string, command, URL, and method extractors, the
  command, URL, and HTTP-method type components, the command and request-builder updaters, and
  `HasReqwestClient`.
- **`reference/providers/`, about 16 pages** — the providers a wiring names directly: `Call`,
  `BoxHandler`, `ReturnInput`, the layered extractors, `StreamToBody`, the two input dispatchers,
  and the adapters that interpret no syntax of their own.
- **`reference/namespace/`, 9 pages** — `HypershellNamespace` with its full route table,
  `HypershellErrorHandler`, the contexts `HypershellCli` and `HypershellHttp`, and the five backend
  bundles.
- **`reference/types/`, 6 pages** — the three stream wrappers, `ChildOutputStream`, and the list
  maps `WrapCall` and `WrapStaticArg`.
- **`reference/hypershell_macro.md`** — the `hypershell!` macro's rewriting rules and its edges,
  with the desugared type as its *Under the hood*.

The prelude is a re-export module rather than a construct, so the index documents what it brings
into scope, and the reference index's lookup table routes each re-exported name to its page.

A provider or syntax that `HypershellNamespace` does not include keeps its page, and its *Usage*
section says plainly that a context must wire it to use it. That is a fact about using the item, not
a defect report; why it is left out, and whether it works, are recorded in the project's `issues.md`
and stay there.

### The comparison and the limitations

- **`shell-scripts.md`** — Hypershell against writing the same pipeline as a shell script, and
  against the typed-DSL designs it resembles, tagless final and Servant. It answers the *shell
  scripting vs rust* queries and carries the trade-offs the announcement post's disadvantages
  section made. **It has no internal document yet**; see [Knowledge-base
  prerequisites](#knowledge-base-prerequisites).
- **`limitations.md`** — the high-level limits of the design and status, written from the README and
  the architecture: a proof of concept that is lightly tested, programs fixed at compile time, typed
  stages stricter than a shell, extensions that add syntax but cannot replace the standard syntax's
  meaning, the nightly toolchain, and long compile errors. It names no bugs and no unimplemented
  features; those stay in [issues.md](../../projects/hypershell/issues.md).

## Prerequisites

### Code prerequisites

**DC1 in [tasks.md](../tasks.md) must land before the pages that quote providers**, which are the
reference, `architecture/interpretation`, `guides/extending-the-language`, and the examples that
show a provider. The work, recorded in the project's
[housekeeping](../../projects/hypershell/issues.md#housekeeping):

- **Adopt `#[uses(...)]`** for the hand-written `where` bounds, which almost every provider carries
  today.
- **Decide whether `HasReqwestClient` becomes an `#[implicit]` argument**, the only field read that
  could.
- **Replace the one live `UseDelegate` table** in `providers/pipe.rs` with the `open` statement; a
  probe confirmed that `open` accepts its bounded generic key.
- **Drop the six `#[derive_delegate(UseDelegate<…>)]` attributes** on the extractor and updater
  components. Removing them is breaking for a downstream user who still builds `UseDelegate` tables,
  and that breakage is accepted.
- **Worth doing, not blocking**: name `ExtractArgs` in its own tail bound, as the other list
  providers do, so its page can describe direct recursion; and remove the `ReturnInput` that
  duplicates CGP's, so the reference does not document two constructs with one name.

The examples that show only a program and a context, such as `hello` through `save-webpage`, do not
wait on DC1 and can be written first.

### Knowledge-base prerequisites

- **A comparison document**, `projects/hypershell/shell-script-comparison.md`, named for what it
  compares against per
  [projects/AGENTS.md](../../projects/AGENTS.md#the-shape-of-a-project-section): what a shell script
  does that Hypershell does not, what the type-level form adds, where the shell is the better
  choice, and the relationship to tagless final and Servant. Its sources are the announcement post's
  trade-offs and related-work sections, re-verified against the current code.
- **A confirmed run of `compare_and_branch`**, recorded in its example document.

### Release conditions

**A Hypershell release built on `cgp` 0.8.0.** The crates on crates.io are 0.1.0 against `cgp` 0.4.1
and assemble the language from presets, so an install snippet naming them would install code the
pages do not describe. Until a release exists, the index gives a git dependency on the default
branch and says why. The `v0.8.0` branch must also be the default before source links point at it.

## The source post

[Hypershell: a type-level DSL for shell-scripting](../blog/hypershell-release.md) gets a pointer to
the Hypershell index when the section publishes. The post stays as it is, including its embedded CGP
primer and its preset-based code; its record lists what has drifted.

## Maintaining it

Two properties are worth defending. **The one-line context stays on the index**, near the top,
rather than moving into the assembly page as the section grows. And **the limitations page and the
comparison keep the costs** the announcement post was candid about: the toolchain, the compile-time
work, and the long diagnostics, stated as the design's limits rather than as a list of defects.
