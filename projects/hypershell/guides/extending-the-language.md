# Extending the language

Hypershell is built so that anyone can extend its language without changing the core crates. This
guide covers each kind of extension: new handler syntax, new argument syntax, new control syntax, a
new error type, and a different interpretation of existing syntax, which is the one case the current
namespace makes awkward. The mechanisms are in [interpretation](../architecture/interpretation.md)
and [assembly](../architecture/assembly.md); the repository's own extensions are documented in
[examples](../examples/README.md).

## Add handler syntax

**A new pipeline stage needs a syntax type, a provider that matches it, a bundle entry, and a route.**
The hash crate is the worked case. Its syntax is an empty struct:

```rust
pub struct Checksum<Hasher>(pub PhantomData<Hasher>);
```

Its provider implements `Handler` for that shape, and declares what it needs from the context:

```rust
#[cgp_impl(new HandleStreamChecksum)]
#[uses(CanRaiseError<Input::Error>)]
#[use_type(HasErrorType.Error)]
impl<Input, Hasher> Handler<Checksum<Hasher>, Input>
where
    Input: Unpin + TryStream,
    Hasher: Digest,
    Input::Ok: AsRef<[u8]>,
{
    type Output = GenericArray<u8, Hasher::OutputSize>;

    async fn handle(&self, _tag: PhantomData<Checksum<Hasher>>, mut input: Input) -> Result<Self::Output, Error> {
        let mut hasher = Hasher::new();
        while let Some(bytes) = input.try_next().await.map_err(Self::raise_error)? {
            hasher.update(bytes);
        }
        Ok(hasher.finalize())
    }
}
```

The snippet uses the [`#[uses]`](../../../cgp/reference/attributes/uses.md) and
[`#[use_type]`](../../../cgp/reference/attributes/use_type.md) forms the
[writing-providers](../../../cgp/guides/writing-providers.md) guide recommends. The repository's own
copy states the same bound as `Context: CanRaiseError<Input::Error>` in the explicit form.

A bundle maps the syntax to the provider, putting an input dispatcher in front when the provider
accepts only one input kind. A namespace then routes the syntax to the bundle:

```rust
delegate_components! {
    new HypershellChecksumProvider {
        open HandlerComponent;

        @HandlerComponent.<Hasher> Checksum<Hasher>:
            PipeHandlers<Product![HandleToFuturesStream, HandleStreamChecksum]>,
        @HandlerComponent.BytesToHex:
            HandleBytesToHex,
    }
}

cgp_namespace! {
    new HypershellChecksumNamespace: HypershellNamespace {
        @cgp.extra.handler.HandlerComponent.[
            <Hasher> Checksum<Hasher>,
            BytesToHex,
        ]:
            HypershellChecksumProvider,
    }
}
```

A context joins the extended language by naming the new namespace; see
[`http_checksum_native`](../examples/http-checksum-native.md). Two rules keep an extension working:

- **List the syntax in both the bundle and the route.** Nothing connects the two, and a syntax
  missing from either is unreachable. `PutMethod`, `DeleteMethod`, and `StreamToLines` have providers
  but appear in neither list, which is why they fail to compile.
- **Put a dispatcher in front of a provider that accepts one input kind.** `HandleToTokioAsyncRead`
  and `HandleToFuturesStream` accept bytes and both reader wrappers, so the new stage chains after
  any existing one; see [streams and input dispatch](../architecture/streams-and-input-dispatch.md).

A provider that ignores the syntax, like `HandleBytesToHex`, which implements `Handler<Code, Input>`
for every `Code`, can be reused under any number of syntax types by adding entries.

## Add argument syntax

