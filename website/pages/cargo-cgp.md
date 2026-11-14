# cargo-cgp

The `cargo-cgp` section is the tool's own documentation: nine pages on installing it, running it,
reading its output, and fixing what it reports.

- **URL:** <https://contextgeneric.dev/docs/cargo-cgp/>
- **Source:** [docs/cargo-cgp/](https://github.com/contextgeneric/contextgeneric.dev/tree/main/docs/cargo-cgp)
- **Status:** Current, written against `cargo-cgp` v0.1.0 ahead of its release (task V2), in
  natural-writing style
- **How it was made:** written by an agent from [cargo-cgp/reference/](../../cargo-cgp/reference/README.md)
  and [cargo-cgp/error-code.md](../../cargo-cgp/error-code.md), with every quoted output produced by
  running the tool built from `cargo-cgp`'s `main`; level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md)

## What it covers

The section is a top-level category beside the reference rather than inside it, because a reference
page answers "what does this construct mean" and these answer "how do I run this".
[writing-guides/tooling.md](../writing-guides/tooling.md) specifies its nine pages, in the order a
reader needs them:

- **Overview** (`index.md`, the category's link target): what the tool is and that it is optional,
  the before/after, how it works in two paragraphs, what it costs, and what it does not do. The
  before/after is the **hidden-cause case**: an unchecked call to `area` on a `Rectangle` missing
  `height`, where stable `cargo check` prints an `E0599` that never names `height` and suggests
  `Rectangle::area()`, against the tool's `[CGP-E001]` naming the field. It was chosen over the
  checked case because the raw output leaves the cause out rather than burying it.
- **Installation:** the decision table, including the reader with neither rustup nor Nix; the cargo
  and Nix paths pinned to `v0.1.0`; checking the install, with the library path the driver's
  `--version` needs when run by hand on the cargo path; the Linux-only platform and the CGP v0.8
  target; updating; CI; uninstalling, including `target/cgp`; building from source; and a note on the
  agent skill.
- **Check:** running it from the root; a pasteable `area-demo` package with the deliberate mistake;
  the same mistake pinned to the wiring by `check_components!`, with the raw `help` line it replaces;
  the three settings a check changes; where `target/cgp` goes; forwarded flags; a short editor
  section; and its boundary.
- **Reading the output:** the parts of a rewritten error, then one real example per shape (two causes
  in one error, a component nothing is wired for, a field of the wrong type, an ordinary Rust trait
  that does not hold, a two-caret conflict, a fix in a `help` line), and a selection of the errors
  that pass through unchanged. The ordinary-trait shape keeps the compiler's headline at a check, so
  the page's test for a passed-through error is "no `[CGP-Exxx]` code anywhere"; reached through a
  method call, the same mistake gets a CGP headline.
- **Expand:** when to use it first, the fixed `Rectangle` and its real `--item Rectangle` listing,
  `--item`, choosing a target, the `cargo-expand` comparison quoting the compiler's own expansion, and
  what to expect from the output.
- **Editor integration:** VS Code with the rust-analyzer extension only. The setting in the workspace
  `.vscode/settings.json`, and why not user settings and when not to commit it; each part of the
  command; why `check.overrideCommand` rather than `check.command`; what the editor shows for the
  check page's call-site `Rectangle` program; what the switch changes (a slow first save,
  rust-analyzer's own check options dropped, as-you-type errors not rewritten, the pinned nightly
  disagreeing with the reader's toolchain); turning it off; when it does not work (the
  `cargo check failed to start` warning carrying the tool's message, the same command in a terminal,
  VS Code's `PATH`); and its boundary. It links rust-analyzer's configuration manual and VS Code's
  settings documentation.
- **Troubleshooting:** the symptom index, then sections ordered by how often a reader meets them,
  including the check disagreeing with `cargo check`, a slow first check, and an overridden
  `RUSTC_WORKSPACE_WRAPPER`.
- **Error codes:** one heading per code, so `#cgp-e001` resolves, each with the message form, the
  mistake, the fix, and the compile-errors section that explains the class; then the rewrites with no
  code. The compile-errors page keeps a short section pointing here.
- **Command reference:** the four commands, their options, the variables the tool reads and sets for
  cargo, the files it creates, the exit status, and the driver's two queries.

## How it relates to the knowledge base

[cargo-cgp/reference/](../../cargo-cgp/reference/README.md) stays the source of truth:
[installation.md](../../cargo-cgp/reference/installation.md) behind installation,
[usage.md](../../cargo-cgp/reference/usage.md) behind check, expand, and the command reference,
[troubleshooting.md](../../cargo-cgp/reference/troubleshooting.md) behind troubleshooting, and
[error-code.md](../../cargo-cgp/error-code.md) behind the error codes. The list of errors that pass
through comes from [cargo-cgp/issues/usability.md](../../cargo-cgp/issues/usability.md). The pages
drop what those documents carry for an agent, such as pointers into the implementation and
driver-level debugging, and add a reader choosing an install path.

The programs come from the [area-calculation](../../examples/area-calculation.md) scenario, a value
context with a self-targeted component. The reading page also uses a fieldless `App`, an
environmental context with self-targeted components (a greeter, a farewell, and a scalar comparison
over an abstract type), and two `#[cgp_fn]` functions, and marks the switch from `Rectangle` to
`App`. Every program is in the [`example-code` crate](../site.md#the-example-code-crate): the
deliberate mistakes as fixtures under `tests/compile_fail/cargo_cgp/`, one per heading, and the two
programs the pages say compile under `tests/cargo_cgp/`.

## What a later revision must know

- **The quoted output comes from `cargo-cgp`'s `main`, the v0.1.0 release the pages document,**
  captured with the source-built tool on Linux against the sibling `cgp` checkout on the release
  branch; output naming the version is quoted as `0.1.0`, per the base's
  [rule on versions](../../AGENTS.md#document-official-versions-never-pre-releases). Task V2 in
  [tasks.md](../tasks.md) re-runs every quoted command against the tagged release.
- **Four front-end behaviors are the pages' newest facts:** `cargo cgp --version` (quoted as
  `cargo-cgp 0.1.0`), `cargo cgp update` installing only official releases, `setup` and `update`
  answering `--help` and refusing other arguments, and `target/cgp` sitting in the project's own
  target directory wherever the command runs.
- **The editor page was verified against the rust-analyzer server, not the VS Code window.** An LSP
  client started rust-analyzer with the override as its initialization options, opened and saved the
  check page's program, and printed what the server published and every `window/showMessage`. Every
  quoted editor output comes from it: the rewritten error, the `cargo check failed to start` warning
  (provoked with an unknown `CARGO_CGP_TOOLCHAIN`, then quoted with the pinned nightly's name), and
  cargo's `no such command` naming `cgp` with the tool off `PATH`. A bogus `check.extraArgs` and
  `check.features` beside the override still checked cleanly, while the same `extraArgs` without it
  broke the check, which is the evidence that the override drops those options. The settings and
  command-palette names come from VS Code's and rust-analyzer's documentation, and the restart
  command's name from the extension's `package.json`. How VS Code renders the error in its window is
  unverified.
- **The `example-code` crate patches `cgp` to the sibling checkout,** and its `.stderr` snapshots are
  blessed against it; task V1 removes the patch.
- **The pinned nightly's date appears only where real output contains it.** Commands use
  `nightly-YYYY-MM-DD` and say where to read the real one, so a toolchain bump changes quoted output
  but no instructions.
- **An undeclared trait called inside a `#[cgp_impl]` body is reshaped into `[CGP-E030]`,** like the
  same mistake in a `#[cgp_fn]` body; the reading and error-codes pages say both are covered.

## Maintaining it

- Write and revise every page in natural-writing style, as the
  [tooling guide](../writing-guides/tooling.md#writing-style) requires, keeping tables, lists, and code
  blocks for sets and copied text. Preserve the captured outputs, runnable snippets, command syntax,
  and the error-code entries' anchors and message forms. The pages' prose follows these shapes, which
  a revision keeps:
  - The installation and editor pages separate prerequisites from instructions, and keep
    requirements, command behavior, and limitations in separate paragraphs.
  - The check and expansion pages connect each output to the requirement it exposes.
  - The reading and troubleshooting pages connect each symptom to its cause and remedy;
    troubleshooting runs from toolchain availability through driver loading to version checks.
  - Error-code entries explain why a requirement fails before giving the remedy, and data-state
    entries relate an operation's requirement to the builder or extractor in use.
  - Repeated toolchain and build-authority explanations stay brief.
- **Re-run the commands rather than editing their output.** Every quoted diagnostic and listing came
  from the tool on the program the page shows, and a paraphrase reads as a version mismatch; the
  guide's draft checks are the procedure.
- When the tool's diagnostics change, the internal reference, these pages, and the
  [error catalog](../../cgp/errors/README.md) move together, per the
  [synchronization rule](../../AGENTS.md#the-synchronization-rule). A new code gets a heading on the
  error-codes page in the same change.
