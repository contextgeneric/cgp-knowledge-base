# Hypershell guides

The guides are prescriptive: each says how to do one job with Hypershell and which mistakes to avoid,
where the [architecture](../architecture/README.md) explains why the design is as it is and the
[reference](../reference/README.md) says what each item does. Every code snippet in them was compiled
against the `v0.8.0` branch, and every diagnostic was produced by a probe.

## The catalog

Register each guide here, in [../README.md](../README.md), and in
[../../../summary.md](../../../summary.md) in the same change.

- [writing-a-program.md](writing-a-program.md) — using the language: the prelude and a context,
  runtime values from fields, simple against streaming stages, the adapters between stages, the input
  to pass, checking a program, and the toolchain.
- [extending-the-language.md](extending-the-language.md) — adding handler, argument, and control
  syntax, registering an error type, choosing between an extension namespace and context entries, and
  the three ways to replace an existing syntax's interpretation, which the namespace does not allow
  directly.
- [debugging.md](debugging.md) — checking before reading errors, and the common mistakes with their
  `cargo cgp check` root causes: a missing field, stages that do not agree, a syntax or error type
  with no route, a routed provider that cannot resolve, a conflicting rebinding, and macro failures.

## Public material derived from this

The user-facing and extension pages of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
