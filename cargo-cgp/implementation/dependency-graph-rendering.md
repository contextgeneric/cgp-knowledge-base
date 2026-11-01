# Dependency-graph rendering

The tree beneath a `root cause:` note comes from folding the resolver's per-cause paths into one
rustc-free **dependency graph** and rendering it `cargo tree`-style. The resolver emits a flat path
of structured nodes for each way it reaches a cause. This layer merges the nodes several paths
share, and marks with `(*)` a subtree already drawn. It is a pure function over owned data, so every
shape is unit-tested without a compiler.

## Why a graph rather than a chain per cause

Real wiring produces three shapes a stack of linear chains cannot show:

- **A shared dependency, a diamond:** two providers depend on one failing trait, so their paths
  share a suffix. The shared subtree should appear once.
- **Independent consumers converging on one leaf:** two components read one missing field. The
  heading names the cause once, but both chains stay, since both are real and need the same fix.
- **Subsumption:** one consumer's chain runs through another. The note should lead with the deeper
  chain, with the inner consumer in its place, rather than as a second top-level entry.

A graph whose nodes have structural identity handles all three. A node several paths reach is one
node with several parents, and a subsumed consumer is both a path head and another node's child.

## Node identity

**Nodes are structured data rather than rendered strings, so identity can be faithful where a label
is not.** A
[`ChainNode`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/node.rs)
is a hop or a leaf, and a hop's `DepNode` variant carries the names its `CGP-E1xx` label renders
from, with generics included. Identity is whole-node equality. So a `Redirect` node holds the
dispatched key even though its label shows only the route, and two lookups along one route for
different keys stay distinct rather than merging into a false diamond
([`redirect_distinct_keys`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/redirect_distinct_keys.rs)):

```text
[CGP-E101] consumer trait impl `CanAssemble` for context `App`
└─ [CGP-E102] provider trait impl `Assembler` with context `App` for provider `AssembleParts`
  ├─ [CGP-E101] consumer trait impl `CanBuildValue<Left>` for context `App`
  │ └─ [CGP-E103] redirect lookup to `@ValueBuilderComponent` in `App`
  │   └─ [CGP-E113] missing wiring for `@ValueBuilderComponent.Left` on `App`
  └─ [CGP-E101] consumer trait impl `CanBuildValue<Right>` for context `App`
    └─ [CGP-E103] redirect lookup to `@ValueBuilderComponent` in `App`
      └─ [CGP-E113] missing wiring for `@ValueBuilderComponent.Right` on `App`
```

**Merging is cross-path only.** A linear descent can pass through two hops that render identically
and mean different things, such as a recursive `RedirectLookup` resolving `Outer` then `Inner`, and
merging those would fold the spine into a false cycle. So `from_paths` keeps a within-path repeat as
a fresh node, and registers only a label's first occurrence, so a later path still finds the
canonical one.

## One cause per distinct leaf

A
[`Cause`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/resolved.rs)
is a leaf and every path that reaches it. The de-duplication signature, the consumer coalescing, and
the `help`s all expect each leaf once, and only the rendering reads the extra paths.

**The `Causes` type holds that invariant, so a new construction site cannot break it.** Its field is
private, and every constructor normalizes: `from_sub_chains`, `union`, `headed_by`, and collecting.
Getting this wrong by hand fails silently in two directions. Merging nothing states one mistake once
per contributor, so three consumers on one underived field would name `name`, `name`, and `name`.
Dropping a duplicate's paths loses a chain, so a header would name a consumer whose chain appears
nowhere in the note.

Coalescing several underived fields on one struct is the one case where a heading's leaf differs
from its paths' last entries: the heading reads as one fix, and the graph still branches to each
field
([`coalesce_underived_fields`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/coalesce.rs)).

## Roots and rendering

**A path head is a top-level root only if it is no node's child,** and subsumption follows from that
one rule: in `CanCalculateDensity → … → CanCalculateArea → …`, the shorter path's head is a child
inside the longer one
([`density_3`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/density_3.rs)).
If every head is a child, an all-cyclic input the resolver should never emit, every head becomes a
root, so rendering never yields nothing.

The renderer walks depth-first from each root in first-seen order, and these rules shape what a
reader sees:

- **A node with children is expanded once** and `(*)`-referenced after that, across all the note's
  roots, which also makes the walk terminate on a cycle.
- **A leaf is drawn in full every time,** since it hides no subtree, so the cause reads the same
  wherever a chain ends on it
  ([`parallel_consumers`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/verbose-cascade/parallel_consumers.rs)).
