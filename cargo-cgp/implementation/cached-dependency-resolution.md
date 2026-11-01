# Cached dependency resolution

The typed resolver memoizes its walk at every node, so each distinct obligation resolves once and
its result is reused wherever it recurs, without changing a byte of the output. The soundness of
that reuse is the point of this document: a node's result is not a pure function of the node, so two
guards complete the key.

## Why cache the resolution at all

One CGP mistake makes the walk repeat itself in two ways, and both reduce to resolving one
obligation again. Wiring is lazy, so the same failure surfaces at the `check_components!` entry, at
each hand-written `impl` that references the broken consumer, and at each call, and the
[`DedupLedger`](error-processing.md) would throw away all but one finished walk. And within one
walk, a trait several providers depend on is a diamond, whose subtree would be walked once per
parent.

rustc's query system already memoizes each lookup the walk makes (`clauses_of`, the impl list, the
ADT fields). Nothing memoizes the composite descent that assembles them into a root-cause tree, so
this cache adds only that layer.

Writing the cache also forces each question the resolver asks the compiler to be either provably
pure or explicitly stateful. Purity rests on one invariant: the resolver runs at emit time over
frozen state. The trait set, the impls, the clauses, and the ADT fields are fixed once the crate is
lowered, and trait solving does not change them
([why resolution runs in the emitter](typed-root-cause-resolution.md#why-it-runs-in-the-emitter)).
So a subtree resolved once stays valid for the rest of the crate's compilation.

## What is cached

The stored value is the walk's owned, rustc-free output: for each node, its root-cause sub-chains,
each an owned `Leaf` plus the chain from that node down to it, with the set of obligation
fingerprints the subtree reaches. It holds no `Ty<'tcx>`, no `DefId`, and no compiler handle, so it
can outlive every `TyCtxt`. An `InferCtxt`'s intermediate work could not, since it is
`'tcx`-interned and dies with its closure.

Sub-chains are stored **node-rooted**: a child returns chains that begin at its own label, and its
parent prepends its own. So a value serves a future seed and a splice into a larger walk alike, with
no re-rooting pass, and a seed is simply a node with no ancestors.

Only **non-terminal** nodes are cached. A terminal leaf's classification reads its parent
obligation, which lies outside a leaf-rooted subtree, and a leaf is cheap to derive again. A
non-terminal node's leaves classify against parents within its subtree, so its value is
self-contained.

## Why a node key is not automatically a complete key

**The walk is not a pure function of the node, and the whole soundness argument turns on this.** The
cycle guard cuts a branch when an obligation reappears among its ancestors, so a node's leaves
depend on the ancestors too. Memoizing on the node alone can go wrong in two directions:

- **Under-reporting:** a subtree computed where a descendant looped back to an ancestor was cut
  there. Reused under ancestors that lack that obligation, it silently misses a real cause.
- **Over-reporting:** a subtree computed with no cut, reused under ancestors that would cut, keeps a
  leaf a correct walk would have severed.

A wrong tree that looks clean is the worst outcome for this tool, so two guards complete the key.
Both are no-ops in acyclic wiring, which is nearly all wiring. Keep both even so: the walk must not
rely on the upstream `E0275` interception to keep cycles out, and dropping either would make it rely
on that.

### Population: cache only complete subtrees

**A subtree that a guard cut is never stored.** The cycle guard and the `MAX_DEPTH` backstop both
truncate silently, and both depend on position, since a node deep in one walk has less depth budget
than the same node walked from a shallow one.

**A cut leaves no trace in the finished tree,** so eligibility cannot be derived from the output.
The walk records it instead: a cut sets `incomplete` on its sub-result, and the flag rides up
through every parent (`incomplete |= sub.incomplete`), so no ancestor that folded in the cut is
cached. This over-approximates, since an ancestor above the cycle's entry holds the whole loop and
is safely cacheable. Telling them apart would mean threading the collision's depth back up the
recursion, for a few extra entries in a rare crate. Caching too little costs only a re-walk.

A cached node is therefore complete: every branch ended on a natural terminator, so no branch
depended on the remaining depth budget. A cache hit can even return a fuller subtree than a fresh
bounded walk from a deep position would.

### Consultation: reuse only where no cycle would form

**A cached subtree is reused only when no current ancestor is in its reachable set.** Completeness
settles depth, not cycles. If `N` was cached from a walk that never passed through `A`, its subtree
may run through an obligation equal to `A` with no cut. A later walk that descends through `A` and
reaches `N` must cut there, and splicing in the cached subtree would keep that branch. The cycle
guard handles the node itself being an ancestor, and the reachable set extends that to a descendant
being one.

Within one root context this check never declines. If a complete subtree of `N` reached an ancestor
`A`, then `A` reaches `N` and `N` reaches `A`, so `N`'s own walk met the loop and was cut, and a cut
subtree is never cached. A decline needs the loop's obligation walked under two root contexts:
`Outer: Linked` is a leaf in `Inner`'s walk, while `Outer`'s own walk descends it
([`cross_context_cycle_reuse_distinct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs)).

## The cache key

**The key is one `StableHash` fingerprint of the region-erased obligation and the root context,** so
every input the output depends on must be in it. A 128-bit fingerprint is `Copy` and lifetime-free,
so it outlives any `TyCtxt`, where the interned `Ty<'tcx>` it summarizes cannot.

**The encoding must identify a `DefId` by its path.** `StableHash` walks the whole structure of a
type and encodes each `DefId` by its stable path identity, so two same-named types in different
modules differ
([`same_name_components`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/same_name_components.rs)).
A string of the type's name could not be the identity for that reason. A collision is not
impossible, but it would produce a wrong message on an already-failing build, a risk rustc accepts
for its own caches.

**The root context is an input because rendering depends on it.** `label_for` and `classify_leaf`
compare a node's `Self` against the context: an unmet `DelegateComponent` is a missing wiring only
when its owner is that context. So the same obligation under another context renders differently and
must miss. A consumer obligation on another context is re-rooted there, which keys it identically to
that context's own walk, so the two share an entry
([`cross_context_node_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/cross_context_node_key.rs)).

**The parameter environment is not in the key, which holds only while the walk's environment stays
empty.** Every solver call uses an empty `ParamEnv`, a constant rather than a hidden input, and a
seed holding a type parameter [declines](typed-root-cause-resolution.md#boundaries). A change that
gives the walk a real environment must hash it into the fingerprint, or two identical obligations
under different environments would collide.

## Limits

- **Hit rate at call sites:** a [call-site seed](typed-resolution-call-site.md) carries rigid
  placeholders whose identities are in the fingerprint, so two call sites of one unknown-argument
  trait do not cross-hit. The cache misses where it harmlessly could hit, and nothing else changes.
- **Cost past about 120 hops:** the walk's cost grows with the square of the chain depth, which
  stays a known limit rather than an optimization target.
- **The depth cut's flag is unpinned:** `divergent_wiring` reaches `MAX_DEPTH`, but its overflow is
  worded from the cut's reason rather than from the flag, so clearing the flag changes no output.
  Pinning it needs a subtree a depth cut leaves short and a later walk, nearer the subtree, would
  resolve within the cap.

## Relation to the de-duplication ledger

The cache and the `DedupLedger` act on different axes and both are needed. The ledger compares the
recovered cause after the walk, to decide what is shown. The cache compares obligations before and
during the walk, to decide what is resolved. Two diagnostics can show one cause through different
seeds, such as a wrapper's `[CGP-E003]` block and the check entry it reduces to, which only the
ledger sees. And the cache saves a walk whenever a node recurs, even when a later cause is a strict
sub-cause of an earlier one and the ledger keeps both blocks.

## Where the cache lives

`ResolveCache` sits on `CgpEmitter` beside the ledger, created once per driver invocation over one
crate, so no incremental database can change beneath it. The
[resolve context](architecture.md#the-resolve-context) built per diagnostic borrows it.

**The memo must never hold the `RefCell` borrow across the compute,** in a codebase whose
[compiler hazards](rustc-diagnostic-internals.md) are about a lock that panics on re-entry. It
checks and releases, computes with no borrow held, then borrows again to insert. The recursion is
`resolve_node` calling itself, and the read and write bracket each call rather than spanning it.

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md) and
  [its walk](typed-resolution-walk.md): the descent being cached.
- [Architecture](architecture.md#the-resolve-context): the `ResolveCtx` that carries the cache.

## Tests

The suite is the primary guard: the cache is pure memoization, so any snapshot change would be a
bug. The first two fixtures below each fail when their guard is removed.

- [`wiring/wiring-cycle/cycle_cut_rechecked`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cycle_cut_rechecked.rs):
  the population guard. Within one walk a cut loses no cause, so the fixture checks both components
  of a cycle, and the second walk must resolve afresh what the first left incomplete.
- [`wiring/wiring-cycle/cross_context_cycle_reuse_distinct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs):
  the reuse guard. Its sibling `cross_context_cycle_reuse` merges into one block, so it does not
  show the splice.
- [`wiring/wiring-cycle/mutual_cycle_with_cause`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/mutual_cycle_with_cause.rs):
  a cycle cut in a walk that still resolves, reporting the missing field down the other branch.
- [`checks/check-trait-failure/resolution/diamond_shared_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/diamond_shared_trait.rs):
  an interior hit is output-preserving.

## Source

- [`resolve/cache.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/cache.rs):
  the key, the owned values, and the store.
- [`resolve/walk/leaves/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/walk/leaves):
  `node.rs` memoizes each node and applies both guards, and `entry.rs` folds the root's result into
  a `Resolved`.
- [`emitter/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter):
  `CgpEmitter`, which holds the store and builds the context.
