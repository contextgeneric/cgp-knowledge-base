# CGP Error Codes

`cargo-cgp` puts a stable code on every main message it rewrites into a CGP-specific one and on every
entry of the dependency tree it renders, and this catalog says what each code means, what it reads,
how to fix it, and which [error class](../cgp/errors/README.md) holds its example. The class document
shows the program behind a message, the raw compiler output, and the fixtures that pin it.

The hundreds digit says what a code classifies. A **`CGP-E0xx`** code names a main message, the
diagnostic's headline, and a **`CGP-E1xx`** code names one dependency-tree entry: `CGP-E101` to
`CGP-E109` for the steps of the chain, and `CGP-E110` onward for the root causes it ends at.

## The scheme, and why it looks unlike a Rust code

A CGP error code is the letters `CGP-E` and three digits, in square brackets at the start of the
rewritten message:

```text
error[E0277]: [CGP-E001] missing field `height` on `Rectangle`
```

**The diagnostic's own Rust code is always kept,** because the rewrite restates the error rather than
reclassifying it. `E0277` still explains with `rustc --explain`, the prefix keeps the two namespaces
apart, and searching the output for `CGP-E001` confirms a class.

## When a code is assigned

A code is assigned only when `cargo-cgp` rewrote the main message and identified it as a class of CGP
error. A diagnostic whose main message is not a CGP class keeps rustc's message and plain header, even
when its sub-messages were rewritten. The [uncoded rewrites](#uncoded-rewrites) list each such rewrite.

## Codes

The headline codes come in family blocks of ten, and the block says how the tool recovers the mistake:

| Block | Family | How the tool recovers it |
| --- | --- | --- |
| `CGP-E001` to `CGP-E009` | A trait the context cannot use, and the two type mismatches | The [typed resolver](implementation/typed-resolution/overview.md), with a `root cause:` note over the chain |
| `CGP-E010` to `CGP-E019` | Conflicting wiring, and structural mistakes | The generated items at the caret; rustc's carets show the colliding entries |
| `CGP-E020` to `CGP-E029` | Wiring that never resolves, and the orphan rule | A walk of the lookup, or the impl at the caret |
| `CGP-E030` to `CGP-E039` | Mistakes in what a macro was given | The generated item holding the failing token |
| `CGP-E040` to `CGP-E049` | Wiring keys and values that do not resolve | The name's position in the wiring, read once name resolution is over |
| `CGP-E050` to `CGP-E059` | Extensible data | The typed resolver |
| `CGP-E060` to `CGP-E069` | Structural mistakes, continued | The generated items at the caret |

[Diagnostic reshapes](implementation/driver/diagnostic-reshapes.md) explains how each family is
recognized. Each entry below gives the message, the mistake, what the tool does with rustc's output,
the fix, and the class.

### `CGP-E001`: consumer trait not implemented

- **Message:** `` [CGP-E001] <cause> ``, the root cause in the sentence its tree code words
  (`` [CGP-E001] missing field `height` on `Rectangle` ``).
  - **Several causes:** missing fields, wiring, or table entries on one owner, or data traits one type
    lacks, are stated together (`` missing fields `first_name` and `last_name` on `Person` ``). A list
    of more than four names the first three and counts the rest
    (`` missing fields `alpha`, `beta`, `gamma`, and 3 more on `App` ``).
  - **Mixed causes:** the class sentence with their count,
    `` the consumer trait `<Consumer>` is not implemented for context `<Context>`: 2 root causes ``,
    with `traits` and `are` when a failure spans several components.
- **Means:** the context cannot use a component it is expected to use. The wiring is missing, or a
  transitive dependency of the wired provider is unmet, so the blanket impl that gives the context its
  consumer trait does not apply.
- **From:** an unsatisfied `CanUseComponent` bound at a check entry, a consumer-method call (`E0599`)
  on a context or on a type parameter without the bound, a call to a generic function whose
  consumer-trait bound the context fails, a consumer-trait bound in an impl's own `where` clause, or a
  `Key -> Table` entry whose table lacks the key. A failure the resolver declines keeps rustc's notes
  under the class sentence.
- **Fix:** follow the `root cause:` note. A `help` names each fix the tool can confirm.
- **Class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md).

### `CGP-E002`: provider trait not implemented

- **Message:** `` [CGP-E002] <cause> ``, by the rules of `CGP-E001`. The class sentence is
  `` the provider trait `<Provider trait>` with context `<Context>` is not implemented for provider `<Provider>` ``.
- **Means:** a provider fails to implement its provider trait for the context, because its impl-side
  dependencies do not hold.
- **From:** a failing `#[check_providers(...)]` entry, or a call through the provider's own path
  (`Add::try_compute(&App, …)`). The tree starts at that provider, whatever the context wires. Any
  other resolved failure takes its code from the trait its anchor recovered, even when rustc's headline
  stops on a provider's `IsProviderFor` bound, so such a block is `CGP-E001` or `CGP-E003`. A failure
  the resolver declines restates an `IsProviderFor` headline under this code and keeps rustc's notes.
- **Fix:** follow the `root cause:` note to the dependency the provider lacks.
- **Class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md), and
  [unsatisfied dependency](../cgp/errors/hidden/unsatisfied-dependency.md) for a direct call.

### `CGP-E003`: wrapper trait not implemented

- **Message:** `` [CGP-E003] <cause> ``, by the rules of `CGP-E001`. The class sentence is
  `` the trait `<Wrapper>` is not implemented for context `<Context>` ``, naming a foreign subject or a
  type without wiring plainly (`` for `Router<Arc<App>>` ``).
- **Means:** a trait that is not a CGP component cannot be implemented, because a component it depends
  on fails. The trait is a **wrapper** the programmer wrote, such as one adding a `Send` bound over a
  consumer supertrait, or a `#[cgp_fn]` or `#[blanket_trait]` **blanket trait**. It is the `CGP-E001`
  case without a provider trait behind the failing trait.
- **From:** a raw `E0271`, `E0277`, or `E0599` inside an `impl Wrapper for Context` block, or a blanket
  trait the context cannot satisfy, by a method call or a `where` bound on a called function.
