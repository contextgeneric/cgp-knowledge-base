# Unresolved wiring name

A `delegate_components!` entry names something that does not exist where the wiring is written (a
component not in scope, a key guessed from a trait's name, a provider never declared, a type in an
`@`-path never declared) or a consumer trait where a component belongs, or a provider header derives
a component that is not in scope there, so the compiler reports the name itself (`E0425` "cannot
find type", or `E0782` "expected a type, found a trait"), with suggestions that do not fit wiring.

## What triggers it

This class is a failure of the names in a wiring entry, not of what they wire.
[`delegate_components!`](../../reference/macros/delegate_components.md) writes each entry
`Key: Value` into an impl, `impl DelegateComponent<Key> for Context { type Delegate = Value; }`, so
the key must name a component marker and the value a provider type, both in scope where the table is
written. The macro copies the names as written and cannot check them, because which items exist and
what they are is known only to the compiler, so a wrong name is an
[acceptable failure](../../implementation/writing-guide.md#documenting-how-a-macros-expansion-can-fail-to-compile)
that CGP defers to it. A `#[cgp_impl]` or `#[cgp_provider]` header names a component too, without
writing it: the macro derives the key from the provider trait's path, so the same failure reaches a
provider. Its shapes differ in what the name gets wrong.

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

### A provider header whose component is not in scope

[`#[cgp_impl]`](../../reference/macros/cgp_impl.md) and
[`#[cgp_provider]`](../../reference/macros/cgp_provider.md) derive a provider's component from the
provider trait's path as written, appending `Component` to its last segment, so a provider in
another module than its component imports the key beside the trait:

```rust
mod providers {
    use cgp::prelude::*;

    use crate::components::Greeter; // and `GreeterComponent`

    #[cgp_impl(new GreetHello)]
    impl Greeter {
        fn greet(&self) -> String {
            "Hello".to_owned()
        }
    }
}
```

A header that names the trait by its path, `impl crate::components::Greeter`, derives
`crate::components::GreeterComponent` and needs no import. A path through a module that re-exports
the trait without its key, `impl crate::facade::Greeter`, derives a key that module lacks.

### A provider header that derives another component's name

The derived name is the trait's name as the header writes it, so it names nothing when that is not
the component's name: a trait imported under another name (`use crate::components::Greeter as G;`
and `impl G` derive `GComponent`), or a component whose `name:` renames its key (`AreaComponent`)
or gives it parameters (`AreaCalculatorComponent<Shape>`):

```rust
#[cgp_component {
    name: AreaComponent,
    provider: AreaCalculator,
}]
pub trait CanCalculateArea {
    fn area(&self) -> f64;
}

#[cgp_impl(new UnitArea)] // derives `AreaCalculatorComponent`
impl AreaCalculator {
    fn area(&self) -> f64 {
        1.0
    }
}
```

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
- **A provider header whose component is not in scope:** an `E0425` "cannot find type
  `GreeterComponent` in this scope" on the trait's name in the header, the span the macro gives the
  key. For a key of the same crate, rustc suggests the import on the module's first `use` line. For
  a key of a dependency it suggests none on stable, only "you might be missing a type parameter",
  and on the pinned nightly one only for a key the dependency defines in its own module, since its
  import search does not enter a crate the dependency re-exports. A header through a module that
  re-exports the trait alone reads "cannot find type `GreeterComponent` in module
  `crate::facade`", with an import help and one that rewrites the header to `impl Greeter`.
- **A provider header that derives another component's name:** an `E0425` "cannot find type
  `GComponent`" on the trait's name, with no suggestion, or "you might be missing a type parameter"
  for a `#[cgp_provider]` header, and an `unused_imports` warning on a correct import of the real
  key. A key with parameters gives an `E0107` "missing generics for struct
  `AreaCalculatorComponent`" there instead, whose help adds the argument after the trait's name
  (`impl AreaCalculator<Shape><Square>`), which does not reach the key.
- **A provider that is never declared:** an `E0425` "cannot find type `GreetHello` in this scope"
  at the `#[cgp_impl]` attribute and again at the wiring value. A misspelled value alone gets one,
  whose `help:` suggests a similarly named trait, often the provider trait (`Greeter` for
  `GreetHi`), which cannot be a value.

## Where the root cause is

The root cause is **present and at the caret**: the error names exactly the token to change. The
output does not say what the token should be, and its suggestions point elsewhere: a `dyn`, a type
parameter, a similarly named trait or component, none of which is a wiring fix. The landmark is an
`E0425` or `E0782` whose caret sits on a key or a value inside a `delegate_components!` block, on
the provider of a `#[cgp_impl]` header, or on the provider trait's name in a `#[cgp_impl]` or
`#[cgp_provider]` header, whose message names a `…Component`.

## How cargo-cgp presents it

`cargo-cgp` reshapes each shape into one error that says what the name is and carries the fix in a
`help`, keeping `rustc`'s code. The codes are defined in the
[cargo-cgp error-code catalog](../../../cargo-cgp/error-code.md) (summarized in
[cargo-cgp-codes.md](../error_codes/cargo-cgp-codes.md)):

- **`[CGP-E040]`** for a consumer trait as a key:
  ``the wiring key `CanGreet` is a consumer trait, but a key names a component``, and
  ``help: name its component instead: `GreeterComponent` ``.
- **`[CGP-E041]`** for a component not in scope:
  ``the component `ErrorTypeProviderComponent` is not in scope``, and `help: import the component`
  with `use cgp::core::error::ErrorTypeProviderComponent;` as the line it inserts, the shortest
  public path from a dependency (or a `crate::` path for a local component), with rustc's
  suggestions dropped. The fix also spans the name the error points at, so an editor offers it
  there, and it is machine-applicable when one path imports the component.
  At a provider header, the same code names the trait's component with the same fix; for a header
  through a module that re-exports the trait alone it reads
  ``the component `GreeterComponent` is not in module `crate::facade` ``, with a `note` that the
  macro names the component through that module and a `help` naming the trait through the module
  that defines its component, or re-exporting the component.
- **`[CGP-E070]`** for a provider header that derives another component's name:
  ``the header derives the component `AreaCalculatorComponent` from the trait name `AreaCalculator`, but the component of `AreaCalculator` is `AreaComponent` ``,
  and ``help: name the component in the attribute: `#[cgp_impl(new UnitArea: AreaComponent)]` ``.
  A key with parameters takes the header's arguments in that form
  (`AreaCalculatorComponent<Square>`); a renamed import's `help` also offers importing the trait
  under its own name, and its `note` explains the unused-import warning.
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
- **A provider header:** the component's key imported beside its provider trait, the trait named by
  the path of the module that defines its key, or, for a trait imported under another name or a key
  that `name:` renames, the key named in the attribute, as
  `#[cgp_impl(new UnitArea: AreaComponent)]` or `#[cgp_provider(AreaComponent)]`.

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
- [`wiring/unresolved-wiring-name/provider_header_key_not_imported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_header_key_not_imported.rs):
  a `#[cgp_impl]` and a `#[cgp_provider]` header importing a local provider trait without its key;
  `[CGP-E041]` names the `crate::` path at each.
- [`wiring/unresolved-wiring-name/provider_header_dependency_key_not_imported.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_header_dependency_key_not_imported.rs):
  headers importing a library's provider traits without their keys, one defined in a library
  module, one in a crate the library re-exports, and `cgp`'s `ErrorTypeProvider`; `[CGP-E041]`
  names each key's public path.
- [`wiring/unresolved-wiring-name/component_import_fix.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/component_import_fix.rs):
  headers and a wiring key missing their keys, in modules with and without `use` lines; its JSON
  pins `[CGP-E041]`'s fix, machine-applicable for keys one path reaches and maybe correct for one
  two paths reach.
- [`wiring/unresolved-wiring-name/provider_header_facade.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_header_facade.rs):
  a header naming the trait through a module that re-exports it alone; `[CGP-E041]` in its module
  form.
- [`wiring/unresolved-wiring-name/provider_header_renamed_import.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_header_renamed_import.rs):
  a `#[cgp_impl]` and a `#[cgp_provider]` header naming the trait under another name;
  `[CGP-E070]` names `GreeterComponent` and each attribute's form.
- [`wiring/unresolved-wiring-name/provider_header_renamed_key.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_header_renamed_key.rs):
  a header for a component whose `name:` renames its key; `[CGP-E070]`.
- [`wiring/unresolved-wiring-name/parameterized_name_default_component.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/parameterized_name_default_component.rs):
  a header for a component whose key takes a parameter; `[CGP-E070]` replaces the `E0107`.
- [`wiring/unresolved-wiring-name/parameterized_key_trait_arity.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/parameterized_key_trait_arity.rs):
  the same header without the trait's own argument; the trait's arity `E0107` keeps rustc's
  wording beside the `[CGP-E070]`, whose attribute form keeps the key's parameter name.
- [`wiring/unresolved-wiring-name/provider_header_beside_wrong_half.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_header_beside_wrong_half.rs):
  a header missing its key beside a consumer-trait and a non-CGP-trait header; `[CGP-E041]` beside
  `[CGP-E032]` and `[CGP-E033]`, whose own `E0425`s stay dropped.
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
- [`#[cgp_impl]`](../../reference/macros/cgp_impl.md): the `new` keyword that declares a provider,
  and the component a header derives from its provider trait's path.
- [`#[cgp_provider]`](../../reference/macros/cgp_provider.md): the same derivation for a raw provider
  impl.
- [Conflicting wiring](conflicting-wiring.md): the sibling class, where the names resolve but two
  entries claim one key.
- [Wrong component half](../lowering/wrong-component-half.md): the same consumer/provider confusion
  in a provider definition rather than a wiring key.
- [`E0425`](../error_codes/e0425.md), [`E0782`](../error_codes/e0782.md), and
  [`E0275`](../error_codes/e0275.md): the Rust error codes this class is reported under.
