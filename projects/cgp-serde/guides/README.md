# cgp-serde guides

The guides are prescriptive: each one says how to do one job with cgp-serde, names the default to reach
for, and explains the mistakes to avoid. They assume the [architecture](../architecture/README.md) and
link to the [reference](../reference/README.md) for what each provider does, rather than repeating it.
CGP's own guidance, such as how to write a provider in general, lives under
[cgp/guides/](../../../cgp/guides/README.md); these guides cover only what is specific to cgp-serde.

## The catalog

Register each guide here, in [../README.md](../README.md), and in
[../../../summary.md](../../../summary.md) in the same change.

- [wiring-a-context.md](wiring-a-context.md) — building a context's serialization table: which
  components to open, how to find every type the traversal reaches, key syntax for references,
  lifetimes, and arrays, and how to check the result.
- [writing-a-provider.md](writing-a-provider.md) — writing a new serializer or deserializer: one struct
  for both directions, calling back into the context, reporting errors through Serde, and the lessons
  the library's own defects teach.
- [debugging-wiring.md](debugging-wiring.md) — the common wiring mistakes, each with the code that
  makes it and the diagnostic `cargo cgp check` reports.
- [formats.md](formats.md) — using a context with `serde_json` and other Serde formats, which formats
  work, and how to write the deserialization entry point a format lacks.

## Public material derived from this

The "Wiring an application" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the usage sections of the
repository README.