- **Fix:** follow the `root cause:` note. The tree leads with the trait, then the traits it composes.
- **Class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md).

### `CGP-E004`: field has the wrong type

- **Message:**
  `` [CGP-E004] field `<field>` on `<Context>` has type `<actual>`, but `<expected>` is required ``.
- **Means:** the field exists and derives `HasField`, so the trait bound holds, but its type is not the
  one a provider needs, so the `Value` projection fails.
- **Both forms of the required type:** a requirement written through an
  [abstract type](../cgp/concepts/abstract-types.md) shows the projection, which points at the wiring
  entry, and what it reduces to, which the reader compares with the field:
  `` field `database` on `App` has type `Pool<Sqlite>`, but `Pool<<App as HasDbType>::Db>` (`Pool<Postgres>`) is required ``.
  A concrete requirement reduces to itself and gets no parenthetical.
- **From:** an `E0271` the resolver traced through the wiring to a `HasField` projection.
- **Fix:** change the field's type, or change the provider to accept it. The `note` shows the chain.
- **Class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md).

### `CGP-E005`: abstract type has the wrong type

- **Message:**
  `` [CGP-E005] abstract type `<assoc>` of `<Trait>` on `<Owner>` is `<actual>`, but `<expected>` is required ``,
  reading `associated type` when the trait is not a CGP abstract-type component. The required type
  shows both forms on the rule of `CGP-E004`
  (`` but `Tx<<App as HasDbType>::Db>` (`Tx<Postgres>`) is required ``).
- **Means:** the owner supplies one type for an associated type and a provider requires another. A
  context wires `ErrorTypeProviderComponent` to `UseType<String>`, while a provider pins
  `#[use_type(HasErrorType.{Error = AppError})]`. A `UseType` entry and a hand-written impl read alike.
- **From:** an `E0271` the resolver traced through the wiring to a projection other than `HasField`'s.
- **Fix:** reconcile the two sides. For a `#[cgp_type]` component a `help` names both ways:
  `` wire `<Marker>` to `UseType<<expected>>` in the wiring for `<Owner>`, or change the provider to work with `<actual>` ``.
  The `help` writes the reduced type, since it is an edit the reader types. An ordinary trait's
  associated type has no wiring entry to name, so it gets no `help`.
- **Class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md).

### `CGP-E010`–`CGP-E014`: the duplicate-key wiring-conflict family

These five codes rewrite an `E0119` on a wiring entry's impls, and each shape of collision has its own
fix. The conflict arises when a `delegate_components!` block wires a key or overlapping keys more than
once, or when two namespace entries claim one key, from a `cgp_namespace!` body, a provider's
`#[default_impl(… in …)]`, or the inheritance blanket of a `new Child: Parent` header. The redundant
`IsProviderFor` half of a generated pair is dropped, and rustc's two carets point at the entries. An
`@`-path key reads as its entry wrote it, with a generic segment named by its parameter
(`@ComputerComponent.Code.u64`).

The classes are [conflicting wiring](../cgp/errors/wiring/conflicting-wiring.md),
[overlapping namespace forwarding](../cgp/errors/wiring/namespace-forwarding-conflict.md), and
[namespace override conflict](../cgp/errors/wiring/namespace-override-conflict.md).

- **`CGP-E010`: duplicate wiring.**
  `` [CGP-E010] conflicting wiring: `<Context>` wires <key> twice ``: the same key mapped twice. A key
  is worded as what it is (`` component `<Marker>` ``, `` type `String` ``, or `` `@a.b` ``), and the
  subject is the namespace lookup trait for a collision inside a namespace
  (`` `DefaultImpls1<ShowImplComponent>` wires type `String` twice ``). **Fix:** remove one entry.
- **`CGP-E011`: overlapping wiring.**
  `` [CGP-E011] conflicting wiring: `<Context>` wires <key>, which <source> already covers ``: two
  distinct keys that overlap, whatever the entries map them to: a generic entry over a specific one, an
  `@`-path over a namespace forwarding, or a path covering another. The source is the key that covers
  the other, whichever comes first. When neither covers the other, the key is the one they share and
  the source is the first entry's. A child namespace redefining a key it inherits takes this code, with
  the namespace as subject and the parent as source. **Fix:** remove or narrow the entry.
- **`CGP-E012`: multiple namespaces.**
  `` [CGP-E012] conflicting wiring: `<Context>` joins both `<A>` and `<B>`, but a target type in `delegate_components!` can join only one namespace ``:
  two blanket forwardings that each cover every key, from two joins, or a join and a bare-key `for`
  loop. **Fix:** join one namespace and inherit the others into it, or move a bare `for` key into a path.
- **`CGP-E013`: redirect collision.**
  `` [CGP-E013] conflicting wiring: `<Context>` wires <component> directly, but it is redirected to `<path>` ``:
  a direct entry colliding with an `open` header, a `=>` redirect, a `namespace` join that maps the key
  to a redirected path, or, with a namespace as subject, a binding of a key its parent redirects, as a
  bare marker for a `#[prefix]`ed component does. **Fix (in the `help`):**
  `` wire the provider `<Provider>` with the key `<path>` ``. A redirect appends a component's type
  parameters to the path, so a generic component's key takes a generic segment for each:
  `` wire the provider `UseDelegate<AreaTable>` with the key `@AreaCalculatorComponent.<Shape> Shape` ``.
  The `help` is omitted when the direct entry names no provider a reader wrote.
- **`CGP-E014`: duplicate redirect.**
  `` [CGP-E014] conflicting wiring: `<Context>` redirects <component> twice, to `<path>` and to `<path>` ``,
  or `` twice, both times to `<path>` ``: two `open`s or `=>` mappings, an `open` of a component the
  joined namespace already redirects, one `@`-path registered twice in a `cgp_namespace!` block, or two
  `#[prefix]` attributes into one namespace, whose carets both cover `#[cgp_component]`.
  **Fix:** keep one redirect.

### `CGP-E015`–`CGP-E019`, `CGP-E060`, and `CGP-E061`: structural mistakes

