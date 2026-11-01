# Typed resolution: the call-site anchor

Four anchors recover a failure's obligation from the failing call's own HIR, for a failure whose
spans touch nothing the [span-matching anchors](typed-resolution-anchors.md) can read. The call-site
anchor reads a call through a consumer or blanket trait on a context. Three siblings read
[a call to an extensible-data operation](#calls-to-extensible-data-operations),
[a provider's own method](#calls-to-a-providers-own-method), and
[a bound of a called generic function](#bounds-of-a-called-generic-function). They are tried seventh
to tenth, so a failure a span-matching anchor can recover keeps that more exact recovery.

## The failure shape: wiring that matches unconditionally

The call-site anchor exists for a wiring that answers a whole family of component parameters with
one generic entry, so the method is found and only the provider's deeper dependencies fail. The
natural home is the [handler family](../../cgp/concepts/handlers.md), but any consumer wired this
way gives the same shape. A pipeline runs through two core providers
([handler combinators](../../cgp/reference/providers/handler_combinators.md)), and the tree names
them: `PipeHandlers<Product![A, B]>` folds to `ComposeHandlers<A, B>`, which feeds `A`'s output to
`B` as its input.

The
[`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs)
fixture wires every `Prog<Steps>` to a pipeline of its steps, and the first step reads a `name` field
`App` lacks:

```rust
pub struct Prog<Steps>(pub PhantomData<Steps>);

cgp_namespace! {
    new MyNamespace: DefaultNamespace {
        @cgp.core.error.ErrorTypeProviderComponent:
            UseType<String>,

        // One generic entry serves every program, so the wiring matches unconditionally.
        @cgp.extra.handler.HandlerComponent.<Steps> Prog<Steps>:
            PipeHandlers<Steps>,
    }
}

async fn run_app(app: &App) -> Result<(), String> {
    app.handle(PhantomData::<Prog<Product![HandleName, HandleShout]>>, Vec::new())
        .await?;
    Ok(())
}
```

Because the entry matches any program, rustc's method probe succeeds, and only `HandleName`'s
`Self: HasName` bound fails. So the failure is an `E0277` on the call, and that disarms the
span-matching anchors. No check entry matches the caret, the call sits in no impl, the `E0277` puts
no span on `App`'s definition, and `CanHandle` is foreign and generic. The anchor turns it into one
block led by the cause:

```text
error[E0277]: [CGP-E001] missing field `name` on `App`
  --> src/main.rs:97:16
   |
97 |     app.handle(PhantomData::<Prog<Product![HandleName, HandleShout]>>, Vec::new())
   |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: root cause: [CGP-E110] missing field `name` on `App`
           this is required through the dependency chain:
             [CGP-E101] consumer trait impl `CanHandle<Prog<Product![HandleName, HandleShout]>, _>` for context `App`
             └─ [CGP-E103] redirect lookup to `@cgp.extra.handler.HandlerComponent` in `App`
               └─ [CGP-E102] provider trait impl `Handler<Prog<Product![HandleName, HandleShout]>, _>` with context `App` for provider `PipeHandlers<Product![HandleName, HandleShout]>`
                 └─ [CGP-E102] provider trait impl `Handler<Prog<Product![HandleName, HandleShout]>, _>` with context `App` for provider `ComposeHandlers<HandleName, HandleShout>`
                   └─ [CGP-E102] provider trait impl `Handler<Prog<Product![HandleName, HandleShout]>, _>` with context `App` for provider `HandleName`
                     └─ [CGP-E104] trait impl `HasName` for `App`
                       └─ [CGP-E110] missing field `name` on `App`
```

The re-report at `.await` resolves to the same cause and de-duplicates, and the emitter's gate drops
the `?` cascade, which the resolver never takes. A resolution from these anchors plans as a
[use-site failure](typed-resolution-output.md#emitting-the-transformed-diagnostic) whatever its
rustc code, so its class is the trait the call needs, never the plumbing rustc's headline stopped
on.

## What the call still knows

The anchor reads only HIR and the queries the failing code already cached (`type_of`, `fn_sig`,
`generics_of`). `tcx.typeck` would answer every question, but it would check a body not yet checked
and emit from inside the emitter, which
[aborts the compiler](rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held).

**The receiver names the context,** since a consumer is implemented on it. The anchor follows the
receiver syntactically: a binding to its annotation, initializer, or parameter type, a struct
literal or unit-struct value, a const or static, and a call to its callee's declared return type,
peeling references. These receivers decline here:

- **One only typeck could type,** a method's result or a field access. The
  [use-site anchor](typed-resolution-anchors.md#the-use-site-anchors) may still reach it, as its
  boundary in the [overview](typed-root-cause-resolution.md#boundaries) states.
- **A context type still holding a type parameter,** such as `App<T>` inside `fn run<T>`, whose walk
  the empty parameter environment cannot judge. One instantiation, `App<u32>`, reads as usual.
- **A type that is no context.** A foreign type counts when it carries its own wiring
  ([`foreign_context_error_route`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_error_route.rs)).

**The candidate traits come from the method's name.** Every CGP consumer declaring a `self` method
of that name is tried first, so a consumer keeps `[CGP-E001]`, then every
[blanket trait](typed-resolution-anchors.md#recognizing-a-blanket-trait), headed `[CGP-E003]`
([`cgp_fn_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_use_site.rs)).
CGP's extensible-data traits are left to the data-call anchor.

**A receiver typed by a type parameter fails for the bound its item lacks.** In
`fn run<Context>(context: &Context) { context.greet(); }`, the method exists only under
`Context: CanGreet`. So when exactly one consumer in scope declares the method, it takes no
parameters besides `Self`, and the item does not already bound the parameter by it, the anchor
reports `[CGP-E129]` with no walk, and a `help` naming the bound
([`generic_fn_missing_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_fn_missing_bound.rs)).
The parameter's type is built from the item's generics, since asking `type_of` for it reports a
compiler bug into the diagnostic context the emitter holds.

## Parameters by signature unification, not by convention

The anchor assumes **no calling convention**, and a change must not add one. Reading "the first
argument's `PhantomData` tag" would work for handlers, but CGP does not prescribe how a method
relates its arguments to its trait's parameters, and such a rule would fail every other consumer.
The method's declared signature always records where each parameter appears, so the anchor runs a
small copy of inference: fresh variables for the method's item, `Self` pinned to the context, and
each argument the call writes unified with its declared input. The same mechanism serves both
idioms:

- **A tag:** `PhantomData::<Prog<…>>` against `_tag: PhantomData<Code>` binds `Code`.
- **A value:** `app.format_pair((1_u32, 2_u64))` against `value: T` binds `T = (u32, u64)`
  ([`generic_consumer_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_use_site.rs)).

An argument's type counts as **written** when its syntax determines it: a unit value or struct
literal with its path arguments, a reference to a written expression, a literal of definite type, a
non-generic const, or a call to a callee with a declared return type. The hand lowering behind this
declines anything beyond its small set rather than guess
([`call_site_written_shapes`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/call_site_written_shapes.rs)).

A **tuple literal** is the one shape read partially: its arity is kept and each unwritten element
becomes an unknown. A provider often destructures its input on a tuple, and its impl matches only a
tuple, so collapsing `(Vec::new(), Vec::new())` to one unknown would leave the impl unmatched and
hide a field its branch reads
([`call_site_tuple_input`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/call_site_tuple_input.rs)).

## Unknown parameters become rigid placeholders

What the call does not write, the anchor does not invent. Each unconstrained parameter becomes a
rigid placeholder, because it unifies with nothing concrete and can cross between the walk's fresh
inference contexts, which an inference variable cannot. The walk treats it as unknown in both
directions:

- **It descends through a bound that mentions one,** since a parameter-dependent bound can lead to
  parameter-independent needs. `HandleName`'s `Self: HasName` does not mention the input at all.
- **It never reports a leaf that carries one.** `_: Send` would be a requirement nobody can act on. A
  failure whose every leaf depends on the unknown declines
  ([`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs)).

A placeholder prints as `_`, including one nested in a recovered tuple (`((_, _), _)`).

## Why a wrong guess cannot fabricate an error

The anchor recovers from guesses, since a method name can match several traits, so every seed is
checked against the solver. A candidate that holds is skipped, and one whose walk reaches no
reportable, placeholder-free leaf declines. A wrong guess therefore produces nothing, or a real
failing obligation of the context the programmer named.

The anchor also considers only the calls a diagnostic is about. A failing call's primary span sits
on the method name, on one whole argument, or on the whole call, so a call counts when a primary
span overlaps it without lying strictly inside its receiver or an argument. So an error beside the
call or nested in an argument keeps its own diagnostic rather than being re-anchored and
de-duplicated away
([`unrelated_error_before_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_before_call.rs),
[`unrelated_error_in_call_argument`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/unrelated_error_in_call_argument.rs)).

## Calls to extensible-data operations

The data-call anchor, tried eighth, reads a failing call to a builder, extractor, or cast operation.
Such a call differs in what it is called on: usually a **partial value** another operation produced,
which no receiver reading can type. So the anchor types the value through the chain that built it.
Each step's output is read off the operation's declared signature in a fresh inference context, then
normalized, and a binding is followed to what bound it, including a tuple-struct or tuple-variant
pattern (`Err(remainder)`). A step whose output does not reduce to a concrete type ends the chain
with a decline.

```rust
let _ = Person::builder()
    .build_field(PhantomData::<Symbol!("first_name")>, "Alice".to_owned())
    .build_field(PhantomData::<Symbol!("first_name")>, "Bob".to_owned());
```

The second call seeds `__PartialPerson<IsPresent, IsNothing>: BuildField<Symbol!("first_name")>`,
and the [leaf](typed-resolution-leaves.md#the-leaf-shapes) reads the builder's markers:

```text
error[E0271]: [CGP-E050] field `first_name` of `Person` is already set
  --> src/main.rs:24:22
   |
24 |         .build_field(PhantomData::<Symbol!("first_name")>, "Bob".to_owned());
   |                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: root cause: [CGP-E118] field `first_name` of `Person` is already set
           this is required through the dependency chain:
             [CGP-E104] trait impl `BuildField<Symbol!("first_name")>` for the builder of `Person` with `first_name` set
             └─ [CGP-E118] field `first_name` of `Person` is already set
```

These rules keep it from claiming a call that is not a data operation:

- **Only an operation counts:** the traits of `cgp-field` and `cgp-field-extra`, except the
  field-access traits, which read one field. A method call considers only operations taking `self`,
  so `config.builder()` keeps rustc's "associated function" error
  ([`data_function_called_as_method`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/data_function_called_as_method.rs)).
- **Only a trait in scope at the call counts,** as in the compiler's own lookup, so another library's
  `Config::builder()` keeps rustc's diagnostic
  ([`data_operation_name_not_in_scope`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/data_operation_name_not_in_scope.rs)).
- **A computed tag declines.** `Symbol!` expands to const generic arguments, read through
  `lit_to_const`, which reports nothing. A braced literal is read through its braces, and a computed
  `{ 0 + 1 }` leaves the tag unknown. Its stand-in is a unit constant, since an error constant would
  register a delayed bug
  ([`build_field_twice_computed_tag`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/build_field_twice_computed_tag.rs)).

The anchor also takes two shapes no other anchor sees, because an operation can fail before its
bounds are checked. A builder with a field unset has no `finalize_build`, so the probe reports "no
method named"
([`finalize_build_premature`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/finalize_build_premature.rs)),
and an extractor with one variant left rejects the tag as an `E0308`
([`extract_field_twice`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/extract_field_twice.rs)).
Both are reported while the body is type-checked, so the solver may run. An `E0308` is taken only
when every cause is a field or variant state, since it is otherwise a plain type error. The "no
method named" shape is told apart from the method-bounds `E0599`, which the same probe builds, by
its translatable message's arguments. The result is headed `[CGP-E050]`, and the value is named
plainly unless it carries wiring.

## Calls to a provider's own method

The provider-call anchor, tried ninth, reads a call through a provider's own path, which asserts the
provider trait as a `#[check_providers]` entry does. So it seeds the provider obligation and gives
the provider class `[CGP-E002]`. Candidates are the CGP provider traits in scope that declare a
function of the name. Every argument is an input, and a binding is typed through it, so a matcher's
`shape` argument takes its type from the enclosing signature
([`matcher_missing_arm`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/data/extensible-data/matcher_missing_arm.rs)).
The walk is rooted at the provider trait's context argument, so a call that leaves it unknown
declines.

```rust
let _ = PipeHandlers::<Product![Increment, Increment]>::compute(&(), PhantomData::<()>, 1u8);
```

```text
error[E0599]: [CGP-E002] `Increment` implements `Computer` only with `Input = u8`, not `Input = Result<u8, &str>`
  --> src/main.rs:23:61
   |
23 |     let _ = PipeHandlers::<Product![Increment, Increment]>::compute(&(), PhantomData::<()>, 1u8);
   |                                                             ^^^^^^^
   |
   = note: root cause: [CGP-E127] `Increment` implements `Computer` only with `Input = u8`, not `Input = Result<u8, &str>`
           this is required through the dependency chain:
             [CGP-E102] provider trait impl `Computer<(), u8>` with context `()` for provider `PipeHandlers<Product![Increment, Increment]>`
             └─ [CGP-E102] provider trait impl `Computer<(), u8>` with context `()` for provider `ComposeHandlers<Increment, Increment>`
               └─ [CGP-E102] provider trait impl `Computer<(), Result<u8, &str>>` with context `()` for provider `Increment`
                 └─ [CGP-E127] `Increment` implements `Computer` only with `Input = u8`, not `Input = Result<u8, &str>`
```

## Bounds of a called generic function

The bound-call anchor, tried tenth and gated to `E0277`, reads a call to a free generic function by
path, whose own `where` bound the context fails. Nothing in such a call invokes the trait, so no
receiver carries the context and no span names the trait:

```rust
fn fail<Context: CanRaiseError<String>>() -> Context::Error {
    Context::raise_error(String::new())
}

let _ = fail::<App>(); // `App` wires no error raiser
```

The function's parameters start as fresh variables. The turbofish fills its explicit parameters, and
each argument unifies with its declared input, a binding keeping its references (`greet_all(app)`
for `app: &App` fills `&Context`). Each failing bound on a CGP consumer or blanket trait whose
`Self` is a context is then walked, and a bound on any other trait stays as rustc wrote it. This
case reads ``[CGP-E001] missing wiring for `ErrorRaiserComponent` on `App` ``.

It comes before the by-blanket-trait anchor because rustc's notes name a trait deeper in the chain,
and the tree should start at the bound the call requires
([`consumer_bound_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/consumer_bound_call.rs)).
It reads no method's own bound, which is a [boundary](typed-root-cause-resolution.md#boundaries).

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md): the pipeline overview, the anchor
  order, and the boundaries.
- [Anchoring the starting obligation](typed-resolution-anchors.md): the span-matching anchors.
- [Walking to the root cause](typed-resolution-walk.md): how a seed, placeholders included, is
  descended.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): why `tcx.typeck` is off limits.

## Tests

- [The parent document's catalog](typed-root-cause-resolution.md#tests): the fixture groups that pin
  these anchors.
- [`hidden/unsatisfied-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/hidden/unsatisfied-dependency):
  `cascade_*` and `call_site_*` for the seed, `generic_fn_*` for an unbounded receiver and its declines,
  `provider_called_directly*` for the provider call, and `raise_error_unwired_call`, `consumer_bound_call`,
  `cgp_fn_where_bound`, and `generic_consumer_bound_reference_binding` for the bound call.
- [`data/extensible-data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/data/extensible-data):
  the data-call anchor over chains, pattern bindings, and tags.

## Source

- [`resolve/call_site/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/call_site):
  one file per step: `find_call.rs`, `receiver.rs`, `unbounded.rs`, and `seed.rs` for the call-site
  anchor, `data_call.rs` and `chain.rs` for the data-call anchor, and `provider_call.rs` and
  `bound_call.rs`.
- [`resolve/query/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/query):
  the readers these anchors share with the class detectors: `written_ty.rs`, `lower.rs`,
  `unify_call_inputs.rs`, `binding.rs`, `local_body_exprs.rs`, and `traits_with_method.rs`.
