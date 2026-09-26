# The namespace stage

`namespace.rs` registers the nine fine-grained components under path prefixes in `DefaultNamespace`,
so that its two contexts, `ProductionApp` and `TestApp`, each wire the whole application in two path
entries and differ in one of them.

- **Source** — [namespace.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/web-app/src/namespace.rs)
- **Run** — no test; the contexts are exercised only by their check blocks
- **Needs** — nothing
- **Result** — compiles and passes its checks. A probe called `create_post` on `TestApp`, which
  panicked with `not yet implemented`, and compiled the commented-out flat namespace step on a
  context of its own, which passed all nine checks

## The prefix tree

Each component carries a [`#[prefix]`](../../../cgp/reference/attributes/prefix.md) attribute that
places it under a path in `DefaultNamespace`:

```rust
#[cgp_component(UserCreator)]
#[prefix(@app.core.user in DefaultNamespace)]
pub trait CanCreateUser {
    fn create_user(&self, username: &str, email: &Email) -> Result<User, Error>;
}
```

The nine components fill three paths, and the paths nest under two parents:

| Path | Components |
|---|---|
| `@app.core.user` | `UserCreator`, `UserGetter`, `UserUpdater` |
| `@app.core.post` | `PostCreator`, `PostGetter`, `PostUpdater`, `PostDeleter` |
| `@app.extra.content_filter` | `UsernameCensor`, `SpamMessageDetector` |

The providers are the same thirteen as the [fine-grained stage](fine-grained.md#the-providers),
redefined in this module with the same bounds.

## The bundles

The module builds its wiring in two layers of bundles. The lower layer is four plain bundles keyed by
component name, like those of the fine-grained stage: `PostgresUserComponents`,
`PostgresPostComponents`, `AiContentFilterComponents`, and `DummyContentFilterComponents`, the last
wiring `DummyUserCensor` and `DummySpamMessageDetector`.

The upper layer is three bundles keyed by path, each of which joins `DefaultNamespace` itself:

```rust
delegate_components! {
    new PostgresCoreComponents {
        namespace DefaultNamespace;

        @app.core.user: PostgresUserComponents,
        @app.core.post: PostgresPostComponents,
    }
}

delegate_components! {
    new ProductionExtraComponents {
        namespace DefaultNamespace;

        @app.extra.content_filter: AiContentFilterComponents,
    }
}
```

`DummyExtraComponents` is `ProductionExtraComponents` with `DummyContentFilterComponents` in place of
the AI bundle. The `namespace` line in these bundles is required. A probe wired a copy of
`PostgresCoreComponents` without it and checked two user components on a context that forwarded
`@app.core` to the copy:

```rust
delegate_components! {
    new BareCoreComponents {
        @app.core.user: PostgresUserComponents,
        @app.core.post: PostgresPostComponents,
    }
}
```

Both checks failed with the same root cause, the bundle having no entry for the bare component name
that reaches it:

```text
error[E0277]: [CGP-E002] the provider trait `UserCreator` with context `BareCoreApp` is not implemented for provider `BareCoreComponents`
   = note: root cause: [CGP-E110] provider `BareCoreComponents` does not contain any delegate entry for `UserCreatorComponent`
```

The lookup reaches the bundle keyed by the bare component name, which only the bundle's own
`namespace` line redirects to the paths its entries match; the
[aggregate providers](../../../cgp/concepts/aggregate-providers.md#aggregate-providers-behind-namespace-paths)
concept traces the lookup.

## The contexts

Both contexts hold the database handle, join `DefaultNamespace`, and forward the two top-level paths:

```rust
delegate_components! {
    ProductionApp {
        namespace DefaultNamespace;

        @app.core: PostgresCoreComponents,
        @app.extra: ProductionExtraComponents,
    }
}

delegate_components! {
    TestApp {
        namespace DefaultNamespace;

        @app.core: PostgresCoreComponents,
        @app.extra: DummyExtraComponents,
    }
}
```

So the two share the whole core and differ only in their content filters. The module also keeps, as
a comment, the flat namespace step in between, which wires `ProductionApp` with the three leaf paths
straight to the lower-layer bundles. One `check_components!` block asserts all nine components on
each context.

## What it demonstrates

- Component keys grouped under a shared path, so one entry routes a whole group; see
  [namespaces](../../../cgp/concepts/namespaces.md) and the
  [namespaces and prefixes guide](../../../cgp/guides/namespaces-and-prefixes.md).
- A hierarchy of paths, so a parent path routes its children through a bundle that joins the
  namespace in turn.
- Two contexts whose difference is one line of their wiring.

## Known issues

- **The flat namespace step is a comment** — nothing compiles it; see
  [issues.md](issues.md#housekeeping).

## Public material derived from this

The "Introducing CGP namespaces and paths" and "Hierarchical delegation" sections of the
[v0.8.0 release post](../../../website/blog/v0-8-0-release.md).