These codes name a mistake in the shape of what a macro was given, which the compiler rejects through
the generated items. The raw errors name those items (`__CheckApp`, an impl's type parameter) and
carry suggestions that do not fix the program, so each rewrite uses the program's terms, drops those
suggestions, puts the fix in a `help`, and reports the mistake once, however many errors rustc gives.

The classes are [conflicting wiring](../cgp/errors/wiring/conflicting-wiring.md) for `CGP-E015`,
`CGP-E016`, and `CGP-E061`, [unconstrained generic](../cgp/errors/wiring/unconstrained-generic.md) for
`CGP-E017` to `CGP-E019`, and
[check-trait failure](../cgp/errors/checks/check-trait-failure.md#when-a-check-names-no-parameters)
for `CGP-E060`.

- **`CGP-E015`: a check entry listed twice.**
  `` [CGP-E015] `check_components!` checks `<entry>` twice for `<Context>` ``, from an `E0119`, with
  rustc's carets kept. **Help:** `` remove one of the two `<entry>` entries ``.
- **`CGP-E016`: two check tables sharing a check-trait name.**
  `` [CGP-E016] two `check_components!` tables in one module check `<Context>` ``, or
  `` … name their check trait `<Name>` `` when two `#[check_trait(...)]` attributes give one name, from
  an `E0428`, with the carets labelled as the first and the second table. **Help:**
  `` merge the two tables, or name one table's check trait with `#[check_trait(...)]` ``, or
  `` merge the two tables, or give one of them another `#[check_trait(...)]` name ``.
- **`CGP-E017`: a `for` loop whose key skips its variable.**
  `` [CGP-E017] the `for` loop in the wiring of `<Context>` binds `<T>`, but its key `<key>` does not use it ``,
  one block in place of rustc's `E0207`s, with the caret on the variable. **Help:**
  `` write `<T>` in the key where the type the loop covers goes ``.
- **`CGP-E018`: a `#[default_impl]` on a generic provider impl.**
  `` [CGP-E018] `#[default_impl]` cannot register `<Provider>` for `<key>`, because the provider's impl is generic over `<T>` ``,
  from an `E0207`, for a provider generic over a type or written in the explicit-context form. **Help:**
  `` write `<Provider>`'s impl for `<key>` alone, in the concise `#[cgp_impl]` form without `<T>` ``. A
  provider struct generic over the parameter (`#[cgp_impl(ShowWith<T>)]`) with a type as key gets
  `` write the impl for `<key>` alone, as `#[cgp_impl(<Provider at key>)]` with `<key>` in place of `<T>` ``.
- **`CGP-E019`: a wiring entry whose key skips its generic parameters.**
  `` [CGP-E019] the entry for `<key>` in the wiring of `<Context>` binds `<T>`, but its key does not use it ``,
  or `` … in the namespace `<Namespace>` … ``, naming every such parameter
  (`` binds `T` and `U`, but its key does not use them ``). It replaces the `E0207` for each parameter in
  every impl the entry lowers to, with the caret on the first. **Help:** by what uses the parameter,
  `` write a concrete type in place of `<T>` in `<Provider>`, and remove `<T>` from the entry's generic parameters ``,
  `` write a concrete type in place of `<T>` where the entry uses it, and remove `<T>` from the entry's generic parameters ``
  (a table a `->` entry forwards to), or `` remove `<T>` from the entry's generic parameters ``.
- **`CGP-E060`: a check entry that names no parameters for a component that takes some.**
  `` [CGP-E060] the check of `<entry>` on `<Context>` names no parameters, so it checks the component at the unit parameters `()` ``,
  from an `E0277` on the check impl, which rustc reports as a provider without `IsProviderFor`. The
  component's parameters may be its own (`CanCalculateArea<Shape>`) or its key's
  (`<I> FooKeyComponent<I>`). **Help:**
  `` check it at the parameters its provider implements: `#[check_params(<P>)]` `` for
  `delegate_and_check_components!`, or `` `<entry>: <P>` `` (`` `<entry>: [<P1>, <P2>]` `` for several)
  for `check_components!`. It offers only parameters the context passes the check at, and without one
  the error is not reworded this way.
- **`CGP-E061`: two `#[cgp_auto_dispatch]` traits in one module that share a method name.**
  `` [CGP-E061] two `#[cgp_auto_dispatch]` traits in one module declare the method `<method>` ``, one
  report in place of the two `E0428`s on the items the macro names after the method alone, with its
  carets labelled `declared first here` and `declared again here` and a note naming the two items.
  **Help:** `` rename `<method>` in one of the two traits, or declare the traits in different modules ``.

### `CGP-E020`: wiring that leads back to itself

- **Message:**
  `` [CGP-E020] the wiring for the consumer trait `<Consumer>` on context `<Context>` never resolves, because the lookup leads back to itself ``.
- **Means:** resolving the wiring meets a requirement it is already resolving. A component wired to
  `UseContext` with no other implementation of its consumer trait is the plain case. An `open` error
  route that raises its own `String` through `DebugError`, and a recursive data type serialized through
  providers that re-enter the context, close the same kind of loop.
- **From:** an `E0275` overflow on a `CanUseComponent` bound at a check entry, or on the consumer trait
  at a consumer-method call, whose walk meets an obligation again. The note on the generated `__Check…`
  trait and rustc's advice to raise the recursion limit are dropped.
- **Left as rustc wrote it:** an overflow whose walk is not cut, such as one through a type the compiler
  could not resolve after an earlier `E0425` or `E0412`, which is the error to fix.
- **Fix (in the `help`):**
  `` wire a provider in place of `<Provider>`, which provides `<Provider trait>` for `<Context>` by requiring `<Requirement>` on `<Type>` again ``,
  naming the provider a wiring entry chose, directly or through a redirect. A loop closing inside a
  higher-order provider, such as a dispatcher's inner `UseContext`, gets
  `` wire the component to a provider that does not require the consumer trait it provides ``.
- **Class:** [wiring cycle](../cgp/errors/wiring/wiring-cycle.md).

### `CGP-E021`: wiring that grows without end

- **Message:**
  `` [CGP-E021] the wiring for the consumer trait `<Consumer>` on context `<Context>` never resolves, because each step requires it for a larger type (`<Larger>`, …) ``,
  naming the first larger requirement (`` `CanShow<Vec<u32>>` ``) or, when the lookup grows in the type
  the trait is required of, the first larger type (`` `Vec<u32>` ``).
- **Means:** each step requires the consumer trait again for a larger type, so nothing repeats, and the
  compiler stops at its recursion limit. A provider of `CanShow<T>` that requires `CanShow<Vec<T>>` is
  the plain case.
- **From:** the same `E0275` as `CGP-E020`, when the walk reaches its depth limit without a repeat. The
  same note and advice are dropped, since no limit ends a lookup that grows.
- **Fix (in the `help`):**
  `` wire a provider in place of `<Provider>`, which provides `<Provider trait>` for `<Context>` by requiring `<Requirement>` on `<Type>`, a larger type at every step ``,
  or `` wire the component to a provider whose requirements do not grow with each step `` when no wiring
  entry chose that provider.
- **Class:** [wiring cycle](../cgp/errors/wiring/wiring-cycle.md).

### `CGP-E022`: orphan-rule namespace registration

- **Message:**
  `` [CGP-E022] cannot register the foreign <key> into the foreign namespace `<Namespace>` ``, where
  `<key>` is `` component `<Marker>` ``, `` type `<Type>` ``, or `` path `@…` ``.
- **Means:** the crate registers wiring into a namespace it does not own, keyed on something it does not
  own either. A registration lowers to `impl Namespace<_> for Key`, and the orphan rule rejects a
  foreign-trait impl with no local type covering it.
- **From:** an `E0210`, or its sibling `E0117`, on a `#[default_impl(… in Namespace)]` or
  `#[prefix(… in Namespace)]` registration (naming `__Components__`), or on a `cgp_namespace!` block
  re-opening a foreign namespace (naming `__Table__`).
- **Fix (in the `help`):** own one end. For a registration,
  `` own one end of the wiring: key it on a component defined in this crate, or register it from the crate that defines `<Namespace>` ``.
  For a re-open,
  `` to extend a foreign namespace, define a new local namespace that inherits it: `cgp_namespace! { new MyNamespace: <Namespace> { … } }` ``.
- **Class:** [orphan-rule violation](../cgp/errors/wiring/orphan-rule.md).

### `CGP-E030`: trait used but not declared

- **Message:** `` [CGP-E030] the trait `<Trait>` is used but not declared as a dependency ``.
- **Means:** a `#[cgp_fn]` or `#[cgp_impl]` body calls a consumer or blanket trait on the context,
  through `self` or `Self`, without declaring it. The body lowers to an impl over a generated
  `__Context__`, so a trait it uses must be a `where` bound there.
- **From:** an `E0599`, either "the method `…` exists for reference `&__Context__`, but its trait bounds
  were not satisfied" or "no associated function or constant named `…` found for type parameter
  `__Context__`".
- **Left as rustc wrote it:** a call on another generic parameter (`value: &Value`), since its fix is a
  bound `#[uses]` cannot give, and any `[T]: Sized` cascade an unresolved return type trails, which can
  land off the failing expression, so suppressing it could hide an unrelated error.
- **Fix (in the `help`):** `` declare it as a dependency with `#[uses(<Trait><Args>)]` ``, with the
  arguments the call uses (`#[uses(CanFormatPair<(u32, u64)>)]`). An argument the tool cannot read stays
  as the trait's parameter, and the `help` adds `` , with the type the call uses in place of `<Param>` ``.
  A trait with a lifetime or const parameter gets no `help`.
- **Class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md).

### `CGP-E031`: inner provider used but not imported

- **Message:** `` [CGP-E031] the inner provider `<Inner>` is used but not imported ``.
- **Means:** a higher-order provider's body calls an inner provider as an associated function
  (`<Inner>::method(self)`) that it never imported, so the parameter has no provider-trait bound. It is
  the inner-provider counterpart of [`CGP-E030`](#cgp-e030-trait-used-but-not-declared).
- **From:** an `E0599` "no associated function … found for type parameter `<Inner>`". rustc's suggestion
  leaks `__Context__` and offers the consumer trait, the wrong fix. `Self::method(…)` never qualifies,
  since its fix is a `#[uses]`.
- **Fix (in the `help`):** `` import it with `#[use_provider(<Inner>: <ProviderTrait><Args>)]` ``. A
  generic component's parameters follow the context, as in `#[use_provider(Inner: AreaCalculator<Shape>)]`.
  A parameter the call does not fix stays named, and the `help` adds
  `` , with the type the call uses in place of `<Param>` ``. A provider trait with a lifetime or const
  parameter gets no `help`.
- **Class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md); see also
  [higher-order providers](../cgp/concepts/higher-order-providers.md).

### `CGP-E032`: consumer trait used in a provider impl

- **Message:**
  `` [CGP-E032] `<Consumer>` is a consumer trait, but a `#[cgp_impl]` provider must implement its provider trait `<Provider>` ``.
- **Means:** a `#[cgp_impl]` header names the consumer trait where the provider trait belongs. The macro
  generates an inside-out impl and a `<Consumer>Component` marker that does not exist, so one mistake
  yields a burst of errors (`E0425`, `E0107`, `E0186`, `E0207`) and a downstream check failure.
- **From:** the `E0107` on the header, since the macro inserts the context as a leading generic. The
  sibling errors and the downstream re-report are dropped. A requirement of the impl that fails on its
  own, such as a field the context lacks, is a separate mistake and stays beside this error, as
  `[CGP-E001]` or `[CGP-E004]`.
- **Fix (in the `help`):**
  `` change the impl header to target the provider trait: `impl <Provider>` (not `impl <Consumer>`) ``.
- **Class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md); see also
  [consumer and provider traits](../cgp/concepts/consumer-and-provider-traits.md).

