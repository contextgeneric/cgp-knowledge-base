# JSON

The JSON family converts between Rust values and JSON bytes inside a pipeline, with `serde_json`. It
is the smallest backend crate, `hypershell-json-components`, which is `no_std` with `alloc`.

## `EncodeJson` and `HandleEncodeJson`

`EncodeJson` serializes its input to JSON bytes.

### Definition

```rust
pub struct EncodeJson;

#[cgp_impl(new HandleEncodeJson)]
impl<Context, Code, Input> Handler<Code, Input> for Context
where
    Context: CanRaiseError<serde_json::Error>,
    Input: Serialize,
{
    type Output = Vec<u8>;
    // ...
}
```

### Behavior

The provider calls `serde_json::to_vec`, raising `serde_json::Error`. It ignores the `Code`, so it
answers for whatever syntax a bundle routes to it. Because the input is any `Serialize` value, a
program that starts with `EncodeJson` is called with a Rust value, as in the `rust_playground`
example, which passes a `Request` struct.

## `DecodeJson` and `HandleDecodeJson`

`DecodeJson<T>` deserializes its input bytes into `T`.

### Definition

```rust
pub struct DecodeJson<T>(pub PhantomData<T>);

#[cgp_impl(new HandleDecodeJson)]
impl<Context, Input, Output> Handler<DecodeJson<Output>, Input> for Context
where
    Context: CanRaiseError<serde_json::Error>,
    Input: AsRef<[u8]>,
    Output: DeserializeOwned,
{
    type Output = Output;
    // ...
}
```

### Behavior

The provider calls `serde_json::from_slice`, raising `serde_json::Error`. The target type is named
in the program, so a program ending in `DecodeJson<Vec<Issue>>` has `Vec<Issue>` as its output. The
input must be bytes, so a streaming stage needs `StreamToBytes` before it. A probe round-tripped a
struct through `EncodeJson | DecodeJson<Msg>`.

## `HypershellJsonProvider`

The crate's bundle maps `EncodeJson` to `HandleEncodeJson` and `DecodeJson<Value>` to
`HandleDecodeJson` under an `open HandlerComponent`, and `HypershellNamespace` routes both to it.
`serde_json::Error` is raised with `RaiseAnyhowError` through the namespace's error aggregate.

## Source

- [crates/hypershell-components/src/dsl/json.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-components/src/dsl/json.rs)
- [crates/hypershell-json-components/src/providers/](https://github.com/contextgeneric/hypershell/tree/v0.8.0/crates/hypershell-json-components/src/providers)

## Public material derived from this

Rustdoc for the JSON items.
