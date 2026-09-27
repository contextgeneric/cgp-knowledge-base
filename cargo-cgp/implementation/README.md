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

This section indexes every implementation document. When you add a document, register it here in the
same change.

- [Executable structure](executable-structure.md): the two-executable split (the `cargo-cgp`
  front-end and the `cargo-cgp-driver` rustc wrapper), how the front-end wraps `cargo`, the
  environment contract between the two, and how the split compares to Clippy.
- [The driver](driver.md): the deep dive into `cargo-cgp-driver`. It covers how cargo invokes the
  driver, how the driver prepares the rustc argument vector, and how it reaches the compiler through
  the `rustc_private` `rustc_driver` API. It also covers the transformations the driver applies to
  the diagnostics: the two flag levers (trait solver, verbosity), the generic `CgpEmitter` that
  renders text or JSON like vanilla `rustc`, the emitter that renames CGP wiring notes using the
  live compiler, and the post-processing fallback that keeps un-rewritten CGP constructs readable.
- [Typed root-cause resolution](typed-root-cause-resolution.md): the deeper emitter transformation
  that turns a check-failure diagnostic into its root-cause `cargo tree`. It recovers the chain by
  re-running the check obligation through the trait solver (from inside `emit_diagnostic`, since
  `after_analysis` is unreachable once the crate has errors), descends the wiring to each terminal
  leaf (a `HasField` field or an ordinary bound), and renders the transitive dependency chain with
  each wiring trait replaced by its human form. A main message identified as a CGP class is
  rewritten and stamped with its `[CGP-Exxx]` code (the Rust code kept). The sub-notes become a
  single `root cause:` note over the dependency graph of every leaf, and anything the resolver
  declines falls back to the text rewrite. The document is the pipeline overview, with its
  boundaries and its consolidated tests and source catalogs, over four per-stage documents:
  - [Typed resolution: anchoring the starting obligation](typed-resolution-anchors.md): the six
    span-matching anchors that recover the real consumer obligation from a check entry, a
    hand-written impl, a foreign wrapper chain, a use site, a namespace-joined consumer, or a
    blanket trait.
  - [Typed resolution: the call-site anchor](typed-resolution-call-site.md): the HIR re-read of the
    failing call expression, its signature unification, and the rigid placeholders that stand in for
    what the call never types.
  - [Typed resolution: walking to the root cause](typed-resolution-walk.md): the descent from the
    seeded obligation to every terminal unmet bound, and the decoding, classification, and label
    rendering of each leaf.
  - [Typed resolution: the transformed diagnostic](typed-resolution-output.md): the coded headline
    classes, the single `root cause:` note over every leaf's merged dependency graph, and the
    emitter's application of the rustc-free plan.
- [Cached dependency resolution](cached-dependency-resolution.md): the one cache over the typed
  resolver's walk. It is keyed at *every* node and consulted at every step, and it stores each
  node's owned rustc-free sub-chains, so they persist across diagnostics and close both the
  whole-crate re-report redundancy and the intra-walk diamond. The document covers the soundness
  reasoning: why a node key is not a complete key (the cycle guard makes the walk a function of the
  ancestor set), the incomplete-subtree flag that keeps a guard-truncated subtree out of the cache,
  the reachable-set disjointness check that keeps a reuse from forming a cycle, and the key hashed
  and compared by a `StableHash` fingerprint (of the obligation and its root context) with readable
  fields alongside for inspecting the store. It also explains why cacheability is a statelessness
  proof, not just a speedup.
- [Dependency-graph rendering](dependency-graph-rendering.md): how the `root cause:` note's tree is
  built as one rustc-free **dependency graph**. The resolver emits structured, per-`CGP-E1xx`-code
  nodes as flat root→leaf paths, and error-processing merges them by structural identity (cross-path
  only) into a DAG and renders it `cargo tree`-style with `(*)`-marked shared subtrees. The document
  covers the structured node enum, the root rule (a path head that is also a descendant is not a
  top-level root, giving subsumption for free), the shared-subtree and converging-leaf rendering,
  and worked shapes for a diamond and distinct-key redirects. All merging and rendering happens in
  pure, unit-testable functions.
