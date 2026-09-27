# Hypershell in the Projects section

The public section for Hypershell, the type-level DSL whose programs are Rust types interpreted at
compile time through CGP wiring: thirteen example programs, the design that makes a program a type,
the guides for writing and extending the language, one reference page per construct, and a candid
account of what the proof of concept does not do. The project with measured search demand behind it.

- **Planned URL** — `https://contextgeneric.dev/docs/projects/hypershell/`
- **Ports** — [projects/hypershell/](../../projects/hypershell/README.md)
- **Repository** — [`hypershell`](https://github.com/contextgeneric/hypershell), documented on its
  `v0.8.0` branch, which is the only branch built on `HypershellNamespace`
- **Status** — planned; no page written. The reference and the extension pages wait on DC1

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

A provider that the internal reference records as routed nowhere, or a syntax the namespace does not
route, keeps its page and says so under *Known limitations*, since a reader who finds the name needs
to know it cannot be used as it stands.

### The comparison and the limitations

- **`shell-scripts.md`** — Hypershell against writing the same pipeline as a shell script, and
  against the typed-DSL designs it resembles, tagless final and Servant. It answers the *shell
  scripting vs rust* queries and carries the trade-offs the announcement post's disadvantages
  section made. **It has no internal document yet**; see [Knowledge-base
  prerequisites](#knowledge-base-prerequisites).
- **`limitations.md`** — from [issues.md](../../projects/hypershell/issues.md): the streamed body
  that does not follow redirects, the unusable `StreamToLines`, the syntax a namespace-joining
  context cannot reinterpret, the macro's edges, and the evidence gaps a user would want to know:
  few tests, no wiring checks, and the nightly toolchain. The learning curve falls on the people
  extending the language rather than the people using it; say so here in the project voice.

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
comparison keep the costs** the announcement post was candid about: compile times the project has
not measured are stated as unmeasured rather than dropped, and the diagnostics are shown as they
are.