### `CGP-E033`: `#[cgp_impl]` on a non-CGP trait

- **Message:**
  `` [CGP-E033] `#[cgp_impl]` can only implement a CGP component's provider trait, but `<Trait>` is not a CGP component ``.
- **Means:** the trait is neither a consumer nor a provider trait, so there is no provider trait to
  implement. Unlike [`CGP-E032`](#cgp-e032-consumer-trait-used-in-a-provider-impl), naming another trait
  does not help.
- **From:** the same `E0107` as `CGP-E032`.
- **Fix (in the `help`):**
  `` make `<Trait>` a component, as in `#[cgp_component(<Trait>Provider)]`, and implement its provider trait here (`impl <Trait>Provider`), or drop `#[cgp_impl]` and write a plain `impl` if it is an ordinary trait ``.
  Making it a component alone leaves the consumer trait in the header, which is `CGP-E032`.
- **Class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md); see also
  [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md).

### `CGP-E034`: consumer trait in an inner-provider bound

- **Message:**
  `` [CGP-E034] `<Consumer>` is a consumer trait and cannot bound an inner provider; a higher-order provider imports its provider trait `<Provider>` ``.
- **Means:** an inner-provider bound names the consumer trait, usually through
  [`#[use_provider]`](../cgp/reference/attributes/use_provider.md). The attribute fills in the context
  argument, so `Inner: CanCalculateArea<Self>` gives the consumer trait one argument too many.