- [The resolve context](resolve-context.md): the blueprint, partly implemented, for a
  per-compilation `ResolveCtx` that hosts the caches, the config, and the compiler access, replacing
  the bare `TyCtxt` threaded through the resolver. Develops the cacheable-is-stateless-is-mockable
  equivalence, the Class A/B/C query taxonomy, the lifetime split (a long-lived owned cache store
  plus a per-resolution `'tcx`-scoped context), and the anchoring edge that stays rustc-coupled. The
  eventual CGP-component abstraction and its separate rustc-free stand-in context are recorded as
  deferred later work, not designed here.
- [The error pipeline](error-pipeline.md): the flow that turns rustc's raw diagnostics into readable
  CGP errors, entirely inside the driver (configure rustc, transform each diagnostic, render text or
  JSON), with the front-end forwarding cargo's output untouched.
- [Error processing](error-processing.md): the rustc-free `cargo-cgp-error-processing` crate that
  holds the driver's string-level diagnostic logic: the post-processing text transforms (stripping
  CGP path prefixes, resugaring `Symbol!` and `Path!`, resugaring `Product!`/`Sum!` lists to their
  `Struct!`/`Enum!` forms, rewriting unmet `HasField` bounds into missing-field messages), the
  wiring-message rewrite, the root-cause diagnosis model and the wording that turns it into the
  header, help, and note text, and the dependency-tree renderer. The driver's emitter drives all of
  it, and all of it is unit-tested without a compiler.
- [Resugaring](resugaring.md): the transforms that reverse CGP's type-level expansions, so every
  construct the tool shows is spelled the way the programmer wrote it: `Symbol!`, `Path!`, the
  `Product!`/`Sum!` lists and their `Struct!`/`Enum!` record forms, and the path strips that must
  run first. It has one section per construct with its expansion and its decline cases, and states
  the exact-match rule that keeps a resugaring from claiming syntax nobody wrote. One sub-section
  per implementation (typed over `Ty<'tcx>`, text over `&str`, syntax tree over `syn::Type`)
  explains why three inputs force three separate matchers that must nonetheless agree. The one
  sanctioned divergence is that only a diagnostic may show a form that reads better than it parses.
- [The expand command](expand-command.md): `cargo cgp expand`, which shows the ordinary Rust a
  project's CGP macros generate: a full `cargo-expand`-style expansion whose CGP type-level sugar
  the driver resugars before returning it. Covers why the compiler offers no way to expand only some
  macros, the `cargo rustc` launch and the marker flag that scopes expand mode to one crate, why the
  driver prints the expanded AST from `after_expansion` instead of setting `-Zunpretty=expanded`
  (which bypasses every callback), what running it settled about cargo's handling of a unit that
  yields no artifact, and the selective un-expansion still deferred to a second phase.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): a map of the compiler code that
  builds CGP diagnostics and where it *suppresses* information: the type/const printer, the
  trait-error reporters, the two verbosity switches (`--verbose` versus `-Zverbose-internals`), and
  the specific elision points the driver's `--verbose` injection defeats. It also catalogs the
  **panic hazards** of re-running compiler code inside the emitter (re-entering the `DiagCtxt` lock,
  relating an un-instantiated binder, leaking inference variables across contexts) and how the
  resolver avoids each. Read it when a diagnostic is dropping a cause the tool needs, or before
  adding a compiler interaction that could crash the driver.
- [Testing](testing.md): how the tool is tested: the tests over the argument handling, and the UI
  snapshot suite. The suite is a custom Rust test harness (like Clippy's `compile-test`) that
  compiles fixtures under `tests/ui/` through the tool and diffs committed `.cgp.stderr`,
  `.rust.stderr`, and `.expand.rs` snapshots. The document also covers the bless workflow and how
  the harness compares to Clippy's.
- [Distribution](distribution.md): how the tool is packaged and installed on a machine that has only
  stable Rust: installing both binaries through cargo in lockstep, provisioning the pinned nightly
  with `rustc-dev`, forcing that nightly for the check so the project needs no toolchain of its own,
  and the version preflight that keeps front-end and driver matched. It follows the `rustc_plugin`
  model where Clippy's in-toolchain distribution is closed to an out-of-tree tool. It covers the
  `setup`/`update` subcommands (all provisioning confined to `setup`, a read-only preflight in
  `check`, cargo-delegated update with crates.io version discovery) and running the tool as a Rust
  Analyzer check backend (the JSON pipeline, the `RUSTC_WRAPPER` non-collision, and the isolated
  target directory).
