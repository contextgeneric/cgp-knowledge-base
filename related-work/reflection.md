# Reflection and compile-time introspection

Reflection is the ability of a program to inspect a type's own structure (its fields, its variants,
their names and types) and act on it generically. The inspection may happen at runtime through a type
descriptor a framework walks (Bevy, Go, Java) or at compile time through introspection the compiler
evaluates away (Zig's `comptime`, C++26, D, and Rust's nightly reflection). CGP reaches the same
destination as compile-time reflection, one generic routine that works over any type's fields, but takes
the structure not as *data a routine inspects* but as *types the trait system resolves against*. Its
"reflection" is therefore encoded in the type system, checked when the generic code is written rather
than when it is instantiated, and erased before the program runs.

## Purpose

Reflection lets one piece of code work over the *shape* of a type it was not written for. A serializer,
a dependency-injection container, an ORM, a scene editor, a configuration loader, and a debugger's
pretty-printer each need to walk an arbitrary type's fields by name and type without the type's author
hand-writing support for it. Reflection supplies that by making a type's structure available as
something the program can read: a `reflect.Type` value in Go, a `Class` in Java, a `TypeInfo` in Bevy, a
`std.builtin.Type` in Zig, a `std::meta::info` in C++26, a `TypeId` with introspection methods in nightly
Rust. Generic code then loops over that description and does its job for any type at once, instead of
the type's author writing the same boilerplate again and again.

