# Unresolved wiring name

A `delegate_components!` entry names something that does not exist where the wiring is written (a
component not in scope, a key guessed from a trait's name, a provider never declared, a type in an
`@`-path never declared) or a consumer trait where a component belongs, so the compiler reports the name itself (`E0425` "cannot find
type", or `E0782` "expected a type, found a trait"), with suggestions that do not fit wiring.

## What triggers it

This class is a failure of the names in a wiring entry, not of what they wire.
[`delegate_components!`](../../reference/macros/delegate_components.md) writes each entry
`Key: Value` into an impl, `impl DelegateComponent<Key> for Context { type Delegate = Value; }`, so
the key must name a component marker and the value a provider type, both in scope where the table is
written. The macro copies the names as written and cannot check them, because which items exist and
what they are is known only to the compiler, so a wrong name is an
[acceptable failure](../../implementation/writing-guide.md#documenting-how-a-macros-expansion-can-fail-to-compile)
that CGP defers to it. Its shapes differ in what the name gets wrong.

### A consumer trait as a key

The key of a component is its marker, `{Provider}Component`, not the consumer trait callers use:

```rust
#[cgp_component(Greeter)]
pub trait CanGreet {
    fn greet(&self);
}

delegate_components! {
    Person {
        CanGreet: GreetHello, // should be `GreeterComponent`
    }
}
```

`CanGreet` resolves, but to a trait, and a trait cannot stand where the impl expects a type.

### A component that is not in scope

A component defined in another module or crate must be imported where the table names it:

```rust
use cgp::prelude::*;

delegate_components! {
    App {
        ErrorTypeProviderComponent: UseType<String>, // not in the prelude
    }
}
```

`ErrorTypeProviderComponent` exists, in `cgp::core::error`, but the prelude does not export it, so
the name resolves to nothing here. A component in a sibling module of the same crate fails the same
way without its `use`.

### A key guessed from a trait's name

[`#[cgp_component]`](../../reference/macros/cgp_component.md) names the marker after the provider
trait, and [`#[cgp_type]`](../../reference/macros/cgp_type.md) after the type's provider, so a key
built from the consumer trait's name names nothing:

```rust
#[cgp_type]
pub trait HasScalarType {
    type Scalar;
}

delegate_components! {
    App {
        HasScalarTypeComponent: UseType<f64>, // the component is `ScalarTypeProviderComponent`
    }
}
```

### A provider that is never declared

A value names a provider struct, which must exist:

```rust
#[cgp_impl(GreetHello)] // without `new`, nothing declares `GreetHello`
impl Greeter {
    fn greet(&self) {}
}

delegate_components! {
    Person {
        GreeterComponent: GreetHello,
    }
}
```

The bare [`#[cgp_impl(GreetHello)]`](../../reference/macros/cgp_impl.md) implements the provider
trait for a struct the author is expected to declare, and `#[cgp_impl(new GreetHello)]` declares it.
Without either, the impl and the wiring both name a type that does not exist. A misspelled provider
in the value, `GreeterComponent: GreetHi`, fails the same way at the value alone.

### A type in an `@`-path that is never declared

A path key (`@app.Missing`), or the path a `=>` redirect points at, is a chain of segments. A
segment that is not a lowercase identifier stays the type it spells, so it must exist where the
table is written. A lowercase segment becomes a symbol (`Symbol!("app")`) and needs no declaration:

```rust
delegate_components! {
    App {
        GreeterComponent => @app.Missing, // `Missing` is declared nowhere
        @app.Missing: GreetHello,
    }
}
```

A misspelled type fails the same way, and so does a segment written with a capital by mistake that
was meant as a symbol.

## The raw diagnostic

This section describes what plain `cargo check` prints on stable `rustc`, the fallback when
`cargo-cgp` is not on hand; [How cargo-cgp presents it](#how-cargo-cgp-presents-it) below covers
the readable form. This is a **surfaced** class: the caret sits on the name the user wrote, and the
diagnostic names it. Each shape adds suggestions of its own:

- **A consumer trait as a key:** an [`E0782`](../error_codes/e0782.md) "expected a type, found a
  trait", whose `help:` offers to add `dyn` (`dyn CanGreet: GreetHello`), a trait object no wiring
  key can be.
- **A component that is not in scope:** an [`E0425`](../error_codes/e0425.md) "cannot find type
  `ErrorTypeProviderComponent` in this scope", reported twice at the key, with a `help:` to add a
  type parameter (`ErrorTypeProviderComponent<ErrorTypeProviderComponent>`) and no import. For a
  component of the same crate, rustc reports it once, suggests the right import
  (`use crate::components::GreeterComponent;`), and also suggests a similarly named component of
  another kind (`ComputerComponent`).
- **A key guessed from a trait's name:** the same `E0425`, reported twice, with a `help:` to add a
  type parameter or to use a similarly named item, such as the trait `CanUseComponent` for
  `CanGreetComponent`.
- **A type in an `@`-path:** the same `E0425`, reported at each use of the path, so the redirect and
  the key above each report it. The first gets a `help:` to add a type parameter to the entry's key
  (`GreeterComponent<Missing> => …`), which no wiring entry can take, and a similarly named struct
  is suggested when there is one. A check on the context then overflows (`E0275`) on the lookup
  through the unresolved key.
- **A provider that is never declared:** an `E0425` "cannot find type `GreetHello` in this scope"
  at the `#[cgp_impl]` attribute and again at the wiring value. A misspelled value alone gets one,
  whose `help:` suggests a similarly named trait, often the provider trait (`Greeter` for
  `GreetHi`), which cannot be a value.

## Where the root cause is

The root cause is **present and at the caret**: the error names exactly the token to change. The
output does not say what the token should be, and its suggestions point elsewhere: a `dyn`, a type
parameter, a similarly named trait or component, none of which is a wiring fix. The landmark is an
`E0425` or `E0782` whose caret sits on a key or a value inside a `delegate_components!` block, or on
the provider of a `#[cgp_impl]` header.

## How cargo-cgp presents it

`cargo-cgp` reshapes each shape into one error that says what the name is and carries the fix in a
`help`, keeping `rustc`'s code. The codes are defined in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) (summarized in
[cargo-cgp-codes.md](../error_codes/cargo-cgp-codes.md)):

- **`[CGP-E040]`** for a consumer trait as a key:
  ``the wiring key `CanGreet` is a consumer trait, but a key names a component``, and
  ``help: name its component instead: `GreeterComponent` ``.
- **`[CGP-E041]`** for a component not in scope:
  ``the component `ErrorTypeProviderComponent` is not in scope``, and
  ``help: import it with `use cgp::core::error::ErrorTypeProviderComponent;` ``, the shortest public
  path from a dependency (or a `crate::` path for a local component), with rustc's suggestions
  dropped.
- **`[CGP-E042]`** for a key guessed from a trait's name:
  ``the wiring key `HasScalarTypeComponent` names no component``, and
  ``help: name the component of `HasScalarType` instead: `ScalarTypeProviderComponent` ``.
- **`[CGP-E043]`** for an undeclared provider in a value:
  ``the provider `GreetHi` wired for `GreeterComponent` is not declared``, with a `help` only when a
  provider of that component has a similar name, and rustc's suggestion of a trait dropped.
- **`[CGP-E044]`** for a type in an `@`-path never declared:
  ``the type `Missing` in a wiring path is not declared``, with
  ``help: declare or import the type `Missing`, or write the segment in lowercase to make it a symbol``
  when nothing else says how to fix it. The type-parameter suggestion is dropped and rustc's other
  suggestions stay, since a similarly named struct is a correct near miss. A segment that is a
  component not in scope gets `[CGP-E041]` instead, and the `E0275` overflow a check reports on the
  entry is dropped as its consequence.
- **`[CGP-E038]`** for a `#[cgp_impl]` provider never declared:
  ``the provider `GreetHello` is not declared``, and
  ``help: declare it with `#[cgp_impl(new GreetHello)]` ``. The wiring value's error for the same
  name is dropped as its consequence, and so is the `E0275` overflow a call then reports under the
  tool's next-generation solver.

A name reported twice at one span prints once, and so does a type of one name reported at several
places in `@`-paths. A name that is part of a key or a value without being in an `@`-path, such as
a type argument of a provider, is left as `rustc` wrote it, and so is a name no rule explains.

## Resolving it

Name what the position takes, in scope:

- **A key:** the component marker, `GreeterComponent` for `#[cgp_component(Greeter)]`, imported
  where the table is written when it lives elsewhere, as in
  `use cgp::core::error::ErrorTypeProviderComponent;`.
- **A value:** a declared provider, written with `#[cgp_impl(new GreetHello)]` or declared as its
  own struct, spelled as declared.

## Notes for tooling

The `E0425`s are raised by name resolution, before the compiler builds the HIR, so the tool holds
them and reshapes them after resolution, when it can read the wiring entries back. These cases still
keep `rustc`'s output:

- **A name declared elsewhere but not imported:** a provider, a `#[cgp_impl]` provider, or a type in
  an `@`-path that some module of the crate, or a public module of a dependency, declares is a name
  not in scope rather than one never declared, so the tool does not call it undeclared. `rustc`'s
  suggestion to import it, when it gives one, is the fix
  ([`names_not_imported`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/names_not_imported.rs)).
- **A key two components could be:** two components of one name, in two crates or in two modules,
  or a key guessed from a consumer trait's name that two traits share, make the import or the
  component a guess, and the tool does not guess
  ([`ambiguous_component_names`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/ambiguous_component_names.rs)).
- **A key that is no component under any rule:** only the `Component` suffix on a consumer trait's
  name is recognized; a misspelled component name gets no near miss.
- **A key in another table:** only `delegate_components!` entries are recognized, not a
  `check_components!` entry naming the same wrong key.
- **A type argument outside an `@`-path:** a value such as `UseDelegate<Missing>` keeps both
  `E0425`s and the type-parameter suggestion, since only a type inside a path is recognized
  ([`value_nested_type_not_declared`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_nested_type_not_declared.rs)).

## Backing fixtures

These fixtures pin the class, one group per shape:

- [`wiring/unresolved-wiring-name/consumer_trait_as_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/consumer_trait_as_key.rs):
  the consumer trait `CanGreet` as a key; `[CGP-E040]` names `GreeterComponent`.
- [`wiring/unresolved-wiring-name/error_key_not_imported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/error_key_not_imported.rs):
  `ErrorTypeProviderComponent` without its import; `[CGP-E041]` names
  `cgp::core::error::ErrorTypeProviderComponent`.
- [`wiring/unresolved-wiring-name/component_in_module_not_imported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/component_in_module_not_imported.rs):
  a component of a sibling module without its import; `[CGP-E041]` names the `crate::` path.
- [`wiring/unresolved-wiring-name/scalar_type_guessed_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/scalar_type_guessed_key.rs):
  `HasScalarTypeComponent` for a `#[cgp_type]` trait; `[CGP-E042]`.
- [`wiring/unresolved-wiring-name/consumer_trait_name_as_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/consumer_trait_name_as_key.rs):
  `CanGreetComponent` for a `#[cgp_component]` trait; `[CGP-E042]`.
- [`wiring/unresolved-wiring-name/value_not_declared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_not_declared.rs):
  a misspelled provider as a value; `[CGP-E043]` without a help.
- [`wiring/unresolved-wiring-name/provider_not_declared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_not_declared.rs):
  `#[cgp_impl(GreetHello)]` without `new`, wired and called; one `[CGP-E038]`.
- [`wiring/unresolved-wiring-name/path_segment_not_declared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_not_declared.rs):
  an undeclared type as an `@`-path segment, in a redirect and a key and then checked; one
  `[CGP-E044]`, with the repeat and the `E0275` overflow dropped.
- [`wiring/unresolved-wiring-name/path_segment_near_miss.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_near_miss.rs):
  a misspelled type as a segment; `[CGP-E044]` keeps the compiler's similarly named struct.
- [`wiring/unresolved-wiring-name/path_segment_component_not_imported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_component_not_imported.rs):
  a component of another module as a segment; `[CGP-E041]` names the `crate::` path.
- [`wiring/unresolved-wiring-name/path_segment_nested_type.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_nested_type.rs):
  a type nested in a segment's generic arguments; `[CGP-E044]` without a help.
- [`wiring/unresolved-wiring-name/value_not_declared_near_miss.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_not_declared_near_miss.rs):
  a misspelled provider beside a closer name that provides another component; `[CGP-E043]`'s help
  names the provider of the key's component.
- [`wiring/unresolved-wiring-name/generic_component_value_not_declared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/generic_component_value_not_declared.rs):
  an undeclared provider for a component with a parameter, called; `[CGP-E043]`, with the overflow
  on `App: CanCalculateArea<Rectangle>` dropped.
- [`wiring/unresolved-wiring-name/generic_component_path_type_checked.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/generic_component_path_type_checked.rs):
  an undeclared type in the path a component with a parameter is redirected to, checked at a
  parameter; `[CGP-E044]`, with the check's overflow dropped.
- [`wiring/unresolved-wiring-name/value_not_declared_beside_cycle.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_not_declared_beside_cycle.rs):
  an undeclared provider beside a wiring cycle whose consumer trait's name begins with the first
  component's; the cycle's overflow is kept, as `[CGP-E020]`.
- [`wiring/unresolved-wiring-name/names_not_imported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/names_not_imported.rs):
  providers, a `#[cgp_impl]` provider, and a path type declared in another module or a dependency
  but not imported; each `E0425` is left as rustc wrote it.
- [`wiring/unresolved-wiring-name/ambiguous_component_names.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/ambiguous_component_names.rs):
  a key two components share the name of, and a guessed key two consumer traits could mean; both
  `E0425`s are left as rustc wrote them.
- [`wiring/unresolved-wiring-name/value_nested_type_not_declared.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_nested_type_not_declared.rs):
  an undeclared type nested in a value's generic arguments, left as rustc wrote it.

## Related

- [`delegate_components!`](../../reference/macros/delegate_components.md): the table whose entries
  carry the names, and its Known issues on an undeclared provider.
- [`#[cgp_component]`](../../reference/macros/cgp_component.md) and
  [`#[cgp_type]`](../../reference/macros/cgp_type.md): how a component's marker is named.
- [`#[cgp_impl]`](../../reference/macros/cgp_impl.md): the `new` keyword that declares a provider.
- [Conflicting wiring](conflicting-wiring.md): the sibling class, where the names resolve but two
  entries claim one key.
- [Wrong component half](../lowering/wrong-component-half.md): the same consumer/provider confusion
  in a provider definition rather than a wiring key.
- [`E0425`](../error_codes/e0425.md), [`E0782`](../error_codes/e0782.md), and
  [`E0275`](../error_codes/e0275.md): the Rust error codes this class is reported under.