- **Every CGP construct is rendered in full,** even a hop repeating its parent's program-sized
  `Code`. Shortening it to `<…>` would hide the type the reader is tracing, and they could not tell
  a repeat from a hop whose parameters differ. A reader who wants it shorter is better served by
  [eliding across blocks](#eliding-across-blocks).

The diamond shows the shared subtree expanded under its first branch
([`diamond_shared_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/diamond_shared_trait.rs)):

```text
[CGP-E101] consumer trait impl `CanTop` for context `App`
└─ [CGP-E102] provider trait impl `TopProvider` with context `App` for provider `ProvideTop`
  ├─ [CGP-E101] consumer trait impl `CanLeft` for context `App`
  │ └─ [CGP-E102] provider trait impl `LeftProvider` with context `App` for provider `ProvideLeft`
  │   └─ [CGP-E101] consumer trait impl `CanShared` for context `App`
  │     └─ [CGP-E102] provider trait impl `SharedProvider` with context `App` for provider `ProvideShared`
  │       └─ [CGP-E104] trait impl `HasName` for `App`
  │         └─ [CGP-E110] missing field `name` on `App`
  └─ [CGP-E101] consumer trait impl `CanRight` for context `App`
    └─ [CGP-E102] provider trait impl `RightProvider` with context `App` for provider `ProvideRight`
      └─ [CGP-E101] consumer trait impl `CanShared` for context `App` (*)
```

## Eliding across blocks

One `seen` set threaded through a compilation's blocks lets a later block truncate at a subtree an
earlier one drew. It exists because one mistake surfaces in several diagnostics that legitimately do
not de-duplicate: a wrapper trait keeps its own block, and its chain can share everything below its
first few hops. Three rules keep this honest, each protecting against a specific wrong result:

- **An elided branch still ends at the root cause.** A cross-block `(*)` points into another block
  the reader may not have to hand, so it keeps the marker and appends the distinct leaves beneath it
  (`leaves_below`). A chain that stops short of the cause is the one thing it may never do. A branch
  elided within one note keeps the bare `(*)`, since its subtree is right above it.
- **A render consults only what earlier renders drew.** `seen` is keyed by node value, while a
  within-path repeat is deliberately a distinct node, so a set the current render also filled would
  mark the repeat `(*)` and fold a descent into a false cycle. So a render collects what it draws
  apart and adds it at the end, and within a render only the id-keyed `expanded` elides.
- **A block with no prefix of its own renders in full.** `fully_elided_by` reports every root
  already drawn, and such a block renders against a fresh set. Elision trims a shared tail under a
  block's own prefix, and with no prefix it would remove the whole derivation, leaving a cause with
  no account of where it came from. A childless root is a bare leaf, so it never counts as elided.

An elided block stays actionable alone, since its headline, `help`, and `root cause:` lead still
name the cause. So elision is safe for a consumer that sees one diagnostic at a time, such as an
editor reading JSON.

## The note over the graph

`cause_notes` folds every path of every cause into one graph under the
`this is required through the dependency chain:` heading, and
[the output document](typed-resolution-output.md#the-root-cause-notes) covers how the heading reads.
The emitter's coalesced block builds the same note: when several consumer failures share a cause,
its note folds every member's causes into one graph, so a consumer whose chain runs through another
collapses into it, and no member's chain is dropped.

The resolver produces only paths, and every merge decision is the graph's. An anchor that wraps a
result in an enclosing trait prepends its hop to each path and groups by leaf, rather than nesting
one tree inside another, which is simpler. The
[cache](cached-dependency-resolution.md) stores these node-rooted paths.

## Known limits

- **A wide convergence repeats `(*)` once per parent, and that is not noise to collapse.** Each
  `(*)` ends a distinct branch naming a distinct consumer, so dropping the repeats would leave those
  branches dangling. The length is inherent to wiring in which many traits need one shared thing.
  Only a subtree drawn in another block is worth collapsing.
- **A very long chain costs quadratic work here.** Past about 120 chained hops, every check entry of
  the chain fails and coalesces, so the merged graph folds one path per member, each up to twice the
  chain's length.

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md): the resolver whose walk fills the
  paths.
- [Error processing](error-processing.md): the rustc-free crate this lives in.
- [The driver](driver.md): the emitter that builds the coalesced block's note.

## Tests

- [`tests/error_processing/graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/graph.rs):
  every shape as `insta` inline snapshots, with no compiler, including a within-path repeat, a
  cyclic input, and the cross-block elision.
- [`tests/error_processing/causes.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/causes.rs):
  the `Causes` set: grouping, `union`'s fold and associativity, and `headed_by`.
- [`tests/error_processing/coalesce.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/coalesce.rs):
  merging underived fields while keeping each path.
- [`tests/error_processing/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis):
  the note assembly over the graph.
- [`checks/check-trait-failure/resolution/foreign_getter_missing_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/foreign_getter_missing_wiring.rs),
  and the fixtures cited above: the graph end to end through the compiler.

## Source

- [`diagnosis/node.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/node.rs):
  the structured nodes and their label templates.
- [`diagnosis/graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/graph.rs):
  `DependencyGraph`, its merge, the root rule, and the elision.
- [`diagnosis/resolved.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/resolved.rs):
  `Cause` and `Causes`.
- [`diagnosis/wording/note.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/wording/note.rs):
  `cause_notes`.
- [`tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/tree.rs):
  the `DependencyTree` renderer the graph expands into.
- [`emitter/flush/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter/flush):
  the flush that renders each note against one shared `seen`, and the coalesced block.
