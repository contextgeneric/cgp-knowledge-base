# Diagnostic reshapes

This document covers what the driver's emitter does to each class of CGP mistake rustc reports in its
own terms. [The driver](driver.md) explains the emitter as a program, and the
[typed resolver](typed-root-cause-resolution.md) handles the wiring failures no stage here claims.

## The stages, in order

Each stage recognizes one class and returns a verdict: continue, drop the diagnostic, or reshape it.
The first stage that does not continue decides, so the order is part of the behaviour. The stages run
in this order, from `transform_with` in
[`cgp_emitter.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/cgp_emitter.rs):

1. A misused `#[cgp_impl]`, then a provider trait named in `#[uses]`: [a wrong component half](#reshaping-a-wrong-component-half).
2. An overflow that follows from an unresolved wiring name, then a consumer trait used as a wiring key: [an unresolved wiring name](#reshaping-an-unresolved-wiring-name).
3. [A duplicate-key conflict](#reshaping-a-duplicate-key-conflict), then [an orphan-rule namespace registration](#reshaping-an-orphan-rule-namespace-registration).
4. A method two `#[cgp_auto_dispatch]` traits share, then the other [structural mistakes](#reshaping-a-structural-mistake).
5. An undeclared trait, then an unimported inner provider: [an undeclared dependency](#reshaping-an-undeclared-dependency).
6. [A provider impl written without its macro](#reshaping-a-provider-impl-written-without-its-macro).
7. An unimported abstract type, then an undeclared requirement: [an undeclared dependency](#reshaping-an-undeclared-dependency).
8. A [`?`-operator cascade](#dropping-a-question-mark-cascade), then a later report of a provider impl written without its macro.
9. The [typed resolver](typed-root-cause-resolution.md), then the [text rewrite](#naming-the-traits-behind-a-component-marker).

Three passes run after name resolution rather than as stages, because they need the `TyCtxt` the
`after_expansion` hook provides: [the wiring entries' name-resolution errors](#reshaping-an-unresolved-wiring-name),
[a suggestion naming a generated identifier](#dropping-a-suggestion-that-names-a-generated-identifier),
and [the help on a misspelled `#[use_type]` import](#replacing-the-help-on-a-misspelled-use_type-import).

## Naming the traits behind a component marker

The driver rewrites the compiler's wiring diagnostics to name the consumer and provider traits a
reader thinks in, in place of the internal marker-based phrasing: both the obligation-chain notes
and the primary header the error opens with. Where rustc reports
`` required for `RectangleArea` to implement `IsProviderFor<AreaCalculatorComponent, Rectangle>` ``
and `` required for `Rectangle` to implement `CanUseComponent<AreaCalculatorComponent>` ``, the tool
emits
`` required for the provider `RectangleArea` to implement the provider trait `AreaCalculator` for the context `Rectangle` ``
and `` required for the context `Rectangle` to implement the consumer trait `CanCalculateArea` ``. A
generated parameter in the context's place (`__Context__`, the context a provider impl is generic
over) is not called a context: the provider note leaves it out, and the consumer note names it
plainly (the `a_generated_parameter_is_not_called_a_context` test in
[`rewrite/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/rewrite)).
A provider-side primary header is rewritten further, because an unsatisfied `IsProviderFor` bound
is an identified CGP error class and gains its [CGP error code](../error-code.md):
`` the trait bound `RectangleArea: IsProviderFor<AreaCalculatorComponent, Rectangle>` is not satisfied ``
becomes
`` [CGP-E002] the provider trait `AreaCalculator` with context `Rectangle` is not implemented for provider `RectangleArea` ``,
restating the fact the marker form stands in for, with the diagnostic's own Rust code kept. A
check's `CanUseComponent` header is the [typed resolver](typed-root-cause-resolution.md)'s to word,
so the text rewrite leaves it. This is
the transform the `IsProviderFor` and `CanUseComponent` marker traits otherwise hide: the component
marker names neither trait, its `…Component` suffix is at best an unreliable guess at the provider
trait, and it says nothing at all about the consumer trait.

Recovering the names inverts two links `#[cgp_component]` generates, both built in
[`component_map`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/component_map.rs).
A component marker (`AreaCalculatorComponent`) is an empty struct with no reference to its traits,
so the map is built by walking the trait graph. The provider trait carries
`IsProviderFor<Marker, …>` as a supertrait, so scanning every trait's super-predicates yields each
(provider trait, marker) pair. The consumer trait's blanket impl reads
`impl<C> Consumer for C where C: Provider<C>`, so a blanket impl bounding its *own* self type on a
known provider trait names that provider's consumer. Requiring the bound's self type to be the
impl's self type tells this apart from the provider blanket impl, which bounds the same
provider trait on a projected `<C as DelegateComponent<…>>::Delegate` rather than on `C` itself.
Composing the two gives, per marker, both trait names.

The `IsProviderFor` supertrait is matched by **identity, not spelling**. Each candidate bound's
resolved `DefId` is checked to be the `IsProviderFor` *defined in the `cgp_component` crate* (the
crate that owns the trait, since `cgp` and `cgp_core` only re-export it and a `pub use` mints no new
`DefId`), so a trait merely named `IsProviderFor` in some unrelated crate never seeds an entry, and
the map is provably rooted in real CGP provider traits. The defining crate name lives in
[`config`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/config/cgp_component.rs)
as `CGP_COMPONENT_CRATE`.

Each entry is **keyed by the marker's full path** (`def_path_str`), not its bare name, so two
distinct structs sharing a marker name in different modules occupy separate entries. The map's sole
consumer is the **text-rewrite fallback** below, which has only the marker as rendered into the
diagnostic text, with no `DefId`. It matches the printed marker against each key's trailing
segments: rustc prints a marker bare when its name is unique and qualified when two items share it,
so a qualified `shapes_a::MeasurerComponent` picks out its own entry. When the keys that match stand
for different traits (a bare name two components share), the lookup declines and the message keeps
rustc's wording, so a note never names the other component's trait
([`same_name_marker_rename`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/same_name_marker_rename.rs)). (The [typed root-cause resolver](typed-root-cause-resolution.md) does
not use the map: it reads consumer and provider names straight off the real trait `DefId`s it walks,
part of resolving without depending on `IsProviderFor`, the very supertrait this map is built by
inverting. The map therefore serves only the declined-diagnostic text path, where recognizing
`IsProviderFor`/`CanUseComponent` in rustc's output is essential.)

The walk is expensive (it visits every trait and its blanket impls), so it runs at most once,
wrapped in a
[`ComponentNameMap`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/rewrite/names.rs):
a `LazyLock` whose initializer performs the walk on the first lookup and is cached for every lookup
after. The emitter's `emit_diagnostic` runs once per diagnostic, not once per compilation, so this laziness keeps the walk from repeating. And because a lookup happens only when a message
actually parses as a wiring form (the rewrite functions consult the map last, after matching the
message shape), the walk never runs at all for a diagnostic that mentions no CGP wiring, which is
why the emitter needs no separate "is this a CGP diagnostic?" pre-check. The initializer reaches the
`TyCtxt` from thread-local scope (`rustc_middle::ty::tls`), valid because a wiring message is built
during trait solving when a `TyCtxt` is in scope; the driver supplies it as the plain `fn`
[`build_name_map_from_tls`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/component_map.rs).
Because that initializer is a `fn` pointer capturing no compiler state, the `ComponentNameMap` type
itself carries no compiler types and lives in the rustc-free crate alongside the rewrite it feeds.

Caching across lookups carries no staleness risk. The map draws only on data that is fixed for the
rest of the compilation once the crate is resolved and lowered (the trait set, the `IsProviderFor`
supertraits, and the blanket impls, none of which the type-checking phase that emits these
diagnostics ever mutates), and it stores owned `String`s rather than `DefId`s or other compiler
handles that later interning or arena churn could invalidate. It is one `TyCtxt` for one driver
invocation over one crate, with no cross-session, incremental database (unlike rust-analyzer's) that
could change underneath the cache between calls.

The rewrite itself is a plain string transform, kept in the rustc-free
[`cargo-cgp-error-processing`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing)
crate (module
[`rewrite`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/rewrite))
so it is unit-tested on any toolchain without a `TyCtxt`. Its entry point, `rewrite_message`,
dispatches to the `required for … to implement …` note forms (`rewrite_required_for`) and the
`the trait bound … is not satisfied` header form (`rewrite_trait_bound`, which stamps the
`[CGP-Exxx]` code). Each reads the marker out of the trait's generic arguments and looks the names
up in the map.

The `overflow evaluating the requirement …` header form has its own entry point,
`rewrite_wiring_overflow`, because its wording depends on why the lookup never resolves, which the
overflow's text does not say. Before it rewrites an `E0275`, the emitter walks the consumer
obligation at the caret (`overflow_walk` in the driver's `resolve/overflow.rs`): a check entry's,
or else that of the consumer-method call whose consumer trait the overflow names, recovered by the
call-site anchor's own steps, since a call overflows on the consumer trait itself rather than on
`CanUseComponent`. The text form accepts that requirement when the name map knows the trait as a
consumer (`ComponentNameMap::is_consumer`). The walk reports
how it was cut as a rustc-free `WiringOverflow`. An obligation met again among its own ancestors is
a cycle, stamped `[CGP-E020]` and worded "the lookup leads back to itself"; a `UseContext`
delegation whose only consumer-trait impl is that delegation is the plain case. The depth cap
reached without a repeat is a lookup that grows, stamped `[CGP-E021]` and worded with the first
larger requirement: the first later obligation of the same trait with other arguments, named by its
`Self` type when that type grows. The walk follows a consumer obligation on another context,
one from another crate included when it carries wiring, so a lookup that grows in the type the
consumer trait is required of reaches the cap too
([`divergent_self_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_self_wiring.rs)).
The emitter then drops the note pointing at the generated `__Check…` trait (the
kept caret already covers the check entry) and rustc's advice to raise the recursion limit
(`is_recursion_limit_help_text`), which no limit satisfies, and attaches a `help` naming the
provider whose requirement closes or grows the loop (`wiring_overflow_help`). That provider is the
walk's provider step just above the repeated or first larger requirement, and it is named only when
the obligation above it is a wiring entry's routing, on the context or on a `RedirectLookup` for an
`open` or namespace entry. A provider a higher-order provider holds inside it, such as the inner
`UseContext` a dispatcher routes each variant through, is chosen by no entry, so its block's `help`
names no provider. The
[`use_context_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle.rs),
[`divergent_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring.rs),
and
[`dispatcher_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/dispatcher_cycle.rs)
fixtures pin the reshaped output at a check, and
[`use_context_cycle_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle_call.rs)
and
[`divergent_wiring_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring_call.rs)
at a call. An overflow the walk does not cut keeps rustc's wording and notes, and the typed
resolver never takes an `E0275`: a walk that stops at a bound instead of a cut means that bound's
own evaluation overflowed, which no root cause states truly
([`cross_context_cycle_reuse_distinct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs),
whose cycle runs through a plain trait bound on another context). An overflow can also follow from
an earlier unresolved name: a wiring entry that names a type the compiler could not resolve holds a
`{type error}`, and a lookup through it can overflow with no cycle in the wiring. Its walk meets
neither the cycle guard nor the depth cap, and the earlier error is the one to fix; when the name
is a wiring entry's, the emitter drops the overflow as that entry's consequence instead
([unresolved wiring names](#reshaping-an-unresolved-wiring-name)). The walk does not descend an
obligation holding a `{type error}`, so a type error cannot make it loop, while a real cycle beside
one is still reported
([`type_error_in_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/type_error_in_wiring.rs)).

The emitter applies the full dispatch only to a diagnostic's *main* message and the note rename to
its children, since a CGP error code belongs on a main message alone. A message whose marker is
absent from the map, or any other message, passes through untouched. A **generic component**, one
whose marker carries extra type parameters so that `CanUseComponent`/`IsProviderFor` gain arguments
after the marker (and context), is handled in both forms, but differently by design: the descriptive
notes name the bare trait and elide the parameters, while the header *reattaches* them so the
message stays precise. So `CanUseComponent<AreaCalculatorComponent, f64>` yields the header
`` the consumer trait `CanCalculateArea<f64>` `` and the note "the consumer trait
`CanCalculateArea`"; a two-parameter component arrives tuple-grouped (`(u32, u64)`) and the header
unwraps it to `` `CanCalculateArea<u32, u64>` ``. The map records each component's parameter count,
read off its provider trait, because a one-parameter component whose parameter is a tuple arrives in
the same shape and must stay whole (`CanFormatPair<(u32, u64)>`); and the argument splitter does not
count the `>` of a function pointer's `->` as a closing bracket. One faithful oddity follows from
naming the obligation's subject verbatim: the subject is usually a provider (`RectangleArea`,
`ScaledArea<RectangleArea>`) but is the context itself when the context stands in as its own
provider, so a self-provider case reads
`` the provider `Rectangle` … for the context `Rectangle` ``. The before/after is pinned across the
check-trait-failure fixtures (the `fields/`, `providers/`, `generic/`, `field-types/`, and
`resolution/` subgroups), whose blessed snapshots show the trait-named notes *and* headers;
[`base_area_1`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_1.cgp.stderr)
is the worked example.

The same emitter seam hosts a deeper transformation that rebuilds a diagnostic's sub-messages rather
than rewording them, and it is tried *before* the rename. Where the trait-renaming rewrite edits the
compiler's text in place, the [typed root-cause resolver](typed-root-cause-resolution.md) re-runs
the failing check obligation through the compiler's `InferCtxt` / `ObligationCtxt` API, descends to
each terminal leaf, and replaces rustc's cascade of sub-notes with one `root cause:` note over the
dependency graph of every leaf (wording the coded main message from typed data where the text lookup
could be ambiguous). It falls back to the in-place rename whenever it cannot fully resolve the
cause. That kind of work must happen in the driver, because it needs the live compiler the front-end
never sees; it happens in the *emitter* specifically because the natural `after_analysis` hook is
unreachable once the crate has errors (the resolver document explains why). Whichever of the two
produced the diagnostic, it then passes through the rustc-free
[post-processing](error-processing.md) cleanup, so the type names either transform embeds are
stripped of CGP path prefixes and resugared.

The resolver is not limited to diagnostics worded in CGP terms. A failure that *never names a CGP
construct* can still be a consequence of a CGP component failing (a hand-written `Send`-recovery
wrapper whose `async fn` forwards to a wired method fails with an `E0271` opaque-future mismatch, or
a downstream trait bound needs a method the context cannot supply), so the emitter offers the
resolver every method `E0599`, `E0271`, and `E0277` (not only the ones mentioning a wiring trait).
The resolver anchors such an error on the enclosing hand-written `impl` (whose supertrait is a CGP
consumer trait) and traces the dependency chain from there; if the chain reaches a CGP root cause it
renders the tree, and if it does not it declines and the error passes through untouched. A traced
`E0271` whose cause is *not* a projection mismatch (its opaque `type mismatch resolving …` message
being unreadable) is given the `[CGP-E001]` consumer header, since it is really the consumer trait
failing to be implemented; one that *is* takes the matching mismatch header: `[CGP-E004]` for a
`HasField` value type, `[CGP-E005]` for any other associated type.

## Cleaning a declined consumer-method error

A declined consumer-method `E0599` gets one further cleanup before the fallback rewrite runs.
rustc's method probe, meeting CGP's `self`-less provider methods, frames the failure as a
call-syntax mistake (a "this is an associated function, not a method" caret label, a "found the
following associated functions …" note, and a "use associated function syntax instead" suggestion
that is actively wrong), while the real cause, the unmet wiring bound, sits in a later note. For a
method-bounds `E0599` that mentions a CGP wiring trait, the emitter strips that method-probe advice
(`strip_method_probe_advice`, over the phrasings
[`is_method_probe_advice_text`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs)
recognizes), so the wiring bound is the first note a reader meets. It drops only that one
suggestion: rustc's others stay, such as the bound to restrict a generic parameter with when a
provider body calls a trait method on it
([`undeclared_trait_on_non_context_parameter`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_trait_on_non_context_parameter.rs)).
The
[`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs)
fixture, a use-site failure whose dispatch parameter no anchor can recover so that the resolver
always declines, pins the cleaned output.

## Dropping a question-mark cascade

The emitter also drops a **downstream `?`-operator cascade** of a wiring failure. When
a consumer-method call fails and its result is consumed with `?` (`app.handle(…).await?`), the type
of `expr?` becomes unresolvable, so rustc adds a `Try` / `FromResidual` error on the same expression
that merely restates the wiring failure and dumps the unresolved `<Ctx as Consumer<…>>::Output`
projection. The emitter records the primary span of every CGP failure it recognizes (`cgp_spans`,
populated before de-duplication so even a dropped re-report still anchors its cascade) and, before
trying any transform, suppresses a later diagnostic that both looks like a `?`-operator error
(`is_question_mark_cascade`, matching rustc's stable "the `` ? `` operator can only …" wording) and
whose span overlaps a recorded failure. rustc emits the wiring failure before its cascade, so the
span is always recorded in time. The scope is deliberately tight (only a `?` error sitting on an
expression where a CGP wiring error was already shown is dropped, never a `?` misuse elsewhere),
which makes suppressing an otherwise-untouched `rustc` error sound. The resolver declines
every `?` error, since it is about `Try` on the call's result rather than the call's bounds, so one
with no recorded failure is left as rustc wrote it rather than re-anchored onto the call it
overlaps. It removes the two projection-dumping cascade blocks a `Code`-dispatched use-site failure
would otherwise trail, while the [call-site anchor](typed-resolution-call-site.md) resolves the
failure itself into one block; the pinning fixture is
[`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs).

## Reshaping a duplicate-key conflict

This reshape runs *before* the resolver and the rename, and handles a different failure kind: the
coherence conflict (`E0119`) a duplicate wiring entry produces. A duplicate `delegate_components!`
key makes the expansion emit two overlapping `DelegateComponent` impls, and because each
context-wiring entry also generates an `IsProviderFor` forwarding impl, the compiler reports the
same conflict *twice*: once keyed on `DelegateComponent<…>` and once on `IsProviderFor<…>`, both
internal traits the user never wrote. The transform recognizes the pair as one logical mistake: it
**drops** the redundant `IsProviderFor` diagnostic (emitting nothing) and **rewrites** the
`DelegateComponent` one into a coded headline that names the colliding key(s), keeping rustc's two
carets ("first implementation here" and "conflicting implementation"), which already point at the
two entries. The code is one of `[CGP-E010]`–`[CGP-E014]`, chosen by the shape of the collision.

The `IsProviderFor` suppression is gated on its **companion conflict being confirmed**, because
suppressing a lone `E0119` would leave a failing build with no error at all. Every generated
`IsProviderFor` impl rides alongside another impl from the same macro invocation (the
`DelegateComponent` entry impl of a wiring entry, or the provider-trait impl of a `#[cgp_provider]`
block), and the two conflict exactly when their `IsProviderFor` copies do. So the classifier
suppresses only when a genuine local `IsProviderFor` impl sits at the caret *and* the two colliding
sites each carry a local impl of one *common* other trait, whose own `E0119` rustc then reports. An
`IsProviderFor` conflict with no common companion is left alone. A duplicate provider *name* (two
`#[cgp_impl(new P)]` blocks) never reaches this classifier: rustc stops once name resolution finds a
type defined twice, so the `E0428` is the only error
([`duplicate_provider_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_provider_name.rs)).
Two `#[cgp_impl(P)]` blocks for one provider struct declared once do reach it: the provider-trait
`E0119` is kept and its `IsProviderFor` twin dropped
([`duplicate_provider_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_provider_impl.rs)).

Everything is recovered from the compiler, not the error text. rustc aims the `E0119` at
`tcx.def_span` of the conflicting impl, and the delegate macro re-spans each entry onto its key
token, so
[`detect::conflict`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect/conflict)
matches the caret to that `DelegateComponent` impl (by source range, since the two halves of the
pair carry the same range under different `SyntaxContext`s) and reads the entry off it: its context,
its key, and its `Delegate`. It does the same for the "first implementation here" impl at the
diagnostic's other labelled span. rustc labels that impl only when it is local; an upstream one,
such as the blanket forwarding of a namespace an upstream context joins, appears in a note instead,
and then the classifier declines, since it cannot say what the entry collides with
([`upstream_namespace_join_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/upstream_namespace_join_overlap.rs),
and the namespace-trait form
[`upstream_namespace_inheritance_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/upstream_namespace_inheritance_overlap.rs)).
Otherwise it classifies the shape into one of the five, each with its own code: a **duplicate**
(`CGP-E010`, the two keys render equal), an **overlap** (`CGP-E011`, distinct but colliding keys: a
generic over a specific, or a path prefixing another), **multiple namespaces** (`CGP-E012`, both
keys are blanket forwardings, so the context joins more than one namespace), a **redirect**
collision (`CGP-E013`), or a **duplicate redirect** (`CGP-E014`, both entries redirect). The two
redirect shapes need entries over one key, whose keys render equal or one of which is a blanket
forwarding; two distinct keys are an overlap whatever they map to. An overlap's covering key is the
one whose pattern unifies with the other key once its impl's parameters are fresh inference
variables, whichever entry comes first. When neither does, the two patterns are unified with each
other and the key they share is named, a parameter that meets only another open parameter kept as
written
([`specific_before_generic_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/specific_before_generic_overlap.rs),
[`path_generic_segment_overlap`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/path_generic_segment_overlap.rs),
[`overlapping_redirects`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/overlapping_redirects.rs)). Each
entry's target for the colliding key is read the same way: an ordinary entry's is its `Delegate`, a
`RedirectLookup` for an `open` or `=>` redirect, while a blanket forwarding (a `namespace` join) has
a generic `Delegate`, so its target is recovered by normalizing `<key as Namespace<Ctx>>::Delegate`
for the other entry's concrete key through the trait solver (the same re-entrant normalization the
typed resolver uses). So a namespace that redirects a prefixed component, beside an `open` of the
same component, is a duplicate redirect naming both paths
([`open_prefixed_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/open_prefixed_component.rs)),
and the generic parameter is never named as a provider. A redirect collision's header names only the
redirected path; the *fix* (wire the direct entry's provider under that key) rides in a separate
`help`, kept out of the header so the headline stays one short sentence. A redirect looks a
component up with its type parameters appended to the path, so for a generic component the `help`
names a generic key (`@AreaCalculatorComponent.<Shape> Shape`) rather than the bare path the lookup
never reads
([`open_and_use_delegate`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/open_and_use_delegate.rs)).
The `help` is omitted when the direct entry names no provider a reader wrote. Each key is rendered
to its surface form off the types (a component marker to its name, a `PathCons<…>` to its bare `@…`
path as its entry wrote it (a generic segment printing its parameter name, so an `open` entry's
`<Code> Code.u64` reads `@ComputerComponent.Code.u64`, a type segment keeping its arguments so
`Wrap<u64>` and `Wrap<T>` stay apart, and the `__Wildcard__` tail the macros append left out), an
ordinary type key to its own rendering, a blanket forwarding to the namespace/table trait that keys
it), so the headline names what the programmer wrote. A marker is told from an ordinary type
structurally, by whether a provider trait's delegation blanket keys on it, so a per-type default's
`String` reads as a type rather than as a component nobody defined. The message wording is decided
by the rustc-free
[`plan_wiring_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/wiring.rs)
(and `wiring_conflict_help` for the redirect fix) over the owned `WiringConflict` the classifier
fills in, so it is unit-tested without a compiler.

An `E0119` naming *neither* internal trait can still be a wiring conflict: an entry inside a
namespace conflicts on that namespace's own lookup trait
(`` conflicting implementations of trait `MyNamespace<_>` for type `PathCons<…>` ``). The
classifier's namespace route recognizes that shape by the impls at the carets (a local impl of a
[namespace lookup trait](typed-root-cause-resolution.md), recognized by the single-`Delegate`
fingerprint), and words it through the same `WiringConflict` shapes, with the namespace trait as the
subject, rendered with its leading arguments but without the components table the macro appends
(`DefaultImpls1<ShowImplComponent>`). Four constructs emit such an impl, and all four are read the
same way: a `cgp_namespace!` body entry, a component's `#[prefix(… in Namespace)]` route, a
provider's `#[default_impl(… in Namespace)]` registration, and the inheritance blanket a
`new Child: Parent` header emits. So two `=>` entries on one path become a `[CGP-E014]` duplicate
redirect naming both targets
([`namespace_duplicate_path_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/namespace_duplicate_path_key.rs)),
two `#[default_impl]`s on one key a `[CGP-E010]` duplicate
([`duplicate_default_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/duplicate_default_impl.rs)),
and a child namespace binding a key its parent already binds a `[CGP-E011]` overlap naming the
parent
([`inherited_override_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/inherited_override_conflict.rs)).

One mistake cuts across those shapes and earns its own message: binding a prefixed component by its
bare marker, when the component is addressed by its path. Where the colliding entry is the
`#[prefix]` route itself, its `Delegate` *is* the `RedirectLookup` and is read directly
([`default_impl_unprefixed_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/default_impl_unprefixed_key.rs)).
Where it is an inheritance blanket, whose `Delegate` is a projection rather than a written redirect,
normalizing the parent's `Delegate` for the colliding key recovers the same path, exactly as the
context-level route does for a `namespace …;` join
([`namespace_inherited_unprefixed_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/namespace-override-conflict/namespace_inherited_unprefixed_key.rs)).
Either way the collision reads as a `[CGP-E013]` redirect whose `help` names the entry to write
instead.

The transform is anchored to the genuine CGP traits (by `DefId`, like the rest of the resolver), so
a same-named trait cannot drive it, and it declines a conflict whose carets carry none of the
recognized impls, leaving it to the fallback. The blessed snapshots under
[`wiring/conflicting-wiring/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/conflicting-wiring)
and the namespace classes beside it pin each shape.

## Reshaping a structural mistake

Some mistakes are in the shape of what a macro was given, and the compiler rejects them through the
items the macro generated, so its error names those items and offers a fix that does not apply.
Seven such shapes are reshaped, each recognized from the generated items at the caret by a detector
under
[`detect::structural`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect/structural)
and worded by the rustc-free `plan_structural_mistake` and `structural_mistake_help`:

- **A check entry listed twice** (`[CGP-E015]`): the `E0119` between two identical impls of a
  `check_components!` check trait, recognized by its `CanUseComponent` supertrait, with the entry
  read off the impl at the caret. rustc's carets stay.
- **Two check tables sharing a check-trait name** (`[CGP-E016]`): the `E0428` name resolution
  reports. No query is safe that early, so the driver reads the name from the diagnostic's own
  argument and confirms the span came from a `check_components!` expansion through its expansion
  data alone. The expansion records a macro by the path its call was written with, so the detector
  compares that path's last segment with the macro's name: `cgp::prelude::check_components!`
  counts, and a crate's own macro whose name only ends the same way, such as
  `table_check_components!`, does not. rustc's labels and note name the generated trait, so the two
  carets are relabelled as the first and the second table.
- **A check entry that names no parameters for a component that takes some** (`[CGP-E060]`): an
  `E0277` whose caret is the `Self` span of a check impl (the impl of a trait whose supertrait is
  `CanUseComponent`, as the check-entry anchor finds it) asserting `CanUseComponent<Marker, ()>`,
  where the marker's consumer trait takes parameters. The parameters the help names are the `Params`
  of each `IsProviderFor` impl whose component and context unify with the check's, fully resolved
  and not `()`, each kept only when `Context: CanUseComponent<Marker, Params>` holds in the check
  impl's own environment; with none, the detector declines. The help writes them in the form of the
  macro the check trait comes from (`#[check_params(…)]` for a `delegate_and_check_components!`
  table, read from the trait definition's macro backtrace by the same name rule, and
  `Component: Params` otherwise).
  rustc's notes and its `where` suggestion are dropped, and the caret stays on the entry. The
  detector runs before the typed resolver, which declines the unit-parameter obligation and leaves
  rustc's error, or its `[CGP-E002]` text rewrite, in place.
- **Two `#[cgp_auto_dispatch]` traits in one module sharing a method name** (`[CGP-E061]`): the two
  `E0428`s on the items the macro names after the method alone, the helper `__compute_{method}__`
  and the computer `Compute{Method}`. Neither is enough alone: the helper's caret comes from the
  macro's expansion but sits on the attribute, and the computer's sits on the method name with no
  trace of the macro. So the emitter pairs them as they arrive
  ([`shared_dispatch_method`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/stage/shared_dispatch_method.rs)):
  the macro defines the helper first, so when the computer's `E0428` arrives, a buffered helper
  `E0428` from a `#[cgp_auto_dispatch]` expansion whose method gives the computer's name (the
  rustc-free `dispatch_helper_method` and `dispatch_computer_name` mirror the macro's naming) is
  dropped, and the computer's is reworded, with its two carets labelled as the first and the second
  declaration and a note naming the two generated items. It reads no compiler query, since an
  `E0428` arrives during name resolution.
- **A `for` loop whose key skips its variable** (`[CGP-E017]`): an `E0207` on a parameter of a
  loop-generated `DelegateComponent` entry (or its `IsProviderFor` twin) whose namespace bound's
  variable the key does not mention.
- **A `#[default_impl]` on a generic provider impl** (`[CGP-E018]`): an `E0207` on a parameter of a
  registration impl (a namespace lookup trait other than `DelegateComponent`) that neither its key
  nor its trait arguments use. When the provider it registers uses the parameter (a provider struct
  generic over it), the mistake is recognized only for a type key, and the help names the provider
  with the key's type in the parameter's place.
- **A wiring entry whose key skips its generic parameters** (`[CGP-E019]`): an `E0207` on a
  parameter of a `DelegateComponent` entry, or of a `cgp_namespace!` entry's lookup-trait impl, that
  nothing binds: neither the trait arguments name it, nor an associated-type bound whose arguments
  are bound. A namespace impl is an entry only when no provider impl declares the same parameter,
  since a `#[default_impl]` registration copies its provider impl's parameters, and an entry bounded
  by a lookup trait on the parameter is a `for` loop's. The mistake lists every parameter nothing
  binds, and its help depends on what in the entry uses them: the provider, another part of the
  value, or nothing.

The three `E0207` shapes drop rustc's suggestions, which remove the parameter or add it to the
context, and keep the caret on the parameter alone; `[CGP-E060]` does the same with the entry. One
mistake can produce several errors (a loop's two variables, or an entry's parameters, each in every
impl the entry lowers to), so the emitter reports each recovered mistake once and drops the rest.
The `E0207` detectors print a type by its own name rather than through the trimmed-paths map: an
`E0207` is emitted before any type has been printed with trimmed paths, and the first such print
records itself on the diagnostic context, whose lock the emitter holds
([rustc diagnostic internals](rustc-diagnostic-internals.md)). The fixtures under
[`wiring/conflicting-wiring/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/conflicting-wiring)
(`check_duplicate_entry`, `check_twice_same_context`, `check_twice_qualified_call`, and their
siblings) and
[`wiring/unconstrained-generic/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/unconstrained-generic)
(`for_loop_key_without_var`, `default_impl_generic_provider`, `default_impl_explicit_context`,
`unconstrained_generic`, `entry_generic_shapes`, `entry_generic_checked`, and
`namespace_entry_generic`, and `default_impl_generic_provider_struct` for the generic provider
struct) pin the shapes. The check at unit parameters is pinned under
[`checks/check-trait-failure/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure)
by `generic_component_unit_params`, `qualified_delegate_and_check_unit_params`, and
`check_trait_named_as_wrapper` (in `delegate_and_check_components!`, a component with a type
parameter, the macro called by its path, and a generic key) and `generic_check_without_params` (in
`check_components!`), and the shared dispatch method by `auto_dispatch_shared_method_name`,
`auto_dispatch_shared_method_names`, and `auto_dispatch_shared_method_name_qualified` under
`wiring/conflicting-wiring/`. The pass-through fixture `own_check_components_macro` pins the name
rule's decline.

A doubled `#[prefix]` is not among them: its two namespace registrations collide as a duplicate
redirect, `[CGP-E014]`, which the [duplicate-key reshape](#reshaping-a-duplicate-key-conflict)
words. Both registrations carry the attribute's span, so the namespace route pairs two entries at
one span as the first and the conflicting entry.

## Reshaping an orphan-rule namespace registration

The orphan reshape handles the other coherence-class error, the orphan-rule violation (`E0210`, or
its sibling `E0117`) a namespace registration produces when the crate owns neither end. Registering
wiring into a namespace lowers to `impl<Param> Namespace<Param> for Key`, and Rust's orphan rule
accepts a foreign-trait impl only when a local type covers its parameters. When *both* the namespace
trait and the key are foreign (a downstream crate registering into an upstream namespace it does not
own, keyed on an upstream component it does not own either), nothing is local, and the compiler
rejects it, naming the machinery parameter (`__Components__` from a `#[default_impl]`/`#[prefix]`,
`__Table__` from a `cgp_namespace!` re-open) and framing a CGP wiring decision as a bare coherence
rule. The transform **rewrites** that headline into the coded `[CGP-E022]` form, naming the foreign
namespace and the key the programmer wrote, re-aims the caret at the offending macro alone (dropping
the "uncovered type parameter" label, which does not apply), and adds a `help` carrying the
ownership-based fix the raw error never states.

Everything is recovered from the compiler, not the error text, the reverse of relying on the
`__Components__`/`__Table__` names the message happens to print. A cheap text pre-filter
([`mentions_orphan_param_text`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs))
gates the scan on the `E0210` naming such a machinery parameter, then
[`detect::orphan`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/orphan.rs)
finds the offending impl: a local impl of a *foreign*
[namespace lookup trait](typed-root-cause-resolution.md) (the single-`Delegate` fingerprint, so a
downstream crate's own namespace trait is recognized like CGP's built-in `DefaultNamespace`) for a
*foreign* key. Because rustc emits an `E0210`/`E0117` *only* for a genuine orphan, matching the
caret to that impl (by source range) is the whole confirmation; a lone candidate is used even when
the range match misses, and any ambiguity declines to the fallback. The key renders to its surface
form off the types (a component marker to its name, a `PathCons<…>` to its bare `@…` path) through
the same `describe_key` the conflict classifier uses, and the trigger (which fix to word) is read
from the impl's own machinery parameter name (`__Table__` for a re-open, `__Components__` for a
registration), a reliable `DefId`-independent discriminator. The message wording is decided by the
rustc-free
[`plan_orphan_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/orphan.rs)
(and `orphan_conflict_help` for the fix) over the owned `OrphanConflict` the classifier fills in, so
it is unit-tested without a compiler. The blessed snapshots under
[`wiring/orphan-rule/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/orphan-rule)
pin the component-key, path-key, and re-open shapes.

## Reshaping an undeclared dependency

This reshape handles a macro-lowering mistake: a dependency a CGP definition uses but does not declare (the
[undeclared dependency](../../cgp/errors/lowering/undeclared-dependency.md) class). Each CGP
definition macro lowers its body into an impl over a generated context, and only the declared
dependencies become bounds on it, so each kind of declaration has its own code. Each is recovered
off the compiler by a detector under `detect`, keeps the caret rustc chose, and is worded by a
rustc-free `plan_*` and `*_help` pair in [error processing](error-processing.md).

**An undeclared trait (`[CGP-E030]`).** A trait the body calls on the context without `#[uses(…)]`
fails with an `E0599`: the method-bounds shape for `self.method(…)` ("exists for reference
`&__Context__`"), or the unbounded-type-parameter shape for `Self::method(…)`, whose Fluent main
message is recognized by its plain-string help.
[`detect::detect_undeclared_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/undeclared.rs)
confirms it structurally. The failing call, found by its method segment's span, sits in a generated
impl over a bare type-parameter context (reached by walking up from the call's body owner, through
any `#[async_trait]` coroutine); it is made on that context (a receiver parameter must be declared
as the context, followed through the `let` an `async fn` adds, a `let`'s annotation must name it, and
a qualifying type must name it); it names a function of a CGP consumer or blanket trait; and that trait is not already a
`where` bound of the impl. When several traits share the method name, the one whose definition the
diagnostic's notes touch is taken. The help writes the trait with the arguments the call uses: the
detector instantiates the function's signature with fresh variables, pins `Self` to the context, and
unifies each declared input with the argument's type where that type can be read without typeck (a
written type, through the `expr_written_ty` the call-site anchor also reads, a parameter's declared
type with its late-bound lifetimes made fresh, or a `let` annotation). A trait parameter left
unknown, or resolved to a type holding a lifetime or a generic parameter, stays named for the reader
to replace, and a trait with a lifetime or const parameter gets the header without a help. A call on
any other parameter is left alone, since `#[uses]` cannot bound it. Any `[T]: Sized` cascade the
failed call trails is left as rustc wrote it, because those errors can land off the failing
expression, where suppressing them reliably would risk hiding an unrelated error.

**An unimported inner provider (`[CGP-E031]`).** The body invokes the inner provider as an
associated function, `InnerCalculator::area(self)`, which needs the parameter bounded as
`InnerCalculator: AreaCalculator<Self>`, declared through
`#[use_provider(InnerCalculator: AreaCalculator)]`. Forgetting the import leaves the parameter
unbounded, so rustc reports a vague `E0599` ("no associated function `area` found for type parameter
`InnerCalculator`") whose suggestion leaks the generated `__Context__` and offers the *consumer*
trait as a bound, the wrong fix for a higher-order provider. The transform rewrites it into a
`[CGP-E031]` header naming the inner provider, with the `#[use_provider(…)]` fix in a `help` (a
generic component's parameters written from the call, the way `[CGP-E030]` writes a generic trait's,
with the inner provider as `Self` and the context argument left for the attribute, and no `help` for
a provider trait with a lifetime or const parameter), recovered by
[`detect::detect_missing_use_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/missing_use_provider.rs):
the failing call is an associated-function call `Param::method(…)` on a generic parameter of an
enclosing provider-trait impl, the method belongs to a CGP provider trait, and the parameter is not
already bounded by it. It is gated to the "item on an unbounded type parameter" `E0599` shape
(reported during typeck of the calling body, where the detector's queries are cached, unlike the
resolution-class `E0599` emitted mid-`clauses_of`), recognized by its plain-string help
(`the type parameter is bounded by the trait`), since the `E0599`'s main message is a Fluent
(non-string) message. Its wording is the rustc-free `plan_missing_use_provider` /
`missing_use_provider_help` over the owned `MissingUseProvider`.

**An unimported abstract type (`[CGP-E035]`).** `Self::Error` without `#[use_type]` fails with an
`E0220`, "associated type `Error` not found for `__Context__`", emitted while the compiler lowers
the definition's types, inside the query computing that signature or body.
[`detect::detect_unimported_abstract_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/unimported.rs)
therefore reads only the HIR and trait definitions, never the item being lowered. The type, its
kind, and the type it was sought on come from the diagnostic's arguments (`assoc_ident`,
`assoc_kind`, `qself`), since the main message is a Fluent one. The enclosing item is recognized
from the generated items' fingerprints: a method of an impl that declares the reserved
`__Context__` parameter, of a consumer or provider trait, or of a trait whose local blanket impl
declares that parameter. The trait to import is the one CGP abstract-type component that declares an
associated type of that name, recognized by the `#[cgp_type]` fingerprint; a second such trait
makes the import ambiguous, and the error is left as rustc wrote it. The emitter reports the
mistake once: a later `E0220` for the same trait in the same item, or at the same caret, is dropped.

**An undeclared requirement (`[CGP-E036]`).** A component's `#[extend]` or `#[use_type]` puts a
`where` clause on the provider trait, and a `#[cgp_impl]` provider that does not declare it fails
with an `E0277` on `__Context__`, "required by a bound in" the provider trait, at the attribute and
again at each signature that checks the bound. The emitter gates on the main message naming
`` `__Context__: `` and hands the caret to
[`detect::detect_undeclared_requirement`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/requirement.rs),
which finds the provider impl holding it outside the impl's method bodies (a body's own errors are
not about what the impl declares), checks that the impl implements a CGP provider trait for a
provider type over a parameter context, and evaluates each `where` clause the provider trait places
on the context in the impl's own `param_env`. Each clause that does not hold is a requirement to
name, written with the context folded to `Self` (the name the provider's `#[uses]` gives it), and
one whose trait is an abstract-type component is worded as its `#[use_type]` import. The first such
`E0277` per impl is reworded, with the caret moved to the macro's call site so rustc's note that the
error originates in the attribute macro drops out, and the later ones are dropped.

The two abstract-type paths meet in a provider of a component that imports `Error`. Name resolution
reports a bare `Error` as an `E0425`, "cannot find type `Error` in this scope", before any `TyCtxt`
exists and before anything can say which trait declares an `Error`, so the emitter buffers it
untouched. When the provider's `[CGP-E036]` arrives and one of its requirements is an abstract-type
component, `convert_unresolved_abstract_type` looks in the buffer for an `E0425` naming that
component's type inside the impl, converts the first into the `[CGP-E035]` report, and drops the
rest; a `[CGP-E035]` already reported from an `E0220` explains the requirement the same way. An
explained requirement is left out of the `[CGP-E036]`, which is dropped when none remains, since
the import satisfies the requirement too. A bare `Error` without such a requirement keeps rustc's
`E0425` and its suggestion to import `std::error::Error`, a gap the `error_alias_in_cgp_fn` and
`error_alias_in_provider_body` fixtures pin. The blessed snapshots under
[`lowering/undeclared-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/undeclared-dependency)
pin every shape.

## Reshaping a wrong component half

This macro-lowering mistake is a definition that names the wrong half of a component (the
[wrong component half](../../cgp/errors/lowering/wrong-component-half.md) class), most often a
`#[cgp_impl]` header. `#[cgp_impl(new P)] impl AreaCalculator` is the idiomatic provider form: the
macro turns the header inside out into `impl<__Context__> AreaCalculator<__Context__> for P`,
inserting the context as the leading generic. Naming the component's *consumer* trait
`CanCalculateArea` there instead, or a trait that is not a CGP component at all, makes the macro
generate an inside-out impl of the wrong trait and reference a `…Component` marker that does not
exist. One mistake then produces a burst of cryptic errors: `E0425` (the missing marker), `E0107`
(the wrong trait given one generic argument too many, since the inserted context always exceeds a
consumer trait's arity), `E0186` (`&self` mismatch), `E0207` (`__Context__` unconstrained), plus a
downstream check failure, none naming the real cause. The transform **rewrites** the `E0107`, whose
caret already sits on the misused trait name, into a `[CGP-E032]` (consumer trait) or `[CGP-E033]`
(non-CGP trait) header with the fix in a `help`, and **suppresses** the rest of the cascade so one
clean error remains.

The same reshape covers a higher-order provider's **inner-provider bound** naming the consumer
trait, typically through `#[use_provider]`, which fills the leading context argument in, so
`#[use_provider(Inner: CanCalculateArea)]` generates `Inner: CanCalculateArea<Self>`, the consumer
trait again given one argument too many. That `E0107` on the bound is reshaped into a `[CGP-E034]`
header, and the `E0308` body cascade the malformed bound trails (told from a user's own type error
by its mention of the generated `__Context__`) is suppressed alongside it.

The mistake is recovered off the compiler by
[`detect::detect_cgp_impl_misuses`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/cgp_impl_misuse.rs),
never from error text, using the consumer- and provider-trait fingerprints. Three structural
conditions select the *user's* `#[cgp_impl]` impl and exclude every blanket and forwarding impl the
CGP macros generate (which also carry `__Context__`): the impl has the `#[cgp_impl]`-inserted
`__Context__` generic; its `Self` is a concrete local struct/enum (the provider struct), where the
generated consumer/provider blanket impls have a bare type-parameter `Self`; and its header trait
reference is a token the user wrote (not from a macro expansion), where the generated
`IsProviderFor`/`DelegateComponent` forwarding impls carry a synthesized reference. The header trait
is then classified by
[`consumer_provider_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/resolve/query/cgp_item/component.rs):
a consumer trait yields the provider trait to suggest (`[CGP-E032]`), a provider trait is the
correct target and is skipped, and anything else is a non-CGP trait (`[CGP-E033]`); each of the
impl's inner-provider `where`-bounds is scanned the same way for a consumer trait (`[CGP-E034]`).
Detection is triggered only by the `E0107` (a type-lowering-phase error, always present for this
mistake), because it forces HIR and trait-graph queries that would re-enter the `DiagCtxt` lock and
abort the compiler if run while the earlier-phase `E0425` (emitted mid-name-resolution) is being
handled, the
[re-entrant-emission hazard](rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held).
The sibling `E0425`/`E0186`/`E0207`/`E0308` are suppressed by matching their spans against the impl
body and the `__Context__` parameter's call-site (a sibling arriving before the `E0107` is purged
from the buffer at reshape time), the downstream `NotAProvider` check re-report by matching its
resolved leaf against the offending provider struct (a requirement of the impl that fails on its own
resolves to its own cause through the impl as written, per
[typed-resolution-walk](typed-resolution-walk.md), so that report is kept), and rustc's trailing
`rustc --explain` footer is rebuilt so it does not list the suppressed ones. That footer rebuild is
not particular to this reshape: rustc builds the footer in `print_error_count` from every code it
*registered*, which is a superset of what the emitter emits once it has suppressed a re-report, a
`?`-cascade, or this sibling burst, and once it has *merged* the failures sharing a cause into one
block carrying the first member's code. So `rebuild_explain_footers` runs over the whole flushed
list, keeping the footer's own codes filtered by what survived: an intersection rather than a fresh
set, since rustc lists only codes that *have* an extended explanation and second-guessing that would
offer `--explain` for a code with no such text. A footer whose codes all survive is rewritten
identically, so untouched output is unaffected. And because a footer line always names at least one
code, parsing none from any of them means rustc reworded rather than that there are none. So the
rebuild declines and leaves the footer exactly as written, a stale footer being a far smaller fault
than a silently deleted one. Both the recognition and the code reading live in the rustc-free
[`signals`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs)
module with the emitter's other rustc-phrasing dependencies, where they are unit-tested. The message
wording is decided by the rustc-free
[`plan_cgp_impl_misuse`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/cgp_impl_misuse.rs)
(and `cgp_impl_misuse_help` for the fix) over the owned `CgpImplMisuse` the detector fills in, so it
is unit-tested without a compiler. The blessed snapshots under
[`lowering/wrong-component-half/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/wrong-component-half)
pin the consumer-trait, generic-component, non-CGP-trait, inner-bound, and
provider-trait-in-`#[uses]` shapes, and the consumer-trait header beside a missing field (at a check
or a call), a field of the wrong type, or nothing else.

The mirror mistake names a provider trait in `#[uses(…)]` on a `#[cgp_fn]` or `#[cgp_impl]`, where
a dependency names the consumer trait. `#[uses]` writes `Self: AreaCalculator`, which lacks the
context argument the provider trait takes first, so rustc reports an `E0107` "missing generics for
trait `AreaCalculator`" and suggests the generated `<__Context__>`. The transform rewords it into a
`[CGP-E037]` header naming the consumer trait, with `#[uses(CanCalculateArea)]` in a `help`,
recovered by
[`detect::detect_provider_trait_in_uses`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/uses_misuse.rs).
The `E0107` arrives while the compiler lowers the impl's `where` clause, so the detector reads the
bound from the HIR alone: the caret must be the trait name of a `where` bound on the context
(`Self`, or `__Context__`) of an impl that declares the reserved `__Context__` parameter, the trait
must be a CGP provider trait written without type arguments, and a consumer trait must pair with
it. That consumer trait is the one whose blanket impl routes to the provider trait, searched with
the impl's own trait skipped, since a `#[cgp_fn]` trait's blanket impl may be the impl being
lowered, and querying it would cycle back into the query in flight. The wording is the rustc-free
`plan_provider_trait_in_uses` and `provider_trait_in_uses_help` over the owned
`ProviderTraitInUses`.

The reshape is deliberately specific to `#[cgp_impl]`, keyed on the `__Context__` marker it inserts.
The lower-level `#[cgp_provider]`/`#[cgp_new_provider]` forms (a hand-spelled inside-out impl with a
user-named context) are not covered, and cannot be safely: without that reserved marker,
`impl<Ctx> SomeConsumer<Ctx> for ConcreteType` cannot be told from a legitimate direct impl of a
generic consumer trait on a context, so recognizing it would risk a false positive on valid code.
`#[cgp_impl]` is the idiomatic provider form, so this is the case a programmer overwhelmingly hits.

## Reshaping a provider impl written without its macro

A provider trait has `IsProviderFor` as a supertrait, and `#[cgp_provider]` writes the provider's
impl of it beside the impl of the provider trait. A provider-trait impl written by hand has no
marker impl, so the compiler rejects it on the supertrait with an `E0277` at the impl's `Self` type,
and lists every unrelated implementor of `IsProviderFor` beside it. The emitter recognizes the shape
as the error arrives, gated to an `E0277` whose message names `IsProviderFor` and confirmed
structurally by
[`detect::detect_provider_impl_without_macro`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/macro_less_provider.rs):
the caret is the `Self` type of a local impl whose trait is a CGP provider trait the user named
(`provider_blanket_marker` finds its component marker), the `Self` is a struct, enum, or union, and
no `IsProviderFor` impl exists for that struct and marker. It words the `[CGP-E039]` header and its
`#[cgp_provider]` help from the rustc-free `plan_provider_impl_without_macro` and
`provider_impl_without_macro_help`, drops the implementor list, and remembers the provider, so a
later `E0277` on that provider's `IsProviderFor` bound (the failing check of a context that wires
it) is dropped as the same mistake. The fixtures
[`provider_impl_without_macro`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro.rs)
and
[`provider_impl_without_macro_wired`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro_wired.rs)
pin both.

## Reshaping an unresolved wiring name

This reshape covers a name in a wiring entry that is wrong (the
[unresolved wiring name](../../cgp/errors/wiring/unresolved-wiring-name.md) class): a consumer trait
as a key, a component not in scope, a key guessed from a trait's name, or a provider never declared.
Its difficulty is timing. Every shape but the first is an `E0425` "cannot find type", raised during
name resolution, before the compiler has built the HIR and before any query that reads the crate's
items is safe, and the name's own span carries no trace of the `delegate_components!` that wrote it,
so nothing at emission time says it is a wiring key.

The emitter therefore buffers those `E0425`s untouched, and the driver's `after_expansion` callback,
which the compiler calls right after `resolver_for_lowering` finishes, runs
[`reshape_name_resolution_errors`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/name_resolution.rs).
It reaches the buffer through the same thread-local registration the panic hook uses
(`with_registered_buffer` in `output.rs`), in the three steps of
[`buffer_pass`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/buffer_pass.rs),
which the `#[use_type]` help replacement shares. It collects the buffered `E0425`s under the
output's lock, plans them with the lock released, since a query run while planning can emit a
diagnostic that takes the same lock, and then rewrites them under the lock, after checking that the
candidates are where they were. The planning,
[`detect::plan_unresolved_names`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect/wiring_name),
reads each name's position back from the HIR: the `DelegateComponent` impl (by `DefId`) whose key or
`Delegate` type is exactly the name, or the impl over `__Context__` whose unresolved `Self` is, or
a type inside the `@`-path of such a key or value. A name inside any other larger type, such as a
type argument of a provider, is no entry's key or value and stays as rustc wrote it. Then:

- **A key** is a component not in scope (`[CGP-E041]`) when exactly one component marker of that
  name exists among the traits the crate can see, read from each provider trait's delegation
  blanket. Its import path is a `crate::` path for a local component, and otherwise the shortest
  public path found by walking the module trees of the direct dependencies and following
  re-exports, since `def_path_str` names a crate re-exported under another name by its crate name
  (`cgp::cgp_core::…`). A key that names no component is a guessed one (`[CGP-E042]`) when the name
  without its `Component` suffix names exactly one consumer trait.
- **A value** is an undeclared provider (`[CGP-E043]`), with a near miss looked for among the
  providers of the key's component (`similar_name`). The requirement it leaves unprovable, the
  entry's context implementing the component's consumer trait (`Person: CanGreet`), is recorded in
  the emitter's output beside the buffer, and the emitter drops a later `E0275` overflow on that
  requirement, with whatever parameters the component takes, as the entry's consequence
  (`is_unresolved_wiring_overflow`).
- **A `#[cgp_impl]` header's provider** is a provider never declared (`[CGP-E038]`), and a value
  naming the same provider is dropped as its consequence.
- **A type in an `@`-path** is found by its own span. `delegate_components!` gives a path's
  `PathCons` spine the span of the whole macro call but keeps each segment's span as the user wrote
  it, so the pass walks the key and the `Delegate` type for a path that resolves to nothing at the
  name's span, below a `PathCons` of the base-types crate (`path_segment_at`, in `slot.rs`). A
  segment that names one component marker is a component not in scope (`[CGP-E041]`). Any other is
  `[CGP-E044]`, which replaces only the header, because the compiler's near-miss note and its
  similarly named struct are correct for a type; the "missing a type parameter" suggestion is
  dropped, since no wiring entry has generics to take it, and the pass's own help follows only when
  nothing else is left that says how to fix the name, and only for a whole segment, since a lowercase
  spelling makes a segment a symbol but not a type nested in one. A later report of the same name
  is dropped. A redirect's value also leaves its entry's requirement unprovable, so the overflow
  list records both forms of it, the consumer trait for a call and `CanUseComponent` of the
  component for a check, and the emitter drops the `E0275` on either.

A value, a `#[cgp_impl]` provider, or a path type is called undeclared only when nothing the crate
could import declares a type of its name. A type of that name in any module of the crate, or a
public one of a direct dependency (`is_type_declared`, in `component.rs`), makes the name one the
program did not import, so its `E0425` is left as rustc wrote it, and rustc's import suggestion,
when it gives one, is the fix. A repeat of a name in a wiring entry at the same span is dropped; a
diagnostic outside the entries, repeats included, is left as rustc wrote it.

The consumer trait as a key is different in kind: its `E0782` "expected a type, found a trait" is
raised while the compiler lowers the impl's header, with a `TyCtxt` in scope, so the emitter
recognizes it as it arrives (`detect::detect_consumer_trait_as_key`) and words it as
`[CGP-E040]`, the component read off the consumer trait's provider trait. The wording of every shape is the rustc-free
`plan_unresolved_wiring_name` and `unresolved_wiring_name_help` over the owned
`UnresolvedWiringName`, and `is_missing_type_parameter_help_text` names the suggestion the path case
drops. The blessed snapshots under
[`wiring/unresolved-wiring-name/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/wiring/unresolved-wiring-name)
pin every shape.

## Dropping a suggestion that names a generated identifier

A CGP macro declares some names only in its expansion, and spells each as a reserved identifier,
wrapped in double underscores (`__Context__`, and the lifetimes `'__a__` and `'__a0__` that
`#[cgp_auto_dispatch]` gives an elided one). When a macro cannot name what the user wrote, the
compiler reports the gap and may suggest inserting one of those names into the user's source, where
it does not resolve. The suggestion is wrong whatever the error: for a `Cow<str>` argument of a
`#[cgp_auto_dispatch]` method, `E0106` suggests `Cow<'__a__, str>`, while the `E0726` beside it
suggests the `Cow<'_, str>` that works.

The drop runs in two places. The emitter applies it to each diagnostic of a crate that uses CGP as
it arrives, beside the splice drop below, and so reaches the type-checking errors: an `E0599` whose
bound suggestions include a provider trait with its generated context
(`Greeter</* __Context__ */>`), and an `E0107` whose help adds `__Context__` to a provider-trait
bound. The lifetime errors arrive during name resolution, before an emitted diagnostic can ask
whether the crate uses CGP, so like the wiring-name reshape the pass
[`drop_generated_name_suggestions`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/generated_names.rs)
also runs from the `after_expansion` callback over what name resolution buffered. It reaches the
buffer through the same registration, and only in a crate that links a CGP crate
(`resolve::query::links_cgp`), so a plain Rust error keeps every suggestion.

Either way the drop removes each substitution whose text holds a reserved name
([`reserved_names`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/naming.rs),
a word whose two leading and two trailing underscores surround a name that neither starts nor ends
with an underscore of its own, the rule `is_reserved_name` gives every pass that asks) that the
source file being edited does not contain, since a name the file spells is one the user wrote.
rustc offers the bounds that would let a call resolve as one suggestion with a substitution per
trait, so the drop removes the wrong alternatives and keeps the rest, and a suggestion left with
none goes too, which also keeps it out of the JSON output, where an emptied suggestion would still
show its message. The test reads the text of the suggestion rather than the macro's expansion,
because the suggestion's span sits in the user's own code, where nothing marks it as the macro's.
Three limits follow. The test reads only the file the suggestion edits, so a comment there that
spells the reserved name counts as the user writing it, and the suggestion stays, while a reserved
name the program declares in another file counts as generated, and its suggestion goes. And a
suggestion left with one bound keeps rustc's plural message over it ("the following traits define
an item"). The `retain_substitutions` helper in `edit/children.rs` serves this pass, beside
`retain_suggestions`, which the method-probe cleanup and the splice drop use.

The
[`auto_dispatch_hidden_lifetime`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/auto_dispatch_hidden_lifetime.rs)
fixture pins the name-resolution case: the `E0106` keeps its caret and label, and the `E0726` keeps
the right help. Three fixtures pin the type-checking case:
[`generic_fn_consumer_not_in_scope`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_consumer_not_in_scope.rs)
and
[`missing_use_provider_shared_method_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_shared_method_name.rs)
keep the consumer-trait bounds beside the dropped provider-trait ones, and
[`provider_trait_in_inner_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/provider_trait_in_inner_bound.rs)
loses its only help, in its JSON snapshot too. Two `pass-through/` fixtures pin what keeps such a
suggestion:
[`reserved_lifetime_written`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/reserved_lifetime_written.rs),
a CGP crate whose own code names `'__a__`, and
[`generated_lifetime_without_cgp`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/generated_lifetime_without_cgp.rs),
a crate without CGP whose own attribute macro generates the lifetime.

## Replacing the help on a misspelled `#[use_type]` import

A `#[use_type]` import that misspells its associated type leaves the compiler's help pointing at the
wrong place. `#[use_type(HasScalarType.Scalr)]` rewrites each bare `Scalr` to
`<Self as HasScalarType>::Scalr`, keeping the span of the alias the program wrote, so name
resolution reports `E0576`, "cannot find associated type `Scalr` in trait `HasScalarType`", at that
alias. The header and the "similarly named associated type" note are right, but the help respells
the alias, which leaves the import's `Scalr` in place and fails on an undeclared `Scalar` (the
[unresolved imported abstract type](../../cgp/errors/lowering/unresolved-imported-type.md) class).

The error arrives during name resolution, so the fix also runs from the `after_expansion` callback,
as
[`reshape_use_type_misspellings`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/use_type_misspelling.rs),
in a crate that links CGP, with the collect, detect, and rewrite steps of the wiring-name reshape.
The detection,
[`detect::detect_use_type_misspelling`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/detect/use_type_misspelling.rs),
accepts the `E0576` only when the caret sits in an item a CGP macro generated (the recognition
[`[CGP-E035]`](#reshaping-an-undeclared-dependency) uses) and the source writes the name bare there.
A qualified path the program wrote itself (`<Self as HasScalarType>::Scalr`) is respelled where it
stands, so the compiler's help is right for it and stays. The detection then needs the trait the
import names, and the associated type of it the import meant: the trait's only associated type,
which is the one name an import of the trait can give and the one the compiler suggests whatever its
spelling, or else one the name is a slip of (`similar_name`). The compiler's message names the trait
by its bare name, so when two traits share it, the trait meant is the one whose associated type the
compiler's "associated type … defined here" note points at. The pass drops each suggestion that
edits the alias and adds the rustc-free `use_type_misspelling_help`, which names the rename in the
import, and in each use of the alias unless the import gives an `as` alias of its own. The header
stays the compiler's, without a code. The fixtures `use_type_unknown_assoc`,
`use_type_unknown_assoc_alias`, `use_type_unknown_assoc_no_near_miss`,
`use_type_unknown_assoc_two_types`, `use_type_unknown_assoc_shared_trait_name`, and
`qualified_path_unknown_assoc`, under
[`lowering/unresolved-imported-type/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/lowering/unresolved-imported-type),
pin the six cases.

## Dropping a suggestion spliced after an attribute macro

An attribute macro's generated code carries the attribute's own span, so when rustc rejects that
code it can suggest an insertion at the end of that span, which is the point right after the
attribute's `]`. For `#[cgp_impl(new SquareArea)] impl AreaCalculator<Square>` of a component whose
name takes a parameter, `E0107` suggests `#[cgp_impl(new SquareArea)]<Shape>`, and for a
`#[cgp_auto_getter]` method whose generated body returns the wrong type, `E0308` suggests
`#[cgp_auto_getter].as_deref()`. No edit of the user's source can apply either, since the fault is
in code the macro wrote.

The drop runs from the emitter's transform for every diagnostic, in a crate that uses CGP
(`crate_uses_cgp`, which cannot answer during name resolution), so a plain Rust error keeps every
suggestion. These errors arrive at lowering and type-checking, so each is cleaned as it arrives,
and unlike the generated-name drop this one needs no second pass after name resolution. [`drop_attribute_splices`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/attribute_splice.rs)
recognizes the suggestion by the span it edits, never by its text: a substitution that inserts at a
span an attribute macro's expansion carries (`ExpnKind::Macro(MacroKind::Attr, _)`), exactly where
that expansion's call site ends. It then removes that suggestion through `retain_suggestions` and
leaves the others. The
[`parameterized_name_default_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/parameterized_name_default_component.rs)
and
[`auto_getter_mut_option`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/macro-defects/auto_getter_mut_option.rs)
fixtures pin it, and neither matches plain `cargo check` for that reason. A crate without CGP keeps the suggestion, which
[`attribute_splice_without_cgp`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/attribute_splice_without_cgp.rs)
pins with an attribute macro of its own. An attribute macro that re-spans the user's tokens gives
them its expansion's context at their own locations, so a suggestion there edits the user's code
and stays
([`respanned_token_suggestion`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/respanned_token_suggestion.rs)).
The same insertion at the end of a function-like macro's call is a valid edit, `name!().as_deref()`,
so it stays too
([`function_macro_suggestion`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/function_macro_suggestion.rs)).

## Tests

- [`crates/cargo-cgp-driver/tests/driver/unresolved_overflow.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/tests/driver/unresolved_overflow.rs):
  `is_unresolved_wiring_overflow` over hand-built overflows: a recorded requirement dropped bare,
  with a consumer trait's arguments, or as a check, and a longer trait name, another context, another
  code, or nothing recorded kept.
- [`crates/cargo-cgp-error-processing/tests/error_processing/rewrite/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/rewrite):
  the compiler-free rewrite over a hand-built name map, run on any toolchain: both note forms and
  both header forms; generic components (a single parameter reattached to the header, a
  multi-parameter tuple unwrapped, and the notes eliding parameters); the module-prefix and
  generic-subject/context cases; the non-CGP and unknown-marker pass-throughs; and a check that the
  `ComponentNameMap` lazy initializer is *not* forced when no message matches.
- [`tests/ui/checks/check-trait-failure/generic/generic_area.cgp.stderr`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_area.cgp.stderr):
  the end-to-end regression guard that the transform still names the traits when the component is
  generic: the header reattaches the single `<f64>` parameter, the notes name the traits and elide
  it.
- [`tests/ui/checks/check-trait-failure/generic/generic_area_multi.cgp.stderr`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/generic/generic_area_multi.cgp.stderr):
  the same, for a *three-parameter* component: the header unwraps the `(u32, u64, bool)` tuple to
  `CanCalculateArea<u32, u64, bool>`.
- [`tests/ui/checks/check-trait-failure/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/checks/check-trait-failure):
  the blessed `.cgp.stderr` snapshots across the check subgroups (`fields/`, `providers/`,
  `generic/`, `field-types/`, `resolution/`) pin the trait-renaming transform end to end.

## Source

- [`crates/cargo-cgp-driver/src/emitter/stage/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter/stage): the stages, one module each.
- [`crates/cargo-cgp-driver/src/emitter/pipeline/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/emitter/pipeline): the `Verdict`, the `Reshape`, and `apply_reshape`, which writes one into the diagnostic.
- [`crates/cargo-cgp-driver/src/detect/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/detect): the class detectors the stages call, which fill the rustc-free models.
- [`crates/cargo-cgp-error-processing/src/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis): the models and their wording.
- [`crates/cargo-cgp-driver/src/component_map.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/component_map.rs):
  builds the component-marker → trait-names map by inverting the `IsProviderFor` supertrait
  (anchored by `DefId` identity to the `cgp_component` crate) and the consumer-blanket-impl links,
  and exposes `build_name_map_from_tls`, the `TyCtxt`-reading `fn` the `ComponentNameMap` is built
  with.
- [`crates/cargo-cgp-error-processing/src/rewrite/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/rewrite):
  the rustc-free home of the string rewrite (`message.rs`'s `rewrite_message` and the note/header
  forms) and the lazy `ComponentNameMap` (`names.rs`).
