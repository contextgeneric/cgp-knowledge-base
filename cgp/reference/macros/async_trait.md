# `#[async_trait]`

`#[async_trait]` rewrites each `async fn` declared in a trait into an ordinary method returning
`impl Future`, so a trait can declare async methods without triggering the `async_fn_in_trait` lint.

## Purpose

`#[async_trait]` lets a trait declare async methods in their natural form. A bare `async fn` in a
public trait definition compiles, but the compiler warns with the `async_fn_in_trait` lint, because
callers cannot name the auto-traits, such as `Send`, of the future it returns. The lint-clean
alternative, `fn name(&self) -> impl Future<Output = T>`, is verbose and hides the intent. The macro
lets the author write `async fn` and rewrites the declaration into the `impl Future` form.

The rewrite costs nothing at runtime. It is a plain desugaring to return-position `impl Trait` in
traits, with no boxing, no allocation, and no added `Send` bound, so the returned future is exactly
the one the method body produces. This makes `#[async_trait]` the standard way to write an async
method in a CGP trait, used alongside [`#[cgp_component]`](cgp_component.md) and
[`#[cgp_fn]`](cgp_fn.md).

## Syntax

`#[async_trait]` is an attribute on a trait definition and takes no arguments. Any tokens given as
an argument are ignored, so it is written bare:

```rust
#[async_trait]
pub trait CanFetchStorageObject {
    async fn fetch_storage_object(&self, object_id: &str) -> anyhow::Result<Vec<u8>>;
}
```

Only methods declared `async` change; other methods, associated types, and associated constants pass
through untouched.

### Stacking with other macros

Where `#[async_trait]` goes relative to a host macro depends on what that macro needs:

