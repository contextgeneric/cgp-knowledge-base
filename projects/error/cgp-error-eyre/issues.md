# cgp-error-eyre issues

The crate has one open limitation of its own. The housekeeping it shares with the other backends is
recorded in the project [README](../README.md#confirmed-gaps).

## Defects

### Reports carry no caller location

A report built by the crate cannot record where the application raised it. eyre records a location
through `#[track_caller]` when its `track-caller` feature is on, but the report is built inside a
provider method, and the call reaches that method through CGP's generated consumer and delegation
impls, none of which is `#[track_caller]`. So the location is always the provider's own line. A probe
with the feature on printed, for an error raised from the probe's `main`:

```text
while loading

Caused by:
    no file

Location:
    …/cgp/crates/standalone/error/cgp-error-eyre/src/impls/raise_eyre_error.rs:18:11
```

The crate therefore leaves `track-caller` off, so the default handler prints no location at all
rather than a misleading one. An application that enables eyre's default features itself turns the
feature back on through feature unification and gets the misleading line. A fix would need
`#[track_caller]` on every method the generated impls forward through, which is a change to the CGP
macros rather than to this crate.

**Public material derived from this:** None yet.
