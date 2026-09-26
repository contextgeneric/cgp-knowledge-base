# Issues

This document records what is wrong with or missing from `web-app` on the `v0.8.0` branch, grouped as
defects, missing features, and housekeeping. Every entry was confirmed against the source, by a probe
crate where it says so. Remove an entry in the same change that fixes it in the crate, per
[../../AGENTS.md](../../AGENTS.md#the-shape-of-a-project-section).

## Defects

No defect has been confirmed. The crate compiles, every context passes a check of every component it
can use, and each probe call ended in the `todo!()` its code reaches; see
[testing.md](testing.md#what-a-probe-ran).

## Missing features

- **Nothing runs the crate** — it has no binary and no test, and every provider body is `todo!()`, so
  no method returns. The crate demonstrates wiring, which the build verifies, but a test that
  exercised a filter would need stand-in bodies for the dummy filters and the Postgres providers. It
  would also need `Error` to derive `Debug` before a test could unwrap a result. See
  [testing.md](testing.md#what-is-untested).

## Housekeeping

- **Two wiring steps are comments** — the flat nine-entry table in `fine_grained.rs` and the flat
  namespace table in `namespace.rs` are commented-out blocks, so the build does not check them and
  they can drift from the code around them. A probe compiled both, on contexts of their own, and both
  passed a check of all nine components. Wiring each on a context of its own in the crate, as the
  probe did, would keep them compiled; see [testing.md](testing.md#what-a-probe-ran).
- **Unwired providers** — `fine_grained.rs` and `default_impls.rs` each define `DummyUserCensor` and
  `DummySpamMessageDetector`, and no context in either module wires them. The dummies that are wired
  are separate definitions in `coarse_grained.rs` and, through `DummyContentFilterComponents`, in
  `namespace.rs`.

## Public material derived from this

None yet.
