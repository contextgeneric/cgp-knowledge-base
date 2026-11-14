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
  `v0.8.0` branch, the only branch built on `HypershellNamespace`
- **Verified against** — `hypershell` `v0.8.0` at commit `f55415a`, and `cargo-cgp` built from its
  source at commit `b6a6323`
- **Status** — Draft: 21 Hypershell pages and the section index written, listed in [What is
  written](#what-is-written); the reference, the comparison, and the pages that quote providers wait
  on its [code prerequisites](#code-prerequisites) or a knowledge-base document
- **How it was made** — written by an agent from the project section; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What is written

Twenty-one Hypershell pages and the section index, all those nothing blocks. The site build passes
with them.

- **Section and project** — `docs/projects/index.md`, the section index, which the cgp-serde and
  cgp-examples entries and rows have since joined, and `hypershell/index.md`.
- **Examples** — the index and `hello`, `hello-name`, `http-checksum-cli`, `http-checksum-client`,
  `http-checksum-native`, `nix-manual`, `save-webpage`, `github-issues`, `rust-playground`,
  `bluesky`, and `bluesky-websocket`.
- **Architecture** — the index, `abstract-syntax`, `assembly`, `streams-and-input-dispatch`, and
  `crate-layout`.
- **Guides** — `writing-a-program` and `debugging`, under a generated category index.
- **Limitations** — `limitations.md`.

A revision must respect these facts:

- **Runs and diagnostics were reproduced where they could be.** `hello` and `hello_name` were built and
  run offline and printed what the records say. Every diagnostic the pages quote, and every fix they
  recommend, was re-run in a probe crate against the local checkout. The network examples were not
  re-run, so their pages describe what they print from the records without quoting uncaptured output;
  `rust-playground` says it was not run, since running it publishes a public gist.
- **The diagnostics come from `cargo-cgp` built from source**, which is the v0.1.0 release the site
  documents, per the base's [rule on versions](../../AGENTS.md#document-official-versions-never-pre-releases);
  re-check them against the tagged release.
- **The *Try a change* results** are recorded in the example records for `hello_name`,
  `http_checksum_native`, and `bluesky_websocket`.
- **Source links point at `main`**, so until the `v0.8.0` branch merges they show the older
  preset-based code.
- **The pages publish when the website's `v0.8.0` branch merges**, which depends on Hypershell's own
  `v0.8.0` branch merging by then; moving them off the release branch instead is the author's
  decision.
- **The install instructions assume that merge too**: the index tells a reader to clone the
  repository, or to depend on it by git with its toolchain files copied, rather than naming a
  crates.io version.

## What it covers

Hypershell shows that CGP's wiring is a general mechanism rather than a dependency-injection device: a
pipeline such as `curl | sha256sum | cut` is a Rust type, each piece of syntax is an empty struct, and
the context that runs the program is its interpreter. Its examples are the site's best material on
type-level DSLs, namespaces that assemble a library, dispatch on a handler's input, and extending a
language without touching its crates.

The section serves the type-system reader and the evaluator most. It also answers the one query
cluster in
[seo.md](../seo.md#adding-a-page-is-almost-never-the-answer-and-the-data-says-which-three-cases-to-consider)
with a page planned: the index is written to be the page *rust dsl* lands on, and the comparison with
shell scripts for the *shell scripting vs rust* queries.

**The index says on its first screen that Hypershell is an experimental proof of concept, not a shell
replacement**, as the project says of itself, and that it builds on nightly Rust with the new trait
solver. It shows the one-line context, `namespace HypershellNamespace;` inside the wiring of
`HypershellCli`, near the top, as the section's strongest single demonstration. Every context in the
project is environmental; the interpreting component is parameter-targeted, with the program as a
`Code` selector and the stage's input as the target, and the example pages say so where the first
input dispatch appears.

## The pages still to write

The finished section is close to a hundred pages, most of them reference: about 13 examples, 7
architecture pages, 3 guides, roughly 75 reference pages, a comparison, and the limitations page.

### Examples, architecture, and guides

**These quote providers in the explicit form, so they wait on the code prerequisites:**

- `examples/parallel-compare` — two sub-pipelines run concurrently and compared. The pattern: control
  syntax whose provider calls back into the context to run its operands.
- `examples/compare-and-branch` — a comparison driving `If`. It has no confirmed run, so its record
  needs one first.
- `architecture/interpretation`, which quotes a provider in full, and `architecture/error-handling`.
- `guides/extending-the-language`.

The examples library's `Compare` and `If`, its two extension namespaces, and the checksum bundle they
route are explained on the example pages that use them, not in the reference, since they live in the
unpublished examples crate.

### Reference

One page per construct, split from the nine family documents in
[reference/](../../projects/hypershell/reference/README.md) and grouped by kind. A syntax type and its
interpreting provider share the syntax type's page; the method markers are documented on the
`CanExtractMethodArg` page; each error or detail type is documented on the page of the syntax that
raises it; and the reference index's lookup table routes every folded name. Enumerate against the
source when porting. The groups and their approximate sizes:

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
  `BoxHandler`, `ReturnInput`, the layered extractors, `StreamToBody`, the two input dispatchers, and
  the adapters that interpret no syntax of their own.
- **`reference/namespace/`, 9 pages** — `HypershellNamespace` with its full route table,
  `HypershellErrorHandler`, the contexts `HypershellCli` and `HypershellHttp`, and the five backend
  bundles.
- **`reference/types/`, 6 pages** — the three stream wrappers, `ChildOutputStream`, and the list maps
  `WrapCall` and `WrapStaticArg`.
- **`reference/hypershell_macro.md`** — the `hypershell!` macro's rewriting rules and its edges, with
  the desugared type as its *Under the hood*.

The prelude is a re-export module, not a construct, so the index documents what it brings into scope
and the lookup table routes each re-exported name. A provider or syntax that `HypershellNamespace`
leaves out keeps its page, whose *Usage* says a context must wire it to use it; why it is left out,
and whether it works, stay in the project's `issues.md`.

### The comparison

`shell-scripts.md` sets Hypershell against the same pipeline written as a shell script, and against
the typed-DSL designs it resembles, tagless final and Servant, carrying the trade-offs the
announcement post's disadvantages section made. It has no internal document yet; see
[Knowledge-base prerequisites](#knowledge-base-prerequisites).

## Prerequisites

### Code prerequisites

**These changes must land before the pages that quote providers**: the reference,
`architecture/interpretation`, `guides/extending-the-language`, and the examples that show a provider.
Each is recorded in the project's [housekeeping](../../projects/hypershell/issues.md#housekeeping):

- **Adopt `#[uses(...)]`** for the hand-written `where` bounds that almost every provider carries.
- **Decide whether `HasReqwestClient` becomes an `#[implicit]` argument**, the only field read that
  could.
- **Replace the one live `UseDelegate` table** in `providers/pipe.rs` with the `open` statement; a
  probe confirmed that `open` accepts its bounded generic key.
- **Drop the six `#[derive_delegate(UseDelegate<…>)]` attributes** on the extractor and updater
  components, accepting the breakage for a downstream user who still builds `UseDelegate` tables.
- **Worth doing, not blocking**: name `ExtractArgs` in its own tail bound, as the other list providers
  do, so its page can describe direct recursion; and remove the `ReturnInput` that duplicates CGP's,
  so the reference does not document two constructs with one name.

### Knowledge-base prerequisites

- **A comparison document**, `projects/hypershell/shell-script-comparison.md`, named for what it
  compares against per [projects/AGENTS.md](../../projects/AGENTS.md#the-shape-of-a-project-section):
  what a shell script does that Hypershell does not, what the type-level form adds, where the shell is
  the better choice, and the relationship to tagless final and Servant. Its sources are the
  announcement post's trade-offs and related-work sections, re-verified against the current code.
- **A confirmed run of `compare_and_branch`**, recorded in its example document.

### Release conditions

**A Hypershell release built on `cgp` 0.8.0.** The crates on crates.io are 0.1.0 against `cgp` 0.4.1
and assemble the language from presets, so until a release exists the index gives a git dependency on
the default branch and says why. The `v0.8.0` branch must also be the default before source links
point at it.

## The source post

[Hypershell: a type-level DSL for shell-scripting](../blog/hypershell-release.md) carries a notice at
its top linking the section, and every Hypershell example page links the post back, at its section for
that program where it has one. The post otherwise stays as it is, including its CGP primer and
preset-based code; its record lists what has drifted.

## Maintaining it

- **The one-line context stays near the top of the index**, rather than moving into the assembly page
  as the section grows.
- **The limitations page and the comparison keep the costs** the announcement post was candid about:
  the toolchain, the compile-time work, and the long diagnostics, stated as the design's limits.
