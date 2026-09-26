# The default-implementations stage

`default_impls.rs` binds seven of the nine components to their providers inside a custom namespace,
`DefaultAppComponents`, so that its `ProductionApp` joins that namespace and wires only its content
filters.

- **Source** — [default_impls.rs](https://github.com/contextgeneric/cgp-examples/blob/v0.8.0/web-app/src/default_impls.rs)
- **Run** — no test; the context is exercised only by its check block
- **Needs** — nothing
- **Result** — compiles and passes its check. A probe called `delete_post` on `ProductionApp`, which
  panicked with `not yet implemented`

## The components and providers

The nine components carry the same prefixes as the [namespace stage](namespaces.md#the-prefix-tree),
registered in `DefaultNamespace`, and the thirteen providers are the same as the
[fine-grained stage](fine-grained.md#the-providers). What changes is where the wiring lives.

## The namespace

[`cgp_namespace!`](../../../cgp/reference/macros/cgp_namespace.md) declares `DefaultAppComponents` as
a child of `DefaultNamespace`, in a block with no body, and a second block without `new` then binds
the two creators, each wrapped in its filter:

```rust
cgp_namespace! {
    new DefaultAppComponents: DefaultNamespace
}

cgp_namespace! {
    DefaultAppComponents {
        @app.core.user.UserCreatorComponent:
            FilterCensoredUsername<CreateUserWithPostgres>,

        @app.core.post.PostCreatorComponent:
            FilterSpamMessage<CreatePostWithPostgres>,
    }
}
```

The other five bindings sit on the providers themselves. `GetUserWithPostgres`,
`UpdateUserWithPostgres`, `GetPostWithPostgres`, `UpdatePostWithPostgres`, and
`DeletePostWithPostgres` each register as the namespace's default for their component's full path with
[`#[default_impl]`](../../../cgp/reference/attributes/default_impl.md):

```rust
#[cgp_impl(new GetUserWithPostgres)]
#[default_impl(@app.core.user.UserGetterComponent in DefaultAppComponents)]
impl UserGetter {
    fn get_user(&self, #[implicit] database: &PostgresDb, user_id: &UserId) -> Result<User, Error> {
        todo!()
    }
}
```

The creators are bound in the block rather than by attribute, because their default is a wrapper
around the provider, not the provider alone. So the namespace binds every core path, and binds nothing
under `@app.extra`.

## The context

`ProductionApp` joins `DefaultAppComponents` and wires the one group the namespace leaves open. Its
bundle, `ContentFilterComponents`, has the same two entries as `AiContentFilterComponents` in the
earlier stages, `AiUserCensor` and `AiSpamMessageDetector`, under the name the release post uses at
this point:

```rust
delegate_components! {
    ProductionApp {
        namespace DefaultAppComponents;

        @app.extra.content_filter: ContentFilterComponents,
    }
}
```

A `check_components!` block asserts all nine components on it. The content-filter entry is required:
a probe context that joined `DefaultAppComponents` with no entries of its own passed its check of
`UserGetterComponent` and failed its check of `UserCreatorComponent`, because the default creator's
filter needs the censor:

```text
error[E0277]: [CGP-E001] the consumer trait `CanCreateUser` is not implemented for context `NoFilterApp`
   = note: root cause: [CGP-E107] context `NoFilterApp` does not contain any delegate entry for `@app.extra.content_filter.UsernameCensorComponent`
```

## A default cannot be overridden

A context that joins `DefaultAppComponents` cannot replace one of its defaults. A probe added a direct
entry for one bound path beside the namespace line:

```rust
delegate_components! {
    CachedApp {
        namespace DefaultAppComponents;

        @app.core.user.UserGetterComponent: GetCachedUser,
        @app.extra.content_filter: ContentFilterComponents,
    }
}
```

`cargo cgp check` rejected the entry as overlapping the namespace:

```text
error[E0119]: [CGP-E005] `CachedApp` cannot wire `@app.core.user.UserGetterComponent.*` that is already set through `DefaultAppComponents`
```

A child namespace that rebinds the same path, `new CachedAppComponents: DefaultAppComponents`, fails
the same way. This is the
[namespace override conflict](../../../cgp/errors/wiring/namespace-override-conflict.md), and it
follows from the rule in [namespaces](../../../cgp/concepts/namespaces.md) that a key a namespace
binds is final. A context that needs a different getter must use a namespace other than
`DefaultAppComponents`, which is the limitation the release post's caveats section describes.

## What it demonstrates

- A custom namespace that inherits `DefaultNamespace` and binds providers at its paths; see
  [namespaces](../../../cgp/concepts/namespaces.md).
- Defaults registered two ways: by `#[default_impl]` on a provider, and by a `cgp_namespace!` block
  for a composite provider.
- A context that wires only what the namespace leaves open; see the
  [namespaces and prefixes guide](../../../cgp/guides/namespaces-and-prefixes.md#limitations-why-default_impl-is-for-the-basic-case)
  for when this arrangement fits.

## Known issues

- **Unwired providers** — `DummyUserCensor` and `DummySpamMessageDetector`; see
  [issues.md](issues.md#housekeeping).

## Public material derived from this

The "Default implementations" and "Caveats with default implementations" sections of the
[v0.8.0 release post](../../../website/blog/v0-8-0-release.md).
