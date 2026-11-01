# Typed root-cause resolution

This directory documents the resolver: the emitter transformation that turns a CGP wiring failure into
one coded headline over a `cargo tree`-style dependency chain, by asking the trait solver what failed
rather than parsing rustc's text. Start with the overview, which holds the worked example, what the
resolver declines and why, its boundaries, and the test and source catalogs for the whole directory. The
other documents each cover one stage, in the order a failure passes through them.

- [Overview](overview.md): the worked example, the candidate gate, why the resolver runs in the emitter,
  the anchor order, and the boundaries.
- [Anchoring the starting obligation](anchors.md): the eight anchors that recover the failing obligation
  from a diagnostic's spans.
- [The call-site anchor](call-site.md): the four anchors that re-read a failing call from HIR, its
  signature unification, and the rigid placeholders that stand in for what the call never types.
- [Walking to the root cause](walk.md): the descent to every terminal unmet bound, and the decisions a
  simpler walk would get wrong.
- [Leaves and labels](leaves.md): what ends a branch, which cause each terminal bound is, and how each hop
  reads.
- [The transformed diagnostic](output.md): the headline classes, the single `root cause:` note, the fix
  `help`s, and the plan applied to rustc's diagnostic.

Two documents outside this directory serve the resolver and other parts of the tool:
[Cached dependency resolution](../cached-dependency-resolution.md) memoizes the walk, and
[Dependency-graph rendering](../dependency-graph-rendering.md) merges its paths into the note's tree.
