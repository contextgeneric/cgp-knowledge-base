# Provider impl without the macro

A provider trait is implemented for a provider struct by a plain `impl`, without `#[cgp_provider]` or
`#[cgp_impl]`, so the compiler rejects the impl on the provider trait's own `IsProviderFor`
supertrait with an `E0277`.

## What triggers it

A provider trait has [`IsProviderFor`](../../reference/traits/is_provider_for.md) as a supertrait, so
the impl of the provider trait for a provider struct must come with an impl of `IsProviderFor` for
the same struct and component. [`#[cgp_provider]`](../../reference/macros/cgp_provider.md) writes
both, and so does [`#[cgp_impl]`](../../reference/macros/cgp_impl.md), which lowers to it. An impl
written by hand has no marker impl:

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self) -> String;
}

pub struct GreetHello;

impl<Context> Greeter<Context> for GreetHello { // no `#[cgp_provider]`
    fn greet(_context: &Context) -> String {
        "hello".to_owned()
    }
}
```

The macros cannot catch it, because nothing marks the plain impl as a provider impl until the
compiler checks its supertraits, so the mistake reaches the compiler as an
[acceptable failure](../../implementation/AGENTS.md#documenting-how-a-macros-expansion-can-fail-to-compile).

## The raw diagnostic

This section describes what plain `cargo check` prints on stable `rustc`, the fallback when
`cargo-cgp` is not on hand. This is a **surfaced** class: one [`E0277`](../error_codes/e0277.md)
``the trait bound `GreetHello: IsProviderFor<GreeterComponent, Context>` is not satisfied``, with its
caret on the provider struct in the impl header. A `help:` lists the types that do implement
`IsProviderFor`, eight and a count, which are unrelated to the mistake, and a note says the bound is
required by the provider trait.

A wiring and check of the provider adds a second `E0277` on the context's check, naming the same
unmet `IsProviderFor`.

## Where the root cause is

The root cause is **present and is the headline**: the provider has no `IsProviderFor` impl, and the
caret sits on its name in the impl the user wrote. The output does not say that a macro writes the
impl, and its implementor list points at nothing the reader can use.

## How cargo-cgp presents it

`cargo-cgp` words the `E0277` as `[CGP-E039]`, with the headline
``the impl of `Greeter` for `GreetHello` is written without `#[cgp_provider]` ``, adds a `help` to add
`#[cgp_provider]` to the impl or write the provider with `#[cgp_impl]`, and drops the implementor
list. The tool recognizes it structurally
(the failing span is the `Self` type of a local impl the user wrote of a CGP provider trait, and no
`IsProviderFor` impl exists for that struct and component) and drops the check's `E0277` on the same
provider as its consequence. The codes are in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md).

## Resolving it

Add `#[cgp_provider]` to the impl, or write the provider with `#[cgp_impl]`, the idiomatic form, which
declares the provider struct with `new` and keeps `self` for the context.

## Backing fixtures

- [`lowering/provider-impl-without-macro/provider_impl_without_macro.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro.rs):
  the impl alone; one `[CGP-E039]`.
- [`lowering/provider-impl-without-macro/provider_impl_without_macro_wired.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro_wired.rs):
  the same wired and checked; the check's `E0277` is dropped as the mistake's consequence.

## Related

- [`IsProviderFor`](../../reference/traits/is_provider_for.md): the marker trait the macro's second
  impl provides.
- [`#[cgp_provider]`](../../reference/macros/cgp_provider.md) and
  [`#[cgp_impl]`](../../reference/macros/cgp_impl.md): the macros that write the pair.
- [Wrong component half](wrong-component-half.md): the sibling class, where the header names the
  wrong trait.
- [`E0277`](../error_codes/e0277.md): the Rust error code this class is reported under.
