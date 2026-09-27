# `cgp_namespace!`

`cgp_namespace!` defines a *namespace*: a reusable, named lookup table that maps component keys to
providers, so a concrete context can adopt a whole group of wirings at once and supply only the
entries the namespace leaves open.

## Purpose

`cgp_namespace!` makes groups of component wirings reusable across contexts. With
[`delegate_components!`](delegate_components.md) alone, every context spells out its own table, and
two contexts that should share a wiring must repeat it. A namespace lifts that table out of any one
context and names it, so "this set of providers" becomes something other contexts can join and build
on.

The mechanism is a layer of indirection between a context's table and the providers. A namespace is
not a context but a trait, named after the namespace, with a `Delegate` associated type implemented
per key. A context that joins the namespace forwards every lookup it does not wire itself through
that trait, so the namespace's entries become the context's. The forwarding is keyed by a *path*, a
type-level list of symbols and component names, rather than by a bare component name. Paths are what
let one namespace inherit from another, and what let a context fill one path the namespace leaves
open without disturbing the rest.

The result is preset-style configuration. A context says "use everything in this namespace" and adds
its own entries at paths the namespace routes to but leaves unbound. It cannot replace an entry the
namespace binds, because the namespace's entry and the context's would implement the same lookup and
the compiler rejects the overlap, as [Known issues](#known-issues) explains. So a namespace binds
what every joining context shares and leaves open what each one chooses, with no runtime cost.

## Syntax

`cgp_namespace!` is a function-like macro whose body resembles a `delegate_components!` table under
a namespace header. The simplest form declares a new namespace with `new` and lists entries that map
component keys to paths:

```rust
cgp_namespace! {
    new MyNamespace {
        FooProviderComponent =>
            @MyFooComponent,
    }
}
```

The `new` keyword makes the macro also emit the namespace's lookup trait and a marker struct; omit
it only when both are declared elsewhere. `MyNamespace` names the trait, and the entries inside the
braces are the namespace's wiring.

Two entry forms carry a namespace's meaning, and they produce different table contents:

- **A `=>` entry redirects a key to a path.** `FooProviderComponent => @MyFooComponent` means "when
  this namespace is asked for `FooProviderComponent`, look up the path `@MyFooComponent` instead".
- **A `:` entry binds a key to a provider**, as in `delegate_components!`.
  `[String, u64]: ShowWithDisplay` makes the namespace resolve those keys straight to
  `ShowWithDisplay`.

Paths written with the `@` sigil, such as `@MyFooComponent`, `@app.ErrorRaiserComponent`, and
`@cgp.core.error`, are dotted sequences of symbols and type names that become type-level path lists,
following [`Path!`](path.md).

A namespace inherits from a parent by naming it after a colon in the header:

```rust
cgp_namespace! {
    new ExtendedNamespace: DefaultNamespace {
        @cgp.core.error =>
            @app,
    }
}
```

`ExtendedNamespace` resolves every key `DefaultNamespace` resolves, and adds an entry that rewrites
the `@cgp.core.error` path prefix to `@app`. The parent may be parameterized, since it is parsed as
a path with type arguments. A child entry may add keys the parent does not resolve, but not redefine
one it does.

A namespace with no entries of its own may end at its header, with no braces. This matters most for
an inheriting namespace that exists only to declare its trait and struct and forward every key its
parent resolves:

```rust
cgp_namespace! {
    new AppNamespace: DefaultNamespace
}
```

This expands exactly as `new AppNamespace: DefaultNamespace { }` does, and `new AppNamespace` alone
emits just the struct and the trait. The macro reads a missing body as the empty table only when
nothing follows the header, so any other token there fails with `expected curly braces`. Without
`new`, a header-only `AppNamespace: DefaultNamespace` emits only the inheritance impl, so it
compiles only where the `AppNamespace` trait and its `__AppNamespaceComponents` marker are already
declared. The optional body is specific to `cgp_namespace!`;
[`delegate_components!`](delegate_components.md), its nested tables, and the `for` loop keep their
braces even when empty.

Defining a namespace is half of the pattern. A context joins one through `delegate_components!` with
a `namespace` statement, and a component registers into one with the
[`#[prefix(...)]`](../attributes/prefix.md) attribute on its trait. Both are shown under Expansion
and Examples.

### The shared body grammar

`cgp_namespace!` parses its body with the same code [`delegate_components!`](delegate_components.md)
uses, so every form that macro accepts is accepted here: the three operators, the three key forms
including grouped `@`-paths, per-key generics, the nested-table value, and the `open`, `namespace`,
and `for` statements. That macro's Syntax section is the grammar for each; this section covers only
what differs.

What differs is the item each entry lowers to. A `delegate_components!` entry emits
`impl DelegateComponent<Key> for TargetType`, keyed on the component and implemented for the
context. A `cgp_namespace!` entry emits `impl Namespace<__Table__> for Key`, implemented for the key
and generic over whichever table later consults it. So an entry here answers "where should a lookup
for this key go next", not "which provider does this context use".

That difference decides which shared forms are worth writing. `=>` and `:` carry the namespace's
meaning; the others are legal and rarely what a namespace wants:

- **`->`** still projects through the value's `DelegateComponent` table rather than through the
  namespace, so it names a concrete table inside a definition meant to be table-generic.
- **`open Component;`** generates exactly the entry `Component => @Component,` would, which is
  occasionally a convenient way to root a component's route at its own name.
- **`namespace Other;`** emits a forwarding impl, but inheritance is written with the
  `: ParentNamespace` header instead, which is the form the parent chain, its overlaps, and the
  cycle diagnostics under Known issues are defined for.

The nested-table value also works, and putting a dispatch table in the namespace is the reason to
write it here: every context that joins the namespace inherits the per-type wiring.

```rust
cgp_namespace! {
    new NestedNs {
        FooProviderComponent:
            UseDelegate<new FooTable {
                String: DummyFoo,
                u64: DummyFoo,
            }>,
    }
}
```

The macro lifts `FooTable` into its own struct and
[`DelegateComponent`](../traits/delegate_component.md) impls, exactly as
[`delegate_components!`](delegate_components.md) does, and the entry's `Delegate` is
`UseDelegate<FooTable>`. The legacy form needs
[`#[derive_delegate]`](../attributes/derive_delegate.md) on the component here as anywhere; modern
per-type dispatch belongs on the context, through `open`.

The body accepts no attributes on any entry, whether on a mapping key, a `=>` key, or a key inside a
`for` loop, and rejects each with a spanned `unsupported attribute: …` error.

## Syntax Grammar

The body of `cgp_namespace!` is an optional generic list and `new` keyword, a namespace name, an
optional parent, and an optional braced table:

```ebnf
CgpNamespace    -> Generics? `new`? NamespaceName ( `:` ParentNamespace )? ( `{` NamespaceBody `}` )?

NamespaceName   -> IDENTIFIER GenericArgs?
ParentNamespace -> TypePath GenericArgs?

NamespaceBody   -> Statement* ( Mapping ( `,` Mapping )* `,`? )?
```

`NamespaceBody` is [`delegate_components!`](delegate_components.md)'s `TableBody` production
unchanged, so its `Statement` and `Mapping` productions are defined there. The `:` between
`NamespaceName` and `ParentNamespace` is the inheritance colon, distinct from a mapping's `:`.
`NamespaceName` becomes the trait and, with `new`, the prefix of the marker struct's name. A header
followed by nothing parses as an empty `NamespaceBody`, and a header followed by anything but `{` is
a parse error.

Two of the three statements in the shared production are owned here, because they exist to join a
context's table to a namespace:

```ebnf
NamespaceStmt -> `namespace` IDENTIFIER `;`

ForStmt       -> `for` `<` IDENTIFIER `,` IDENTIFIER `>` `in` TypePath WhereClause?
                 `{` ( NormalMapping ( `,` NormalMapping )* `,`? )? `}`
```

A `NamespaceStmt` forwards every lookup on the table through the named namespace, which is written
as a bare identifier. A `ForStmt` binds a key variable and a value variable, reads each entry of the
table named after `in`, and emits one entry per mapping in its body. Its body admits only the `:`
form, which is why [`delegate_components!`](delegate_components.md) names `NormalMapping`
separately. Its optional `WhereClause` is added to every impl the loop generates, so a bound written
there, as in `for <T, P> in Table where T: Clone { … }`, restricts which keys the loop wires. The
third statement, `OpenStmt`, is owned by [`delegate_components!`](delegate_components.md); in a
namespace body it is another spelling of a `=>` entry. `TypePath` and `WhereClause` are Rust grammar
productions.

The `#[prefix(...)]` attribute, the other half of the pattern and hosted by
[`#[cgp_component]`](cgp_component.md), has its own grammar, `PrefixArgs`, defined in
[`#[prefix]`](../attributes/prefix.md); its path is the one [`Path!`](path.md) defines.

## Expansion

`cgp_namespace!` emits, in order, an optional marker struct, an optional lookup trait, the structs
of any nested tables, and then the impls: the inheritance impl first when a parent is named, then
one impl per entry, then the nested tables' impls. Take the `new` namespace with a single redirect
entry:

```rust
cgp_namespace! {
    new MyNamespace {
        FooProviderComponent =>
            @MyFooComponent,
    }
}
```

Because `new` is present, the macro first emits a marker struct named after the namespace as
`__{Name}Components`, then the lookup trait, which carries a `__Table__` parameter and a `Delegate`
associated type:

```rust
pub struct __MyNamespaceComponents;

pub trait MyNamespace<__Table__> {
    type Delegate;
}
```

Each `=>` entry becomes an impl of the trait for the entry's key, whose `Delegate` is a
[`RedirectLookup`](../providers/redirect_lookup.md) that looks the entry's path up in the table:

```rust
impl<__Table__> MyNamespace<__Table__> for FooProviderComponent {
    type Delegate = RedirectLookup<__Table__, PathCons<MyFooComponent, Nil>>;
}
```

Read back, this says that for the key `FooProviderComponent`, the namespace's answer is "look up the
path `MyFooComponent` in whatever table `__Table__` is". The namespace names no provider for this
key; it only reroutes the lookup, and the provider is whatever the path reaches.

A `:` entry maps the key to the provider directly, with no redirect. From the list key
`[String, u64]: ShowWithDisplay`, the macro emits one impl per key:

```rust
impl<__Table__> DefaultShowComponents<__Table__> for String {
    type Delegate = ShowWithDisplay;
}
impl<__Table__> DefaultShowComponents<__Table__> for u64 {
    type Delegate = ShowWithDisplay;
}
```

When a parent is named, the macro emits one extra blanket impl, before the entries, that resolves
every key the parent resolves. For `new ExtendedNamespace: DefaultNamespace { … }`:

```rust
impl<__Table__, __Key__, __Value__> ExtendedNamespace<__Table__> for __Key__
where
    __Key__: DefaultNamespace<__ExtendedNamespaceComponents>,
    __Key__: DefaultNamespace<__Table__, Delegate = __Value__>,
{
    type Delegate = __Value__;
}
```

For any `__Key__` the parent resolves, `ExtendedNamespace` resolves it to the same `__Value__`. The
first bound, which asks the parent about the child's own marker struct, is what makes a cyclic
parent chain fail at the definitions. The child's entries sit beside this blanket impl rather than
overriding it, so they must be keyed on paths the parent does not resolve; a key both resolve is a
conflict, as Known issues explains. The path-rewriting entry `@cgp.core.error => @app` qualifies: it
is keyed on the `cgp.core.error` path prefix, which `DefaultNamespace` routes to without binding,
and its `Delegate` is a `RedirectLookup` onto the `@app` prefix. So it reroutes a whole subtree of
the parent's routes rather than a single component.

The other half of the pattern attaches a component to a namespace. The
[`#[prefix(...)]`](../attributes/prefix.md) attribute on a component's trait adds one impl of the
same shape for the component's marker, with the path ending at the marker.
`#[prefix(@MyBarComponent in MyNamespace)]` on a `Bar` component registers `BarProviderComponent` at
`@MyBarComponent.BarProviderComponent`, so `MyNamespace`, asked for `BarProviderComponent`,
redirects there. That attribute's document shows the emitted impl and every form it accepts.

Two details of the expansion appear verbatim in compiler errors, so they are worth recognizing. The
table parameter is named `__Table__`, and the inheritance impl uses `__Key__` and `__Value__`. And
every path under `@` becomes a `PathCons`/`Symbol`/`Chars` list: `@my_app.MyFooComponent` expands to
`PathCons<Symbol<6, Chars<'m', …>>, PathCons<MyFooComponent, Nil>>`, with lowercase segments
becoming `Symbol` strings and other segments naming the type.

## Examples

A namespace becomes useful once a context joins it and fills what it leaves open. Start with a
namespace of default per-type providers:

```rust
use cgp::prelude::*;

cgp_namespace! {
    new DefaultShowComponents {
        [String, u64]: ShowWithDisplay,
    }
}
```

A context joins a namespace inside `delegate_components!` with a `namespace` statement and may add
entries at paths the namespace does not bind. This one joins `DefaultNamespace` and pulls defaults
in through a `for` loop over `DefaultShowComponents`:

```rust
pub struct AppB;

delegate_components! {
    AppB {
        namespace DefaultNamespace;

        for <T, Provider> in DefaultShowComponents {
            @test.ShowImplComponent.T: Provider,
        }
    }
}
```

The `namespace DefaultNamespace;` statement makes `AppB` answer every lookup it does not wire itself
through `DefaultNamespace<AppB>`. The `for` loop wires `AppB`'s `ShowImplComponent` path for each
type `T` that `DefaultShowComponents` resolves, using that entry's provider.

A direct entry on the same context can supply a type the pulled-in defaults do not cover. Here the
per-type registry `DefaultImpls1<ShowImplComponent>` has a default only for `String`, so the context
adds `u64` itself:

```rust
delegate_components! {
    AppA {
        namespace DefaultNamespace;

        for <T, Provider> in DefaultImpls1<ShowImplComponent> {
            @test.ShowImplComponent.T: Provider,
        }

        @test.ShowImplComponent.u64:
            ShowWithDisplay,   // u64 has no registered default, so the context supplies one
    }
}
```

Had the registry carried a `u64` default as well, the loop's impl and the direct entry would both
cover that path, and the compiler would reject the pair with `E0119`.

Inheritance composes the same way at the namespace level. `ExtendedNamespace: DefaultNamespace`
resolves everything `DefaultNamespace` does plus the child's own entries, and a context joining
`ExtendedNamespace` gets the combined result.

## Related constructs

These constructs are the ones `cgp_namespace!` sits between:

- [`#[cgp_component]`](cgp_component.md): defines the components a namespace maps, and hosts
  [`#[prefix(...)]`](../attributes/prefix.md), which registers a component into a namespace under a
  path.
- [`delegate_components!`](delegate_components.md): where a context joins a namespace with its
  `namespace` statement and writes its own entries.
- [`delegate_and_check_components!`](delegate_and_check_components.md): also joins a namespace, but
  checks only the entries written directly in its block; the merged wiring is verified with a
  standalone [`check_components!`](check_components.md).
- [`RedirectLookup`](../providers/redirect_lookup.md): resolves each redirect entry, walking
  [`DelegateComponent`](../traits/delegate_component.md) tables along the path.
- [`DefaultNamespace` and `DefaultImpls1`](../traits/default_namespace.md): the built-in namespace
  and the per-type default registries in `cgp-component`.

## Known issues

A context that joins a namespace with `namespace N;` cannot also wire, directly on itself, a path
`N` already binds. The `namespace N;` statement emits a blanket
`impl<Key> DelegateComponent<Key> for Ctx where Key: N<Ctx>`, which covers every path `N` resolves,
and a direct `@path: Provider` entry emits a second `DelegateComponent` impl for that path, so the
compiler rejects the overlap with `E0119`. Overriding therefore works only on a path the namespace
routes to without binding it: register the component's [`#[prefix]`](../attributes/prefix.md)
redirect in a namespace the context joins, and leave the leaf path unbound so the context can supply
it. A path the namespace binds with a `:` entry or a
[`#[default_impl]`](../attributes/default_impl.md) cannot be overridden on the context; change it in
the namespace instead. The same rule stops an inheriting namespace from redefining a key its parent
binds. The macro cannot detect this whole-program overlap, so the compiler reports it; the
[namespace override conflict](../../errors/wiring/namespace-override-conflict.md) error class has
the full anatomy.

A related overlap arises when a context emits two blanket forwardings: joining two namespaces, or
writing a bare-key `for` loop (`for <Key, Value> in Table { Key: Value }`) beside a `namespace`
statement. That is why a loop key is embedded in a path, as in `@app.SomeComponent.Key: Value`. This
is the [overlapping namespace forwarding](../../errors/wiring/namespace-forwarding-conflict.md)
error class.

A component routed into a joined namespace by a [`#[prefix]`](../attributes/prefix.md), with no
entry that ever binds a provider at its path, reaches an empty slot. No `#[default_impl]`, body
entry, or direct wiring answers it, and a `check_components!` reports the lookup as unsatisfied
(`E0277`). This is the
[unregistered namespace path](../../errors/checks/unregistered-namespace-path.md) error class.

A circular parent chain is rejected at the `cgp_namespace!` definitions, and its two shapes fail
differently. A chain through two or more namespaces, such as `new A: B` with `new B: A`, makes the
inheritance impl's first bound loop, reported as `E0275` overflow at both definitions
(`overflow evaluating the requirement '__Key__: A<__BComponents>'`, and its mirror). A
self-inheriting `new A: A` does not overflow: its forwarding impl has a value parameter nothing
determines, so it fails with `E0207`
(`the type parameter '__Value__' is not constrained by the impl trait, self type, or predicates`).
Both mean the parent chain is not acyclic, and only the first says so recognizably. This is the
[namespace inheritance cycle](../../errors/wiring/namespace-inheritance-cycle.md) error class.

The `namespace` statement names its namespace by a bare identifier, so a namespace from another
module cannot be written as a path: `namespace some_mod::MyNs;` fails with
``expected `;` `` at the `::`. Import the namespace trait first and join it by its name. The `for` statement's `in`
clause and the inheritance header both accept a path.

## Source

- Entry point: `cgp_namespace` in
  [crates/macros/cgp-macro-lib/src/cgp_namespace.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_namespace.rs),
  which parses a `NamespaceTable`, rejects attributes on its entries, and emits the evaluated table.
- Logic:
  [crates/macros/cgp-macro-core/src/types/namespace/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/namespace/):
  `table.rs` parses the header (`new`, namespace name, optional `: parent`) and builds the trait,
  struct, per-entry impls, and the parent-inheritance impl; `inherit.rs` builds the inheritance
  entry; `eval.rs` holds the emitted `EvaluatedNamespaceTable`.
- `#[prefix(...)]` attribute (registers a component into a namespace): parsed in
  [crates/macros/cgp-macro-core/src/types/attributes/prefix.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/attributes/prefix.rs);
  the matching `RedirectLookup` provider impl is emitted by
  [crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/to_redirect_lookup_impl.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/types/cgp_component/evaluated/to_redirect_lookup_impl.rs).
- Runtime traits: `DefaultNamespace`/`DefaultImpls1`/`DefaultImpls2` in
  [crates/core/cgp-component/src/namespaces.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/namespaces.rs)
  and `RedirectLookup` in
  [crates/core/cgp-component/src/providers/redirect_lookup.rs](https://github.com/contextgeneric/cgp/blob/main/crates/core/cgp-component/src/providers/redirect_lookup.rs).
- Internal walkthrough (the pipeline, the item each entry form generates, the corner-case handling,
  and the index of tests and expansion snapshots):
  [implementation/entrypoints/cgp_namespace.md](../../implementation/entrypoints/cgp_namespace.md).
