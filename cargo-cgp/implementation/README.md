# cargo-cgp Implementation Reference

This directory documents the *internals* of `cargo-cgp`: how the tool is built, not how it is used.
It is the documentation an agent reviewing, debugging, or extending the source reads first. It
records the current state of the code in one place, so an agent can pick up a subsystem from where
the last one left off rather than reconstructing it from the crates each time. The authoring rules,
the document shape, and the synchronization rule that binds these documents to the code live in
[AGENTS.md](AGENTS.md), on top of the knowledge-base-wide rules in [../AGENTS.md](../AGENTS.md).

Each document explains how one subsystem *works* and *why it is built that way*. That includes where
it depends on the compiler's unstable `rustc_driver` behavior, and how the design compares to a
related tool that has already solved the same problem. That comparison is not decoration: Clippy is
the closest working example of this compiler integration, and `cargo-expand` of printing an expanded
crate, so knowing where `cargo-cgp` agrees with one of them and where it diverges is often the
fastest way to understand why a piece of code is shaped the way it is. A subsystem with no such
counterpart carries no comparison at all.

## Catalog

This section indexes every implementation document, or the directory that holds a family of them, whose
own `README.md` lists its documents. When you add a document, register it in the same change.

- [Architecture](architecture.md): the map of the tool: the crates and where the rustc-free line
  sits, the flow of a diagnostic (configure, transform, render), the driver's module layers, and the
  `ResolveCtx` that carries the compiler handle and the cache.
- [Executable structure](executable-structure.md): the two-executable split (the `cargo-cgp`
  front-end and the `cargo-cgp-driver` rustc wrapper), how the front-end wraps `cargo`, the
  environment contract between the two, and how the split compares to Clippy.
- [The driver](driver/README.md): `cargo-cgp-driver` as a program, how it runs the compiler, and what
  the emitter's stages do to each class of CGP mistake.
- [Typed root-cause resolution](typed-resolution/README.md): the emitter transformation that replaces a
  wiring failure with one coded headline over its dependency chain, by asking the trait solver what
  failed: the overview and boundaries, then one document per stage.
- [Cached dependency resolution](cached-dependency-resolution.md): the one cache over the typed
  resolver's walk. It is keyed at *every* node and consulted at every step, and it stores each
  node's owned rustc-free sub-chains, so they persist across diagnostics and close both the
  whole-crate re-report redundancy and the intra-walk diamond. The document covers the soundness
  reasoning: why a node key is not a complete key (the cycle guard makes the walk a function of the
  ancestor set), the incomplete-subtree flag that keeps a guard-truncated subtree out of the cache,
  the reachable-set disjointness check that keeps a reuse from forming a cycle, and the key hashed
  and compared by a `StableHash` fingerprint of the obligation and its root context. It also explains why cacheability is a statelessness
  proof, not just a speedup.
- [Dependency-graph rendering](dependency-graph-rendering.md): how the `root cause:` note's tree is
  built as one rustc-free **dependency graph**. The resolver emits structured, per-`CGP-E1xx`-code
  nodes as flat root→leaf paths, and error-processing merges them by structural identity (cross-path
  only) into a DAG and renders it `cargo tree`-style with `(*)`-marked shared subtrees. The document
  covers the structured node enum, the root rule (a path head that is also a descendant is not a
  top-level root, giving subsumption for free), the shared-subtree and converging-leaf rendering,
  and worked shapes for a diamond and distinct-key redirects. All merging and rendering happens in
  pure, unit-testable functions.
- [Error processing](error-processing.md): the rustc-free `cargo-cgp-error-processing` crate that
  holds the driver's string-level diagnostic logic: the post-processing text transforms (stripping
  module paths, resugaring `Symbol!` and `Path!`, resugaring `Product!`/`Sum!` lists to their
  `Struct!`/`Enum!` forms, rewriting unmet `HasField` bounds into missing-field messages), the
  wiring-message rewrite, the root-cause diagnosis model and the wording that turns it into the
  header, help, and note text, and the dependency-tree renderer. The driver's emitter drives all of
  it, and all of it is unit-tested without a compiler.
- [Resugaring](resugaring.md): the transforms that reverse CGP's type-level expansions, so every
  construct the tool shows is spelled the way the programmer wrote it: `Symbol!`, `Path!`, the
  `Product!`/`Sum!` lists and their `Struct!`/`Enum!` shapes, and the path strips that must
  run first. It has one section per construct with its expansion and its decline cases, and states
  the exact-match rule that keeps a resugaring from claiming syntax nobody wrote. One sub-section
  per implementation (typed over `Ty<'tcx>`, text over `&str`, syntax tree over `syn::Type`)
  explains why three inputs force three separate matchers that must nonetheless agree, and why
  every form they show is real syntax.
- [The expand command](expand-command.md): `cargo cgp expand`, which shows the ordinary Rust a
  project's CGP macros generate: a full `cargo-expand`-style expansion whose CGP type-level sugar
  the driver resugars before returning it. Covers why the compiler offers no way to expand only some
  macros, the `cargo rustc` launch and the marker flag that scopes expand mode to one crate, why the
  driver prints the expanded AST from `after_expansion` instead of setting `-Zunpretty=expanded`
  (which bypasses every callback), what running it settled about cargo's handling of a unit that
  yields no artifact, and the limitation that every macro is expanded.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): a map of the compiler code that
  builds CGP diagnostics and where it *suppresses* information: the type/const printer, the
  trait-error reporters, the two verbosity switches (`--verbose` versus `-Zverbose-internals`), and
  the specific elision points the driver's `--verbose` injection defeats. It also catalogs the
  **panic hazards** of re-running compiler code inside the emitter (re-entering the `DiagCtxt` lock,
  relating an un-instantiated binder, leaking inference variables across contexts, freezing the
  crate store during name resolution) and how the driver avoids each. Read it when a diagnostic is
  dropping a cause the tool needs, or before adding a compiler interaction that could crash the
  driver.
- [Testing](testing.md): how the tool is tested: the unit tests, one test target per crate, and the
  UI snapshot suite. The suite is a custom Rust test harness (like Clippy's `compile-test`) that
  compiles fixtures under `tests/ui/` through the tool and diffs committed `.cgp.stderr`,
  `.rust.stderr`, and `.expand.rs` snapshots. The document also covers the bless workflow and how
  the harness compares to Clippy's.
- [Distribution](distribution/README.md): how the tool reaches a machine that has only stable Rust and
  stays in step with its pinned nightly: provisioning through cargo and rustup, the Nix package, the
  nightly bump, and Rust Analyzer integration.
