# JSON providers

The `cgp-serde-json` crate connects the serialization components to `serde_json` through CGP's
[`TryComputer`](../../../cgp/reference/components/try_computer.md) handler, so that encoding to and
decoding from JSON are themselves wireable, fallible operations that raise errors through the context's
[error handling](../../../cgp/concepts/modular-error-handling.md). It provides two `Code` types that
name the operations, three providers, and one convenience method. The crate is `no_std` and links `alloc`.

The providers are optional. A context can always serialize with `serde_json::to_string` and a
[`SerializeWithContext`](context-adapters.md#serializewithcontext), and deserialize by driving a
[`DeserializeWithContext`](context-adapters.md#deserializewithcontext) seed with a
`serde_json::Deserializer`. The providers add error conversion, the end-of-input check, and a place in
the context's wiring.

## `SerializeJson` and `DeserializeJson`

`SerializeJson` and `DeserializeJson<T>` are the `Code` types a context uses to key its
`TryComputerComponent` entries for JSON encoding and decoding.

### Definition

```rust
pub struct SerializeJson;

pub struct DeserializeJson<T>(pub PhantomData<T>);
```

Both live in `cgp_serde_json::code`.

### Behavior

They carry no data and exist to be matched on. `DeserializeJson<T>` names the target type, which
`DeserializeFromJsonReader` requires; `SerializeToJsonString` and `DeserializeFromJsonString` accept
any code, so `SerializeJson` is a convention rather than a requirement. A context opens the handler
component and keys on them:

```rust
delegate_components! {
    App {
        open {
            ValueSerializerComponent,
            ValueDeserializerComponent,
            TryComputerComponent,
        };

        ErrorTypeProviderComponent: UseAnyhowError,
        ErrorRaiserComponent: RaiseAnyhowError,

        // ... value serializer and deserializer entries ...

        @TryComputerComponent.SerializeJson:
            SerializeToJsonString,
        @TryComputerComponent.<T> DeserializeJson<T>:
            DeserializeFromJsonString,
    }
}
```

Callers then run `context.try_compute(PhantomData::<SerializeJson>, &value)` and
`context.try_compute(PhantomData::<DeserializeJson<Payload>>, &json)`, with `CanTryCompute` imported
from `cgp::extra::handler`.

## `SerializeToJsonString`

`SerializeToJsonString` serializes a value to a compact JSON string through the context.

### Definition

```rust
#[cgp_impl(new SerializeToJsonString)]
#[use_type(HasErrorType.Error)]
#[uses(CanSerializeValue<Value>, CanRaiseError<serde_json::Error>)]
impl<Code, Value> TryComputer<Code, &Value> {
    type Output = String;
    ...
}
```

### Behavior

The provider calls `serde_json::to_string` on the value wrapped in `SerializeWithContext`, so the output
is compact JSON shaped by the context's wiring, and a `serde_json::Error`, such as one a provider raised
with `Error::custom`, is converted into the context's error type with `raise_error`. It ignores its
`Code`.

### Context dependencies

`CanSerializeValue<Value>`, `HasErrorType`, and `CanRaiseError<serde_json::Error>`.

### Pairing

The deserializing counterparts are [`DeserializeFromJsonReader`](#deserializefromjsonreader) and
[`DeserializeFromJsonString`](#deserializefromjsonstring).

### Known issues

- **Only compact strings.** There is no pretty-printing provider and no provider that writes to an
  `io::Write`; both are available by calling `serde_json` with a `SerializeWithContext` directly.

## `DeserializeFromJsonReader`

`DeserializeFromJsonReader` deserializes a value from any `serde_json` reader through the context, and
checks that nothing follows the value.

### Definition

```rust
#[cgp_impl(new DeserializeFromJsonReader)]
#[use_type(HasErrorType.Error)]
#[uses(CanDeserializeValue<'de, Value>, CanRaiseError<serde_json::Error>)]
impl<Value, R, 'de> TryComputer<DeserializeJson<Value>, R>
where
    R: Read<'de>,
{
    type Output = Value;
    ...
}
```

`Read` is `serde_json::de::Read`, implemented by `serde_json`'s `StrRead`, `SliceRead`, and `IoRead`.

### Behavior

The provider builds a `serde_json::Deserializer` over the reader, deserializes the value through the
context, and calls `end` so that trailing input is an error: `"a" x` fails with
`trailing characters at line 1 column 5`. Every `serde_json` error is converted with `raise_error`.

It accepts any of `serde_json`'s readers, so a context can deserialize from a string, a byte slice, or
an `io::Read`, which the announcement post predates. The reader's `'de` lifetime flows through to
`CanDeserializeValue<'de, Value>`, so a borrowing reader such as `StrRead` can produce a value that
borrows from the input, such as a `&str`; an `IoRead` cannot lend its input, so borrowing values fail
there as they would in plain `serde_json`.

### Context dependencies

`CanDeserializeValue<'de, Value>`, `HasErrorType`, and `CanRaiseError<serde_json::Error>`.

### Pairing

The serializing counterpart is [`SerializeToJsonString`](#serializetojsonstring).

## `DeserializeFromJsonString`

`DeserializeFromJsonString<InDeserializer>` deserializes from anything that is a `str`, by wrapping it
in a `StrRead` and handing it to an inner provider.

### Definition

```rust
pub struct DeserializeFromJsonString<InDeserializer = DeserializeFromJsonReader>(
    pub PhantomData<InDeserializer>,
);

#[cgp_impl(DeserializeFromJsonString<InDeserializer>)]
#[use_type(HasErrorType.Error)]
impl<Code, Value, S, InDeserializer> TryComputer<Code, S>
where
    InDeserializer: for<'a> TryComputer<Self, Code, StrRead<'a>, Output = Value>,
    S: AsRef<str>,
{
    type Output = Value;
    ...
}
```

### Behavior

The provider is a small [higher-order provider](../../../cgp/concepts/higher-order-providers.md) over
the reader provider: it accepts a `String`, a `&str`, or any `AsRef<str>`, and delegates to
`InDeserializer`, which defaults to `DeserializeFromJsonReader`. Its bound on the inner provider holds
for every lifetime of the `StrRead`, so the output type cannot depend on the input's lifetime, and a
value that borrows from the input string cannot be produced this way. Values that borrow from elsewhere
are unaffected: the arena example's `Cluster<'a>` borrows from the context's arena, not from the input,
and deserializes through this provider.

### Context dependencies

Whatever `InDeserializer` requires; for the default, `CanDeserializeValue<'de, Value>` for every `'de`,
`HasErrorType`, and `CanRaiseError<serde_json::Error>`.

### Pairing

The serializing counterpart is [`SerializeToJsonString`](#serializetojsonstring).

## `CanDeserializeJsonString`

`CanDeserializeJsonString<T>` is a blanket trait that gives any suitably wired context a
`deserialize_json_string` method.

### Definition

```rust
#[cgp_fn(CanDeserializeJsonString)]
#[use_type(HasErrorType.Error)]
pub fn deserialize_json_string<T>(&self, serialized: &str) -> Result<T, Error>
where
    DeserializeFromJsonString: for<'a> TryComputer<Self, DeserializeJson<T>, &'a str, Output = T>,
{ ... }
```

It lives in `cgp_serde_json::impls`.

### Behavior

[`#[cgp_fn]`](../../../cgp/reference/macros/cgp_fn.md) turns the function into the trait
`CanDeserializeJsonString<T>`, moving the generic `T` onto the trait. The method therefore takes no
turbofish: `app.deserialize_json_string::<Cluster>(json)` fails to compile with "method takes 0 generic
arguments", and the target type is given by annotating the result instead, as in
`let cluster: Cluster<'_> = app.deserialize_json_string(json)?;`.

The function calls `DeserializeFromJsonString` directly rather than through the context's
`TryComputerComponent`, so a context needs no handler wiring to use it, only value deserializers for
the types involved and its error components. Because it goes through `DeserializeFromJsonString`, it
shares that provider's restriction: the result cannot borrow from the input string.

### Context dependencies

`HasErrorType`, `CanRaiseError<serde_json::Error>`, and `CanDeserializeValue<'de, T>` for every `'de`.
A context that omits the error components does not get the method, and the compiler reports only that
`deserialize_json_string` exists but its trait bounds were not satisfied, as `E0599`, without naming
the missing component. That is the hidden-cause shape the error catalog records as an
[unsatisfied dependency](../../../cgp/errors/hidden/unsatisfied-dependency.md).

### Pairing

No serializing counterpart. Serializing to a string is done with `SerializeToJsonString` through
`try_compute`, or with `serde_json::to_string` and a `SerializeWithContext`.

### Known issues

- **There is no serializing convenience method.** The crate is asymmetric: deserialization has a method
  on the context, serialization does not.
- **Missing error wiring is reported without its cause.** See context dependencies above.

## Source

- [`crates/cgp-serde-json/src/code/`](https://github.com/contextgeneric/cgp-serde/tree/v0.8.0/crates/cgp-serde-json/src/code) — `SerializeJson` and `DeserializeJson`.
- [`crates/cgp-serde-json/src/providers/to_string.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-json/src/providers/to_string.rs) — `SerializeToJsonString`.
- [`crates/cgp-serde-json/src/providers/from_reader.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-json/src/providers/from_reader.rs) — `DeserializeFromJsonReader`.
- [`crates/cgp-serde-json/src/providers/from_str.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-json/src/providers/from_str.rs) — `DeserializeFromJsonString`.
- [`crates/cgp-serde-json/src/impls/deserialize.rs`](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-json/src/impls/deserialize.rs) — `CanDeserializeJsonString`.

## Public material derived from this

The "Wiring an application" and "Arena-allocating deserialization" pages of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), and the rustdoc for the crate.
