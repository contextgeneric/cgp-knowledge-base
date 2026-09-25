# Abstract syntax

A Hypershell program is an ordinary Rust type assembled from empty marker structs, and that
decision is what lets the same program run differently under different contexts. This document
describes the kinds of syntax the language has, how they nest, and the `hypershell!` macro that sits
on top of them. The per-item detail is in the [reference](../reference/README.md); the general
technique is [type-level DSLs](../../../cgp/concepts/type-level-dsls.md).

## Every piece of syntax is an empty marker

**Each syntax type is a struct holding only `PhantomData` over its parameters, with no methods and
no trait impls.** The definitions in
[`hypershell-components/src/dsl/`](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-components/src/dsl)
are all of this shape:

```rust
pub struct SimpleExec<Path, Args>(pub PhantomData<(Path, Args)>);

pub struct StreamingHttpRequest<Method, Url, Params>(pub PhantomData<(Method, Url, Params)>);

pub struct StreamToStdout;
```

A syntax type's parameters are themselves syntax: `Path` is an argument expression, `Args` an
argument list, `Method` a method marker. So a program is one large type, and nothing in it describes
how any part behaves. The meaning comes from the provider a context wires for each shape, described
in [interpretation.md](interpretation.md). Swapping that provider changes what every program using
the shape does, without editing any program.

A program is also never instantiated. It reaches a context as `PhantomData::<Program>`, the `Code`
argument of `handle`, and the only runtime value that flows is the program's input.

## Four kinds of syntax

The syntax types fall into four groups. The groups differ in which component interprets them, which
is why the distinction matters when adding syntax.

**Handler syntax is a pipeline stage**, interpreted by the `Handler` component. It takes an input and
produces an output: `SimpleExec` and `StreamingExec` run a command, `SimpleHttpRequest` and
`StreamingHttpRequest` send a request, `ReadFile` and `WriteFile` touch the file system,
`EncodeJson` and `DecodeJson<T>` convert JSON, and the stream conversions (`StreamToBytes`,
`StreamToString`, `StreamToStdout`, `BytesToString`, `BytesToStream`, `StreamToLines`) adapt one
stage's output into another stage's input. The extension crates add `Checksum<Hasher>`, `BytesToHex`,
and `WebSocket<Url, Params>`.

**Argument syntax is an expression that produces a string, a path, a URL, or a method**, interpreted
by one of four extractor components rather than by `Handler`. It is a small language inside the
handler syntax:

- `StaticArg<Arg>` — a literal, usually a `Symbol!`, formatted through `Default` and `Display`.
- `FieldArg<Tag>` — the value of the context field named `Tag`, read through
  [`HasField`](../../../cgp/reference/traits/has_field.md). This is how a program reads a runtime
  value it cannot hold itself.
- `JoinArgs<Args>` — a `Product!` list of arguments joined into one. What "joined" means depends on
  the extractor: concatenation for a string or URL, `PathBuf::join` for a command path.
- `UrlEncodeArg<Arg>` — an argument percent-encoded for a URL query.
- `GetMethod`, `PostMethod`, `PutMethod`, `DeleteMethod` — HTTP method markers.

**Argument-list syntax configures a process or a request** rather than producing one value, and is
interpreted by an updater component: `WithArgs<Args>` appends each argument to a command,
`FieldArgs<Tag>` appends every item of an iterable field, and `WithHeaders<Headers>` with
`Header<Key, Value>` sets request headers. `WithStaticArgs<Args>` is not a struct but a type alias
that wraps each element of a list in `StaticArg`, through the `WrapStaticArg` trait, so
`WithStaticArgs<Product!["-l"]>` is exactly `WithArgs<Product![StaticArg<"-l">]>`.

**Control syntax composes other programs.** `Pipe<Handlers>` threads a list of stages end to end.
`Use<Provider, Code>` runs a named provider inline, bypassing the context's wiring for that stage.
`ConvertTo<T>` converts its input with `Into`. And `Box<Code>`, the standard `Box` used as syntax,
runs `Code` behind a boxed future; see [interpretation.md](interpretation.md#control-syntax).

## Internal syntax that users never write

**Two backend crates define "core" syntax that exists only so a provider can delegate a shared step
back to the context.** `CoreExec<Path, Args>` in `hypershell-tokio-components` spawns a configured
child process, and `CoreHttpRequest<Method, Url, Params>` in `hypershell-reqwest-components` builds
and sends a request. The user-facing `SimpleExec` and `StreamingExec` both call `CoreExec`, and both
HTTP syntaxes call `CoreHttpRequest`, through the context:

```rust
let mut child = context.handle(PhantomData::<CoreExec<CommandPath, Args>>, ()).await?;
```

Making the shared step a piece of syntax, rather than a helper function, means a context can rewire
it. A context that wants every command spawned differently replaces the `CoreExec` provider once, and
both execution syntaxes follow. The namespace routes both core syntaxes like any other, so they can
also be written in a program, though nothing documents them for that use.

## The surface syntax

**`hypershell!` rewrites tokens and emits the plain type a programmer could write by hand.** Its
three rules are that a top-level `|` builds a `Pipe<Product![…]>`, that a bracketed list immediately
after an identifier becomes `<Product![…]>`, and that a string literal becomes `Symbol!("…")`. The
hello-world program

```rust
pub type Program = hypershell! {
        SimpleExec<
            StaticArg<"echo">,
            WithStaticArgs["hello", "world!"],
        >
    |   StreamToStdout
};
```

is exactly this type:

```rust
pub type Program = Pipe<Product![
    SimpleExec<
        StaticArg<Symbol!("echo")>,
        WithStaticArgs<Product![Symbol!("hello"), Symbol!("world!")]>,
    >,
    StreamToStdout,
]>;
```

The rules apply recursively inside every group, so a `|` inside angle brackets builds a nested
`Pipe`, which is how the examples write a sub-pipeline as a type argument. The macro has sharp edges.
It emits `Pipe`, `Product!`, and `Symbol!` unqualified, it panics rather than reporting an error on
an unbalanced `<`, and a `|` splits at the token level, so it flattens a comma list around it. The
exact rules and those edges are in [the macro reference](../reference/macro.md).

Keeping the macro this thin is deliberate. The language remains fully usable without it, an extension
adds syntax without touching it, and it never needs to know what a piece of syntax means.

## Source

- The syntax types: [crates/hypershell-components/src/dsl/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-components/src/dsl)
- `WrapStaticArg`: [crates/hypershell-components/src/traits/wrap_static_arg.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/traits/wrap_static_arg.rs)
- The core syntax: [crates/hypershell-tokio-components/src/dsl/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-tokio-components/src/dsl) and [crates/hypershell-reqwest-components/src/dsl/mod.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-reqwest-components/src/dsl/mod.rs)
- The macro: [crates/hypershell-macro/src/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-macro/src)

## Public material derived from this

Page 1, "Programs as types", of the planned [Hypershell deep dive](../../../website/deep-dives/hypershell.md).
