# Shell-scripting DSL

This example builds on [Hypershell](../projects/hypershell/README.md), a type-level shell-scripting
DSL whose programs are ordinary Rust *types* interpreted at compile time by whichever context runs
them. It progresses from a fixed CLI program, through the component that interprets a program and the
three layers of wiring that assemble the language, to a custom context that supplies runtime values
and an extension that adds new syntax and a new error type. It is a template for any embedded DSL
where the program's *syntax* should be decoupled from its *semantics* so each can vary independently.
The general pattern is described in [type-level DSLs](../cgp/concepts/type-level-dsls.md).

The contexts here are **environmental contexts**: `HypershellCli`, `MyApp`, and `ExtendedApp` exist to
carry the wiring and a few runtime values, holding no program data. The handler components are
**parameter-targeted**, with the program arriving as a type-level `Code` selector and its data as the
`Input`, and the wiring dispatches on both. See the
[modularity hierarchy](../cgp/concepts/modularity-hierarchy.md) for what that arrangement buys.

The snippets use the Hypershell crates at their
[`v0.8.0` branch](https://github.com/contextgeneric/hypershell/tree/v0.8.0): `hypershell`,
`hypershell-components`, `hypershell-tokio-components`, and `hypershell-hash-components`, plus `hex`,
`sha2`, `tokio`, and `cgp-error-anyhow`. Every snippet was compiled and run against that branch in
one crate. All snippets assume `use hypershell::prelude::*;`, which re-exports `cgp::prelude::*`,
and the handler items come from `cgp::extra::handler`. The project's own mechanics are documented in
[projects/hypershell/](../projects/hypershell/README.md), and this example links there rather than
re-explaining them.

The concepts each step demonstrates are documented in full in the reference; this example only notes
which one is in play and links to it:

- the computation component the DSL is built on — [`Handler` / `CanHandle`](../cgp/reference/components/handler.md) in the [handler family](../cgp/concepts/handlers.md)
- writing a provider that interprets one syntax — [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md) with [`#[uses]`](../cgp/reference/attributes/uses.md) and [`#[use_type]`](../cgp/reference/attributes/use_type.md)
- raising source errors into the context's abstract error — [`CanRaiseError`](../cgp/reference/components/can_raise_error.md)
- dispatching on the program and on the input — the `open` statement of [`delegate_components!`](../cgp/reference/macros/delegate_components.md) and [`RedirectLookup`](../cgp/reference/providers/redirect_lookup.md)
- bundling wiring into a reusable provider — [aggregate providers](../cgp/concepts/aggregate-providers.md)
- routing the language and inheriting it — [namespaces](../cgp/concepts/namespaces.md) with [`cgp_namespace!`](../cgp/reference/macros/cgp_namespace.md) and [`#[prefix]`](../cgp/reference/attributes/prefix.md)
- composing handlers into a pipeline provider — [`PipeHandlers`](../cgp/reference/providers/handler_combinators.md)
- reading runtime values from the context — [`#[derive(HasField)]`](../cgp/reference/derives/derive_has_field.md)

## A program is a type

The smallest DSL program is a type, not a value. The `hypershell!` macro provides shell-like surface
syntax, a pipe operator and bracketed argument lists, that desugars into a chain of phantom-typed
syntax markers. This program runs `echo hello world!` and streams the result to standard output:

```rust
pub type Hello = hypershell! {
        SimpleExec<
            StaticArg<"echo">,
            WithStaticArgs["hello", "world!"],
        >
    |   StreamToStdout
};
```

The macro is sugar only. The `|` becomes a `Pipe<Product![...]>` of stages, the bracketed `[...]` a
`<Product![...]>` type-level list, and each string literal a `Symbol!` type-level string, since a
program lives entirely at the type level where a `&str` value cannot appear. The program is exactly
this plain type, which the compiler confirms is the same type:

```rust
pub type HelloExpanded = Pipe<Product![
    SimpleExec<
        StaticArg<Symbol!("echo")>,
        WithStaticArgs<Product![Symbol!("hello"), Symbol!("world!")]>,
    >,
    StreamToStdout,
]>;
```

The program carries no data; it describes *what* to do, and the *how* is supplied by the context that
runs it. The macro's rules and edges are in the
[Hypershell macro reference](../projects/hypershell/reference/macro.md).

## Running a program on a context

A context runs a program by calling `handle`, passing the program as a `PhantomData` type argument and
an input value. `HypershellCli` is a predefined empty context for programs that need no runtime values:

```rust
#[tokio::main]
async fn main() -> Result<(), Error> {
    HypershellCli
        .handle(PhantomData::<Hello>, Vec::new())
        .await?;

    Ok(())
}
```

The `Vec::new()` is the program's standard input, which `echo` ignores. Running it prints
`hello world!`.

## The component that interprets a program

Every stage of a program is interpreted by one component: CGP's
[`Handler`](../cgp/reference/components/handler.md), the async, fallible corner of the
[handler family](../cgp/concepts/handlers.md). Its consumer trait `CanHandle` is what `handle` above
resolves to:

```rust
#[async_trait]
#[cgp_component(Handler)]
#[prefix(@cgp.extra.handler in DefaultNamespace)]
#[derive_delegate(UseDelegate<Code>)]
#[derive_delegate(UseInputDelegate<Input>)]
#[use_type(HasErrorType.Error)]
pub trait CanHandle<Code, Input> {
    type Output;

    async fn handle(
        &self,
        _tag: PhantomData<Code>,
        input: Input,
    ) -> Result<Self::Output, Error>;
}
```

`Code` is the program fragment being interpreted, `Input` is the data flowing in (a process's standard
input, an HTTP body), and the associated `Output` is what the fragment produces. The phantom
`PhantomData<Code>` is how a *type* is passed where a value is expected: one context hosts a handler
for every fragment of the language, each keyed by a distinct `Code` type. Interpreting a program is
therefore resolving `CanHandle` for that type. The `#[prefix]` attribute registers the component under
the path `@cgp.extra.handler`, which is where the namespace below routes it.

## Abstract syntax, decoupled from its meaning

A syntax marker like `SimpleExec` is nothing but a phantom struct, with no interpreter attached:

```rust
pub struct SimpleExec<Path, Args>(pub PhantomData<(Path, Args)>);
```

This is the point of the design: how a program is *written* is decoupled from how it is
*interpreted*. `SimpleExec` names a piece of syntax; what it *does* is decided by which provider a
context wires for the `Code = SimpleExec<…>` case. The syntax is the DSL's abstract grammar, and the
providers are its interpreters. The kinds of syntax Hypershell has, including the argument
sub-language that `StaticArg` belongs to, are described in
[abstract syntax](../projects/hypershell/architecture/abstract-syntax.md).

## Interpreting one syntax with a provider

An interpreter is a `Handler` provider for one piece of syntax. Written with
[`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md), it reads like an ordinary method
implementation, with `self` as the context, while the context stays generic. This example adds a new
piece of syntax to the language, `DecodeHex`, and a provider that decodes a hexadecimal string into
bytes:

```rust
pub struct DecodeHex;

#[cgp_impl(new HandleDecodeHex)]
#[uses(CanRaiseError<FromHexError>)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input>
where
    Input: AsRef<[u8]>,
{
    type Output = Vec<u8>;

    async fn handle(&self, _tag: PhantomData<Code>, input: Input) -> Result<Vec<u8>, Error> {
        hex::decode(input.as_ref().trim_ascii()).map_err(Self::raise_error)
    }
}
```

Two things make the provider reusable across contexts. It never names a concrete error type: the
[`#[uses(CanRaiseError<FromHexError>)]`](../cgp/reference/attributes/uses.md) import lets it convert
`hex`'s error into the context's own abstract error through
[`CanRaiseError`](../cgp/reference/components/can_raise_error.md), so a context using `anyhow`,
`eyre`, or its own error type reuses it unchanged. And it takes nothing from the `Code`, so it is
written for any `Code` and the wiring decides which syntax it answers for. Hypershell's own providers
usually match a syntax shape instead, as `HandleSimpleExec` does with
`Handler<SimpleExec<CommandPath, Args>, Input>`; see
[interpretation](../projects/hypershell/architecture/interpretation.md).

## Dispatching on the syntax and on the input

A single provider interprets one syntax, so something must route each `Code` to its interpreter.
Hypershell does this with [aggregate providers](../cgp/concepts/aggregate-providers.md), one per
backend crate, whose tables `open` the handler component and map each syntax to its provider with a
path key. This is an abridged view of the Tokio crate's bundle:

```rust
delegate_components! {
    new HypershellTokioProvider {
        open {
            HandlerComponent,
            CommandUpdaterComponent,
            // …
        };

        @HandlerComponent.<Path, Args> SimpleExec<Path, Args>:
            HandleSimpleExec,
        @HandlerComponent.<Path, Args> StreamingExec<Path, Args>:
            PipeHandlers<Product![
                HandleToTokioAsyncRead,
                HandleStreamingExec,
                WrapTokioAsyncRead,
            ]>,
        // …
    }
}
```

The keys are *types*, which is what lets an entry bind generic parameters like `Path` and `Args` and
match every use of `SimpleExec`. The `open` statement resolves the component through its
[`RedirectLookup`](../cgp/reference/providers/redirect_lookup.md), which appends *every* parameter of
`CanHandle<Code, Input>` to the path before looking it up. So a key that ends after the syntax matches
it with any input, and a key that continues with a second segment dispatches on the input as well.
The `StreamingExec` entry's first stage, `HandleToTokioAsyncRead`, is itself a bundle of such keys,
with a generic first segment so it ignores the syntax and converts whatever input arrives:

```rust
delegate_components! {
    new HandleToTokioAsyncRead {
        open HandlerComponent;

        @HandlerComponent.<Code> Code.<S> FuturesAsyncReadStream<S>:
            FuturesToTokioAsyncRead,
        @HandlerComponent.<Code> Code.<S> TokioAsyncReadStream<S>:
            ReturnInput,
        @HandlerComponent.<Code> Code.[Vec<u8>, String]:
            HandleBytesToTokioAsyncRead,
    }
}
```

This is why a streaming stage accepts bytes or either kind of stream without the program saying so;
see [streams and input dispatch](../projects/hypershell/architecture/streams-and-input-dispatch.md).
Wiring the `StreamingExec` entry to [`PipeHandlers`](../cgp/reference/providers/handler_combinators.md)
composes the three stages into one provider, threading each one's output into the next.

## Assembling the language with a namespace

A real DSL has many syntaxes across several bundles, and several contexts that should share them. A
[namespace](../cgp/concepts/namespaces.md) captures the routing once. `HypershellNamespace` is defined
with [`cgp_namespace!`](../cgp/reference/macros/cgp_namespace.md), inheriting CGP's `DefaultNamespace`,
and routes each prefixed path to the bundle that serves it:

```rust
cgp_namespace! {
    new HypershellNamespace: DefaultNamespace {
        @cgp.core.error.ErrorTypeProviderComponent:
            UseAnyhowError,

        @cgp.extra.handler.HandlerComponent.[
            <Path, Args> SimpleExec<Path, Args>,
            <Path, Args> StreamingExec<Path, Args>,
            StreamToStdout,
            // … every Tokio syntax
        ]:
            HypershellTokioProvider,

        @cgp.extra.handler.HandlerComponent.[
            <Method, Url, Headers> SimpleHttpRequest<Method, Url, Headers>,
            <Method, Url, Headers> StreamingHttpRequest<Method, Url, Headers>,
            // …
        ]:
            HypershellReqwestProvider,
        // … the error raisers, the argument extractors, and the other bundles
    }
}
```

Each key is a *path*, written with the `@` sigil, that begins with the prefix the component registered
through `#[prefix]`. The array form groups several `Code` keys that share one bundle. The language is
thus assembled in three layers: bundles that map syntax to providers, a namespace that routes syntax
to bundles, and contexts that join the namespace. The whole route table is in the
[Hypershell namespace reference](../projects/hypershell/reference/contexts-and-namespace.md), and one
lookup is traced through all three layers in
[assembly](../projects/hypershell/architecture/assembly.md#one-lookup-end-to-end).

## Running on a custom context

A program that reads runtime values, a URL or a name, needs a context that carries them. Deriving
[`HasField`](../cgp/reference/derives/derive_has_field.md) exposes a struct's fields so that argument
syntax like `FieldArg<"name">` can read them, and joining `HypershellNamespace` inside
[`delegate_components!`](../cgp/reference/macros/delegate_components.md) inherits the whole language:

```rust
use hypershell::namespaces::HypershellNamespace;

pub type Greet = hypershell! {
        SimpleExec<
            StaticArg<"echo">,
            WithArgs[
                StaticArg<"Hello,">,
                FieldArg<"name">,
            ],
        >
    |   StreamToStdout
};

#[derive(HasField)]
pub struct MyApp {
    pub name: String,
}

delegate_components! {
    MyApp {
        namespace HypershellNamespace;
    }
}
```

The `namespace HypershellNamespace;` statement makes every lookup `MyApp` does not wire directly fall
back to the namespace, so `MyApp` interprets the full DSL without restating any wiring. `WithArgs`
mixes a static argument with `FieldArg<"name">`, which resolves through `HasField` to the context's
`name` field. Running `Greet` on `MyApp { name: "Alice".into() }` prints `Hello, Alice`.
`HypershellCli` is wired the same way with an empty struct.

## Extending the language

A language extension adds syntax and its interpreters without forking the core. It needs a bundle that
maps the new syntax to providers and a namespace that inherits `HypershellNamespace` and routes the new
syntax to the bundle. This extension adds the `DecodeHex` syntax from earlier, together with the
`Checksum<Hasher>` and `BytesToHex` syntax and providers that the `hypershell-hash-components` crate
ships without a bundle:

```rust
use cgp::core::error::ErrorRaiserComponent;
use cgp_error_anyhow::RaiseAnyhowError;
use hex::FromHexError;
use hypershell_hash_components::dsl::{BytesToHex, Checksum};
use hypershell_hash_components::providers::{HandleBytesToHex, HandleStreamChecksum};
use hypershell_tokio_components::providers::HandleToFuturesStream;

delegate_components! {
    new MyExtensionProvider {
        open HandlerComponent;

        @HandlerComponent.DecodeHex:
            HandleDecodeHex,
        @HandlerComponent.<Hasher> Checksum<Hasher>:
            PipeHandlers<Product![
                HandleToFuturesStream,
                HandleStreamChecksum,
            ]>,
        @HandlerComponent.BytesToHex:
            HandleBytesToHex,
    }
}

cgp_namespace! {
    new MyNamespace: HypershellNamespace {
        @cgp.core.error.ErrorRaiserComponent.FromHexError:
            RaiseAnyhowError,

        @cgp.extra.handler.HandlerComponent.[
            DecodeHex,
            <Hasher> Checksum<Hasher>,
            BytesToHex,
        ]:
            MyExtensionProvider,
    }
}
```

The `Checksum` entry wires a pipeline rather than a single provider: `HandleToFuturesStream` adapts
whatever input arrives into the `TryStream` that `HandleStreamChecksum` folds into a digest. The
namespace also routes the new error type, `FromHexError`, to
[`RaiseAnyhowError`](../projects/error/cgp-error-anyhow/reference.md#raiseanyhowerror), since
`HypershellNamespace` knows only the error types its own providers raise; the route's path names
`ErrorRaiserComponent`, which must therefore be imported. A context joins the extended language by
naming the new namespace:

```rust
pub type Decode = hypershell! {
        SimpleExec<
            StaticArg<"echo">,
            WithStaticArgs["68656c6c6f2c20776f726c6421"],
        >
    |   DecodeHex
    |   StreamToStdout
};

pub type FileChecksum = hypershell! {
        ReadFile<FieldArg<"path">>
    |   Checksum<Sha256>
    |   BytesToHex
    |   StreamToStdout
};

#[derive(HasField)]
pub struct ExtendedApp {
    pub path: String,
}

delegate_components! {
    ExtendedApp {
        namespace MyNamespace;
    }
}

check_components! {
    #[check_trait(CheckExtendedApp)]
    ExtendedApp {
        HandlerComponent: [
            (Decode, Vec<u8>),
            (FileChecksum, ()),
        ],
    }
}
```

`Decode` prints `hello, world!`, and an invalid string such as `xyz` fails with the raised
`Odd number of digits`. `FileChecksum` takes `()` as its input, since `ReadFile` starts the program,
and prints the same digest `sha256sum` does. The
[`check_components!`](../cgp/reference/macros/check_components.md) block asserts, at the definition,
that `ExtendedApp` can run both programs with their inputs, so a missing route fails there with a root
cause rather than at the call. The only change a context makes to speak the extended language is the
namespace name, and the whole resolution is settled at compile time.

One kind of extension this approach does not allow is rebinding a syntax the inherited namespace
already binds, such as giving `SimpleExec` a different provider; the new entry conflicts with the
inherited one. The alternatives are in
[extending the language](../projects/hypershell/guides/extending-the-language.md#replace-the-interpretation-of-existing-syntax).