- **From:** the `E0107` on the bound. The `E0308` body cascade that mentions `__Context__` is dropped.
- **Fix (in the `help`):**
  `` name the provider trait in the bound, idiomatically `#[use_provider(… : <Provider>)]` (not the consumer trait `<Consumer>`) ``.
- **Class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md); see also
  [higher-order providers](../cgp/concepts/higher-order-providers.md).

### `CGP-E035`: abstract type used but not imported

- **Message:** `` [CGP-E035] the abstract type `<Type>` is used but not imported ``.
- **Means:** a `#[cgp_fn]`, `#[cgp_impl]`, or `#[cgp_component]` definition names an abstract type of
  the context, as `Self::Error` or a bare `Error`, without
  [`#[use_type]`](../cgp/reference/attributes/use_type.md), which adds the bound and rewrites the bare
  name.
- **From:** an `E0220` "associated type `Error` not found", reported once per definition, when exactly
  one abstract-type component declares the name. A bare `Error` is an `E0425` from name resolution,
  before anything says which trait declares it, so it takes this code only when a requirement of the
  component names that trait (see [`CGP-E036`](#cgp-e036-requirement-not-declared)), whose `E0277`s are
  then dropped.
- **Left as rustc wrote it:** a name two abstract-type traits declare, which makes the import ambiguous,
  and a bare `Error` no requirement explains, which keeps rustc's suggestion to import
  `std::error::Error`.
- **Fix (in the `help`):** `` import it with `#[use_type(<Trait>.<Type>)]` ``, and write the type bare.
- **Class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md).

### `CGP-E036`: requirement not declared

- **Message:**
  `` [CGP-E036] the provider trait `<ProviderTrait>` requires `<Trait>` of the context, but the provider `<Provider>` does not declare it ``
  (`them` for several, in the component's order).
- **Means:** a component requires a trait of every context, through
  [`#[extend(…)]`](../cgp/reference/attributes/extend.md) or `#[use_type(…)]`, which lowers to a `where`
  clause on the provider trait. A `#[cgp_impl]` provider must satisfy it from its own declarations, even
  when its body never uses the trait.
- **From:** an `E0277` on `__Context__: <Trait>` at the attribute or a method signature, checked with the
  solver in the impl's environment. It is reported once per provider, without rustc's note that the error
  originates in the macro. An abstract type the provider also uses unimported is
  [`CGP-E035`](#cgp-e035-abstract-type-used-but-not-imported) instead. A requirement naming the context
  writes it as `Self`.
- **Fix (in the `help`s):** `` declare it as a dependency with `#[uses(<Trait>)]` `` for a trait, and
  `` import it with `#[use_type(<Trait>.<Type>)]` `` for an abstract-type component. Several read
  `` declare them as dependencies with `#[uses(<A>, <B>)]` `` and `` import them with `#[use_type(…)]` ``.
- **Class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md).

### `CGP-E037`: provider trait in `#[uses]`

- **Message:**
  `` [CGP-E037] `<Provider>` is a provider trait and cannot be a `#[uses]` dependency; a dependency names its consumer trait `<Consumer>` ``.
- **Means:** [`#[uses]`](../cgp/reference/attributes/uses.md) writes `Self: <Trait>`, so a provider trait,
  whose first parameter is the context, gets one argument too few. It is the mirror of
  [`CGP-E034`](#cgp-e034-consumer-trait-in-an-inner-provider-bound).
- **From:** an `E0107` "missing generics for trait `<Provider>`", whose rustc `help` adds the generated
  `<__Context__>`.
- **Fix (in the `help`):**
  `` name the consumer trait instead: `#[uses(<Consumer>)]` (not the provider trait `<Provider>`) ``.
- **Class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md).

### `CGP-E038`: `#[cgp_impl]` provider not declared

- **Message:** `` [CGP-E038] the provider `<Provider>` is not declared ``.
- **Means:** `#[cgp_impl(GreetHello)]` without `new` implements the provider trait for a struct nothing
  declares. `new` makes the macro declare it.
- **From:** an `E0425` from name resolution on the `Self` of an impl declaring `__Context__`. The `E0425`
  of a wiring value naming the same provider, and the `E0275` a call then reports, are dropped.
- **Left as rustc wrote it:** a provider some module of the crate or a public module of a dependency
  declares, which is not in scope rather than undeclared, so rustc's import suggestion stands.
- **Fix (in the `help`):** `` declare it with `#[cgp_impl(new <Provider>)]` ``, or declare the struct.
- **Class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E039`: provider impl without the macro

- **Message:**
  `` [CGP-E039] the impl of `<Trait>` for `<Provider>` is written without `#[cgp_provider]` ``.
- **Means:** a plain `impl` implements a provider trait. The trait has `IsProviderFor` as a supertrait,
  and only `#[cgp_provider]` or `#[cgp_impl]` writes the provider's impl of it.
- **From:** an `E0277` naming `IsProviderFor` on the `Self` of the impl. rustc's implementor list is
  dropped, and so is a later `E0277` on the same bound, such as the failing check of a context wiring it.
- **Fix (in the `help`):**
  `` add `#[cgp_provider]` to the impl of `<Trait>`, or write the provider with `#[cgp_impl]` ``.
- **Class:** [provider impl without the macro](../cgp/errors/lowering/provider-impl-without-macro.md).

### `CGP-E040`: consumer trait as a wiring key

- **Message:**
  `` [CGP-E040] the wiring key `<Consumer>` is a consumer trait, but a key names a component ``.
- **Means:** a key names `CanGreet` where its marker `GreeterComponent` belongs, so a trait stands where
  `DelegateComponent` takes a type.
- **From:** an `E0782` "expected a type, found a trait" on the key. rustc's `dyn` suggestion is dropped.
- **Fix (in the `help`):** `` name its component instead: `<Component>` ``.
- **Class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E041`: component not in scope

- **Message:** `` [CGP-E041] the component `<Component>` is not in scope ``.
- **Means:** a key names a component that exists but is not imported where the table is written, such as
  `ErrorTypeProviderComponent`, which the prelude does not export.
- **From:** an `E0425` from name resolution on a key, or on a whole segment of an `@`-path in a key or
  value, when exactly one marker of that name exists among the traits the crate can see. Two of one name
  decline. A repeat at one key prints once, and rustc's suggestions are dropped.
- **Fix (in the `help`):** `` import it with `use <path>;` ``. The path is a `crate::` path for a local
  component, and otherwise the shortest public path from a direct dependency's root, since the compiler's
  own printing can name a re-exported crate by a name that does not compile.
- **Class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E042`: wiring key names no component

- **Message:** `` [CGP-E042] the wiring key `<Key>` names no component ``.
- **Means:** a key was guessed from a consumer trait's name with `Component` appended
  (`HasScalarTypeComponent`), while the marker follows the provider trait (`ScalarTypeProviderComponent`).
- **From:** an `E0425` from name resolution on a key, when no component has that name and the name without
  its suffix names exactly one consumer trait. A repeat at one key prints once.
- **Fix (in the `help`):** `` name the component of `<Consumer>` instead: `<Component>` ``.
- **Class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E043`: provider not declared

- **Message:** `` [CGP-E043] the provider `<Provider>` wired for `<Key>` is not declared ``.
- **Means:** a wiring value names a provider struct nothing declares, often a misspelling.
- **From:** an `E0425` from name resolution on a value. rustc's suggestion of a similarly named trait is
  dropped, and so is the `E0275` on the requirement the entry leaves unprovable, whatever parameters the
  component takes.
- **Left as rustc wrote it:** a provider declared elsewhere but not in scope, as for `CGP-E038`.
- **Fix:** declare the provider or name one that exists. A `help` appears only for a near miss among the
  component's providers, `` a provider of `<Key>` with a similar name exists: `<Provider>` ``.
- **Class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E044`: type in a wiring path not declared

- **Message:** `` [CGP-E044] the type `<Name>` in a wiring path is not declared ``.
- **Means:** an `@`-path in a key, or in the value of a `=>` redirect, names a type nothing declares. A
  segment that is not a lowercase identifier stays the type it spells, and only a lowercase one becomes a
  symbol.
- **From:** an `E0425` from name resolution on a type inside the path of a `DelegateComponent` impl's key
  or `Delegate`. A segment naming one component marker is `CGP-E041`. Only the header is replaced, so
  rustc's near miss for a type stays, while its "missing a type parameter" suggestion goes. A later report
  of one name prints once, and the `E0275` on a value's requirement is dropped.
- **Left as rustc wrote it:** a type declared elsewhere but not in scope, as for `CGP-E038`.
- **Fix (in the `help`):**
  `` declare or import the type `<Name>`, or write the segment in lowercase to make it a symbol ``, only
  when nothing else says how to fix the name, and only for a whole segment, since a type nested in a
  segment's arguments has no lowercase form.
- **Class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E050`: extensible-data operation not implemented

- **Message:** `` [CGP-E050] <cause> `` (`` [CGP-E050] missing variant `Bar` on `Big` ``), by the rules of
  `CGP-E001`. The class sentence is `` the trait `<Trait>` is not implemented for `<Type>` ``, naming the
  data trait and its subject plainly.
- **Means:** a cast, builder, or extractor operation is called on a value whose field or variant is not in
  the state the operation needs, or on a type without the data derive it needs. The trait is implemented
  only for valid states, tracked by the presence markers of the partial types a derive generates. The tree's
  leaf names the cause: `CGP-E118` to `CGP-E126`, a missing field as `CGP-E110`, or an ordinary bound as
  `CGP-E117`.
- **From:** a call to an operation of a trait `cgp-field` or `cgp-field-extra` defines (other than field
  access such as `HasField`), by method or type-relative path, on a value the
  [data-call anchor](implementation/typed-resolution/call-site.md#calls-to-extensible-data-operations)
  types. It fails as an `E0277`, an `E0271`, an `E0599`, or an `E0308` on a tag argument. The same causes
  reached through a check or a consumer keep `CGP-E001`, and a `#[cgp_auto_dispatch]` call keeps `CGP-E003`.
- **Fix:** follow the cause. Drop a second setting or extraction, set an unset field, add a missing variant
  or align a payload type, add the derive a `help` names, or call the method a `help` names.
- **Class:** [extensible data](../cgp/errors/data/extensible-data.md).

## Dependency-tree entry codes (`CGP-E1xx`)

Each entry of a `root cause:` note's tree carries one code per rendering template, the root cause
included, and the `root cause:` line repeats the code of the cause it names:

```text
= note: root cause: [CGP-E110] missing field `name` on `App`
        this is required through the dependency chain:
          [CGP-E101] consumer trait impl `CanGreet` for context `App`
          └─ [CGP-E102] provider trait impl `Greeter` with context `App` for provider `GreetHello`
            └─ [CGP-E104] trait impl `HasName` for `App`
              └─ [CGP-E110] missing field `name` on `App`
```

These codes are the steps of the chain:

- **`CGP-E101`: consumer trait impl.** `` consumer trait impl `<Trait>` for context `<Ctx>` ``. A type
  without wiring of its own is not a context, so it is named plainly:
  `` consumer trait impl `HasScalarType` for `NoScalar` ``.
- **`CGP-E102`: provider trait impl.**
  `` provider trait impl `<Trait>` with context `<Ctx>` for provider `<Provider>` ``. Directly above a
  `CGP-E115` leaf for the same provider, which has no such impl, it reads
  `` provider trait `<Trait>` required of provider `<Provider>` with context `<Ctx>` ``.
- **`CGP-E103`: redirect lookup.** `` redirect lookup to `@…` in `<Table>` ``, naming the table the path
  is looked up in: the context, or an aggregate provider that `open`s a component in its own table. Two
  lookups along one route for different dispatch keys read alike but keep separate branches and leaves.
- **`CGP-E104`: trait impl (general).** `` trait impl `<Trait>` for `<Type>` ``, for any other trait,
  named with all its arguments (`` trait impl `EncodeVariants<App>` for `Sum![u64, f64]` ``). A partial
  value of extensible data is named in words, since its type is generated:
  `` trait impl `BuildField<Symbol!("host")>` for the builder of `Config` with `host` and `port` set ``.

These codes are the root causes:

- **`CGP-E110`: missing field.** `` missing field `<f>` on `<T>` ``. **Helps:** a near miss first,
  `` a similar field exists on `<T>`: `<g>` ``; a tuple position written as a string tag,
  `` a field of the tuple struct `<T>` is keyed by `Index<0>`, not by `Symbol!("0")` ``; and, when the
  struct derives `HasField` for its other fields, `` add the field `<f>: <type>` to `<T>` ``. The same
  leaf states a field a builder operation names that its struct lacks (a `build_from` source's field),
  which gets the near miss alone, since adding it can leave another field the merge never sets.
- **`CGP-E111`: unimplemented accessor.** `` `HasField` not derived for field `<f>` of `<T>` ``, or
  `` … fields `<f>` and `<g>` of `<T>` ``, since the derive emits an impl per field and they are one
  mistake. **Help:** `` add `#[derive(HasField)]` to `<T>` ``.
- **`CGP-E112`: field type mismatch.** The leaf face of `CGP-E004`, with the same wording, so the two
  cannot state one requirement two ways.
- **`CGP-E113`: missing delegate entry.** `` missing wiring for `<key>` on `<Ctx>` ``: the context wires
  no provider for a component, or terminates no namespace path. **Helps:** a near miss first,
  `` a similar key exists in the wiring of `<Ctx>`: `<key>` ``, then
  `` wire `<key>` to a provider in the wiring of `<Ctx>` ``. A path holding a reference or an erased
  lifetime gets no entry `help`, since the reader could not paste it.
- **`CGP-E114`: missing dispatch entry.** `` missing entry for `<key>` in provider `<T>` ``: the sibling of
  `CGP-E113` for a table that is not the context: an
  [aggregate provider](../cgp/concepts/aggregate-providers.md), including a table a `Key -> Table` entry
  forwards to, or a [`UseDelegate` or `UseInputDelegate`](../cgp/reference/providers/use_delegate.md)
  table lacking a branch, as a pipeline stage whose output no later dispatcher handles. The key may be an
  `@`-path. **Help:** `` add an entry for `<key>` to `<T>` ``, unless the reader could not paste the key. The
  other way out is to feed the stage a type the table covers.
- **`CGP-E115`: not a provider.** `` `<X>` is not a provider of `<T>` ``: a type in a provider slot that
  does not implement the provider trait, such as a request type where a handler belongs. The owner is not a
  table missing an entry, so the fix is an actual provider. **Helps,** each only when the solver confirms it:
  - **Adapter:** ``wire `WithProvider<ReadDisplayName>` in place of `ReadDisplayName` ``, with the `use`
    it needs when the prelude does not export it. Any impl of the provider trait whose `Self` is a type over
    one bounded parameter counts, and no adapter is named by its name.
  - **`UseField` on a multi-method getter:**
    ``wire `UseFields` in place of `UseField<…>`, which reads each method's field by the method's name``.
  - **`UseDelegate` on a component without `#[derive_delegate]`:**
    ``dispatch with `open AreaCalculatorComponent;` and one `@AreaCalculatorComponent.Shape: <provider>` entry per type, in place of `UseDelegate<AreaTable>` ``.
  - **A provider of other components:**
    ``` `SayBye` provides `Farewell`: wire it under `FarewellComponent`, or wire a provider of `Greeter` here ```.
- **`CGP-E116`: associated type mismatch.** The leaf face of `CGP-E005`, with the same wording.
- **`CGP-E117`: ordinary trait bound.** `` the trait bound `<S: Trait>` is not satisfied ``: the compiler's
  wording, with an empty CGP list written `Product![]` where the compiler prints `Nil`. When rustc's headline
  already states the bound, the tool keeps it, and the note carries the tree alone.
- **`CGP-E118`: field already set.** `` field `<f>` of `<T>` is already set ``: a builder operation needs the
  field unset, as a second `build_field` or a second merge source does.
- **`CGP-E119`: fields not set.** `` field `<f>` of `<T>` is not set ``, or
  `` fields `<f>` and `<g>` of `<T>` are not set ``: an operation such as a finalize or `take_field` needs
  them set.
- **`CGP-E120`: missing variant.** `` missing variant `<V>` on `<T>` ``: a cast between enums whose variants
  do not match, or a construction by a tag the enum lacks. **Help:** `` a similar variant exists on `<T>`: `<W>` ``.
- **`CGP-E121`: variants not extracted.** `` variant `<V>` of `<T>` is not extracted ``, or
  `` variants … of `<T>` are not extracted ``: an extractor is finalized while it may still yield them, as a
  matcher that leaves one out does.
- **`CGP-E122`: variant type mismatch.** `` variant `<V>` on `<T>` has type `<actual>`, but `<expected>` is required ``:
  a cast between enums whose same-named variants carry different payloads. An `E0271` block states it as its
  headline, under its anchor's class code.
- **`CGP-E123`: data trait not implemented.** `` `<T>` does not implement `<Trait>` ``: a trait only a data
  derive implements, on a type that is not a partial value, several merging into one sentence. **Help:**
  `` add `#[derive(HasFields, ExtractField)]` to `<T>` ``, when the type is a struct or enum the crate defines,
  of a kind each derive accepts.
- **`CGP-E124`: variant already extracted.** `` variant `<V>` of `<T>` is already extracted ``: rustc reports
  it as an `E0308` on the tag argument, since only the other variants' impls remain.
- **`CGP-E125`: field not optional.** `` field `<f>` of `<T>` is not optional ``: an optional builder's
  operation on a field a core builder holds set or unset. **Help:**
  `` call `to_optional` on the builder first to hold each field as optional, with `use cgp::extra::field::impls::ToOptional;` in scope ``,
  when the builder takes it.
- **`CGP-E126`: builder or extractor in the wrong place.** `` an extractor of `<T>` does not implement `<Trait>` ``
  (`` a builder of `<T>` … ``): a partial value given to an operation that needs a trait only the struct or
  enum implements, as `downcast` on the remainder of a downcast. **Help:**
  `` call `downcast_fields` in place of `downcast` on an extractor, with `use cgp::core::field::impls::CanDowncastFields;` in scope ``,
  when one holds.
- **`CGP-E127`: provider for other arguments.** `` `<P>` implements `<Trait>` only for `<A>`, not `<B>` ``, or
  `` `<P>` implements `<Trait>` only with `<Param> = <A>`, not `<Param> = <B>` ``: a provider whose impls differ
  from the wiring in exactly one argument: the context, as for
  `#[cgp_impl(new GreetPerson)] impl Greeter for Person` wired on `Robot`, or a component parameter, as for a
  pipeline stage that takes `u64` after one that returns `String`. Several impls join with "or", and an impl's
  own generic parameters print as `_`. Unlike `CGP-E115`, the type is a provider, so the cause names no `help`.
- **`CGP-E128`: wiring without `IsProviderFor`.** `` the wiring of `<C>` on `<X>` has no `IsProviderFor` impl ``:
  a hand-written `DelegateComponent` impl without the `IsProviderFor` impl `delegate_components!` writes beside
  each entry. A check passes, since it needs only the delegate's impl, but every consumer call fails. **Help:**
  `` replace the hand-written `DelegateComponent` impl with `delegate_components! { <X> { <C>: <P> } }` ``, when
  the program wrote the impl.
- **`CGP-E129`: unbounded type parameter.** `` the type parameter `<T>` of `<f>` is not bounded by `<Trait>` ``:
  a consumer method called on a value of a type parameter without the bound. rustc's advice to use
  associated-function syntax is dropped. **Help:** `` add the bound `<T>: <Trait>` to `<f>` ``.

## Uncoded rewrites

These rewrites improve a diagnostic's readability without classifying its main message, so they carry no
code of their own:

- **Root-cause notes and dependency chains:** one `root cause: …` note over the chains of every recovered
  cause, and a `help` for each fix, on a coded or a kept rustc message.
  [The transformed diagnostic](implementation/typed-resolution/output.md) owns them.
- **Obligation-note renaming:** the `required for … to implement …` notes of an unresolved diagnostic name
  the consumer and provider traits instead of the wiring traits. A generated parameter such as `__Context__`
  is never called a context.
- **Path stripping:** rustc's module paths go (`cgp::prelude::Chars` becomes `Chars`), but a qualifier that
  tells two types apart stays (`std::io::Error` beside a crate's own `Error`), and so does the path of a
  `use` statement a `help` writes. It applies to every rewritten message, and to any other only when a
  resugaring below fired there.
- **Resugaring:** `Symbol!`, `Product!`, `Sum!`, `Struct!`, `Enum!`, and `Path!` restore the surface syntax of
  their expansions. An open-ended path, which rustc prints with `_` for the tail the macros append, has no
  `Path!` spelling, so it stays a list, and a rewritten message names it as its key (`@foo.bar`).
  [Resugaring](implementation/resugaring.md) owns the rules.
- **Missing-field clauses:** an unmet `` `HasField<Symbol!("name")>` `` clause in a sub-message becomes
  `` missing field `name` on `Context` `` when the diagnostic shows the context implementing `HasField` for
  another field.
- **Method-probe advice removal:** rustc's "this is an associated function, not a method" framing and its "use
  associated function syntax instead" suggestion go from a consumer-method `E0599` the resolver declined, both
  artifacts of CGP's `self`-less provider methods, so the unmet wiring bound leads.
- **A misspelled `#[use_type]` import's help:** on an `E0576` at a bare alias in a generated item, the
  compiler's suggestion to respell the alias, which does not compile, becomes
  `` rename `<Type>` to `<Similar>` in the `#[use_type]` import from `<Trait>` and in each use of `<Type>` ``,
  without the last clause when the import gives an `as` alias. The class is
  [unresolved imported abstract type](../cgp/errors/lowering/unresolved-imported-type.md).

## Maintaining this catalog

The codes are defined in the code, so this catalog tracks them under the
[synchronization rule](AGENTS.md#what-the-synchronization-rule-means-here). The constants live in the
[`code`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/code.rs)
module, and every message and `help` is worded in the rustc-free
[`diagnosis`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis)
and [`rewrite`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/rewrite)
modules, from what the driver's `detect` and `resolve` modules recover.

A new main-message class takes the next free number in its family's block, and a family that outgrows its
block takes the next free one; `CGP-E030` to `CGP-E039` is full. A new tree step takes the next
number from `CGP-E101` to `CGP-E109`, and a new root cause the next from `CGP-E110` onward. Add the constant and
register the code here in the same change. A rewrite that does not classify its main message goes under
[uncoded rewrites](#uncoded-rewrites) instead.
