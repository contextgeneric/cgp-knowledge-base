# `#[impl_generics(...)]`

`#[impl_generics(...)]` declares generic parameters on the blanket impl a [`#[cgp_fn]`](../macros/cgp_fn.md) generates, and on that impl alone, so a type that a context supplies through a field is inferred rather than exposed as a trait parameter.

## Purpose

A `#[cgp_fn]` copies every generic parameter written on the function onto both the generated trait and the generated impl. That is the right placement for a parameter the caller chooses, and the wrong one for a type the body needs but nobody chooses: a database handle, a value that only has to be printable, a scalar read from a field. The context already fixes that type through the field the body reads, so a parameter on the trait would make every caller, and every capability built on top, declare the parameter and repeat its bounds for a type they never touch.

`#[impl_generics(...)]` is the third placement. Its parameters land on the impl's generic list only, so the trait stays free of them, and the compiler infers each one from the `HasField<…, Value = T>` bound that an [`#[implicit]`](implicit.md) argument of that type produces. The result is a capability that reads as "this works with any `name` field of a compatible type", without a trait parameter, a wiring line, or an associated-type declaration. It is the first form to reach for when a body needs a type it does not fix; [naming a type dependency](../../guides/naming-a-type-dependency.md) is the prescriptive account of when to stay here and when to climb to an [abstract type](../../concepts/abstract-types.md).

The cost is that the type is concealed rather than named. It exists only where a value of it flows through an implicit argument, so nothing else can refer to it: not the capability's own signature, not another capability, and not a second provider.

## Syntax

The attribute is written beneath `#[cgp_fn]` and takes a comma-separated list of generic parameters, each written as it would appear inside an `impl<…>` list:

```rust
#[cgp_fn]
#[impl_generics(Name: Display)]
pub fn greet(&self, #[implicit] name: &Name) -> String {
    format!("Hello, {name}!")
}
```

Each parameter is appended to the impl's generic list, after the `__Context__` parameter and after any generics the function declares itself. An inline bound stays with the parameter. A bound may also be written in the function's own `where` clause, which lands on the impl as well. The attribute may be repeated, and repeats concatenate, but the idiomatic form is one attribute carrying a comma-separated list.

Every parameter must be pinned by the type of an implicit argument. Rust accepts a parameter on an impl only where the impl determines it, and the only place a `#[cgp_fn]` impl determines one is the `Value = T` associated-type binding of an implicit argument's field bound. `&Name` pins `Name`, and a nested position such as `&Pool<Db>` pins `Db`. A parameter absent from every implicit argument is rejected as unconstrained; see Known issues.

The list accepts a lifetime or a const parameter as well as a type parameter, because the parser reads Rust `GenericParam` productions. Type parameters are the case the attribute exists for.

`#[impl_generics(...)]` is read only by `#[cgp_fn]`. [`#[cgp_impl]`](../macros/cgp_impl.md) does not collect it and does not need an equivalent: a provider impl's own generic list is already impl-only, so a provider declares such a parameter there directly, and the same `Value = T` binding constrains it. [`#[cgp_component]`](../macros/cgp_component.md) does not collect it either, because it does not generate an impl of its own to carry a parameter. On both hosts the attribute passes through onto the generated items, where the compiler reports it as an unknown attribute; see Known issues.

## Syntax Grammar

The attribute argument of `#[impl_generics]` is a comma-separated list of generic parameters:

```ebnf
ImplGenericsArgs -> GenericParam ( `,` GenericParam )* `,`?
```

`GenericParam` is the Rust grammar's own production for one entry of a generic parameter list: a lifetime parameter, a type parameter with optional bounds, or a const parameter. The list may be empty and the attribute may be repeated. Because the production is Rust's, a parameter default such as `T = u32` parses; the compiler then rejects the generated impl, as Known issues records.

## Expansion

`#[impl_generics(...)]` adds its parameters to the generated impl's generic list and nothing to the trait. From the `greet` function above, the macro emits:

```rust
pub trait Greet {
    fn greet(&self) -> String;
}

impl<__Context__, Name: Display> Greet for __Context__
where
    Self: HasField<Symbol!("name"), Value = Name>,
{
    fn greet(&self) -> String {
        let name: &Name = self.get_field(PhantomData::<Symbol!("name")>);
        format!("Hello, {name}!")
    }
}
```

The `Value = Name` binding makes the impl legal: it is the associated-type binding that determines `Name`, so the parameter is constrained even though neither the trait nor the self type mentions it. The inline bound `Name: Display` travels with the parameter exactly as written.

The impl's generic list is ordered: `__Context__` first, then the function's own generics, then the `#[impl_generics]` parameters. A `fn scale<Scalar>` carrying `#[impl_generics(Db)]` emits `impl<__Context__, Scalar, Db>`. Rust requires lifetimes to lead a generic list, and the emitted list keeps that order regardless of where a lifetime was declared, because `syn` prints lifetime parameters first.