**A new argument expression needs a string-extractor provider, plus routes for every extractor that
should accept it.** An argument that produces a string works as a command argument and a URL through
the layered providers `ExtractStringCommandArg` and `ExtractStringUrlArg`, but only where it is
routed. `UrlEncodeArg` shows the cost of routing it in one place only: it is routed for the string
extractor alone, so it works inside a `JoinArgs` that builds a URL and nowhere else. Route a new
argument under `@hypershell.core.StringArgExtractorComponent`, and also under the command and URL
extractors when it should stand alone in those positions; see
[arguments](../reference/arguments.md#wiring).

## Add control syntax

**Syntax whose operands are whole programs needs a provider that calls back into the context for
each operand.** The examples library's `Compare` and `If` are the worked cases. `HandleIf` requires
`CanHandle` for each of its three sub-programs and awaits them in turn:

```rust
#[cgp_impl(new HandleIf)]
impl<Context, CodeCond, CodeThen, CodeElse, InputCond, InputBranch, Output>
    Handler<If<CodeCond, CodeThen, CodeElse>, (InputCond, InputBranch)> for Context
where
    Context: CanHandle<CodeCond, InputCond, Output = bool>
        + CanHandle<CodeThen, InputBranch, Output = Output>
        + CanHandle<CodeElse, InputBranch, Output = Output>,
{ /* … */ }
```

Because each operand is resolved through the context, any program the context can run may appear as
an operand, including another piece of control syntax. The operands' inputs are packed into the
syntax's own input, here a pair, so the caller shapes its input after the program. `Compare` shows
the concurrent variant, starting both operands and joining them. See
[the examples library](../examples/README.md#the-examples-library).

## Register a new error type

**A provider that raises an error type the namespace does not know needs a route for that type.**
Add it on the namespace or context that joins the extension. The `bluesky_websocket` example routes
the WebSocket crate's error beside its `namespace` statement:

```rust
@cgp.core.error.ErrorRaiserComponent.TungsteniteError:
    RaiseAnyhowError,
```

`RaiseAnyhowError` suits any type implementing `std::error::Error`, and `DebugAnyhowError` any type
with only `Debug`. The path names `ErrorRaiserComponent`, so it must be imported from
`cgp::core::error`. A missing route fails at the first provider that raises the type, as shown in
[debugging](debugging.md#a-raised-error-type-has-no-route). Details passed to `CanWrapError` need
nothing, since the namespace wraps every detail with `DebugAnyhowError`.

## Choose between an extension namespace and context entries

**Publish a namespace when several contexts share the extension, and add context entries for a single
context.** A namespace that inherits `HypershellNamespace` layers routes onto the whole language, and
namespaces chain: `HypershellCompareNamespace` inherits the checksum namespace, which inherits the
base. Context entries beside `namespace HypershellNamespace;` do the same for one context without a
new type. Either way, write the full prefixed path, since the `open` statement does not combine with a
joined namespace when the component carries a `#[prefix]`.

## Replace the interpretation of existing syntax

**A context or child namespace cannot rebind a syntax that `HypershellNamespace` already routes.** The
namespace binds each syntax path to a bundle, and a second binding for the same path conflicts with
the inherited one. Probes confirmed both forms fail with `E0119`: an entry for `SimpleExec` beside
`namespace HypershellNamespace;`, and the same entry in a namespace inheriting it. This is the
[namespace override conflict](../../../cgp/errors/wiring/namespace-override-conflict.md) class. Three
routes remain, and a probe confirmed the first two:

- **Choose the provider in the program with `Use`.** `Use<MyProvider, SimpleExec<…>>` runs
  `MyProvider` for that stage on any context. The choice then lives in the program rather than the
  context.
- **Write a namespace that inherits `DefaultNamespace` and lists its own routes.** It can route
  `SimpleExec` to a new provider and everything else to the existing bundles, at the cost of
  restating every route it keeps, including the error routes.
- **Add new syntax** with the new behavior instead of changing the old one.

Rebinding the core steps is where this bites hardest. `CoreExec` exists so that one entry can change
how every command is spawned, but that entry is bound by `HypershellNamespace` like any other. The
gap is recorded in [issues.md](../issues.md#missing-features).

## Public material derived from this

Page 4, "Extending the language", of the planned
[Hypershell deep dive](../../../website/deep-dives/hypershell.md).
