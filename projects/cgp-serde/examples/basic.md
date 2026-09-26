# `basic`

One struct serialized to a JSON string and read back through the same context, showing a complete
round trip in which the struct derives only `CgpData` and its bytes are encoded as hex by wiring.

- **Source** — [crates/cgp-serde-tests/src/tests/basic.rs](https://github.com/contextgeneric/cgp-serde/blob/v0.8.0/crates/cgp-serde-tests/src/tests/basic.rs)
- **Run** — `cargo test -p cgp-serde-tests basic`
- **Needs** — nothing beyond the build
- **Result** — passes; asserts the exact JSON `{"quantity":42,"message":"hello","data":"010203"}` and
  that deserializing it gives back the original value

## A struct with no serialization derive

The data type derives `CgpData` and the standard comparison traits the assertions need, and nothing
from Serde:

```rust
#[derive(Debug, Eq, PartialEq, CgpData)]
pub struct Payload {
    pub quantity: u64,
    pub message: String,
    pub data: Vec<u8>,
}
```

`CgpData` exposes the field list and the builder that
[`SerializeFields` and `DeserializeRecordFields`](../reference/records.md) walk. Wired to those two
providers, the struct serializes as a JSON object keyed by its field names and is read back from one;
see [derive-free records](../architecture/derive-free-records.md).

## One context, both directions

`App` is a fieldless environmental context. It opens three components, and keys the two
serialization components on the value type, wiring a provider in each direction for the struct and for
each of its field types, which is everything the record providers re-enter the context for:

```rust
pub struct App;

delegate_components! {
    App {
        open {
            ValueSerializerComponent,
            ValueDeserializerComponent,
            TryComputerComponent,
        };
        // ... error entries ...

        @ValueSerializerComponent.u64: UseSerde,
        @ValueSerializerComponent.String: SerializeString,
        @ValueSerializerComponent.Vec<u8>: SerializeHex,
        @ValueSerializerComponent.Payload: SerializeFields,

        @ValueDeserializerComponent.[u64, String]: UseSerde,
        @ValueDeserializerComponent.Payload: DeserializeRecordFields,
        @ValueDeserializerComponent.Vec<u8>: SerializeHex,
        // ... JSON entries ...
    }
}
```

The two directions are wired separately and need not name the same provider. `String` is serialized by
`SerializeString` and deserialized by `UseSerde`, which write and read the same JSON string. `Vec<u8>`
names `SerializeHex` in both tables, because one struct implements both directions of the hex
encoding; see [component design](../architecture/component-design.md#one-struct-both-directions).

Changing the encoding is a wiring edit. With `Vec<u8>` wired to `SerializeBase64` in both tables, a probe
serialized the same value as `{"quantity":42,"message":"hello","data":"AQID"}` and read it back.

## JSON as operations on the context

The third opened component is CGP's [`TryComputer`](../../../cgp/reference/components/try_computer.md)
handler, keyed on the JSON [`Code` types](../reference/json.md#serializejson-and-deserializejson). Its
entries make encoding and decoding operations the context runs, and the error entries give those
operations an error type to raise into:

```rust
ErrorTypeProviderComponent: UseAnyhowError,
ErrorRaiserComponent: RaiseAnyhowError,

@TryComputerComponent.SerializeJson: SerializeToJsonString,
@TryComputerComponent.<T> DeserializeJson<T>: DeserializeFromJsonString,
```

The test then calls both through `try_compute`, with `CanTryCompute` imported from
`cgp::extra::handler`:

```rust
let serialized = context
    .try_compute(PhantomData::<SerializeJson>, &value)
    .unwrap();

let deserialized: Payload = context
    .try_compute(PhantomData::<DeserializeJson<Payload>>, &serialized)
    .unwrap();
```

In this handler the `Code` is a selector and the input is the target, per the
[modularity hierarchy](../../../cgp/concepts/modularity-hierarchy.md#what-actually-varies-the-context-and-the-target).
The generic `<T> DeserializeJson<T>` entry sends every target type to one provider, and the deserializing
call passes a `&String`, which [`DeserializeFromJsonString`](../reference/json.md#deserializefromjsonstring)
accepts because it takes any `AsRef<str>`. A failure reaches the caller as an `anyhow::Error` carrying
`serde_json`'s message: in a probe, omitting the `data` field from the input failed with
`missing field: data at line 1 column 33`.

## Checking both directions

Two `check_components!` tables list every value type the context encodes. The deserializing one lifts
the component's `'de` lifetime into [`Life`](../../../cgp/reference/types/life.md):

```rust
check_components! {
    #[check_trait(CanDeserializeApp)]
    <'de> App {
        ValueDeserializerComponent: [
            (Life<'de>, u64),
            (Life<'de>, String),
            (Life<'de>, Vec<u8>),
            (Life<'de>, Payload),
        ]
    }
}
```

The serializing table lists the same four types bare. Each table carries its own `#[check_trait]` name
because both check the same context in one module, as the
[wiring guide](../guides/wiring-a-context.md#check-every-value-type) recommends. Neither table checks the
`TryComputer` entries.

## What it demonstrates

- A struct serialized and deserialized with no serialization derive: see
  [derive-free records](../architecture/derive-free-records.md) and [records](../reference/records.md).
- Per-type dispatch with the `open` statement across three components at once: see
  [wiring a context](../guides/wiring-a-context.md#open-the-components-and-dispatch-per-type).
- JSON as wireable, fallible operations that raise into the context's error type: see
  [JSON providers](../reference/json.md) and
  [wiring a context](../guides/wiring-a-context.md#wire-the-error-components-when-the-json-providers-are-used).
- Checking a deserializing component with `Life<'de>`: see
  [components](../reference/components.md#candeserializevalue).

## Known issues

The test pins only the success path. It feeds no invalid input, so neither the missing-field message
above nor any other failure is asserted; see [testing.md](../testing.md#what-is-untested).

## Public material derived from this

The "Wiring an application" page of the planned
[cgp-serde deep dive](../../../website/deep-dives/cgp-serde.md), which takes its code from this test.