- **With `#[cgp_component]`**, the convention is to place `#[async_trait]` first, so it rewrites the
  trait before the component macro reads it. CGP's own async components are written this way.
  Placing it after `#[cgp_component]` also works, because the component macro forwards an
  unrecognized attribute onto every item it generates, as its
  [Known issues](cgp_component.md#known-issues) record. `#[async_trait]` then rewrites the consumer
  and provider traits and passes through the generated impls. The components of the
  [`transfer`](../../../projects/cgp-examples/transfer/reference/components.md) example crate use
  this order, below `#[cgp_component]` and `#[prefix]`, and build without the lint firing.
- **With `#[cgp_fn]`**, which builds the trait from a function, `#[async_trait]` goes below
  `#[cgp_fn]` on the `async fn`. `#[cgp_fn]` copies it onto the trait and the impl it generates.

The component form looks like this:

```rust
#[async_trait]
#[cgp_component(StorageObjectFetcher)]
pub trait CanFetchStorageObject {
    async fn fetch_storage_object(&self, object_id: &str) -> anyhow::Result<Vec<u8>>;
}
```

and the `#[cgp_fn]` form like this:

```rust
#[cgp_fn]
#[async_trait]
pub async fn fetch_storage_object(
    &self,
    #[implicit] storage_client: &Client,
    object_id: &str,
) -> anyhow::Result<Vec<u8>> {
    /* ... */
}
```

## Expansion

For each `async` method in the trait, `#[async_trait]` removes the `async` keyword and replaces the
return type `T` with `impl ::core::future::Future<Output = T>`. The trait above expands to:

```rust
pub trait CanFetchStorageObject {
    fn fetch_storage_object(
        &self,
        object_id: &str,
    ) -> impl ::core::future::Future<Output = anyhow::Result<Vec<u8>>>;
}
```

A method without a return type is treated as returning `()`:

```rust
// async fn run(&self);
fn run(&self) -> impl ::core::future::Future<Output = ()>;
```

### Items other than traits pass through

The macro rewrites only trait definitions and returns any other item, most importantly an `impl`
block, unchanged. This is what lets it compose with the macros that generate both a trait and its
impls. An `async fn` is already legal in an impl on stable Rust, and only a trait declaration
triggers the lint. So a provider keeps its natural `async fn` body while the trait carries the
rewritten signature, and the two agree because an `async fn` desugars to exactly such a
future-returning method.

[`#[cgp_fn]`](cgp_fn.md) shows the composition. Given an async `#[cgp_fn]` carrying
`#[async_trait]`, `#[cgp_fn]` first produces a trait and a blanket impl, and attaches
`#[async_trait]` to both:

```rust
#[async_trait]
pub trait FetchStorageObject {
    async fn fetch_storage_object(&self, object_id: &str) -> anyhow::Result<Vec<u8>>;
}

#[async_trait]
impl<__Context__> FetchStorageObject for __Context__
where
    Self: HasField<Symbol!("storage_client"), Value = Client>,
{
    async fn fetch_storage_object(&self, object_id: &str) -> anyhow::Result<Vec<u8>> {
        let storage_client: &Client =
            self.get_field(PhantomData::<Symbol!("storage_client")>);
        /* ... */
    }
}
```

`#[async_trait]` then runs on each item. On the trait it rewrites the declaration to
`fn fetch_storage_object(&self, object_id: &str) -> impl ::core::future::Future<Output = anyhow::Result<Vec<u8>>>`.
On the impl it does nothing, so the `async fn` body stays as written and satisfies the trait's
`impl Future` method.

## Examples

The most common use declares an async component. The consumer trait carries `#[async_trait]`, so its
method is an `impl Future` declaration, and each provider implements it with an ordinary `async fn`:

```rust
use cgp::prelude::*;

#[async_trait]
#[cgp_component(StorageObjectFetcher)]
pub trait CanFetchStorageObject {
    async fn fetch_storage_object(&self, object_id: &str) -> anyhow::Result<Vec<u8>>;
}

#[cgp_impl(new FetchS3Object)]
impl StorageObjectFetcher {
    async fn fetch_storage_object(
        &self,
        #[implicit] storage_client: &Client,
        #[implicit] bucket_id: &str,
        object_id: &str,
    ) -> anyhow::Result<Vec<u8>> {
        let output = storage_client
            .get_object()
            .bucket(bucket_id)
            .key(object_id)
            .send()
            .await?;

        Ok(output.body.collect().await?.into_bytes().to_vec())
    }
}
```

The same operation as a single implementation uses [`#[cgp_fn]`](cgp_fn.md) with `#[async_trait]`
directly below it, as Syntax shows. In both forms the author writes only `async fn`, and the macro
generates the lint-clean declaration.

## Related constructs

These constructs are the ones `#[async_trait]` is used with:

- [`#[cgp_component]`](cgp_component.md): builds the consumer and provider traits of an async
  component.
- [`#[cgp_fn]`](cgp_fn.md): generates an async trait and blanket impl from a function.
- [`#[cgp_impl]`](cgp_impl.md): writes providers for an async component with ordinary `async fn`
  bodies, which the macro's passthrough on impl blocks leaves alone.
- [`delegate_components!`](delegate_components.md) and [`check_components!`](check_components.md):
  treat an async component exactly like a synchronous one, since wiring is independent of asyncness.

## Known issues

An async trait method with a default body is mishandled, because `#[async_trait]` rewrites only the
signature. It strips `async` and changes the return type to `impl Future`, but leaves the body
verbatim instead of wrapping it in an `async { … }` block. The result is a non-async method whose
body returns a plain value and may use `.await`, which fails to compile. The case is rare, because
async trait methods are almost always declarations and providers supply the behavior, but a
default-bodied `async fn` in an `#[async_trait]` trait is not supported. A body returning a plain
`1` fails with ``E0277: `{integer}` is not a future``, which names the body's type rather than the
rewrite; wrap the body in an `async { … }` block by hand, or move it to a provider.

The generated future carries no `Send` bound. The rewrite produces a bare `impl Future<Output = T>`,
so the future is `Send` only when the concrete future happens to be, and the trait cannot require
it. Code that spawns the future on a multi-threaded executor, which demands `Send` futures, must
recover the bound by other means, as described in
[recovering `Send` bounds](../../concepts/send-bounds.md). The bound one would write,
Return Type Notation (`App: CanFetch<fetch(..): Send>`), is unstable, and stable Rust rejects it
with `E0658: return type notation is experimental`.

**The attribute arguments are discarded, so a typo'd option gives no feedback.**
`#[async_trait(anything)]` compiles exactly as `#[async_trait]` does, and on an `impl` block the
attribute is a no-op, which can wrongly suggest a provider needed it.

## Source

- Entry point: `async_trait` in
  [crates/macros/cgp-async-macro/src/lib.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-async-macro/src/lib.rs),
  a `#[proc_macro_attribute]` that discards its attribute arguments and forwards the annotated item
  to `impl_async`.
- Rewrite:
  [crates/macros/cgp-async-macro/src/impl_async.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-async-macro/src/impl_async.rs):
  it parses the item as a `syn::ItemTrait`, and on success replaces each `async` signature's output
  with `-> impl ::core::future::Future<Output = ...>` and clears the `async` keyword; an item that
  does not parse as a trait is returned unchanged.
- Prelude re-export:
  [crates/main/cgp-core/src/prelude.rs](https://github.com/contextgeneric/cgp/blob/main/crates/main/cgp-core/src/prelude.rs),
  so `use cgp::prelude::*;` brings it into scope.
- Internal walkthrough (the parse-or-passthrough structure, the signature rewrite, the default-body
  limitation, and the index of tests):
  [implementation/entrypoints/async_trait.md](../../implementation/entrypoints/async_trait.md).
