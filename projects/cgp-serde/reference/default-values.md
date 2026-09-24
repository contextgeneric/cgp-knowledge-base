# `DeserializeDefault`

`DeserializeDefault<Provider>` deserializes an optional value, producing the type's `Default` when the
input is null and delegating to an inner provider otherwise. It is the only
[higher-order provider](../../../cgp/concepts/higher-order-providers.md) among the serialization
providers, and the only one of them that delegates without re-entering the context.

## `DeserializeDefault`

`DeserializeDefault<Provider>` substitutes `Value::default()` for a null input and otherwise hands the
input to `Provider`.

### Definition

```rust
#[cgp_impl(new DeserializeDefault<Provider>)]
#[use_provider(Provider: ValueDeserializer<'a, Value>)]
impl<'a, Value, Provider> ValueDeserializer<'a, Value>
where
    Value: Default,
{ ... }
```

[`#[use_provider]`](../../../cgp/reference/attributes/use_provider.md) completes the inner bound to
`Provider: ValueDeserializer<'a, Self, Value>`. The private `DefaultVisitor` implements `visit_none`,
returning `Value::default()`, and `visit_some`, calling `Provider::deserialize(context, deserializer)`.

### Behavior

The provider asks the deserializer for an optional value. With JSON, `null` produces the default, so a
`u64` wired to `DeserializeDefault<UseSerde>` reads `null` as `0`, and any other input is passed to the
inner provider, so `7` reads as `7`. The inner provider handles the same `Value` type, and it is named
in the wiring rather than resolved through the context, because resolving `Value` through the context
would lead back to `DeserializeDefault` itself.

The provider handles a null value, not an absent one. A struct field wired to it still has to appear in
the input: [`DeserializeRecordFields`](records.md#deserializerecordfields) reports a missing field as
`missing field: d` before any field provider runs. The provider also has no default for its parameter,
so the inner provider must always be named.

### Context dependencies

None through the context. The inner `Provider` must implement `ValueDeserializer<'de, Context, Value>`
for the same context, and brings its own dependencies.

### Pairing

No serializing counterpart. Serializing writes the value itself, so a default value is written like any
other.

### Known issues

- **A missing field is not defaulted.** The provider cannot run for a field the input omits, so it does
  not provide the equivalent of Serde's `#[serde(default)]`; see the known issues of
  [`DeserializeRecordFields`](records.md#deserializerecordfields).

## Source

- [`crates/cgp-serde/src/providers/default.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde/src/providers/default.rs) — `DeserializeDefault` and `DefaultVisitor`.

## Public material derived from this

The rustdoc for `DeserializeDefault`, and the page on what the library does not do in the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md).
