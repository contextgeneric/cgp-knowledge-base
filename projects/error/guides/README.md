# Guides for the error backends

These guides are prescriptive: they say which backend and which provider to wire for a given source
type, and how to recognize and fix the wiring mistakes a backend invites. They apply to all three
crates, whose design is shared and set out in [../architecture.md](../architecture.md).

- [choosing-a-backend.md](choosing-a-backend.md) — anyhow, eyre, or a boxed standard error against
  the generic providers, how to route each source and detail type, the wiring forms, and how to test
  a downstream project against a local change to the crates.
- [debugging.md](debugging.md) — a non-standard source through the raise provider, a raiser without
  its error type, two backends mixed on one context, a `String` routed back to itself, a borrowed
  detail, and a custom eyre hook installed too late, each with its snippet and `cargo cgp check`
  output.

**Public material derived from this:** None yet.
