# Arguments

The argument family is the small expression language inside Hypershell's syntax: literals, context
fields, joined segments, and URL-encoded values, each interpreted by an extractor component rather
than by `Handler`. Three extractors produce a string, a command argument, and a URL; the fourth, for
HTTP methods, is in [http.md](http.md). The components and most providers are in
`hypershell-components`, with `JoinExtractArgs` in the Tokio crate and `UrlEncodeStringArg` in the
reqwest crate. The design is in [interpretation](../architecture/interpretation.md#arguments-have-their-own-components).

## `CanExtractStringArg` and `StringArgExtractor`

`CanExtractStringArg<Arg>` is the base extractor: it turns an argument syntax into a string.

### Definition

```rust
#[cgp_component(StringArgExtractor)]
#[prefix(@hypershell.core in DefaultNamespace)]
#[derive_delegate(UseDelegate<Arg>)]
pub trait CanExtractStringArg<Arg> {
    fn extract_string_arg(&self, _phantom: PhantomData<Arg>) -> Cow<'_, str>;
}
```

### Behavior

The method is synchronous and infallible, and returns a `Cow` so a provider may borrow from the
context. Every provider in the repository returns an owned string. The component is used directly
for header keys and values and for WebSocket URLs, and indirectly by the command and URL extractors
below. It is registered at `@hypershell.core.StringArgExtractorComponent`.

## `CanExtractCommandArg` and `HasCommandArgType`

`CanExtractCommandArg<Arg>` turns an argument syntax into the context's abstract command-argument
type, used for command paths, command arguments, and file paths.

### Definition

```rust
#[cgp_type]
#[prefix(@hypershell.core in DefaultNamespace)]
pub trait HasCommandArgType {
    type CommandArg;
}

#[cgp_component(CommandArgExtractor)]
#[prefix(@hypershell.core in DefaultNamespace)]
#[derive_delegate(UseDelegate<Arg>)]
pub trait CanExtractCommandArg<Arg>: HasCommandArgType {
    fn extract_command_arg(&self, _phantom: PhantomData<Arg>) -> Self::CommandArg;
}
```

### Behavior

The extractor is infallible. The Tokio bundle fixes `CommandArg` to `PathBuf` with `UseType`, and
every consumer bounds it as `AsRef<OsStr>` or `AsRef<Path>`. The components are registered at
`@hypershell.core.CommandArgTypeProviderComponent` and `@hypershell.core.CommandArgExtractorComponent`.

## `CanExtractUrlArg` and `HasUrlType`

`CanExtractUrlArg<Arg>` turns an argument syntax into the context's abstract URL type, and can fail.

### Definition

```rust
#[cgp_type]
#[prefix(@hypershell.core in DefaultNamespace)]
pub trait HasUrlType {
    type Url;
}

#[cgp_component(UrlArgExtractor)]
#[prefix(@hypershell.core in DefaultNamespace)]
#[derive_delegate(UseDelegate<Arg>)]
pub trait CanExtractUrlArg<Arg>: HasUrlType + HasErrorType {
    fn extract_url_arg(&self, _phantom: PhantomData<Arg>) -> Result<Self::Url, Self::Error>;
}
```

### Behavior

The reqwest bundle fixes `Url` to `url::Url`. The extractor returns the context's error, so a URL
that does not parse reports through the error type; a probe with `StaticArg<"not a url">` failed
with `relative URL without a base`.

## `StaticArg` and `ExtractStaticArg`

`StaticArg<Arg>` is a literal argument, normally a `Symbol!` written as a string in `hypershell!`.

### Definition

```rust
pub struct StaticArg<Arg>(pub PhantomData<Arg>);

#[cgp_impl(new ExtractStaticArg)]
impl<Context, Arg> StringArgExtractor<StaticArg<Arg>> for Context
where
    Arg: Default + Display,
{ ... }
```

### Behavior

The provider constructs `Arg::default()` and formats it with `Display`. `Symbol!` types implement
both, producing their string, and any other type that does is accepted as well. The provider needs
nothing from the context.

## `FieldArg` and `ExtractFieldArg`

`FieldArg<Tag>` is the value of the context field named `Tag`, and is how a program reads a runtime
value.

### Definition

```rust
pub struct FieldArg<Tag>(pub PhantomData<Tag>);

#[cgp_impl(new ExtractFieldArg)]
impl<Context, Tag> StringArgExtractor<FieldArg<Tag>> for Context
where
    Context: HasField<Tag, Value: Display>,
{ ... }
```

### Behavior

The provider reads the field through [`HasField`](../../../cgp/reference/traits/has_field.md) and
formats it with `Display`, so the field may be a `String` or any displayable value. The field name is
chosen by the program, not by the provider, which is why this read cannot be an
[`#[implicit]`](../../../cgp/reference/attributes/implicit.md) argument. A context missing the
field fails to compile; through a check, `cargo cgp check` reports a `[CGP-E106]` root cause,
"missing field `name` on `HypershellCli`".

### Context dependencies

`HasField<Tag>` with a `Display` value, usually from `#[derive(HasField)]`.

## `JoinArgs`, `JoinStringArgs`, and `JoinExtractArgs`

`JoinArgs<Args>` joins a `Product!` list of arguments into one, with a meaning that depends on the
extractor asked for it.

### Definition

```rust
pub struct JoinArgs<Args>(pub PhantomData<Args>);

pub struct JoinStringArgs;

#[cgp_impl(JoinStringArgs)]
impl<Context, Arg, Args> StringArgExtractor<JoinArgs<Cons<Arg, Args>>> for Context
where
    Context: CanExtractStringArg<Arg>,
    JoinStringArgs: StringArgExtractor<Context, JoinArgs<Args>>,
{ ... }

#[cgp_impl(JoinStringArgs)]
impl<Context> StringArgExtractor<JoinArgs<Nil>> for Context { ... }

pub struct JoinExtractArgs;

#[cgp_impl(JoinExtractArgs)]
impl<Context, Arg, Args> CommandArgExtractor<JoinArgs<Cons<Arg, Args>>> for Context
where
    Context: CanExtractCommandArg<Arg> + HasCommandArgType<CommandArg = PathBuf>,
    JoinExtractArgs: CommandArgExtractor<Context, JoinArgs<Args>>,
{ ... }

#[cgp_impl(JoinExtractArgs)]
impl<Context> CommandArgExtractor<JoinArgs<Nil>> for Context
where
    Context: HasCommandArgType<CommandArg = PathBuf>,
{ ... }
```

### Behavior

As a string or a URL, `JoinArgs` concatenates the elements with no separator, which is how the
`github_issues` example builds a URL from a base, literal path pieces, and encoded fields. As a
command argument, it joins the elements with `PathBuf::join`, skipping an empty tail, so
`JoinArgs[FieldArg<"base_dir">, StaticArg<"Cargo.toml">]` yields `base_dir/Cargo.toml`.
`JoinExtractArgs` requires `CommandArg = PathBuf` exactly, so it is tied to the Tokio bundle's type
choice.

### Context dependencies

The corresponding extractor for each element.

## `UrlEncodeArg` and `UrlEncodeStringArg`

`UrlEncodeArg<Arg>` percent-encodes another argument for a URL.

### Definition

```rust
pub struct UrlEncodeArg<Arg>(pub PhantomData<Arg>);

#[cgp_impl(new UrlEncodeStringArg)]
impl<Context, Arg> StringArgExtractor<UrlEncodeArg<Arg>> for Context
where
    Context: CanExtractStringArg<Arg>,
{ ... }
```

### Behavior

The inner argument is extracted as a string and encoded with `url::form_urlencoded::byte_serialize`,
which encodes a space as `+`, the form encoding, rather than `%20`. The provider lives in
`hypershell-reqwest-components`.

## `ExtractStringCommandArg`, `ExtractStringUrlArg`, and `ExtractUrlFieldArg`

These providers build the command and URL extractors from the string extractor, or from a typed field.

### Definition

```rust
#[cgp_impl(new ExtractStringCommandArg)]
impl<Context, Arg> CommandArgExtractor<Arg> for Context
where
    Context: HasCommandArgType + CanExtractStringArg<Arg>,
    Context::CommandArg: From<String>,
{ ... }

#[cgp_impl(new ExtractStringUrlArg)]
impl<Context, Arg> UrlArgExtractor<Arg> for Context
where
    Context: HasUrlType + CanExtractStringArg<Arg> + CanRaiseError<<Context::Url as FromStr>::Err>,
    Context::Url: FromStr,
{ ... }

#[cgp_impl(new ExtractUrlFieldArg)]
impl<Context, Tag> UrlArgExtractor<FieldArg<Tag>> for Context
where
    Context: HasUrlType + HasErrorType + HasField<Tag, Value = Context::Url>,
    Context::Url: Clone,
{ ... }
```

### Behavior

`ExtractStringCommandArg` extracts the argument as a string and converts it with `From<String>`.
`ExtractStringUrlArg` extracts a string and parses it, raising the parse error, which is
`url::ParseError` under the reqwest bundle. `ExtractUrlFieldArg` instead clones a field that already
holds a `Url`.

### Known issues

`ExtractUrlFieldArg` is wired nowhere, so a context cannot store a pre-parsed `Url` field without
adding its own entry; see [issues.md](../issues.md#defined-but-unrouted-providers).

## Wiring

`HypershellBaseProvider` maps `StaticArg`, `FieldArg`, and `JoinArgs` under the string extractor to
`ExtractStaticArg`, `ExtractFieldArg`, and `JoinStringArgs`; `StaticArg` and `FieldArg` under the
command extractor to `ExtractStringCommandArg`; and all three under the URL extractor to
`ExtractStringUrlArg`. `HypershellTokioProvider` maps `JoinArgs` under the command extractor to
`JoinExtractArgs`, and `HypershellReqwestProvider` maps `UrlEncodeArg` under the string extractor to
`UrlEncodeStringArg`. `HypershellNamespace` routes each of these paths under `@hypershell.core` to
the bundle that serves it.

The routing means an argument syntax works only in the extractors it is routed for. `UrlEncodeArg`
is routed for strings, so it works inside a `JoinArgs` that builds a URL, but not directly as a
command argument or a URL.

## Source

- [crates/hypershell-components/src/components/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-components/src/components)
- [crates/hypershell-components/src/dsl/arg.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/arg.rs) and [args.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/args.rs)
- [crates/hypershell-components/src/providers/string_arg.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/providers/string_arg.rs) and [url_arg.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/providers/url_arg.rs)
- [crates/hypershell-tokio-components/src/providers/join_args.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-tokio-components/src/providers/join_args.rs)
- [crates/hypershell-reqwest-components/src/providers/url_encode.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-reqwest-components/src/providers/url_encode.rs)

## Public material derived from this

Rustdoc for the argument items.
