# Testing

`web-app` has no tests and no binary, so the only checks the repository runs are the check blocks of
its four modules, at compile time. On the `v0.8.0` branch `cargo build -p cgp-example-web-app`
passes, and so does every check. This document records what the checks pin, what probes showed them
catch, what a probe ran, and what nothing exercises.

## What the checks pin

Every context is checked for every component it can use:

| Module | Context | Checked by | Components checked |
|---|---|---|---|
| `coarse_grained` | `ProductionApp` | its `delegate_and_check_components!` table | the four it wires |
| `fine_grained` | `ProductionApp` | `check_components!` | all nine |
| `namespace` | `ProductionApp` and `TestApp` | one `check_components!` block | all nine, on each |
| `default_impls` | `ProductionApp` | `check_components!` | all nine |

A check covers a component's whole provider chain, so a check of `UserCreatorComponent` also verifies
that the context implements `CanCensorUsername`, which the creator's filter wrapper uses. That is why
the probes below report a missing filter at the creator's check as well as at the filter's own.

## What the checks catch

A probe context joined `DefaultNamespace` and forwarded only the core path, leaving the extras out:

```rust
delegate_components! {
    CoreOnlyApp {
        namespace DefaultNamespace;

        @app.core: PostgresCoreComponents,
    }
}
```

With all nine components checked, `cargo cgp check` failed with two errors at the check lines, one
per missing filter. It grouped each filter with the creator whose wrapper uses it:

```text
error[E0277]: [CGP-E001] the consumer traits `CanCreateUser` and `CanCensorUsername` are not implemented for context `CoreOnlyApp`
   = note: root cause: [CGP-E107] context `CoreOnlyApp` does not contain any delegate entry for `@app.extra.content_filter.UsernameCensorComponent`
error[E0277]: [CGP-E001] the consumer traits `CanCreatePost` and `CanDetectSpamMessage` are not implemented for context `CoreOnlyApp`
   = note: root cause: [CGP-E107] context `CoreOnlyApp` does not contain any delegate entry for `@app.extra.content_filter.SpamMessageDetectorComponent`
```

The mistake is the missing `@app.extra` entry, and the root cause names the full path the namespace
routes each filter to. The other five checks passed, since the getters, updaters, and deleter need
nothing from the extras. Three further probes are recorded with the stage they concern:

- **A bundle that does not join the namespace** — `[CGP-E110]` at the check lines; see
  [namespaces.md](namespaces.md#the-bundles).
- **A default-impls context without its filter entry** — `[CGP-E107]` at the creator's check; see
  [default-impls.md](default-impls.md#the-context).
- **A context or child namespace that overrides a default** — `[CGP-E005]` at the entry; see
  [default-impls.md](default-impls.md#a-default-cannot-be-overridden).

## What a probe ran

A probe crate with a path dependency on the crate compiled the two wiring steps the crate keeps only as
comments, each on a context of its own: the flat nine-entry table of `fine_grained.rs` and the flat
namespace table of `namespace.rs`. Both passed a check of all nine components.

The same crate called one method on a context of three stages: `get_user` and `create_user` on the
coarse `ProductionApp`, `create_post` on the namespace stage's `TestApp`, and `delete_post` on the
default-impls `ProductionApp`. Each call panicked with `not yet implemented`. For `create_user` and
`create_post`, the panic comes from the dummy censor or spam detector, whose `todo!()` runs before
any database code.

## What is untested

These have no test, and the probes above are the only evidence beyond the build:

- **Every method** — each provider body is `todo!()`, so no call returns.
- **The filter thresholds** — nothing exercises the rejection above a score of 0.8, since the filters
  that would supply a score are `todo!()` as well.
- **The commented steps** — the build does not compile them; only the probe did.
- **Compile failures** — there are no compile-fail tests.

## Public material derived from this

None yet.