The impl's `where` clause keeps the ordering [`#[cgp_fn]`](../macros/cgp_fn.md) documents: the function's own predicates, then the predicates the companion attributes contribute, then the `HasField` bounds from the implicit arguments last.

## Examples

A capability whose one type dependency each context fixes through a field, and a second capability built on it that never learns the type exists:

```rust
use cgp::prelude::*;
use core::fmt::Display;

#[cgp_fn]
#[impl_generics(Name: Display)]
pub fn greet(&self, #[implicit] name: &Name) -> String {
    format!("Hello, {name}!")
}

#[cgp_fn]
#[uses(Greet)]
pub fn announce(&self) -> String {
    format!("{} Welcome aboard.", self.greet())
}

#[derive(HasField)]
pub struct Person {
    pub name: String,
}

#[derive(HasField)]
pub struct Robot {
    pub name: u32,
}
```

`Person` and `Robot` both implement `Greet` and `Announce` through the blanket impls, with nothing wired: the compiler resolves `Name` to `String` for one and to `u32` for the other. Both are **value contexts**, since the wired type is the data the greeting reads, and both capabilities are **self-targeted**. Had `greet` taken `Name` as a function generic, `announce` would have to declare `<Name>`, repeat `Name: Display`, and pass the parameter on to everything that calls it.

## Related constructs

`#[impl_generics(...)]` is specific to [`#[cgp_fn]`](../macros/cgp_fn.md), whose generics split it extends with a third placement. The parameter is pinned by an [`#[implicit]`](implicit.md) argument through the [`HasField`](../traits/has_field.md) bound it produces. [`#[extend_where]`](extend_where.md) is the trait-side counterpart, a predicate on the trait's own parameters that callers must see, and [`#[uses]`](uses.md) is the other kind of private requirement, a capability bound on `Self`. When the type must be named in a signature or shared by two capabilities, the form to climb to is an abstract type declared with [`#[cgp_type]`](../macros/cgp_type.md) and imported with [`#[use_type]`](use_type.md); [naming a type dependency](../../guides/naming-a-type-dependency.md) works out that decision.

## Known issues

A parameter absent from every implicit argument is rejected by the compiler with `E0207` (`the type parameter 'Name' is not constrained by the impl trait, self type, or predicates`), with the caret on the parameter inside the attribute. The macro lowers the impl faithfully and cannot tell the intended fix, which is either to read a field whose type mentions the parameter or, if the caller should choose the type, to make it a function generic instead.

A parameter cannot appear in the capability's own signature, because only the impl declares it. Naming it in a return type or an explicit (non-implicit) parameter fails during name resolution: a qualified path such as `Db::Row` reports `E0433` with the label `use of undeclared type`, and a bare `Db` reports `E0425` with the label `not found in this scope`, both under the headline `cannot find type 'Db' in this scope`. This is the [out-of-scope generated name](../../errors/lowering/out-of-scope-generated-name.md) error class, and the condition that forces promotion to an abstract type.

A parameter named after the function shadows the generated trait. `fn count` with `#[impl_generics(Count: Display)]` puts a trait `Count` and a parameter `Count` in scope together, and inside the generated impl the trait's name resolves to the parameter, so the compiler reports `E0404` (`expected trait, found type parameter 'Count'`) on the function name. Renaming the parameter, or the trait through `#[cgp_fn(CanCount)]`, resolves it.

A parameter default such as `#[impl_generics(T: Display = u32)]` parses, because the argument is a Rust `GenericParam`, and the compiler then rejects the generated impl with `defaults for generic parameters are not allowed here`, a deny-by-default lint scheduled to become a hard error.

On any host other than `#[cgp_fn]` the attribute is not consumed and reaches the compiler as `cannot find attribute 'impl_generics' in this scope`, once per generated item on a `#[cgp_component]`. Neither host reports it as a misplaced CGP attribute.

## Source

- Parsing: the `impl_generics` field of `FunctionAttributes` in [crates/macros/cgp-macro-core/src/types/attributes/function.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/function.rs), which reads the argument as a comma-separated list of `syn::GenericParam`.
- Injection: the parameters are appended to the impl's generic list in `to_item_impl`, in [crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_fn/preprocessed.rs), after the leading `__Context__` and the function's own generics.
- Implementation documents (the pipeline that lowers the attribute, its failure mode, and the index of tests and snapshots): [implementation/entrypoints/cgp_fn.md](../../implementation/entrypoints/cgp_fn.md) and [implementation/asts/cgp_fn.md](../../implementation/asts/cgp_fn.md).
