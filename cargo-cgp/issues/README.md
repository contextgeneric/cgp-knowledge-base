# Pending issues

This directory tracks what `cargo-cgp` does not do well today: a cause it cannot recover, or one it
recovers but presents poorly. Each entry names a gap and links the fixture that shows it, so the next
agent can pick up the work without rediscovering it.

Every issue is backed by a fixture under
[`tests/ui/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui), so the list holds problems
a reader can see happen. When an issue is fixed, delete its entry and change the fixture's header to
`//@quality: acceptable`; the fixture stays in its class directory. A plain Rust or Cargo error with
nothing to do with CGP is out of scope.

The issues split on whether the root cause is *recoverable* from the tool's output, and one test
decides: if no downstream processing of the text could reconstruct the cause, it is a hidden root
cause; if a careful reader or tool could, it is a usability issue. The distinction decides how much
the tool must do, because recovering absent information needs the compiler's state, while
re-presenting present information is post-processing. Each fixture records it in its `//@quality:`
header.

- [Hidden root cause](hidden-root-cause.md): cases where the output lacks the cause. None is open today,
  and the document records the two kinds the driver's flags defeat, so they are recognized again.
- [Usability issues](usability.md): output that carries the cause but buries it. The harness lists these
  fixtures with `cargo test -p cargo-cgp-ui-tests --test ui -- --list`.

The [CGP error catalog](../../cgp/errors/README.md) maps every error class and whether its cause is present
in the output.
