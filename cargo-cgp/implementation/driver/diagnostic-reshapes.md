# Diagnostic reshapes

The emitter recognizes each class of CGP mistake rustc reports in its own terms, and rewrites it to
name what the programmer wrote. [The driver](program.md) explains the emitter as a program, and the
[typed resolver](../typed-resolution/overview.md) handles the wiring failures no stage here claims.

Three rules hold across the reshapes, and a new one should keep them:

- **Recover the mistake from the compiler, not from the error text.** Text may route or pre-filter a
  diagnostic, but a detector confirms it structurally, and CGP's traits are anchored by `DefId` or
  by their generated shape, so a same-named trait cannot drive a rewrite. A detector that cannot
  confirm declines, and rustc's error stands.
- **Mind when the error arrives.** A query run while the compiler is lowering types, or during name
  resolution, can re-enter the diagnostic context and
  [abort the compiler](../rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held).
  So each detector reads only what is safe at its error's phase, and several read only HIR.
- **Keep the wording rustc-free.** A detector fills an owned model, and a `plan_*` and `*_help` pair
  in [error processing](../error-processing.md) words it, so the wording is tested without a compiler.

## The stages, in order

Each stage recognizes one class and returns a verdict: continue, drop the diagnostic, or reshape it.
The first that does not continue decides, so the order is part of the behaviour. The stages run in
this order, from `transform_with` in
[`cgp_emitter.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/cgp_emitter.rs):

1. A misused `#[cgp_impl]`, then a provider trait named in `#[uses]`: [a wrong component half](#reshaping-a-wrong-component-half).
2. An overflow that follows from an unresolved wiring name, then a consumer trait used as a wiring key: [an unresolved wiring name](#reshaping-an-unresolved-wiring-name).
3. [A duplicate-key conflict](#reshaping-a-duplicate-key-conflict), then [an orphan-rule namespace registration](#reshaping-an-orphan-rule-namespace-registration).
4. A method two `#[cgp_auto_dispatch]` traits share, then the other [structural mistakes](#reshaping-a-structural-mistake).
5. An undeclared trait, then an unimported inner provider: [an undeclared dependency](#reshaping-an-undeclared-dependency).
6. [A provider impl written without its macro](#reshaping-a-provider-impl-written-without-its-macro).
7. An unimported abstract type, then an undeclared requirement: [an undeclared dependency](#reshaping-an-undeclared-dependency).
8. A [`?`-operator cascade](#dropping-a-question-mark-cascade), then a later report of a provider impl written without its macro.
9. The [typed resolver](../typed-resolution/overview.md), then the [text rewrite](#naming-the-traits-behind-a-component-marker).

Three passes run after name resolution rather than as stages, because they need the `TyCtxt` the
`after_expansion` hook provides:
[the wiring entries' name-resolution errors](#reshaping-an-unresolved-wiring-name),
[a suggestion naming a generated identifier](#dropping-a-suggestion-that-names-a-generated-identifier),
and
[the help on a misspelled `#[use_type]` import](#replacing-the-help-on-a-misspelled-use_type-import).

## Naming the traits behind a component marker

The text rewrite serves a diagnostic the resolver declined. It renames the compiler's marker-based
notes to the traits a reader thinks in, because a component marker names neither trait:

```text
required for `RectangleArea` to implement `IsProviderFor<AreaCalculatorComponent, Rectangle>`
required for the provider `RectangleArea` to implement the provider trait `AreaCalculator` for the context `Rectangle`
```

An unsatisfied `IsProviderFor` main message also gains `[CGP-E002]`, and a check's `CanUseComponent`
header stays the resolver's to word. The full dispatch applies only to a main message and the note
rename to its children, since a code belongs on a main message alone. A message whose marker is
absent from the map passes through.

**The name map inverts two links `#[cgp_component]` generates.** A provider trait carries
`IsProviderFor<Marker, …>` as a supertrait, matched by `DefId` to `cgp_component`, which yields each
provider and marker. A consumer's blanket reads `impl<C> Consumer for C where C: Provider<C>`, and
requiring the bound's self type to be the impl's tells it from the provider blanket, which bounds a
projected `Delegate`. The resolver does not use this map, since it reads names off the `DefId`s it
walks.

These points are easy to break:

- **Entries are keyed by the marker's full path,** because rustc prints a marker bare when its name
  is unique and qualified when two share it. When the keys a printed name matches stand for
  different traits, the lookup declines, so a note never names the other component's trait
  ([`same_name_marker_rename`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/same_name_marker_rename.rs)).
- **The map is lazy and consulted last, after the message parses as a wiring form,** so the walk
  over every trait never runs for a diagnostic that mentions no wiring, and the emitter needs no "is
  this CGP?" pre-check. Its initializer is a plain `fn` pointer reaching the `TyCtxt` through
  thread-local scope, so `ComponentNameMap` itself holds no compiler type. It stays valid for the
  compilation, since the traits and impls it reads are fixed by then.
- **A header reattaches a generic component's parameters while a note elides them.** The map records
  each component's parameter count, because a one-parameter component whose parameter is a tuple
  arrives in the shape of two parameters (`CanFormatPair<(u32, u64)>`).
- **The subject is named as the obligation gives it.** It is usually a provider, but a context that
  stands in as its own provider reads `` the provider `Rectangle` … for the context `Rectangle` ``.
- **A generated parameter in the context's place is not called a context:** the provider note leaves
  `__Context__` out, and the consumer note names it plainly.

**A declined consumer-method `E0599` loses rustc's method-probe advice first.** Meeting CGP's
`self`-less provider methods, the probe frames the failure as a call-syntax mistake, with a "use
associated function syntax" suggestion that is actively wrong, while the unmet bound sits in a later
note. `strip_method_probe_advice` drops that suggestion only, so rustc's others stay
([`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs),
[`undeclared_trait_on_non_context_parameter`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_trait_on_non_context_parameter.rs)).

### Wiring overflows

**An `E0275` is worded by why the lookup never resolves, which its text does not say.** The emitter
walks the consumer obligation at the caret first, a check entry's or a consumer-method call's, and
the walk reports how it was cut:

- **A cycle** (`[CGP-E020]`, "the lookup leads back to itself"): an obligation met again among its
  ancestors
  ([`use_context_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle.rs),
  [`use_context_cycle_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle_call.rs)).
- **A lookup that grows** (`[CGP-E021]`): the depth cap reached with no repeat, worded with the
  first larger requirement
  ([`divergent_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring.rs),
  [`divergent_self_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_self_wiring.rs)).

The emitter then drops the note on the generated `__Check…` trait and rustc's advice to raise the
recursion limit, which no limit satisfies. Its `help` names the provider that closes or grows the
loop, but only when a wiring entry chose that provider, so a provider held inside a higher-order
provider is not named
([`dispatcher_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/dispatcher_cycle.rs)).

**An overflow the walk does not cut keeps rustc's wording,** as does one on a check that carries a
generic parameter, whose wiring the walk cannot read
([`generic_check_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/generic_check_cycle.rs)).
The resolver never takes an `E0275`, because a walk that stops at a bound means that bound's own
evaluation overflowed, which no root cause states truly
([`cross_context_cycle_reuse_distinct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs)).
An overflow can also follow from an unresolved name, whose `{type error}` makes a lookup overflow
with no cycle. When the name is a wiring entry's, the emitter drops the overflow as
[that entry's consequence](#reshaping-an-unresolved-wiring-name).

## Dropping a question-mark cascade

Once a consumer call fails and its result meets `?`, the type of `expr?` cannot be resolved, so
rustc adds a `Try` or `FromResidual` error that restates the failure and dumps the unresolved
projection. The emitter records the primary span of every CGP failure it recognizes, before
de-duplication so a dropped re-report still anchors its cascade, and drops a later `?` error whose
span overlaps one. rustc emits the failure before its cascade, so the span is always recorded in
time.

The scope is deliberately tight: a `?` misuse elsewhere stays, and the resolver declines every `?`
error, since it would otherwise re-anchor one onto the call it overlaps. Only the `?` cascade is
dropped, never a `[T]: Sized` one, which can land off the failing expression, where suppressing it
would risk hiding an unrelated error
([`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs)).

## Reshaping a duplicate-key conflict

A duplicate `delegate_components!` key emits two overlapping `DelegateComponent` impls, and each
entry's `IsProviderFor` forwarding impl overlaps too, so the compiler reports one mistake twice, on
two traits the user never wrote. The reshape **drops** the `IsProviderFor` half and **rewrites** the
other into a coded headline naming the colliding keys, keeping rustc's two carets.

**The drop needs its companion confirmed, because suppressing a lone `E0119` could leave a failing
build with no error.** It fires only when a genuine local `IsProviderFor` impl sits at the caret and
the two colliding sites each carry a local impl of one common other trait, whose own `E0119` rustc
reports. A delegation entry colliding with a provider impl has no common trait, so it is left alone.
Two `#[cgp_impl(P)]` blocks for one struct keep the provider-trait error
([`duplicate_provider_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_provider_impl.rs)),
and two `#[cgp_impl(new P)]` blocks never reach this, since rustc stops at the `E0428`
([`duplicate_provider_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_provider_name.rs)).

**The entries are read off the impls at the carets.** The macro re-spans each entry onto its key
token, so the caret finds the impl, matched by source range, since the pair's two halves differ in
syntax context. rustc labels the other impl only when it is local, so an upstream one means the
classifier cannot say what the entry collides with, and declines
([`upstream_namespace_join_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/upstream_namespace_join_overlap.rs)).

Each shape has its own code:

| Code | Shape |
| --- | --- |
| `CGP-E010` | A duplicate: the two keys render equal |
| `CGP-E011` | An overlap: distinct keys that collide, a generic over a specific or a path prefixing another |
| `CGP-E012` | Multiple namespaces: both keys are blanket forwardings |
| `CGP-E013` | A redirect collision: an entry and a redirect over one key |
| `CGP-E014` | A duplicate redirect: both entries redirect |

These points need care:

- **An overlap's covering key is found by unification,** with the impl's parameters fresh, whichever
  entry comes first. When neither covers the other, the key they share is named
  ([`specific_before_generic_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/specific_before_generic_overlap.rs),
  [`path_generic_segment_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/path_generic_segment_overlap.rs)).
- **A blanket forwarding's target needs the solver.** A `namespace` join has a generic `Delegate`,
  so its target is recovered by normalizing `<key as Namespace<Ctx>>::Delegate` for the other
  entry's key, and the generic parameter is never named as a provider
  ([`open_prefixed_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/open_prefixed_component.rs)).
- **A redirect collision's fix rides in a `help`,** so the headline stays one sentence. A redirect
  appends a generic component's parameters to its path, so the `help` names a generic key rather
  than the bare path the lookup never reads
  ([`open_and_use_delegate`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/open_and_use_delegate.rs)).
  It is omitted when the direct entry names no provider a reader wrote.
- **Keys render as the entry wrote them.** A marker is told from an ordinary type by whether a
  provider trait's blanket keys on it, so a per-type default's `String` reads as a type.

**A conflict inside a namespace names neither trait,** landing on the namespace's own lookup trait,
so the classifier recognizes it by the impls at the carets. Four constructs emit such an impl: a
`cgp_namespace!` entry, a `#[prefix]` route, a `#[default_impl]` registration, and an inheritance
blanket
([`namespace_duplicate_path_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/namespace_duplicate_path_key.rs),
[`duplicate_default_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_default_impl.rs),
[`inherited_override_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/inherited_override_conflict.rs)).
A doubled `#[prefix]` is a duplicate redirect, its two entries paired at one span.

**Binding a prefixed component by its bare marker earns its own message,** a `[CGP-E013]` whose
`help` names the entry to write. The path comes from the `#[prefix]` route's `Delegate`, or from
normalizing the parent's for an inheritance blanket
([`default_impl_unprefixed_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/default_impl_unprefixed_key.rs),
[`namespace_inherited_unprefixed_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/namespace_inherited_unprefixed_key.rs)).

## Reshaping a structural mistake

Some mistakes are in the shape of what a macro was given, and the compiler rejects them through the
generated items, so its error names those items and offers a fix that does not apply. Each shape is
recognized from the generated items at the caret, by a detector under
[`detect::structural`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect/structural):

| Code | Mistake | Error, and what makes it safe |
| --- | --- | --- |
| `CGP-E015` | A check entry listed twice | `E0119` on two impls of a check trait; rustc's carets stay |
| `CGP-E016` | Two check tables sharing a check-trait name | `E0428` during name resolution, so only the span's expansion data is read |
| `CGP-E060` | A check entry naming no parameters for a component that takes some | `E0277` at a check impl asserting `CanUseComponent<Marker, ()>` |
| `CGP-E061` | Two `#[cgp_auto_dispatch]` traits sharing a method name | Two `E0428`s, paired as they arrive with no query |
| `CGP-E017` | A `for` loop whose key skips its variable | `E0207` on a loop-generated entry |
| `CGP-E018` | A `#[default_impl]` on a generic provider impl | `E0207` on a registration impl |
| `CGP-E019` | A wiring entry whose key skips its generic parameters | `E0207` on an entry nothing binds |

These corners need care:

- **`CGP-E015` is a `check_components!` table's.** A `delegate_and_check_components!` table that
  lists an entry twice wires it twice too, so the check impls' `E0119` restates the `[CGP-E010]`
  and is dropped, the impl's macro read from its span
  ([`delegate_and_check_entry_twice`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/delegate_and_check_entry_twice.rs)).
- **`CGP-E016` compares the macro's last path segment,** so `cgp::prelude::check_components!` counts
  and a crate's own `table_check_components!` does not
  ([`own_check_components_macro`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/own_check_components_macro.rs)).
  It reads both definitions' macros, from the caret and from rustc's earlier-definition label, so a
  table colliding with a trait the program wrote keeps rustc's error
  ([`own_trait_named_like_check_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/own_trait_named_like_check_trait.rs)),
  and the message names each table's macro. A name is read as derived only when both tables come
  from one macro and it carries that macro's prefix, `__Check` or `__CanUse`.
- **`CGP-E060`'s help offers only parameters that hold.** They are the `Params` of each
  `IsProviderFor` impl unifying with the check's component and context, fully resolved and not `()`,
  each kept only when `CanUseComponent` holds in the check impl's environment. With none, the
  detector declines. It runs before the resolver, which declines the unit-parameter obligation
  ([`generic_component_unit_params`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/generic_component_unit_params.rs)).
- **`CGP-E061` needs both errors.** The helper's caret comes from the macro's expansion but sits on
  the attribute, and the computer's sits on the method name with no trace of the macro. The macro
  defines the helper first, so the computer's arrival finds the buffered helper
  ([`auto_dispatch_shared_method_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/auto_dispatch_shared_method_name.rs)).
- **`CGP-E019` tells a namespace entry from a registration,** since a `#[default_impl]` copies its
  provider impl's parameters: an entry is the only impl declaring its parameter. An entry bounded by
  a lookup trait on the parameter is a `for` loop's.
- **One mistake can produce several `E0207`s,** a loop's two variables or a parameter in each impl
  an entry lowers to, so each is reported once.
- **The `E0207` detectors print a type by its own name,** rather than through the trimmed-paths map.
  An `E0207` comes before any type was printed with trimmed paths, and the first such print records
  itself on the diagnostic context, whose lock the emitter holds. The name drops a qualifier, so a
  key written `std::io::Error` reads `Error` in these messages.

## Reshaping an orphan-rule namespace registration

Registering wiring into a namespace lowers to `impl<Param> Namespace<Param> for Key`, so a crate
that owns neither end gets an `E0210` or `E0117` naming a machinery parameter (`__Components__`,
`__Table__`) and framing a wiring decision as a bare coherence rule. The reshape `[CGP-E022]` names
the namespace and the key, keeps the caret on the macro alone, and adds the ownership fix.

An `E0210` must name the machinery parameter before the impl scan runs, while the rarer `E0117`,
which names none, goes to the scan directly, so a plain Rust orphan reaches it too. rustc emits these
errors only for a genuine orphan, so a caret on a local impl of a foreign namespace trait for a foreign
key, with no local type among the trait's arguments, is the whole confirmation. `DelegateComponent` has
a namespace trait's shape, but its `Self` is a wiring table rather than a key, so `delegate_components!`
on a foreign type keeps rustc's errors
([`orphan_registration_beside_foreign_table`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/orphan-rule/orphan_registration_beside_foreign_table.rs)).

A `#[default_impl]`'s caret is the `#[cgp_impl]` attribute while its impl is spanned on the key, so the
range match misses, and a lone candidate is used instead. That fallback needs a caret a `cgp_`-named
macro of CGP's proc-macro crate generated, read from the macro's definition so that a renaming import
keeps the code and a program's own similarly named macro does not take it
([`orphan_registration_under_renamed_macro`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/orphan-rule/orphan_registration_under_renamed_macro.rs)),
or an unrelated `impl Display for Vec<u8>` would read as the registration beside it
([`orphan_registration_beside_plain_orphan`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/orphan-rule/orphan_registration_beside_plain_orphan.rs),
[`plain_orphan_beside_type_registration`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/plain_orphan_beside_type_registration.rs)).
Two orphan registrations in one crate leave the choice ambiguous, so both keep rustc's `E0210`
([`two_orphan_registrations`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/orphan-rule/two_orphan_registrations.rs)).

The key prints by its own name, for the reason the `E0207` detectors do: an `E0210` holds no type
in its message, so nothing has printed one with trimmed paths yet. The impl's own machinery parameter
says which fix to word
([`wiring/orphan-rule/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/orphan-rule)).

## Reshaping an undeclared dependency

A CGP macro lowers a body into an impl over a generated context, and only declared dependencies
become bounds on it. So each kind of declaration has its own code (the
[undeclared dependency](../../../cgp/errors/lowering/undeclared-dependency.md) class), and each reshape
keeps the caret rustc chose
([`lowering/undeclared-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/undeclared-dependency)).

**An undeclared trait (`[CGP-E030]`)** fails with an `E0599`, as `self.method(…)` or
`Self::method(…)`. The detector confirms that the call sits in an impl a `#[cgp_fn]` or `#[cgp_impl]`
lowered, over a bare type-parameter context, walking up from its body owner since an impl's item span
does not reliably cover it. The macro is read from the impl's spans, since the explicit-context form of
`#[cgp_impl]` declares no reserved `__Context__`. A hand-written impl, with or without `#[cgp_provider]`,
takes neither `#[uses]` nor `#[use_provider]`, so it keeps rustc's error
([`undeclared_calls_in_plain_impls`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_calls_in_plain_impls.rs)). It also confirms that the call is on that context, names a function of a CGP consumer or
blanket trait, and that the trait is no `where` bound yet.

- **A call on any other parameter is left alone,** since `#[uses]` cannot bound it.
- **When several traits share the method,** the one whose definition the diagnostic's notes touch is
  taken.
- **The help writes the trait with the arguments the call fixes,** by unifying what can be read
  without typeck. A parameter left unknown, or holding a lifetime or a generic parameter, stays
  named for the reader to replace, and a trait with a lifetime or const parameter gets no help.
- **A trailing `[T]: Sized` cascade is left,** for the reason
  [the `?` stage](#dropping-a-question-mark-cascade) gives.

**An unimported inner provider (`[CGP-E031]`)** is `InnerCalculator::area(self)` on a parameter with
no bound, in an impl a CGP macro lowered. rustc's `E0599` leaks `__Context__` and offers the consumer trait, the wrong fix for a
higher-order provider. It is gated to the unbounded-type-parameter shape, reported during typeck,
where the queries are cached, unlike the resolution-class `E0599`. Its main message is a Fluent one,
so it is recognized by its plain-string help.

**An unimported abstract type (`[CGP-E035]`)** is `Self::Error` without `#[use_type]`, an `E0220`
emitted while the compiler lowers the definition's types. So the detector reads only HIR and trait
definitions, never the item being lowered, and takes the type from the diagnostic's arguments. The
trait to import is the one abstract-type component declaring that name, and a second such trait
makes the import ambiguous, so rustc's error stays.

**An undeclared requirement (`[CGP-E036]`)** comes from a component's `#[extend]` or `#[use_type]`,
which puts a `where` clause on the provider trait, so a provider that does not declare it fails with
an `E0277` on `__Context__`. The detector finds the provider impl holding the caret outside its
method bodies, since a body's errors are not about what the impl declares, and evaluates each clause
in the impl's own `param_env`. The first report per impl is reworded, with the caret moved to the
macro's call site, and the later ones dropped.

**The two abstract-type paths meet.** A bare `Error` in a provider of a component that imports it is
an `E0425` from name resolution, before anything can say which trait declares it, so the emitter
buffers it untouched. When the `[CGP-E036]` arrives naming an abstract-type component, it converts
the buffered `E0425` into the `[CGP-E035]` report, and leaves that requirement out, since the import
satisfies it too. A bare `Error` without such a requirement keeps rustc's suggestion to import
`std::error::Error`, a known gap
([`error_alias_in_cgp_fn`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_in_cgp_fn.rs),
[`error_alias_in_provider_body`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_in_provider_body.rs)).

## Reshaping a wrong component half

A definition can name the wrong half of a component (the
[wrong component half](../../../cgp/errors/lowering/wrong-component-half.md) class), most often in a
`#[cgp_impl]` header. The macro turns `impl AreaCalculator` inside out, inserting the context as the
leading generic. Naming the consumer trait `CanCalculateArea` there, or a non-CGP trait, gives one
mistake a burst of cryptic errors: `E0425`, `E0107`, `E0186`, `E0207`, and a downstream check
failure. The reshape rewrites the `E0107`, whose caret sits on the misused name, into `[CGP-E032]`
or `[CGP-E033]`, and suppresses the rest. An inner-provider bound naming the consumer trait, usually
through `#[use_provider]`, is the sibling `[CGP-E034]`
([`lowering/wrong-component-half/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/wrong-component-half)).
An inner-provider bound is one on a type parameter other than `__Context__` whose trait takes
`__Context__` first after any lifetimes, the shape `#[use_provider]` writes. A `#[uses]` bound sits on the context, so
a wrong argument count there keeps rustc's error, and an impl without a `#[cgp_impl]` mistake keeps
its own errors
([`uses_wrong_arity`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/uses_wrong_arity.rs),
[`provider_body_error_beside_unrelated_e0107`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/provider_body_error_beside_unrelated_e0107.rs)).

**Three structural conditions select the user's impl and exclude every generated one,** which also
carries `__Context__`: it has the inserted `__Context__`, its `Self` is a concrete local struct or
enum, and its header trait reference is a token the user wrote.

**Only the `E0107` triggers detection,** because the detector's queries would re-enter the
diagnostic lock during the earlier `E0425`. The siblings are suppressed by their spans against the
impl body and the macro's call site, and one that arrived first is purged from the buffer. A span is
all that ties one to the mistake, so a typo of the program's own in that body is dropped too, and
appears once the header is fixed. A
downstream check re-report is dropped when its leaf is the offending provider, but a requirement of
that impl that fails on its own resolves to its own cause and stays
([the walk](../typed-resolution/walk.md#a-provider-whose-header-names-the-consumer-trait)).

**The reshape is deliberately specific to `#[cgp_impl]`.** Without the reserved `__Context__`,
`impl<Ctx> SomeConsumer<Ctx> for ConcreteType` from `#[cgp_provider]` cannot be told from a
legitimate impl of a generic consumer on a context, so recognizing it would risk a false positive on
valid code.

**The mirror mistake names a provider trait in `#[uses(…)]` (`[CGP-E037]`).** `Self: AreaCalculator`
lacks the context argument, so rustc reports an `E0107` and suggests `<__Context__>`. It arrives
while the compiler lowers the impl's `where` clause, so the bound is read from HIR, and the search
for the consumer trait skips the impl's own trait, whose blanket may be the impl being lowered,
which would cycle into the query in flight.

**The `rustc --explain` footer is rebuilt for every flush, not only here.** rustc builds it from
every code it registered, a superset of what survives the emitter's drops and merges.
`rebuild_explain_footers` filters the footer's own codes rather than building a fresh set, since
rustc lists only codes with an extended explanation. If it parses no code from any footer line,
rustc reworded them, so it leaves the footer as written, a stale footer being a smaller fault than a
deleted one.

## Reshaping a provider impl written without its macro

A provider trait has `IsProviderFor` as a supertrait, and `#[cgp_provider]` writes that impl. A
hand-written provider-trait impl has none, so the compiler rejects it with an `E0277` at the impl's
`Self` and lists every unrelated implementor. The detector confirms the caret is the `Self` of a
local impl of a CGP provider trait the user named, on a struct, enum, or union with no
`IsProviderFor` impl for that marker. It words `[CGP-E039]` and remembers the provider, so a later
failing check of a context wiring it is dropped as the same mistake
([`provider_impl_without_macro`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro.rs),
[`provider_impl_without_macro_wired`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro_wired.rs)).

## Reshaping an unresolved wiring name

A wrong name in a wiring entry (the
[unresolved wiring name](../../../cgp/errors/wiring/unresolved-wiring-name.md) class) is hard because
of timing. Most shapes are an `E0425` from name resolution, before the HIR exists and before any
query that reads the crate is safe, and the name's span carries no trace of `delegate_components!`.

**So the emitter buffers those errors untouched, and the `after_expansion` hook reshapes them.** The
pass collects them under the output's lock, plans with the lock released, since a planning query can
emit a diagnostic that takes the same lock, then rewrites them under the lock after checking the
candidates are where they were. Planning reads each name's position back from the HIR. A name inside
any other larger type, such as a provider's type argument, is no entry's key or value, and stays as
rustc wrote it.

| Position | Code | Reading |
| --- | --- | --- |
| A key naming one component marker | `CGP-E041` | A component not in scope, with its shortest public import path |
| A key whose name without `Component` names one consumer | `CGP-E042` | A guessed key |
| A value | `CGP-E043` | An undeclared provider, with a near miss among the component's providers |
| A `#[cgp_impl]` header's provider | `CGP-E038` | A provider never declared; a value naming it is dropped as the consequence |
| A type in an `@`-path, found by its own span | `CGP-E041` or `CGP-E044` | A component not in scope, or a type not declared |

These points need care:

- **An undeclared name must be declared nowhere the crate could import from.** A type of that name
  in any module, or public in a direct dependency, means the program did not import it, so its
  `E0425` stays and rustc's import suggestion is the fix.
- **A value leaves its requirement unprovable,** which later overflows. The pass records it beside
  the buffer, and the emitter drops that `E0275` as the entry's consequence, in the consumer form
  for a call and the `CanUseComponent` form for a check.
- **`CGP-E044` replaces only the header,** since the compiler's near-miss note is right for a type.
  Only the "missing a type parameter" suggestion goes, since no wiring entry has generics to take
  it.
- **A repeat at the same span is dropped,** while a diagnostic outside the entries stays, repeats
  included.

**A consumer trait as a key differs in kind** (`[CGP-E040]`). Its `E0782` arises while the compiler
lowers the impl's header, with a `TyCtxt` in scope, so the emitter recognizes it as it arrives
([`wiring/unresolved-wiring-name/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/unresolved-wiring-name)).

## Dropping a suggestion that names a generated identifier

A CGP macro spells the names it declares only in its expansion as reserved identifiers
(`__Context__`, the lifetime `'__a__`). rustc may suggest inserting one into the user's source,
where it does not resolve, so the suggestion is wrong whatever the error. For a `Cow<str>` argument
of a `#[cgp_auto_dispatch]` method, `E0106` suggests `Cow<'__a__, str>`, while the `E0726` beside it
suggests the `Cow<'_, str>` that works
([`auto_dispatch_hidden_lifetime`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/auto_dispatch_hidden_lifetime.rs)).

**The drop runs in two places, only in a crate that uses CGP.** The emitter applies it as each
diagnostic arrives. Lifetime errors arrive during name resolution, before an emitted diagnostic can
ask whether the crate uses CGP, so the `after_expansion` hook runs it again over what was buffered.

**It reads the suggestion's text, because the span sits in the user's own code,** where nothing
marks it as the macro's. It removes each substitution holding a reserved name the edited file does
not contain, since a name the file spells is one the user wrote
([`reserved_lifetime_written`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/reserved_lifetime_written.rs)).
rustc offers alternative bounds as one suggestion with several substitutions, so the wrong ones go
and the rest stay
([`generic_fn_consumer_not_in_scope`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_consumer_not_in_scope.rs)).
A suggestion left with none goes too, or JSON would still show its message
([`provider_trait_in_inner_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/provider_trait_in_inner_bound.rs)).

Three limits follow from reading one file: a comment there that spells the name keeps the
suggestion, a reserved name the program declares in another file counts as generated, and a
suggestion left with one bound keeps rustc's plural message.

## Replacing the help on a misspelled `#[use_type]` import

`#[use_type(HasScalarType.Scalr)]` rewrites each bare `Scalr` to `<Self as HasScalarType>::Scalr`,
keeping the alias's span, so name resolution reports an `E0576` there. The header and note are
right, but the help respells the alias, which leaves the import wrong (the
[unresolved imported abstract type](../../../cgp/errors/lowering/unresolved-imported-type.md) class).

The fix runs from the `after_expansion` hook, with the same collect, plan, and rewrite steps as the
wiring-name pass. It takes the `E0576` only when the caret sits in an item a CGP macro generated and
the source writes the name bare, since a path the program qualified itself is respelled where it
stands, so rustc's help is right for it. The type meant is the trait's only associated type, or one
the name is a slip of. When two traits share the name, the compiler's "defined here" note says
which. The header stays the compiler's, without a code
([`lowering/unresolved-imported-type/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/unresolved-imported-type)).

## Dropping a suggestion spliced after an attribute macro

An attribute macro's generated code carries the attribute's span, so rustc can suggest an insertion
right after its `]`, such as `#[cgp_auto_getter].as_deref()`, which no edit of the user's source can
apply
([`auto_getter_mut_option`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/auto_getter_mut_option.rs),
[`parameterized_name_default_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/parameterized_name_default_component.rs)).
`drop_attribute_splices` recognizes it by the span it edits, never its text: an insertion at a span
an attribute macro's expansion carries, exactly where that expansion's call site ends.

Three neighbors must keep their suggestions: a crate without CGP
([`attribute_splice_without_cgp`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/attribute_splice_without_cgp.rs)), a token an attribute macro re-spanned, which is still the
user's code
([`respanned_token_suggestion`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/respanned_token_suggestion.rs)), and the end of a function-like macro's call, a valid edit
([`function_macro_suggestion`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/function_macro_suggestion.rs)).

## Tests

- [`tests/driver/unresolved_overflow.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/unresolved_overflow.rs):
  which overflows count as a wiring entry's consequence.
- [`tests/error_processing/rewrite/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/rewrite):
  the text rewrite over a hand-built name map, including that the lazy map is not forced when no
  message matches.
- [`tests/ui/checks/check-trait-failure/generic/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure/generic):
  the rewrite's parameters end to end.
- [`tests/ui/wiring/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring) and
  [`tests/ui/lowering/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering):
  each class above, cataloged by the [error classes](../../../cgp/errors/README.md).

## Source

- [`emitter/stage/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter/stage):
  the stages, one module each.
- [`emitter/pipeline/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter/pipeline):
  the `Verdict`, the `Reshape`, and `apply_reshape`.
- [`emitter/name_resolution.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/name_resolution.rs),
  [`generated_names.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/generated_names.rs),
  [`use_type_misspelling.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/use_type_misspelling.rs),
  and
  [`attribute_splice.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/attribute_splice.rs):
  the passes and the suggestion drops.
- [`detect/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect):
  the class detectors, which fill the rustc-free models.
- [`cargo-cgp-error-processing/src/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis):
  the models and their wording.
- [`component_map.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/component_map.rs)
  and
  [`cargo-cgp-error-processing/src/rewrite/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/rewrite):
  the name map and the string rewrite.
