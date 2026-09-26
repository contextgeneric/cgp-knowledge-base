# `greet`

`greet` writes one greeting three ways, as a CGP function, as a component with two providers, and as
a provider over an abstract name type, each in its own binary on a `Person` struct with a `name`
field. Its library holds only a hand-written expansion of the component.

- **Source** — [greet/](https://github.com/contextgeneric/cgp-examples/tree/v0.8.0/greet), on the
  `v0.8.0` branch; see [which revision](../README.md#which-revision-these-documents-describe)
- **Run** — `cargo run -p cgp-example-greet --bin <name>`, with `greet-function`, `greet-component`,
  or `greet-abstract-type`
- **Needs** — nothing
- **Result** — each binary printed `Hello, Alice!`
- **Worked example** — none; the closest teaching material is the
  [area calculation](../../../examples/area-calculation.md) example, which also wires a value context

## What it is

The crate is the smallest program in the repository, and the only one that wires a **value context**:
`Person` is the data the greeting reads, and it carries the wiring itself. Every component is
self-targeted. The three binaries are independent, each declaring its own traits, providers, and
`Person`, and none of them uses the library:

| Binary | Source | Defines | How `Person` gets `greet` |
|---|---|---|---|
| `greet-function` | `bin/greet_function.rs` | a `#[cgp_fn]` function | the blanket impl the function's trait carries |
| `greet-component` | `bin/greet_component.rs` | the `Greeter` component and two providers | one wiring entry, to `GreetHello` |
| `greet-abstract-type` | `bin/greet_abstract_type.rs` | the component, an abstract `Name` type, and one provider | one wiring entry, and a direct `HasNameType` impl |

The library, `src/lib.rs`, exports one module, `greet_expanded`, which writes out by hand the items
`#[cgp_component]` generates for `CanGreet`. It is not the macro's current output; see
[expansion.md](expansion.md).

## The binaries

### `greet-function`

The greeting is a function whose `name` argument is read from the context's field:

```rust
#[cgp_fn]
pub fn greet(&self, #[implicit] name: &str) {
    println!("Hello, {name}!");
}
```

[`#[cgp_fn]`](../../../cgp/reference/macros/cgp_fn.md) turns it into a `Greet` trait with one blanket
impl for any context whose `name` field is a `String`, which is what the
[`#[implicit]`](../../../cgp/reference/attributes/implicit.md) `&str` form requires. `Person` derives
`HasField` and needs no wiring.

### `greet-component`

The greeting becomes a [component](../../../cgp/reference/macros/cgp_component.md), `CanGreet` with
the provider trait `Greeter`, so that a context can choose how it greets. Two providers read the same
field and differ in their message:

```rust
#[cgp_impl(new GreetHello)]
impl Greeter {
    fn greet(&self, #[implicit] name: &str) {
        println!("Hello, {name}!");
    }
}
```

`GreetHi` prints `Hi, {name}!`. `Person` wires `GreeterComponent: GreetHello`, so choosing the other
greeting is a one-entry change; nothing wires `GreetHi`. The file also declares a `HasNameType` it
never uses.

### `greet-abstract-type`

The provider leaves the name's type to the context, importing it with
[`#[use_type]`](../../../cgp/reference/attributes/use_type.md) and bounding it in a `where` clause:

```rust
#[cgp_type]
pub trait HasNameType {
    type Name;
}

#[cgp_impl(new GreetHello)]
#[use_type(HasNameType.Name)]
impl Greeter
where
    Name: Display,
{
    fn greet(&self, #[implicit] name: &Name) {
        println!("Hello, {name}!");
    }
}
```

The provider then requires a `name` field whose type is the context's `Name`, and a `Display` impl
for it. `Person` supplies the type by implementing `HasNameType` directly, `type Name = String;`,
rather than by wiring `NameTypeProviderComponent` to `UseType<String>`. Either works, and the
[`#[cgp_type]`](../../../cgp/reference/macros/cgp_type.md) reference calls the direct impl often the
clearest choice.

## Idioms

The binaries use current CGP idioms: fields are read as `#[implicit]` arguments, providers are
`#[cgp_impl]` blocks, and the abstract type is imported with `#[use_type]` and written bare. Only the
library's hand-written expansion shows an older shape.

## Status and gaps

The three programs run and print what their code says. The crate's gaps are recorded in full in
[issues.md](issues.md):

- **No check blocks** — no binary asserts its wiring with `check_components!`.
- **An outdated expansion** — `greet_expanded.rs` differs from what the macro generates.

## The documents

- [expansion.md](expansion.md) — `greet_expanded.rs` compared with the macro's output, and what the
  difference changes.
- [testing.md](testing.md) — what running the binaries shows, and what nothing tests.
- [issues.md](issues.md) — the missing feature and housekeeping.

## Public material derived from these documents

None yet.

## How it relates to the rest of the base

The greeting is the running example of the `/cgp` skill's introduction and of many reference
documents, which write it in their own forms; nothing links this crate. The constructs it shows are
documented in [`#[cgp_fn]`](../../../cgp/reference/macros/cgp_fn.md),
[`#[cgp_component]`](../../../cgp/reference/macros/cgp_component.md),
[`#[cgp_type]`](../../../cgp/reference/macros/cgp_type.md), and the
[modularity hierarchy](../../../cgp/concepts/modularity-hierarchy.md), which explains how much
choice a value context leaves: one provider per value type, program-wide.
