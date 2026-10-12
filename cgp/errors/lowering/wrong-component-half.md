# Wrong component half

A CGP definition names one half of a component where the other half belongs, applies `#[cgp_impl]`
to a trait with no provider half, or puts one half's attribute on the other, so the macro gives a
trait the wrong number of arguments and the compiler reports an `E0107` arity error, or an unknown
attribute, about the generated code.

## What triggers it

This class is a *lowering* failure in how a definition refers to a component. A component has two
halves, described in [consumer and provider traits](../../concepts/consumer-and-provider-traits.md):
the consumer trait `CanCalculateArea` that callers use and a context implements, and the provider
trait `AreaCalculator<Context>` that providers implement, with the context moved to a leading
parameter. Each attribute expects one half and writes the context argument for that half:

- **`#[cgp_impl]`** implements a provider trait, so it inserts the context as the leading argument
  of the trait in its header.
- **[`#[use_provider]`](../../reference/attributes/use_provider.md)** bounds an inner provider by a
  provider trait, so it inserts the context in the bound.
- **[`#[uses]`](../../reference/attributes/uses.md)** declares a trait the context implements, a
  consumer trait, so it writes the bound without a context argument.

Naming the other half gives the trait one argument too many (a consumer trait where a provider trait
belongs) or one too few (a provider trait where a consumer trait belongs). The macros cannot catch
it, because they do not resolve the trait names they are given, so the mistake reaches the compiler
as an
[acceptable failure](../../implementation/AGENTS.md#documenting-how-a-macros-expansion-can-fail-to-compile).
The shapes follow, one per position. The last, an attribute on the wrong half, is a CGP defect
instead, since the macro reads its own attributes and could reject it.

### A consumer trait in a `#[cgp_impl]` header

The header of a provider names the provider trait; naming the consumer trait is the most common form
of the mistake:

```rust
#[cgp_component(AreaCalculator)]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_impl(new RectangleArea)]
impl CanCalculateArea { // should be `impl AreaCalculator`
    fn area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
        width * height
    }
}
```

The macro turns the header inside out into
`impl<__Context__> CanCalculateArea<__Context__> for RectangleArea` and derives the component marker
from the trait name, `CanCalculateAreaComponent`, which nothing declares. A component with type
parameters fails the same way, since the context is always one argument more than the consumer trait
takes.

### `#[cgp_impl]` on a trait that is not a component

A trait without [`#[cgp_component]`](../../reference/macros/cgp_component.md) has no provider half
at all:

```rust
pub trait Greet {
    fn greet(&self);
}

#[cgp_impl(new GreetHello)]
impl Greet { // `Greet` is an ordinary trait
    fn greet(&self) {
        println!("hello");
    }
}
```

The expansion is the same inside-out impl, of a trait that takes no context parameter, and the
marker it names, `GreetComponent`, does not exist.

### A consumer trait in an inner-provider bound

A [higher-order provider](../../concepts/higher-order-providers.md) imports its inner provider by
the provider trait:

```rust
#[cgp_impl(new ScaledArea<InnerCalculator>)]
#[use_provider(InnerCalculator: CanCalculateArea)] // should be `AreaCalculator`
impl<InnerCalculator> AreaCalculator {
    fn area(&self, #[implicit] scale_factor: f64) -> f64 {
        InnerCalculator::area(self) * scale_factor * scale_factor
    }
}
```

`#[use_provider]` writes the bound `InnerCalculator: CanCalculateArea<Self>`, giving the consumer
trait a context argument it does not take.

### A provider trait in `#[uses]`

`#[uses]` declares a dependency of the context, which is a consumer trait:

```rust
#[cgp_fn]
#[uses(AreaCalculator)] // should be `CanCalculateArea`
pub fn double_area(&self) -> f64 {
    self.area() * 2.0
}
```

`#[uses]` writes `Self: AreaCalculator`, which lacks the context argument the provider trait takes
first. The same holds for `#[uses]` on a `#[cgp_impl]` provider.

### A provider attribute on a component

`#[uses]` is an attribute of the definitions that lower to an impl (`#[cgp_fn]` and `#[cgp_impl]`).
A component declares what it requires of every context with
[`#[extend]`](../../reference/attributes/extend.md) instead, and `#[cgp_component]` forwards an
attribute it does not recognize onto the items it emits, so the `#[uses]` reaches the compiler
unprocessed:

```rust
#[cgp_component(Greeter)]
#[uses(HasName)] // should be `#[extend(HasName)]`
pub trait CanGreet {
    fn greet(&self);
}
```

This shape is a defect of `#[cgp_component]` rather than an acceptable failure: the macro already
parses `#[extend]` and `#[use_type]` beside it, so it could reject `#[uses]` with a pointer to
`#[extend]`. Its [known issues](../../reference/macros/cgp_component.md#known-issues) record the
forwarding behavior.

## The raw diagnostic

This section describes what plain `cargo check` prints on stable `rustc`, the fallback when
`cargo-cgp` is not on hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers
the readable form. This is a **surfaced** class whose cause is named but misread: the headline is an
[`E0107`](../error_codes/e0107.md) arity error on the trait the user wrote, framed as a count of
generic arguments rather than as the wrong half. Each shape adds its own companions:

- **A consumer trait in a `#[cgp_impl]` header:** a burst of lowering errors. An
  [`E0425`](../error_codes/e0425.md) "cannot find type `CanCalculateAreaComponent` in this scope"
  comes first, on the attribute, with a `help:` that replaces the attribute with
  `AreaCalculatorComponent`. The `E0107` follows, "trait takes 0 generic arguments but 1 generic
  argument was supplied", on the header trait, with a `help:` to "remove the unnecessary generics"
  the user never wrote. For a component without type parameters, an `E0186` ("method `area` has a
  `&self` declaration in the trait, but not in the impl") and an [`E0207`](../error_codes/e0207.md)
  on the unconstrained `__Context__` follow, the latter suggesting `RectangleArea<__Context__>`. A
  call of the component then fails too, with an `E0599`, since the provider implements no provider
  trait.
- **`#[cgp_impl]` on a trait that is not a component:** the same burst, with the `E0425` on
  `GreetComponent`.
- **A consumer trait in an inner-provider bound:** the `E0107` on the trait in the `#[use_provider]`
  attribute, and an `E0308` "mismatched types" in the body, "expected `&InnerCalculator`, found
  `&__Context__`", because the inner call now resolves to the consumer trait's method.
- **A provider trait in `#[uses]`:** an `E0107` "missing generics for trait `AreaCalculator`" on the
  name in the attribute, whose `help:` adds the generated parameter,
  `#[uses(AreaCalculator<__Context__>)]`, writing a name the user never declared into their source.
- **A provider attribute on a component:** a code-less "cannot find attribute `uses` in this scope",
  whose `help:` suggests the built-in `#[used]`.

## Where the root cause is

The root cause is **present but misread**. The `E0107` caret sits on the trait name the user wrote,
the exact token to change, and the attribute error names `uses`, but neither says that the trait is
the wrong half of its component or which half belongs there. The surrounding helps point at wrong
fixes: deleting generics the macro inserted, adding the generated `__Context__`, renaming the
attribute to `AreaCalculatorComponent`, parameterizing the provider struct by `__Context__`, or
using `#[used]`. In the header shapes the `E0107` is not even first: the `E0425` arrives before it,
since name resolution runs before the compiler lowers the impl's types, and the `E0186` and `E0207`
after it repeat the same mistake.

The landmark is an `E0107` whose caret sits on a trait name inside a `#[cgp_impl]` header or a CGP
attribute. Read the trait it names and compare it with the half the position expects: a provider
trait in a `#[cgp_impl]` header or a `#[use_provider]` bound, a consumer trait in `#[uses]`.

## How cargo-cgp presents it

`cargo-cgp` reshapes four of the shapes into one error each, on the `E0107`, naming both halves and
carrying the fix in a `help`; it keeps `rustc`'s `E0107` code. The codes are defined in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) (summarized in
[cargo-cgp-codes.md](../error_codes/cargo-cgp-codes.md)):

- **`[CGP-E032]`** for a consumer trait in the header:
  `` `CanCalculateArea` is a consumer trait, but a `#[cgp_impl]` provider must implement its provider trait `AreaCalculator` ``,
  and
  ``help: change the impl header to target the provider trait: `impl AreaCalculator` (not `impl CanCalculateArea`)``.
  The sibling `E0425`, `E0186`, and `E0207` and the downstream check report are dropped. A
  requirement of the impl that fails on its own, such as a field the context lacks, is a second
  mistake, so it is reported beside the `[CGP-E032]` as the error the program gives once the header
  is fixed.
- **`[CGP-E033]`** for a trait that is not a component:
  `` `#[cgp_impl]` can only implement a CGP component's provider trait, but `Greet` is not a CGP component ``,
  with a `help` to make `Greet` a component, as in `#[cgp_component(GreetProvider)]`, and implement
  its provider trait in the header (`impl GreetProvider`), or to drop `#[cgp_impl]` and write a
  plain `impl`.
- **`[CGP-E034]`** for a consumer trait in an inner-provider bound:
  `` `CanCalculateArea` is a consumer trait and cannot bound an inner provider; a higher-order provider imports its provider trait `AreaCalculator` ``,
  with a `help` naming `#[use_provider(… : AreaCalculator)]`. The `E0308` body cascade is dropped.
- **`[CGP-E037]`** for a provider trait in `#[uses]`:
  `` `AreaCalculator` is a provider trait and cannot be a `#[uses]` dependency; a dependency names its consumer trait `CanCalculateArea` ``,
  and
  ``help: name the consumer trait instead: `#[uses(CanCalculateArea)]` (not the provider trait `AreaCalculator`)``.

The provider attribute on a component keeps `rustc`'s output, a gap described under
[Notes for tooling](#notes-for-tooling).

## Resolving it

Name the half the position expects:

- **A `#[cgp_impl]` header:** name the provider trait, `impl AreaCalculator`.
- **A trait that is not a component:** make it one and implement its provider trait,
  `#[cgp_component(GreetProvider)]` on `Greet` and `impl GreetProvider` in the header, or write a
  plain `impl Greet for GreetHello` with the struct declared, if it is an ordinary trait. Making
  `Greet` a component alone leaves its consumer trait in the header, the first shape.
- **A `#[use_provider]` bound:** name the provider trait,
  `#[use_provider(InnerCalculator: AreaCalculator)]`.
- **A `#[uses]` dependency:** name the consumer trait, `#[uses(CanCalculateArea)]`.
- **A requirement on a component:** use `#[extend(HasName)]` in place of `#[uses(HasName)]`.

## Notes for tooling

The provider attribute on a component is the shape still left as `rustc` wrote it. Its error comes
from name resolution, before the HIR exists, and carries no error code, so the emitter could
recognize it only from the attribute's span and the `#[cgp_component]` beside it in the source. The
better fix is in `cgp`: since the shape is a macro defect, `#[cgp_component]` rejecting `#[uses]`
with a pointer to `#[extend]` would remove the class's last unreshaped case at its source.

## Backing fixtures

These fixtures pin the class, one group per shape:

- [`lowering/wrong-component-half/consumer_trait_in_provider_impl_called.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_called.rs):
  a consumer trait in the header, the only mistake, checked and called; one `[CGP-E032]`.
- [`lowering/wrong-component-half/consumer_trait_in_provider_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl.rs):
  the same beside a field the context lacks, reported as a `[CGP-E001]` block beside the
  `[CGP-E032]`.
- [`lowering/wrong-component-half/consumer_trait_in_provider_impl_call_missing_field.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_call_missing_field.rs):
  the same reached by a call on the context rather than a check.
- [`lowering/wrong-component-half/consumer_trait_in_provider_impl_field_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_field_type.rs):
  the same beside a field of the wrong type, reported as `[CGP-E004]`.
- [`lowering/wrong-component-half/consumer_trait_in_provider_impl_generic.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/consumer_trait_in_provider_impl_generic.rs):
  a generic component's consumer trait in the header; `[CGP-E032]`.
- [`lowering/wrong-component-half/cgp_impl_on_non_cgp_trait.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/cgp_impl_on_non_cgp_trait.rs):
  `#[cgp_impl]` on an ordinary trait; `[CGP-E033]`.
- [`lowering/wrong-component-half/higher_order_use_provider_consumer_trait.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/higher_order_use_provider_consumer_trait.rs):
  a consumer trait in `#[use_provider]`; `[CGP-E034]`, with the `E0308` cascade dropped.
- [`lowering/wrong-component-half/uses_provider_trait.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/uses_provider_trait.rs):
  a provider trait in a `#[cgp_fn]`'s `#[uses]`; `[CGP-E037]`.
- [`lowering/wrong-component-half/uses_provider_trait_in_impl.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/uses_provider_trait_in_impl.rs):
  the same on a `#[cgp_impl]` provider; `[CGP-E037]`.
- [`lowering/wrong-component-half/uses_on_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/uses_on_component.rs):
  `#[uses]` on a `#[cgp_component]`, left as `rustc` wrote it with its `#[used]` suggestion
  (`usability`).

## Related

- [Consumer and provider traits](../../concepts/consumer-and-provider-traits.md): the two halves of
  a component and why each position names one of them.
- [`#[cgp_impl]`](../../reference/macros/cgp_impl.md),
  [`#[use_provider]`](../../reference/attributes/use_provider.md),
  [`#[uses]`](../../reference/attributes/uses.md), and
  [`#[extend]`](../../reference/attributes/extend.md): the positions and the half each expects.
- [Undeclared dependency](undeclared-dependency.md): the sibling class, where a dependency is used
  but not declared at all.
- [`E0107`](../error_codes/e0107.md), [`E0425`](../error_codes/e0425.md), and
  [`E0207`](../error_codes/e0207.md): the Rust error codes this class is reported under.
- [Debugging CGP compile errors](../../guides/debugging.md#grep-for-the-suspected-line-instead-of-reading-the-whole-log):
  the grep that recognizes the class by its `E0107`.
