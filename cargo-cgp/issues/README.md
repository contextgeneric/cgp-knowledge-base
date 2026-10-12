# Pending issues

This directory tracks the work `cargo-cgp` has not yet done: the problems the tool is meant to solve
but does not solve today. Unlike the rest of the knowledge base, which describes how the tool
*currently* works, this category deliberately describes behavior that is absent or intended: it is a
checklist of gaps, not a record of the design. Each entry names a gap, points at the evidence for
it, and says what closing it requires, so the next agent can pick up a concrete piece of work
without rediscovering it.

Every issue is backed by a test case. An issue is worth reporting only if a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui) reproduces it, so each
entry links the fixture that exposes it, and a class of issue with no reproducing fixture is treated
as **resolved** and deleted from these documents rather than kept as a hypothetical. This keeps the
checklist honest: it lists problems a reader can see happen, not problems we imagine. When an issue
is fixed, delete its entry and move its fixture to the passing category (below); the git history
records the evolution, and a stale "fixed" note is worse than none.

Two things are out of scope. First, the classes the tool **already** handles well: `cargo cgp check`
compiles the workspace through a `rustc_driver` wrapper that both injects `-Znext-solver=globally`,
surfacing the CGP dependency bounds the default solver hides, and rewrites the CGP error classes it
recognizes into a root-cause-first form stamped with `[CGP-Exxx]` codes. Those resolved classes are
recorded as fixtures of `acceptable` quality (and in the CGP error catalog), not as issues here;
this directory tracks only what the tool does *not* yet do well: a cause it cannot recover, or one
it recovers but presents poorly. Second, this catalog is only about the diagnostics CGP produces; a
plain Rust or Cargo error that has nothing to do with CGP is not `cargo-cgp`'s problem to reformat
and is not recorded here.

## Organization

The issues split along one axis: whether the root cause is *recoverable* from the tool's output at
all, or merely hard to read. That axis matters because it decides who the issue is for and how much
the tool must do to close it: recovering absent information needs the compiler-internal foothold,
while re-presenting present information is post-processing. Each `tests/ui/` fixture records the
same distinction in its `//@quality:` header field (`hidden`, `usability`, or `acceptable`), while
its directory names its error class.

- [Hidden root cause](hidden-root-cause.md): **tool-oriented**, about *sufficiency* rather than
  format. It catalogs the edge cases where `cargo-cgp` does not emit enough information for any
  downstream consumer (a formatter, an IDE, or an AI agent) to identify the root cause from the
  output alone, no matter how that output is processed. These are the cases that justify the tool's
  compiler-internal access, because only a tool reading the compiler's own state can supply what the
  ordinary text output has lost. It lists five extensible-data failures whose output never names
  the cause, and records the two archetypes the driver's flags (`-Znext-solver=globally` and
  `--verbose`) defeat, so they are recognized again.
- [Usability issues](usability.md): **human-oriented**, about *readability*. It lists output that
  does carry the root cause but buries it (foremost the sheer verbosity of a CGP compile error), so
  a reader must wade through volume, encoding, and generated-type noise to reach a cause that is
  nonetheless present. Its fixtures carry `//@quality: usability`; the harness lists them with
  `cargo test -p cargo-cgp-ui-tests --test ui -- --list`.

The dividing line is a single test: if no amount of downstream processing of the text could
reconstruct the root cause, the issue is a hidden root cause; if a sufficiently careful reader or
tool could, it is a usability issue. Both draw their evidence from the fixtures and read them
against the [CGP error catalog](../../cgp/errors/README.md), which maps every error class CGP
produces and, class by class, whether the root cause is present in the output or suppressed.

The fixtures that are *not* open problems need no issues document because there is nothing to fix.
[`tests/ui/ok/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/ok) is the
clean-compile baseline: correctly-wired programs that check with empty output. An *error* fixture
whose cause `cargo-cgp` presents well has `acceptable` quality; the typed root-cause resolver has
carried most of the check-trait-failure class there. Their snapshots are the standing proof the
tool keeps producing good output. As a usability issue is closed, its fixture's header changes from
`//@quality: usability` to `//@quality: acceptable`; the fixture stays in its class directory.
