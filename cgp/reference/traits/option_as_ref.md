# `OptionAsRef`

`OptionAsRef<T>` borrows the value inside an `Option` as a `&T`, for any `Option<U>` whose `U`
implements `AsRef<T>`. It is the bound an `#[implicit]` argument of type `Option<&str>` generates, so
the field may be an `Option<String>`, an `Option<Cow<str>>`, or an `Option<Box<str>>` without the
argument needing an allocator of its own.

## Purpose

The trait lets an `#[implicit] nickname: Option<&str>` argument read any `Option<U>` whose `U`
converts to `&str`. The two obvious bounds do not work: `Value = Option<String>` ties the field to one
type and pulls in `alloc`, and `Value: AsRef<str>` fails because `Option<String>` does not implement
`AsRef<str>`. `OptionAsRef<T>` names the conversion instead of the field's concrete type.

The plain `&str` case does not need such a helper, because `AsRef<str>` already covers a `String`,
a `Cow<str>`, and a `Box<str>` field. See [`#[implicit]`](../attributes/implicit.md) for the whole table
of argument forms.

## Definition

```rust
pub trait OptionAsRef<T: ?Sized> {
    fn option_as_ref(&self) -> Option<&T>;
}

impl<T: ?Sized, U> OptionAsRef<T> for Option<U>
where
    U: AsRef<T>,
{
    fn option_as_ref(&self) -> Option<&T> {
        self.as_ref().map(|value| value.as_ref())
    }
}
```

The `?Sized` bound is what lets `T` be `str`, which is unsized.

## Behavior

An `#[implicit] nickname: Option<&str>` argument generates a bound and a binding:

```rust
Self: HasField<Symbol!("nickname"), Value: OptionAsRef<str> + 'static>,
// ...
let nickname: Option<&str> = OptionAsRef::option_as_ref(
    HasField::get_field(self, PhantomData::<Symbol!("nickname")>),
);
```

The call is fully qualified, so a local trait with the same method name cannot capture it.

## Examples

A context with an `Option<String>` field answers the argument, and so does one with an
`Option<Cow<str>>` or an `Option<Box<str>>` field:

```rust
#[cgp_fn]
pub fn describe(&self, #[implicit] nickname: Option<&str>) -> String {
    match nickname {
        Some(name) => format!("aka {name}"),
        None => "anonymous".to_owned(),
    }
}

#[derive(HasField)]
pub struct App {
    pub nickname: Option<String>,
}
```

## Related constructs

- [`#[implicit]`](../attributes/implicit.md): the whole table of argument forms, and the plain `&str`
  case, which does not need a helper.
- [`HasField`](has_field.md): the trait the bound is stated on.
- [`WithProvider`](../providers/with_provider.md): the adapter that makes a getter keep the
  `Option<String>` field.

## Source

- The trait and its blanket impl are in
  [crates/core/cgp-field/src/traits/option_as_ref.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-field/src/traits/option_as_ref.rs),
  re-exported through `cgp::core::field::traits`.

## Public pages derived from this document

The public reference is organized one page per named construct, so this document feeds
[`option_as_ref`](https://contextgeneric.dev/docs/reference/traits/field-access/option_as_ref). A
change here is propagated to it, per the
[synchronization rule](../../../AGENTS.md#the-synchronization-rule).