CGP's [extensible-data machinery](../cgp/concepts/extensible-records.md) delivers the same payoff,
which is why the comparison is foundational. The knowledge base's account of extensible records says the
derive "brings the row-polymorphism of languages like PureScript and the structural typing of records to
Rust", and structural, name-driven access to a type's fields is exactly what reflection provides. The
two diverge on *what the structure is made into* and *when the access is checked*. A reflection facility
turns the structure into a value, a descriptor a routine inspects at runtime or in a `comptime` block.
CGP turns it into a *type*, a type-level list a generic routine resolves against through trait
recursion, checked by the compiler at the definition site. This document meets the reader who thinks in
`TypeInfo`, `@typeInfo`, and `#[derive(Reflect)]`, gives Bevy, Zig's `comptime`, and Rust's nightly
reflection full treatment, and then shows where CGP's type-level mirror of reflection lands, grounded in
a real worked example, [`cgp-serde`](https://github.com/contextgeneric/cgp-serde)'s reflection-driven
serializer, set against facet and the Rust MVP. It is the introspection counterpart to the
runtime-mechanism comparison in [dynamic dispatch](dynamic-dispatch.md), and it leans on
[row polymorphism](row-polymorphism.md) for the structural-typing theory underneath.

## The concept in depth

Reflection spans a spectrum from fully runtime to fully compile-time, and CGP sits at one precise end
of it. At the runtime end, a type carries metadata the program inspects while it runs: Java's `Class`,
Go's `reflect.Type`, C#'s reflection with attributes, Python's `__dict__` and `getattr`, and Bevy's
`bevy_reflect`. In the middle, a derive generates a static descriptor that runtime code walks without
re-monomorphizing, the approach Rust's facet takes. At the compile-time end, the compiler evaluates the
introspection during compilation and emits only the specialized result: Zig's `comptime`, D's
`__traits` and CTFE, C++26's static reflection (P2996, voted into C++26 in June 2025, with its `^^`
reflection operator, `std::meta::info` values, and `[: :]` splicers
([P2996R13](https://isocpp.org/files/papers/P2996R13.html))), and now the Rust nightly effort. The three
systems this document treats in full, Bevy at the runtime end, Zig's `comptime` as the compile-time
model, and Rust's MVP as the effort bringing that model to Rust, span the whole spectrum. CGP sits just
past the compile-time end, where the structure is not even a compile-time *value* but a *type*.

The uses are the same all along the spectrum, which is why the comparison to CGP is about mechanism
rather than purpose. Runtime and compile-time reflection alike power serialization (Go's `encoding/json`
on struct tags, Java's Jackson, serde's derive, facet), dependency injection and frameworks (Spring
reflecting over annotations), object-relational mapping (Hibernate), and tooling (editors, debuggers,
test discovery). CGP's extensible-data machinery targets the same jobs: [serialization](https://github.com/contextgeneric/cgp-serde),
builders that assemble a struct from independent parts, and visitors over an enum's variants. The
question this document answers is therefore not *what* reflection is for but *how* each system makes a
type's shape available, and what that choice costs and guarantees.

### Runtime reflection: Bevy

Bevy's [`bevy_reflect`](https://docs.rs/bevy_reflect/latest/bevy_reflect/) (at version 0.19 as of this
writing) is the prominent Rust runtime-reflection system, and it is the runtime counterpart to
everything CGP does statically: a full facility for inspecting, accessing, and mutating a value's
structure while the program runs. It exists because a game engine must do things the type system
cannot fix at compile time. It must load a scene from disk into components whose types are chosen by
the file, drive an inspector UI over arbitrary user components, and serialize a heterogeneous world
without naming every type. `bevy_reflect` gives Rust, a language with no built-in reflection, that
facility as a library, built from a derive, a trait, a descriptor, and a runtime registry.

#### The `Reflect` trait and dynamic value access

The `Reflect` trait makes a value dynamically inspectable, and it is layered on a weaker
`PartialReflect`. The crate documents `PartialReflect` as "the foundational trait of bevy_reflect, used
for accessing and modifying data dynamically", and `Reflect` as the trait "used for downcasting to
concrete types". A type opts in with `#[derive(Reflect)]`, after which a value can be handled as a
`Box<dyn Reflect>`, accessed *by string field name* through the `Struct` subtrait's `field` method, and,
because `Reflect` is stronger than `PartialReflect`, downcast back to its concrete type at runtime with
`try_downcast_ref::<T>()` ([`bevy_reflect` documentation](https://docs.rs/bevy_reflect/latest/bevy_reflect/);
[Bevy reflection overview, Tainted Coders](https://taintedcoders.com/bevy/reflection)). This is the
defining runtime move. The type is erased into `dyn Reflect`, and its structure is recovered by asking
the value at run time rather than by knowing it at compile time. Field access by name returns an
`Option`, so a wrong name is a runtime `None`, not a compile error.

#### `TypeInfo`: the static shape descriptor

Backing the dynamic access is `TypeInfo`, a description of a type's shape that is available without an
instance. The `#[derive(Reflect)]` macro generates a [`TypeInfo`](https://docs.rs/bevy/latest/bevy/reflect/enum.TypeInfo.html)
(a `StructInfo`, `EnumInfo`, `TupleStructInfo`, and so on) enumerating the type's fields or variants
with their names and registered types, "compile-time type information for various reflected types"
made accessible at runtime. This is the descriptor a generic routine walks. A serializer iterates a
`StructInfo`'s fields, a UI builds one widget per named field, and each is written once against
`TypeInfo` rather than per concrete type. It is the runtime-reflection analogue of Zig's `@typeInfo`
result and of CGP's `Fields` type: the same field-and-variant listing, made into a value read at run
time.

#### The type registry and what it powers

The runtime `TypeRegistry` turns per-type descriptors into a working framework. The derive also
generates a `GetTypeRegistration` impl, and registering a type stores its `TypeInfo` together with
associated `TypeData`, extra per-type function tables such as how to serialize it or reflect it as a
component, in a [`TypeRegistry`](https://docs.rs/bevy/latest/bevy/reflect/struct.TypeRegistry.html),
which Bevy keeps in the world as the `AppTypeRegistry` resource. With a type registered, Bevy can look
it up by name or `TypeId` at run time, serialize an arbitrary registered component into a scene through
a `DynamicSceneBuilder`, deserialize a scene back into live components, and drive an editor over types
it was never specialized for. The registry is exactly what a compile-time system does not need and
cannot have: a runtime table mapping types to their structure and behavior, consulted while the program
runs.

#### The cost and the safety surface

Runtime reflection's power is paid for in cost and safety, and Bevy's shape shows both plainly. Every
reflective access goes through dynamic dispatch on `dyn Reflect`, a downcast, or a registry lookup keyed
by type, none of which inline and each of which adds runtime work, the same overhead that makes
reflection-based serialization a known hot-path cost elsewhere. Because access is by string name
against a value whose type is erased, a mismatch (a renamed field, a type never registered, a wrong
downcast) surfaces at run time as a `None`, an error, or a panic, rather than as a compile error. This
is the runtime end of the spectrum in full: maximal flexibility, including over types discovered at run
time, bought with runtime cost and runtime failure modes. It is what CGP trades entirely away.

### Compile-time metaprogramming: Zig's `comptime`

Zig's `comptime` is the reference design for compile-time reflection, and it is the closest functional
analogue of what CGP achieves: the introspection runs during compilation and leaves no trace in the
program. Where Bevy inspects a value at run time, Zig inspects a *type* at compile time and emits only
the specialized result, so a generic-over-structure routine compiles to the code a hand-written one
would. `comptime` is not a reflection API bolted onto the language but a general facility, running
ordinary Zig code at compile time, of which type introspection is one use. That generality is what the
Rust effort admires and cannot yet match. The snippets below were compiled with Zig 0.16.

#### `comptime` values and parameters

Zig can evaluate code and pass values, including types, at compile time. A parameter marked `comptime`
must be known at compile time, and because a *type* is an ordinary `comptime` value of type `type`, a
function can take a type as a parameter and compute with it during compilation
([Comptime, zig.guide](https://zig.guide/language-basics/comptime/)). Generic functions in Zig are
functions with `comptime` type parameters; there is no separate generics feature. This is the substrate
reflection runs on: since types are values the compiler can inspect and manipulate, introspecting one is
calling a builtin on a `comptime` value.

#### `@typeInfo`: a type's structure as comptime data

The builtin `@typeInfo(T)` decomposes a type into structured `comptime` data describing its shape. It
returns a `std.builtin.Type`, a tagged union whose active field says whether `T` is a struct, an enum, a
union, a pointer, an integer, and so on, each carrying the relevant details. Since Zig 0.14 the tags are
spelled in lowercase, so a struct is matched as `.@"struct"` rather than `.Struct`, and each field of a
struct carries a `name`, a `type`, and a `default_value_ptr`
([Zig language reference](https://ziglang.org/documentation/master/#typeInfo)). This is Zig's
`TypeInfo`, but it is a *compile-time* value: it exists only during compilation, and code that reads it
is evaluated away. It is the direct ancestor of Rust's nightly introspection and the compile-time twin of
Bevy's runtime `TypeInfo`.

#### `inline for` and `@field`: iterating the shape

Reflection becomes useful through `inline for`, which unrolls a loop over a `comptime` collection, and
`@field`, which accesses a field by a `comptime`-known name. The canonical pattern reads a type's fields
with `std.meta.fields`, iterates them with an unrolled `inline for`, and reaches each field's value with
`@field`. This version writes any struct as a JSON-like object and compiles with Zig 0.16:

```zig
const std = @import("std");

fn jsonStringify(value: anytype, writer: anytype) !void {
    try writer.writeAll("{");
    inline for (std.meta.fields(@TypeOf(value)), 0..) |field, i| {
        if (i > 0) try writer.writeAll(", ");
        try writer.print("\"{s}\": {any}", .{ field.name, @field(value, field.name) });
    }
    try writer.writeAll("}");
}
```

This writes one serializer that works over any struct. Because `inline for` unrolls at compile time and
`@field` resolves statically, it compiles to the code a hand-written serializer would, "the
expressiveness of runtime reflection with the performance of hand-written code"
([*Compile-Time Reflection with @typeInfo*](https://hive.blog/hive-196387/@scipio/learn-zig-series-32-compile-time-reflection-with-typeinfo)).
The `field.name` is the reflected field name recovered as a compile-time string, the counterpart of what
every reflection system stores and of CGP's `Tag::VALUE`. A real recursive serializer would switch on
`@typeInfo(field.type)` to decide how to write each field; this one formats every field with `{any}`.

#### `@Type`: reflection in reverse

Zig's introspection runs in both directions, which most reflection facilities lack. `@Type` *constructs*
a type from a `std.builtin.Type` value. Where `@typeInfo` reads a type into data, `@Type` writes data
back into a type, so a program can compute a new struct's field list at compile time and materialize it
as a real type ([Zig language reference](https://ziglang.org/documentation/master/#Type)). This is
compile-time type synthesis, the analogue of C++26's splicers, and CGP cannot do it. CGP can build
type-level *lists* and partial-record companions, but it cannot synthesize a new nominal type from
computed structure.

#### Zero cost, checked at instantiation

The defining trade of `comptime` is that it is zero-cost but checked late. Because all of it runs at
compile time, a `comptime` routine leaves no runtime metadata, no dispatch, and no cost, the payoff CGP
also claims. But `comptime`, like C++ templates, is checked at *instantiation*. A generic `comptime`
routine is fully type-checked only when applied to a concrete type, so an error inside it surfaces at
the use site, per instantiation, in the template-error style Zig shares with C++. There is no separate
declaration-site check that a `comptime` function is well-formed for all valid inputs. This is the one
axis on which CGP diverges sharply from the model it otherwise mirrors, and a later section develops it.

### Compile-time reflection comes to Rust

Rust has historically had no reflection at all, and the effort to add compile-time reflection is now
concrete enough to study from its source and tracking issues. It matters to CGP because its stated goal
is to supply, from the compiler, exactly the structural information CGP's derives generate by hand. The
picture has three parts: the userspace crates that filled the gap, the nightly compiler MVP and its
current shape, and the design questions still open before it can stabilize. Everything below about the
nightly API was read from the compiler source on the day of writing; it is unstable and will change.

#### Why Rust had none, and the userspace answers

Rust filled the absence of reflection with `#[derive]` proc macros that generate specialized code per
type, and the cost of that choice motivates the reflection effort. The prominent userspace attempt, the
[**facet**](https://fasterthanli.me/articles/introducing-facet-reflection-for-rust) crate, makes the
argument sharply. serde's derives generate *monomorphized code* for each type, so `serde_json::to_string_pretty`
is instantiated anew for every type, dozens of specialized copies, bloating compile times and binaries,
with `syn` "often in the critical path of builds". Facet's `#[derive(Facet)]` instead generates *data*:
a compile-time `const SHAPE: &Shape` descriptor holding each field's name, offset, type shape, and
function pointers, which generic *runtime* reflection code walks once instead of being re-monomorphized
per type. Facet is therefore runtime reflection driven by compile-time-generated const data, a point
between Bevy's fully runtime registry and Zig's fully compile-time introspection. The narrower
[`dtolnay/reflect`](https://github.com/dtolnay/reflect) is a proof of concept in a different direction:
a compile-time reflection API for writing proc macros.

#### The nightly MVP: `core::mem::type_info`

The nightly compiler effort is the more consequential development. Its [tracking issue #146922](https://github.com/rust-lang/rust/issues/146922),
opened in September 2025 and active into 2026, records the feature gate `#![feature(type_info)]` and
consolidates an earlier [reflection tracking issue #142577](https://github.com/rust-lang/rust/issues/142577)
that Oli Scherer (`oli-obk`) opened in June 2025. The API lives in
[`library/core/src/mem/type_info.rs`](https://github.com/rust-lang/rust/blob/master/library/core/src/mem/type_info.rs)
and has two halves. The first classifies a type: `Type::of::<T>()` returns a `Type` whose single field
is a `kind: TypeKind`, and `TypeId::info()` does the same from a `TypeId`:

```rust
#![feature(type_info)]
use core::mem::{Type, TypeKind};

const KIND: TypeKind = Type::of::<(u32, bool)>().kind; // TypeKind::Tuple
```

`TypeKind` now has variants `Tuple`, `Array`, `Slice`, `DynTrait`, `Struct`, `Enum`, `Union`, `Bool`,
`Char`, `Int`, `Float`, `Str`, `Reference`, `Pointer`, `FnPtr`, and `Other`, grown from the
[tuples-first MVP (PR #146923)](https://github.com/rust-lang/rust/pull/146923) through dedicated PRs
for [ADTs (#151142)](https://github.com/rust-lang/rust/pull/151142),
[trait objects (#151239)](https://github.com/rust-lang/rust/pull/151239), and
[function pointers (#152173)](https://github.com/rust-lang/rust/pull/152173). The second half is what
matters for the CGP comparison: a type's fields and variants are reached through query methods on
`TypeId`, indexed by source order, rather than through a descriptor struct. `variants()` counts an
enum's variants (one for a struct), `variant(i)` returns a `VariantId` with a `name()`, `fields(v)`
counts the fields of variant `v`, and `field(v, f)` returns a `FieldId` whose `name()`, `type_id()`, and
`offset()` are the data a reflection consumer needs. The source's own doc tests read:

```rust
#![feature(type_info)]
use std::any::TypeId;

struct Point { x: u32, y: u32 }

assert_eq!(const { TypeId::of::<Point>().fields(0) }, 2);
assert_eq!(const { TypeId::of::<Point>().field(0, 0).name() }, "x");
assert_eq!(const { TypeId::of::<Point>().field(0, 0).type_id() }, TypeId::of::<u32>());
```

Further queries cover `non_exhaustive()`, `generics()` (a slice of `Generic::Lifetime`, `Type`, or
`Const`), `size()`, `is_signed()`, `element_ty()`, `array_len()`, `points_to()`, `points_mutably()`, and
`function_ptr()`. Trait reflection lives beside it in `core::any`: `TypeId::trait_info_of::<dyn Trait>()`
returns an `Option<TraitImpl<T>>` whose `get_vtable()` yields the `DynMetadata` for building a fat
pointer ([PR #152003](https://github.com/rust-lang/rust/pull/152003), merged February 2026). The
surface has therefore moved well past "tuples or bust", and the remaining work is stabilization rather
than more kinds.

#### Compile-time-only: the `#[rustc_comptime]` restriction

The single most important design decision is that this reflection is callable *only at compile time*,
and the source enforces it. `TypeId::info` is documented "It can only be called at compile time", and
every query method carries a `#[rustc_comptime]` attribute, a compiler marker that pins it to
compile-time evaluation. The [project goal](https://rust-lang.github.io/rust-project-goals/2026/reflection-and-comptime.html)
states the reason: supporting runtime calls would require "some global table somewhere that maps all
`TypeId`s to their repr", which it calls "an obvious no-go". By restricting reflection to `const`
contexts, Rust keeps the zero-cost property. The reflection is evaluated during compilation and nothing
about it survives into the running program, exactly as in Zig `comptime`. A visible tension the source
flags is lifetimes: `Type::of` yields `TypeId`s "not necessarily derived from types that outlive
`'static`", which "will be able to break invariants that other `TypeId` consuming crates may have
assumed", and a dedicated PR for non-`'static` reflection ([#152381](https://github.com/rust-lang/rust/pull/152381))
is part of the linked work.

#### How Zig's `comptime` inspired it, and why Rust chose const-fn reflection

The relationship to Zig's `comptime` is inspiration without adoption, and the project goal is explicit
about it. Zig demonstrated that first-class compile-time type introspection combined with compile-time
code execution can subsume both runtime reflection and macro-based codegen at zero cost, which is the
facility the Rust effort wants. The goal is even named "reflection *and comptime*", and the
`#[rustc_comptime]` marker borrows the word. But the goal **declines full Zig-style `comptime` for
now**, "because the compiler is not set up in a way to permit proc macros from accessing type
information from the current crate", and estimates the architectural change at "more than 5 years
away". The pragmatic path is `const fn` introspection over `TypeId`: `comptime`'s ambition narrowed to
what Rust's architecture can deliver soon, with general `comptime` much later and Zig as the
acknowledged model rather than the immediate target.

#### The road to stabilization: open questions and the RFC

Despite the implemented surface, the feature is at the very start of the stabilization process, and the
tracking issue is candid about what remains. Its checklist has every box unchecked: implement the goal,
discuss general reflection with the lang team, discuss the non-`'static` `TypeId` question, write an
RFC, update documentation, and only then a stabilization PR. Its unresolved questions cut to the
foundations: whether to use many fine-grained intrinsics or one intrinsic returning an enum, what semver
guarantees reflection can retain, whether reflection should exist at all given that it "allows causing
monomorphization-time errors ... for much more fine-grained details of a generic parameter `T`", whether
anything lifetime-aware is possible, and whether a non-const-eval scheme (const generics, or proc macros)
would be better. Oli Scherer champions the effort on the compiler side, with Scott McMurray for lang
and Josh Triplett for libs-api, and the plan spans 2026 to 2028: expand and refine the surface, validate
it by giving `facet`, `bevy_reflect`, and `reflect` a nightly feature that "obsoletes having derives and
makes the derives no-ops", and only then seek lang and libs-api buy-in and write the RFC. The ambition is
that crates like Bevy will "just work" with arbitrary types instead of requiring authors to
`#[derive(Component)]`.

## How CGP expresses it

CGP reaches compile-time reflection's payoff by a different route. It encodes a type's structure as
*types* and processes them with *trait resolution*, so the type system does the "reflection" rather
than a routine inspecting a descriptor. A struct's shape becomes a type-level list through a
[derive](../cgp/reference/derives/derive_has_fields.md), generic code recurses over that list through
trait impls the way Zig's `inline for` iterates `@typeInfo`, and the whole computation is checked at the
definition site and erased before runtime. The [`cgp-serde`](https://github.com/contextgeneric/cgp-serde)
crate makes the parallel concrete, and set against facet and the Rust MVP it shows exactly where the
type-level encoding differs from value reflection. Its serializer wires an **environmental context**: the
`Self` of `SerializeFields` is an application such as `AppA`, and the serialized `Value` is a parameter.

### A type's shape becomes a type, not a descriptor

The foundational move is that `#[derive(HasFields)]` lifts a struct's structure into the type system as
a type-level list, CGP's form of the `TypeInfo`, `Shape`, `std.builtin.Type`, and `FieldId` descriptors
the reflection systems build. Deriving it gives a struct a `Fields` associated type that is a
[`Product!`](../cgp/reference/macros/product.md) of [`Field<Symbol!("name"), Type>`](../cgp/reference/types/field.md)
entries, and an enum a [`Sum!`](../cgp/reference/macros/sum.md) of them:

```rust
#[derive(HasFields)]
pub struct Config {
    pub host: String,
    pub port: u16,
}

// generated:
// impl HasFields for Config {
//     type Fields = Product![
//         Field<Symbol!("host"), String>,
//         Field<Symbol!("port"), u16>,
//     ];
// }
```

This is the same information a reflection descriptor carries, each field's name and type, but it is a
*type*, not a value. The Rust MVP's `FieldId` answers `name()` with a `&'static str` and `type_id()` with
a `TypeId`. CGP's `Field<Tag, Value>` is a *type* whose `Tag` is a type-level
[`Symbol!`](../cgp/reference/macros/symbol.md) string and whose `Value` is the field's actual type as a
type parameter. That difference, the field type carried as a *type* rather than an opaque `TypeId`
value, is what lets CGP dispatch on it, and it is the crux of the comparison below.

### `cgp-serde`: reflection-driven serialization in the trait system

The `cgp-serde` crate's [`SerializeFields`](https://github.com/contextgeneric/cgp-serde/blob/main/crates/cgp-serde/src/providers/fields.rs)
provider is a complete, working example of compile-time reflection expressed entirely through traits:
one generic serializer that works over any `HasFields` type, the CGP counterpart of the Zig
`jsonStringify` above. It serializes any value whose shape is known to the type system as a map,
delegating to a trait that recurses over the field list:

```rust
#[cgp_impl(new SerializeFields)]
impl<Value> ValueSerializer<Value>
where
    Value: HasFields,
    Value::Fields: FieldsSerializer<Self, Value>,
{
    fn serialize<S>(&self, value: &Value, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        let s = serializer.serialize_map(None)?;
        Value::Fields::serialize_fields(self, value, s)
    }
}
```

The `FieldsSerializer` trait is the `inline for` of CGP: a recursion over the
[`Cons`/`Nil`](../cgp/reference/types/cons.md) product list, with a recursive-step impl for a non-empty
list and a base-case impl for the empty one:

```rust
impl<Context, Value, Tag, FieldValue, Rest> FieldsSerializer<Context, Value>
    for Cons<Field<Tag, FieldValue>, Rest>
where
    Tag: StaticString,                         // the field name, as a const &'static str
    Value: HasField<Tag, Value = FieldValue>,  // read this field from the value
    Context: CanSerializeValue<FieldValue>,    // serialize the field through the context's wiring
    Rest: FieldsSerializer<Context, Value>,    // recurse on the remaining fields
{
    fn serialize_fields<S: SerializeMap>(context: &Context, value: &Value, mut serializer: S)
        -> Result<S::Ok, S::Error>
    {
        let field_value = value.get_field(PhantomData);
        serializer.serialize_entry(Tag::VALUE, &SerializeWithContext { context, value: field_value })?;
        Rest::serialize_fields(context, value, serializer)
    }
}

impl<Context, Value> FieldsSerializer<Context, Value> for Nil { /* serializer.end() */ }
```

Every reflection concept has a precise counterpart here. The recursion over `Cons`/`Nil` is the loop
over the field list. `Tag::VALUE`, the field name recovered as a compile-time `&'static str` through the
[`StaticString`](../cgp/reference/traits/static_format.md) trait, is the `field.name` a reflection
system reads, produced with no runtime metadata. `value.get_field(PhantomData)` is the by-name field
access, resolved statically through [`HasField`](../cgp/reference/traits/has_field.md) rather than by a
runtime lookup or a `@field` builtin. And `Context: CanSerializeValue<FieldValue>` is the *recursive*
step: serializing each field's value by dispatching on the field's *type*, which routes back through the
context's own serialization wiring. The deserialization dual,
[`DeserializeRecordFields`](https://github.com/contextgeneric/cgp-serde/blob/main/crates/cgp-serde/src/providers/record.rs),
is even more visibly reflective. It reads a field name as a runtime `String` from the input map and
compares it against each field's compile-time `Tag::VALUE`, routing the value into a `SetOptional`
builder: reflection reading names in both directions.

### `cgp-serde` versus facet versus the reflection MVP

The three approaches solve the same problem, write serialization once rather than per type, and
comparing them shows what the type-level encoding buys and costs. The organizing axis is *what a type's
shape is turned into, and how the generic code consumes it*:

- **serde's derive** generates *code*: a bespoke `Serialize` impl per struct. The logic is duplicated
  through generated code for every type, which is the compile-time and binary bloat facet objects to.
- **facet** generates *data*: a `const SHAPE: &Shape` value per type, walked by a shared *runtime*
  reflection routine. It avoids re-monomorphizing the serializer per type, shrinking the binary, but
  pays runtime reflection cost to walk the shape and dispatch through the shape's function pointers.
- **the Rust MVP** has the *compiler* provide the data: `TypeId::of::<T>().field(0, i)` yields each
  field's name, type id, and offset, needing no derive at all, consumed by `const`-evaluated code at
  compile time.
- **`cgp-serde`** generates *type-level data*: a `Product!` of `Field<Tag, Value>` through the
  `HasFields` derive, walked by a shared *compile-time* routine, `FieldsSerializer` trait recursion,
  that monomorphizes and inlines to direct code.

Two differences make CGP's position distinct rather than merely another point. First, the field's *type*
is preserved as a *type*, not erased to a value. Facet's `Shape` and the MVP's `FieldId::type_id()`
carry the field's type as an opaque descriptor, a `Shape` pointer or a `TypeId`, from which a generic
function cannot be instantiated directly. Recursion into a field's own type is therefore mediated by
stored function pointers (facet) or is not yet expressible from the raw reflection (the MVP). CGP's
`Field<Tag, FieldValue>` carries `FieldValue` as a real type parameter, so `SerializeFields` can write
`Context: CanSerializeValue<FieldValue>` and recurse into a fully typed, statically checked serializer
for the field's type, the recursion a `TypeId` cannot drive. Second, `cgp-serde` dispatches each field
through the *context's* `CanSerializeValue` wiring, so the same type serializes differently under
different application contexts, the [per-context choice](../cgp/concepts/coherence.md) that facet,
serde, and the MVP, each with one fixed interpretation per type, do not have.

The honest costs are equally clear. Unlike facet, `cgp-serde` does *not* solve the monomorphization
problem. Its `FieldsSerializer` recursion instantiates per field list, so it produces specialized code
per type just as serde's output does. What it saves is the *authoring* duplication (the logic is written
once) and what it gains is *configurability* (the wiring), not binary size. And unlike the Rust MVP,
`cgp-serde` requires the `#[derive(HasFields)]` opt-in. It cannot serialize a foreign type that did not
derive the machinery, exactly the restriction the MVP is designed to remove for value-reflection
consumers.

### Checked when the code is written, not when it is instantiated

*When* generic-over-structure code is checked separates CGP from `comptime`, from C++ templates, and
from const-fn reflection, and CGP checks it early. Zig's `comptime` and the MVP's `const fn` reflection
are checked at *instantiation*: a `comptime` routine or a reflection-driven `const fn` is fully checked
only when applied to a concrete type, so an error surfaces at the use site, per instantiation. CGP's
generic code is checked at its *definition*. The `where` clause on the `FieldsSerializer` impl
(`Tag: StaticString`, `Value: HasField<Tag>`, `Context: CanSerializeValue<FieldValue>`) is verified once
against the bounds, and [`check_components!`](../cgp/reference/macros/check_components.md) verifies that
a context supplies everything its wiring transitively needs. This is the modular type checking that
[type classes](type-classes.md) give and templates do not, and CGP inherits it because its reflection is
expressed as trait bounds the compiler checks up front rather than as code re-checked at each
instantiation.

### Reflection that also selects behavior and configures types

CGP applies the same type-level-shape idea beyond inspecting data, to two things a structural reflection
facility does not directly address: choosing implementations and fixing abstract types. Reflection
systems inspect a type's fields and values, and some frameworks then use that to select behavior. Spring
wires beans by reflecting over annotations, and Bevy associates `TypeData` with registered types. So
behavior selection by reflection is real, but it is a runtime, registry-mediated act layered on top of
the introspection. CGP folds behavior selection into the same compile-time type-level table that carries
its structural information. A [component](../cgp/reference/macros/cgp_component.md) is keyed by a
type-level marker, a context's [`delegate_components!`](../cgp/reference/macros/delegate_components.md)
table maps markers to providers, and the [`#[cgp_type]`](../cgp/reference/macros/cgp_type.md) machinery
lets a context fix an abstract *type*, its `Error` or its `Scalar`, through that same table with
[`UseType<T>`](../cgp/reference/providers/use_type.md). The `cgp-serde` serializer shows this in action.
`Context: CanSerializeValue<FieldValue>` resolves each field's serializer through the context, so the
reflection that walks the shape and the wiring that interprets each field are one mechanism.

### What CGP cannot do

The runtime and open-introspection powers of reflection have no CGP analogue, and the boundary deserves
plain statement. Because CGP's structural information is a type computed at compile time, it cannot
inspect a value whose type is known only at runtime, downcast a `dyn` value, serialize a type discovered
from a plugin loaded at startup, or drive an editor over types registered in a runtime table. Those are
exactly what `bevy_reflect` exists to do, and Bevy's runtime reflection, not CGP, is the right tool for
them. CGP also cannot *construct* an arbitrary new nominal type the way Zig's `@Type` or C++26's
splicers can. Its type-level `Product!` and `Sum!` lists and partial-record companions are a
constrained, closed form of type construction, not open type synthesis. And CGP's structural machinery is
**opt-in per type**. It works only for types that `#[derive(HasFields)]` or
[`#[derive(CgpData)]`](../cgp/reference/derives/derive_cgp_data.md), so it cannot introspect a foreign
type that did not derive it, the same limitation facet and `bevy_reflect` have today, and precisely the
restriction the nightly reflection MVP is being built to lift, though for value consumers rather than
type-level ones.

## What users like and dislike

Reflection is one of the most relied-upon facilities in mainstream software, and the reasons are
consistent. It lets a framework be written once and work over every user type (serialization, dependency
injection, ORMs, editors, test frameworks, and configuration all lean on it), which is why Java, C#, Go,
and Python ship it and why ecosystems form around it. Runtime reflection additionally works on
*arbitrary* types, including ones the framework author never saw, with no cooperation from the type
beyond being reflectable. Compile-time reflection promises the same generality with none of the runtime
cost. Zig's users prize "the expressiveness of runtime reflection with the performance of hand-written
code", and the facet and Rust-reflection efforts are motivated by cutting the compile-time and binary
bloat that per-type derive codegen imposes
([fasterthanli.me](https://fasterthanli.me/articles/introducing-facet-reflection-for-rust)).

The complaints split by when the reflection runs. Runtime reflection is criticized on three counts.
*Performance*: Go's reflection-based `encoding/json` is "fundamentally slow" because it re-inspects
types on every call, and Java reflection is a well-known hot-path cost
([*The Hidden Cost of Reflection in Go*](https://dev.to/devflex-pro/the-hidden-cost-of-reflection-in-go-why-your-code-is-slower-than-you-think-41ee)).
*Type safety*: it "bypasses compile-time type safety" and produces "stringly typed" access where a
field named by a `json:"..."` tag or a `getField("name")` call fails at runtime, "quite like a
dynamically typed language" ([Go reflection guide](https://medium.com/@mojimich2015/golang-reflection-the-guide-to-runtime-type-inspection-manipulation-and-best-practices-303087684576)).
*Tooling and safety*: renaming a field silently breaks reflective access, dead-code elimination must be
defeated to keep metadata, and reflection can bypass access control. Java's *type erasure* adds a
further limit: reflection cannot distinguish `List<Integer>` from `List<Float>` at runtime because the
parameter is gone ([*Linguistic Reflection in Java*](https://arxiv.org/pdf/cs/9810027)). Compile-time
reflection answers the performance and much of the safety objection, since the checks run before the
program does, but trades them for its own costs: instantiation-time error messages in the template and
`comptime` style, added compile-time work, the conceptual weight of metaprogramming, and, as the Rust
tracking issue asks, the risk of enabling "monomorphization-time errors ... for much more fine-grained
details of a generic parameter" that make generic code fail deep inside instantiation rather than at its
interface.

## How CGP compares

CGP and reflection make opposite choices on the two axes that organize the whole spectrum, *when the
structure is available* and *what form it takes*. On *timing*, runtime reflection makes structure
available while the program runs, paying dispatch and inspection cost on every use and deferring errors
to runtime. Compile-time reflection and CGP both resolve it during compilation and pay nothing at
runtime. On *form*, every reflection system, runtime or compile-time, makes the structure into *data*
that code inspects: a `TypeInfo`, a `Shape`, a `std.builtin.Type`, a `FieldId`. CGP makes it into a
*type* that trait resolution dispatches on. That second difference buys CGP its distinctive properties.
Because the structure is a type and the field types are carried as types, generic code is a set of trait
impls checked modularly at their definition rather than per instantiation, it can recurse into a field's
own type with full static checking, and the same type-level encoding extends from inspecting data to
selecting providers and configuring abstract types. What CGP gives up for this is generality and runtime
reach: it introspects only types that opted in by deriving its machinery, and only at compile time.

Honest positioning names where each wins, and here it comes with a twist: CGP and Rust's emerging
compile-time reflection are more complementary than competing. When a program must inspect types at
runtime, to deserialize into a type chosen from a config file, serialize a heterogeneous registry of
components, build an editor or a debugger over live values, or reflect over a foreign type that cannot
be made to derive anything, runtime reflection is the right and only tool of the two, and `bevy_reflect`
or facet, not CGP, is what to reach for. When a program wants generic-over-structure code that costs
nothing at runtime, is checked when written, recurses into field types with full type information, and
drives behavior and type selection as well as data walking, CGP delivers that on stable Rust today, as
`cgp-serde` shows. The two lines could converge, but less directly for CGP than for facet or Bevy. The
nightly MVP produces reflection as *const values* (`TypeId`, `FieldId`, `&'static str`), which
value-reflection libraries consume natively and which the project goal aims to let them use with no
derive. CGP consumes reflection as *types* (`Product!`, `Field<Tag, Value>`), a different projection
the const-value MVP does not supply. For CGP to shed its `#[derive(HasFields)]` the way the goal
envisions for `#[derive(Reflect)]`, the compiler would need to expose a type's shape *as types*, a
type-level counterpart to the value-level MVP that is not part of the current scheme. Until then CGP's
derive stands in for the compiler-provided reflection Rust is still building, and the reflection MVP is
best read not as a rival to CGP but as the same underlying idea, reflected into values where CGP
reflects it into types.

## Presenting CGP to someone who knows this

A reader who thinks in `TypeInfo`, `@typeInfo`, or `TypeId::field` holds most of CGP's structural
machinery already, so map the vocabulary and then mark the one shift. A `#[derive(HasFields)]` type's
`Fields` is a **compile-time type descriptor**, exactly like a `Shape`, a `std.builtin.Type`, or the
MVP's field queries, except that it is a *type*, not a value. A generic impl recursing over the
[`Cons`/`Nil`](../cgp/reference/types/cons.md) list, as `cgp-serde`'s `FieldsSerializer` does, is an
**`inline for` over the fields**, resolved by the trait system instead of a `comptime` loop or a
const-fn walk. `Tag::VALUE` is the reflected **field name**. And
[`check_components!`](../cgp/reference/macros/check_components.md) guarantees that the generic code
type-checks for this concrete type, discharged when the code is written rather than at instantiation.
Framed this way, CGP is *compile-time reflection encoded in the type system*: the Zig `comptime` idea
they know, expressed as trait resolution over type-level shapes, with the modular checking they may wish
`comptime` and templates had.

Correct at once the expectation that CGP offers a reflection *API*: an object to inspect, a descriptor to
query, a value to walk. It does not. There is no `TypeInfo` to hold, no field list to iterate
imperatively, no `TypeId::of::<T>()` to call. The structure is a type that trait impls dispatch on, so
"reflecting" over it means writing a recursive impl, not calling `fields()`. For the Zig or C++26
reader, the sharp framing is that CGP's `Product!` and `Sum!` are the `@typeInfo` result reified as
types and its trait recursion is the `inline for`, but CGP cannot `@Type`-construct arbitrary new types
and cannot introspect a type that did not derive the shape, a real limit against a true reflection
facility. For the Rust reflection reader, the precise point is that CGP carries a field's *type as a
type* where the MVP's `FieldId` carries it as an opaque `TypeId`, which is why CGP can recurse into a
typed, checked serializer for each field and the raw MVP cannot yet. The two encode the same shape but
project it into different domains, values versus types. For the Bevy or Java reader, the pitch is the
pair of things runtime reflection makes them pay for and CGP does not: *no runtime cost*, because the
introspection is resolved away instead of walked on every call, and *no stringly typed runtime failure*,
because a field or trait the context lacks is a compile error at the wiring site rather than a `None` or
an exception in production.

Avoid calling CGP "a reflection system". It has no runtime type information, no descriptor to inspect,
and no ability to reflect over a type that did not opt in, and a reader sold on that framing will look
for an introspection API and find trait bounds instead. Say precisely what CGP is: compile-time
structural reflection encoded as types and resolved by the trait system, checked at the definition site,
erased before runtime, carrying field types as types so it can recurse into them, and extended from
inspecting a type's data to selecting its behavior and configuring its abstract types. A reader who has
paid the runtime tax of reflection, or fought a template's instantiation-time errors, will hear that as a
considered trade rather than a missing feature.

## Sources

The public version of this document is the website's
[reflection comparison page](https://contextgeneric.dev/docs/comparisons/reflection), ported per the
[comparison page guide](../website/writing-guides/related-work.md); a change here updates that page
in the same change.

The account of the related work draws on the official documentation and primary write-ups of each
reflection system, the Rust project's own tracking issues, pull requests, and library source for its
compile-time-reflection effort, and cited community writing for sentiment. The Zig snippet was compiled
with Zig 0.16; the Rust snippets are the nightly source's own doc tests; the CGP snippets are taken from
the [`cgp-serde`](https://github.com/contextgeneric/cgp-serde) source and the knowledge base's
[extensible records](../cgp/concepts/extensible-records.md) and
[extensible variants](../cgp/concepts/extensible-variants.md) material.

- [Bevy `bevy_reflect` documentation](https://docs.rs/bevy_reflect/latest/bevy_reflect/), [`Reflect` trait](https://docs.rs/bevy/latest/bevy/reflect/trait.Reflect.html), [`TypeInfo`](https://docs.rs/bevy/latest/bevy/reflect/enum.TypeInfo.html), [`TypeRegistry`](https://docs.rs/bevy/latest/bevy/reflect/struct.TypeRegistry.html), and [Bevy Reflection (Tainted Coders)](https://taintedcoders.com/bevy/reflection) — the `Reflect`/`PartialReflect` traits, `TypeInfo`, the runtime `TypeRegistry` and `AppTypeRegistry`, `#[derive(Reflect)]`, downcasting, `TypeData`, and scene serialization that make Bevy the Rust runtime-reflection exemplar.
- [Zig language reference](https://ziglang.org/documentation/master/), [Comptime (zig.guide)](https://zig.guide/language-basics/comptime/), and [*Compile-Time Reflection with @typeInfo*](https://hive.blog/hive-196387/@scipio/learn-zig-series-32-compile-time-reflection-with-typeinfo) — `comptime` values and parameters, `@typeInfo` and `@Type`, `std.meta.fields`, `inline for`, `@field`, the lowercase `std.builtin.Type` tags, and the zero-runtime-cost, instantiation-checked model that inspired the other systems languages.
- [Rust tracking issue #146922 (`type_info`)](https://github.com/rust-lang/rust/issues/146922), [tracking issue #142577 (reflection, closed as duplicate)](https://github.com/rust-lang/rust/issues/142577), the source at [`library/core/src/mem/type_info.rs`](https://github.com/rust-lang/rust/blob/master/library/core/src/mem/type_info.rs) and [`library/core/src/any.rs`](https://github.com/rust-lang/rust/blob/master/library/core/src/any.rs), and the implementation PRs [#146923 (MVP)](https://github.com/rust-lang/rust/pull/146923), [#151142 (ADTs)](https://github.com/rust-lang/rust/pull/151142), [#151239 (trait objects)](https://github.com/rust-lang/rust/pull/151239), [#152003 (`trait_info_of`)](https://github.com/rust-lang/rust/pull/152003), [#152173 (`FnPtr`)](https://github.com/rust-lang/rust/pull/152173), and [#152381 (non-`'static` reflection)](https://github.com/rust-lang/rust/pull/152381) — the exact API (`Type::of`, `TypeId::info`, `TypeKind`, the `variant`/`field` queries, `VariantId`, `FieldId`, `TraitImpl`), the `#[rustc_comptime]` compile-time-only restriction, the implemented surface, and the open stabilization checklist and design questions.
- [Rust Project Goals — *Reflection and comptime* (2026)](https://rust-lang.github.io/rust-project-goals/2026/reflection-and-comptime.html) — the plan to make reflection-crate derives no-ops, the explicit rejection of full Zig-style `comptime` near-term and of runtime reflection, the 2026 to 2028 timeline, and the champions (Oli Scherer, Scott McMurray, Josh Triplett).
- [fasterthanli.me, *Introducing facet: Reflection for Rust*](https://fasterthanli.me/articles/introducing-facet-reflection-for-rust) and [`dtolnay/reflect`](https://github.com/dtolnay/reflect) — facet's derive-generates-data approach (a `const Shape` walked by runtime reflection) and its motivation in serde's monomorphization cost, and a compile-time reflection API for proc-macro authors.
- [`cgp-serde` `SerializeFields`](https://github.com/contextgeneric/cgp-serde/blob/main/crates/cgp-serde/src/providers/fields.rs) and [`DeserializeRecordFields`](https://github.com/contextgeneric/cgp-serde/blob/main/crates/cgp-serde/src/providers/record.rs) — the worked CGP example: a generic serializer and deserializer that recurse over a type's `HasFields` shape through trait resolution, recovering field names through `StaticString` and dispatching each field through the context's `CanSerializeValue` wiring.
- [P2996R13, *Reflection for C++26*](https://isocpp.org/files/papers/P2996R13.html) and [*Reflection in C++26 (P2996)*](https://learnmoderncpp.com/2025/07/31/reflection-in-c26-p2996/) — the `^^` reflection operator, `std::meta::info`, `consteval` metafunctions, and splicers `[: :]`, voted into C++26 in June 2025, the C++ realization of compile-time reflection.
- [Go FAQ — reflection and interfaces](https://go.dev/doc/faq), [*The Hidden Cost of Reflection in Go*](https://dev.to/devflex-pro/the-hidden-cost-of-reflection-in-go-why-your-code-is-slower-than-you-think-41ee), [*Golang Reflection guide*](https://medium.com/@mojimich2015/golang-reflection-the-guide-to-runtime-type-inspection-manipulation-and-best-practices-303087684576), and [*Linguistic Reflection in Java*](https://arxiv.org/pdf/cs/9810027) — the `reflect` package and struct tags, the runtime performance and type-safety ("stringly typed") costs, and Java's type-erasure limitation, the mainstream runtime-reflection landscape CGP contrasts with.
