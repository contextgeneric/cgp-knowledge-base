# Typed resolution: the call-site anchor

This document covers the seventh to tenth anchors of the driver's
[typed root-cause resolution](typed-root-cause-resolution.md): recovering a use-site failure's
obligation from the failing call expression's own HIR, when its spans touch nothing the
[span-matching anchors](typed-resolution-anchors.md) can read. The seventh, the call-site anchor,
reads a call through a consumer or blanket trait on a context; the eighth, the data-call anchor,
reads a call to one of CGP's extensible-data operations, whose value is usually another operation's
result ([below](#calls-to-extensible-data-operations)); the ninth, the provider-call anchor, reads
a provider trait's method called through the provider's own path
([below](#calls-to-a-providers-own-method)); and the tenth, the bound-call anchor, reads a bound of
a generic function at the call that instantiates it ([below](#bounds-of-a-called-generic-function)).
(An eleventh anchor, `resolve_use_site_blanket_trait`, is tried after them for a blanket trait
required as a `where` *bound* elsewhere; it is described in
[anchoring the starting obligation](typed-resolution-anchors.md) and reuses this anchor's
`contexts_at_spans`.)

The call-site anchor exists for the use-site failure that leaves *no usable span at all*, and its
design follows from working out what can still be known once the spans are gone. This document
builds the failure shape from a small self-contained program, shows why every span-matching anchor
declines on it, and then develops each recovery step with the reasoning behind it.

## The failure shape: wiring that matches unconditionally

The shape arises whenever a context's wiring answers a whole *family* of component parameters with
one generic entry, so that resolving the method always finds a provider and only that provider's
deeper dependencies fail. The natural home of this pattern is the
[handler family](../../cgp/concepts/handlers.md), an advanced corner of CGP whose
`CanHandle<Code, Input>` consumer turns an `Input` value into an output, with a phantom `Code`
*type* selecting which computation runs, so one context can host many computations and wire each
`Code` differently. Nothing below is specific to handlers, though: any consumer whose wiring matches
unconditionally and fails only in its dependencies produces the same shape.

The two combinators that sequence such a pipeline are core CGP providers (from `cgp-handler`, not
from any example), and the recovered tree renders them by name, so a reader needs their shape. Both
are documented in full under
[handler combinators](../../cgp/reference/providers/handler_combinators.md):

- **`ComposeHandlers<ProviderA, ProviderB>`** runs two handlers back to back, feeding the *output*
  of the first as the *input* of the second. So its two dependencies are asymmetric:
  `ProviderA: Handler<Ctx, Code, Input>` on the pipeline's own input, and
  `ProviderB: Handler<Ctx, Code, ProviderA::Output>` on whatever the first stage *produces*. That
  asymmetry is what this section turns on.
- **`PipeHandlers<Product![A, B, C]>`** generalizes that to a type-level list, folding it right to
  left into `ComposeHandlers<A, ComposeHandlers<B, C>>`, so a three-stage pipeline threads its input
  through `A`, then `B`, then `C`, each stage's output type feeding the next stage's input type. A
  program written with a pipe operator (a step, then another step, then another) desugars to exactly
  this.

Both are zero-sized dispatch plumbing the programmer never writes by hand. They appear only because
a pipeline program's wiring expands to them, which is precisely why a diagnostic that stops on one
names no cause a reader can act on.

The following program (condensed from the
[`cascade_after_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cascade_after_use_site.rs)
fixture) wires every pipeline program `Prog<Steps>`, whatever its `Steps`, to a `PipeHandlers`
composition of those steps. The first step reads the context's `name` field, which `App` does not
have; that missing field is the root cause the anchor must recover:

```rust
/// A program is a *type*: a pipeline of steps, selected by the phantom `Code` tag.
pub struct Prog<Steps>(pub PhantomData<Steps>);

#[cgp_auto_getter]
pub trait HasName {
    fn name(&self) -> &str;
}

/// First pipeline step: read the context's `name` field — the dependency `App` cannot meet.
#[async_trait]
#[cgp_impl(new HandleName)]
#[use_type(HasErrorType.Error)]
impl<Code, Input> Handler<Code, Input>
where
    Self: HasName,
    Input: Send,
{
    type Output = String;

    async fn handle(&self, _tag: PhantomData<Code>, _input: Input) -> Result<String, Error> {
        Ok(self.name().to_owned())
    }
}

// A second step, `HandleShout`, uppercases the `String` the first step produces. It is
// defined the same way, its dependencies all hold, and it plays no part in the failure.

cgp_namespace! {
    new MyNamespace: DefaultNamespace {
        @cgp.core.error.ErrorTypeProviderComponent:
            UseType<String>,

        // One generic entry serves *every* program: any `Prog<Steps>` runs as the pipeline of
        // its steps. This is what makes the wiring match unconditionally.
        @cgp.extra.handler.HandlerComponent.<Steps> Prog<Steps>:
            PipeHandlers<Steps>,
    }
}

#[derive(HasField)]
pub struct App {
    // No `name` field.
}

delegate_components! {
    App {
        namespace MyNamespace;
    }
}

async fn run_app(app: &App) -> Result<(), String> {
    app.handle(PhantomData::<Prog<Product![HandleName, HandleShout]>>, Vec::new())
        .await?;
    Ok(())
}
```

Because the `<Steps> Prog<Steps>` entry matches *any* program, rustc's method probe succeeds
(`handle` exists for `App`), and only later does the provider's transitive `Self: HasName` bound
fail. So the failure arrives as an `E0277` on the call, not the `E0599` "method not found" a
directly-missing method produces, and that difference disarms every span-matching anchor. There is
no `check_components!` entry, so no check impl's span matches the caret. The call sits in a plain
`fn`, not inside an `impl` block, so the impl-site and wrapper-chain anchors find no enclosing impl.
An `E0599` would have carried a "method not found for this struct" span on `App`'s definition (the
handle the by-component use-site anchor grabs), but this `E0277` points only at the call. And the
consumer trait `CanHandle` is foreign and generic, so the by-consumer anchor, restricted to local
consumers whose only generic is `Self`, is out too. Without this anchor, the diagnostic would fall
to the text rewrite, which reports the failure *three times* (once per rustc re-report at the call
and its `.await`) under `[CGP-E002]` headers naming `PipeHandlers<…>` and `ComposeHandlers<…>`, the
dispatch plumbing, as the failing "provider", with the missing `name` field appearing nowhere.

## What the call still knows

The spans are useless, but the call expression itself contains almost everything the walk's seed
obligation `App: CanHandle<Code, Input>` needs, provided it is read from HIR alone. `tcx.typeck`,
the query that would answer every question at once, replays its cached diagnostics when forced and
so aborts the compiler from inside the emitter (the re-entrancy hazard in
[rustc diagnostic internals](rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held));
HIR, by contrast, is fully built long before analysis, and the only queries this recovery touches
(`type_of`, `fn_sig`, `generics_of` on items the failing code already named) are cached by the very
type-checking that produced the diagnostic.

**The receiver names the context.** A consumer trait is implemented on the context, so in a
consumer-method call the receiver *is* the context by construction. No guessing is involved, only
reading the receiver's type without typeck. The anchor follows the receiver expression
syntactically: a path to a binding leads to a `let` (typed by its annotation, or by a struct-literal
initializer) or to a fn parameter (typed by the enclosing signature, like the fixture's
`app: &App`); a struct literal, unit-struct value, const, or static names its type directly; a call
to a non-generic fn, or to a tuple-struct or enum-variant constructor (`Shape::Circle(…)`), takes
the callee's declared return type; references are peeled along the way. A receiver whose type
genuinely needs inference (a method call's result, a field access) declines, as does a generic
context, whose type arguments are exactly what the missing typeck results would have supplied, and a
type that is no context. A context from another crate qualifies when it carries `DelegateComponent`
wiring of its own (`is_context_adt`), so a call on a context a library exports recovers its root
cause as a call on a local one does
([`foreign_context_error_route`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/foreign_context_error_route.rs)).
The trait candidates come from the method *name*, and are of two kinds: every CGP **consumer
trait** (recognized structurally, in any crate) declaring a `self` method of that name, tried first
so a directly-wired consumer keeps its precise recovery; then every `#[cgp_fn]` / `#[blanket_trait]`
**blanket trait** declaring such a method, as recognized by `is_blanket_trait` (see
[anchoring the starting obligation](typed-resolution-anchors.md)). A blanket trait is a blanket-impl
trait that is not a CGP component (no provider trait, no `DelegateComponent`), consumed like a
consumer (`app.describe()`) and seeding the same walkable obligation `Ctx: Describe` whose `Self` is
the context. Because it is not a CGP component, its result takes the `[CGP-E003]` code rather than
`[CGP-E001]`, the same class the impl-site anchor gives such a trait reached through a wrapper, by
clearing the `Resolved::consumers_are_cgp` flag the walk sets. This is what recovers a direct call
to a `#[cgp_fn]` trait the context cannot satisfy: an `E0599` whose real cause (a field one composed
blanket trait reads) rustc buries in a mid-stack note under its method-probe candidate list
([`cgp_fn_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/cgp_fn_use_site.rs)).
A call to one of CGP's extensible-data operations (a cast, a builder, an extractor) is not a
candidate here: the data-call anchor tried next takes it, since its value is usually another data
operation's result ([below](#calls-to-extensible-data-operations)).

## Parameters by signature unification, not by convention

Recovering the component's parameters (the `Code` and `Input` in `CanHandle<Code, Input>`) is where
a design choice had to be made, and the choice is to assume **no calling convention at all**.

The tempting shortcut is a convention: in the handler family, the first argument is a
`PhantomData<Code>` tag, so "read the first argument's turbofish" would recover the `Code` here. But
CGP does not prescribe how a consumer method relates its arguments to its trait parameters: the
`PhantomData` tag is one family's idiom, not a rule. A consumer someone else defines may carry its
parameter in an ordinary value argument (`fn format_pair(&self, value: T)`), in a differently-shaped
tag type, spread across several arguments, or nowhere recoverable. Hard-coding any one shape would
quietly privilege one library's style and fail on every other.

What *is* always true is that the method's own declared signature records exactly where each trait
parameter appears among its inputs, which is the very information type inference consumes at a real
call. So the anchor runs a miniature of the same process the compiler would: it mints a fresh
inference variable for every parameter of the method's item, pins `Self` to the receiver's context,
and unifies each argument whose type the call *writes* syntactically against the corresponding
declared input. Whatever those unifications pin down, through the signature's own use of the trait's
generics, is recovered. The two fixture shapes show the same mechanism serving both idioms:

- In the program above, the argument `PhantomData::<Prog<Product![HandleName, HandleShout]>>` is
  unified with the declared input `_tag: PhantomData<Code>`, which binds
  `Code = Prog<Product![HandleName, HandleShout]>`.
- In
  [`generic_consumer_use_site`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/generic_consumer_use_site.rs),
  a consumer `CanFormatPair<T>` with the plain value method `fn format_pair(&self, value: T)` is
  called as `app.format_pair((1_u32, 2_u64))`; the written tuple type `(u32, u64)` is unified with
  the declared `value: T`, which binds `T = (u32, u64)`. No tag argument exists, and none is needed.

An argument's type counts as *written* when it is determined by the expression's own syntax: a
unit-struct or unit-variant value with its written path arguments, a struct literal, a reference to
a written expression, a literal whose type is definite (`"…"`, `true`, `'c'`, suffixed numerics), or
a call to a non-generic fn or a tuple-struct or enum-variant constructor (its declared return type).
Each written type is lowered by a deliberately small syntactic HIR-type lowering (paths to ADTs and
aliases through the cached `type_of`, defaulted parameters filled in, lifetimes erased, and a
literal const argument read as the compiler reads it) that declines anything beyond it rather than
guess.

A **tuple literal** is the one shape read *partially*: its *structure* is recovered even when some
elements' types are not written, each unwritten element seeded as a fresh inference variable (folded
into a placeholder with the rest of the seed). This matters because a provider commonly destructures
its input on a tuple shape (a branching interpreter taking `(condition_input, branch_input)`, a
comparison taking `(input_a, input_b)`), and its impl matches only against a tuple, never a flat
unknown. Collapsing a tuple whose every leaf is unwritten (`(Vec::new(), Vec::new())`) to one opaque
placeholder, as the all-or-nothing reading of the other shapes would, leaves such a provider's impl
unmatched and hides a cause that sits inside a *written* branch of the input or, as with the field a
condition reads, a branch that does not depend on the input at all. The recovered arity and its
written elements are real call-side information; only the leaves the call does not type stay
unknown, and those are never reported. The
[`call_site_tuple_input`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/hidden/unsatisfied-dependency/call_site_tuple_input.rs)
fixture pins the shape.

## Unknown parameters become rigid placeholders

What the call does not write, the anchor does not invent. The fixture's second argument is
`Vec::new()`: its element type was never resolved (the trait resolution failing is precisely why),
and no syntactic reading can supply it. Each parameter left unconstrained after unification is
folded into a rigid **placeholder** type: rigid so it unifies with nothing concrete and can cross
between the walk's fresh inference contexts, unlike an inference variable.

The walk then treats a placeholder as an *unknown*, in both directions. It **descends through**
bounds that mention one, because a parameter-dependent bound can still lead to parameter-independent
dependencies deeper down. In the example, `HandleName`'s `Self: HasName` does not mention the input
at all, so the missing `name` field is reachable whatever the input turns out to be. But it **never
reports** a leaf that still carries one: a bound like `Input: Send` with an unknown `Input` is
unknowable, and reporting `_: Send` would fabricate a requirement the programmer cannot act on. Only
a root cause that holds *whatever the unknown parameter is* survives; a failure whose every leaf
depends on the unknown declines to the fallback
([`generic_consumer_unwritten_arg`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/use-site/generic_consumer_unwritten_arg.rs)
pins that boundary with the same `CanFormatPair` call with the tuple passed through a plain
variable, whose type the call no longer writes). In the rendered output a placeholder prints as the
`_` the programmer would write, including one nested inside a recovered tuple (`((_, _), _)`). The
tree renderer walks a tuple's elements rather than printing rustc's raw `!N` placeholder form.

Put together, the example's failure becomes one block, led by the cause, in place of three
plumbing-worded blocks with no cause:

```text
error[E0277]: [CGP-E001] missing field `name` on `App`
  --> src/main.rs:93:16
   |
93 |     app.handle(PhantomData::<Prog<Product![HandleName, HandleShout]>>, Vec::new())
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

The re-report rustc raises where the result is awaited resolves to the same cause and de-duplicates
away, and the `?`-operator cascade the call trails is dropped by the emitter's `?`-cascade gate (see
[The driver](driver.md)), since the resolver never takes a `?` error. A resolution from this anchor
is also planned as a use-site failure whatever its rustc code, so its class is the consumer trait
the call needs, never the dispatch plumbing rustc's own headline stopped on (see
[Emitting the transformed diagnostic](typed-resolution-output.md#emitting-the-transformed-diagnostic)).

## Why a wrong guess cannot fabricate an error

The anchor recovers from *guesses* (a method name can match several consumer traits, a receiver
binding can be misread), so every seed is gated on reality before anything is reported. The anchor
is tried after every span-matching recovery except the by-blanket-trait one; a candidate obligation
that actually *holds* is skipped; and one that fails but whose walk reaches no reportable,
placeholder-free leaf declines to the fallback. A mis-guessed consumer or context therefore produces
either nothing or a genuine failing obligation of the context the programmer named, never an
invented diagnostic.

The anchor also considers only the calls the diagnostic is about. A failing call's primary span sits
on the method name, on one whole argument (the `PhantomData` tag in the example above), or on the
whole call, as does the re-report rustc raises where the result is awaited. So `method_calls_at`
collects a call only when a primary span overlaps it without lying strictly inside its receiver or
one of its arguments. Two kinds of unrelated error keep their own diagnostic instead of being
re-anchored onto the call and de-duplicated away: an error beside the call (an `Rc` passed to a
`T: Send` function on the line before `person.greet()`), whose span the call does not overlap, and
an error nested in an argument (`person.greet(count(Rc::new(1)))`), whose span lies strictly inside
it. The impl-site anchor reads a forwarding call through the same rule.

## Calls to extensible-data operations

The data-call anchor, `resolve_data_call`, is tried eighth, after the call-site anchor, for a failing
call to one of CGP's extensible-data operations: a builder's `build_field`, `take_field`, or
`finalize_build`, an extractor's `extract_field` or `finalize_extract`, a cast's `upcast` or
`downcast`, and the other traits of the `cgp-field` and `cgp-field-extra` crates. Such a call
differs from a consumer call in what it is called on. Its value is a struct or an enum, or more often
a *partial value* another operation produced: the builder `Person::builder()` returns, the builder a
previous `build_field` returns, or the remainder an `Err(remainder)` pattern takes out of a failed
extraction. None of these is a context, and the receiver reading above types none of the produced
ones.

So the anchor types the value through the chain of operations that built it. Each step is a call to
a data operation, by method (`builder.build_field(PhantomData::<Symbol!("first_name")>, …)`) or by
type-relative path (`Person::builder()`); its output is read off the operation's declared signature
in a fresh inference context, with `Self` pinned to the step's input and each written argument
unified with its declared input, then normalized once the trait obligation is solved. A binding is
followed to what bound it: a `let`, or a field of a tuple-struct or tuple-variant pattern in a
`let`, an `if let`, or a `match` arm (`Err(remainder)` takes the error field of the `Result` its
scrutinee has). The chain ends at a value the call-site anchor already types (a constructor, a
literal, an annotated binding), and a step whose output does not reduce to a concrete type ends it
with a decline. A program that builds one field twice shows the whole path:

```rust
#[derive(CgpData)]
pub struct Person {
    pub first_name: String,
    pub last_name: String,
}

let _ = Person::builder()
    .build_field(PhantomData::<Symbol!("first_name")>, "Alice".to_owned())
    .build_field(PhantomData::<Symbol!("first_name")>, "Bob".to_owned());
```

The anchor types `Person::builder()` as `__PartialPerson<IsNothing, IsNothing>` and the first
`build_field` as `__PartialPerson<IsPresent, IsNothing>`, seeds the failing second call as
`__PartialPerson<IsPresent, IsNothing>: BuildField<Symbol!("first_name")>`, and the
[walk](typed-resolution-walk.md) reads the builder's markers:

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

Reading the tag needs one more piece of the small lowering. `Symbol!("first_name")` expands to
`Symbol<10, Chars<'f', …>>`, whose length and characters are const generic arguments, so a literal
const argument is lowered through the compiler's `lit_to_const` query, which builds the constant
from the literal without evaluating anything (and so reports nothing). Any other const argument,
such as a computed `{ 0 + 0 }`, leaves the tag unknown and the call declines.

Three rules keep the anchor from claiming a call that is not a data operation:

- **Only data operations qualify:** the traits of the two crates, except the field-access traits
  (`HasField`, `HasFieldMut`, `FieldGetter`, `MutFieldGetter`), which read one field of a value
  rather than operate on a whole record or enum.
- **Only a trait in scope at the call qualifies.** The compiler's method lookup considers only the
  traits in scope, and records them per call, so a method of another library that shares a name
  (`Config::builder()` on a type that never derived a builder, in a module without CGP's prelude)
  keeps rustc's diagnostic
  ([`data_operation_name_not_in_scope`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/pass-through/data_operation_name_not_in_scope.rs)).
- **The seed is gated** as the call-site anchor's is: a seed that holds is skipped, and a walk that
  reaches no reportable cause declines.

The anchor also takes two diagnostic shapes no other anchor sees, because a data operation can fail
before its bounds are checked. A builder finalized with a field unset has no `finalize_build` at all,
since only the all-set builder implements `FinalizeBuild`, so the method probe reports an `E0599` "no
method named `finalize_build`"; and an extractor with one variant left settles `extract_field` on
the one impl that remains and rejects the tag argument as an `E0308`. Both are reported while the
calling body is type-checked, as the method-bounds `E0599` is, so the solver may run on them (see
[rustc diagnostic internals](rustc-diagnostic-internals.md#re-entering-the-diagnostic-context-lock-was-already-held)).
The emitter sends both to this anchor alone, and takes an `E0308` only when every cause the walk
finds is a field or variant state (`Leaf::is_data_state`), since a mismatched argument is otherwise
a plain type error. The "no method named" shape is recognized by the arguments its translatable
message names (`item_kind`, `item_ident`), and told apart from the method-bounds `E0599`, which the
probe builds from the same diagnostic, by that one's plain-string message.

A failure this anchor resolves is headed `[CGP-E050]` (`Resolved::data_operation`), the value named
plainly unless it carries wiring. When the seed is itself the cause, the operation having no impl at
all (`FinalizeBuild` on a builder with a field unset), the chain still starts with the operation's
own step, so it names the finalize the cause is about. The causes and their wording belong to
[the transformed diagnostic](typed-resolution-output.md).

## Calls to a provider's own method

The provider-call anchor, `resolve_provider_call`, is tried ninth, for a call that names a provider
and calls its provider trait's method directly, with no consumer trait between them:

```rust
#[cgp_computer]
pub fn increment(value: u8) -> Result<u8, &'static str> {
    value.checked_add(1).ok_or("overflow")
}

let _ = PipeHandlers::<Product![Increment, Increment]>::compute(&(), PhantomData::<()>, 1u8);
```

Such a call asserts the provider trait itself, much as a `#[check_providers]` entry does, so the
anchor seeds and walks the provider obligation. The provider is the type the path names, read by the
small lowering. The candidate traits are the CGP provider traits in scope at the call that declare
a function of the called name; a provider method takes its context as an argument rather than as
`self`, so every function counts. The seed then unifies the call's arguments with the function's
declared inputs, as a data operation's type-relative call does: every argument is an input, and
one that is a binding is typed through it, so `MatchWithHandlers::<…>::compute(&(), PhantomData::<()>, shape)`
takes `shape`'s type from the enclosing signature. Here the seed is
`PipeHandlers<Product![Increment, Increment]>: Computer<(), (), u8>`.

The walk is rooted at the provider trait's context, its first type argument after `Self`, so a
call whose context argument stays unknown declines. The result records the provider, which makes
the block the provider class `[CGP-E002]`, and the context is named plainly unless it carries
wiring. In the example the walk reaches the second stage, which `PipeHandlers` gives the first
stage's `Result` output, and the provider-for-other-arguments leaf states it:

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

The same gates as the other call anchors keep it from claiming a call that is not this shape: a
call whose trait is not in scope is left alone, a seed that holds is skipped, and a walk that
reaches no reportable cause declines.

## Bounds of a called generic function

The bound-call anchor, `resolve_bound_call`, is tried tenth, gated to `E0277`, for a call to a
generic function whose own `where` bound the context fails. Nothing in such a call invokes the
trait, so no receiver carries the context and no span names the trait:

```rust
fn fail<Context: CanRaiseError<String>>() -> Context::Error {
    Context::raise_error(String::new())
}

let _ = fail::<App>(); // `App` wires no error raiser
```

The call itself asserts the bound, so the anchor reads it off the function. It finds a call by a
path to a free generic function that a primary span is about, by the call-site anchor's rule; a
caret on the turbofish lies in the callee, not in an argument, so it counts. The function's
parameters start as fresh variables. The turbofish's written types fill its explicit type
parameters in order, and each argument's type is unified with the declared input it fills. That
type is written by the argument's syntax, or declared for a binding with its references kept
(`greet_all(app)` for `app: &App` fills `&Context`), or read as the call-site anchor reads a
receiver. The function's own clauses are then instantiated, and each bound on a CGP consumer trait
or blanket trait whose `Self` is a context, fully known, and failing is seeded and walked. The
result is `[CGP-E001]` for a consumer trait and `[CGP-E003]` for a blanket trait, and here it reads:

```text
error[E0277]: [CGP-E001] missing wiring for `ErrorRaiserComponent` on `App`
```

The anchor is tried before the by-blanket-trait anchor, whose own trait comes from rustc's notes:
for a consumer trait required as a bound (`fn greet_twice<Context: CanGreet>(…)`), those notes name
a trait deeper in the chain, a getter the provider uses, and the tree would start there instead of
at the bound the call requires. A bound on any other trait (`T: Clone`) is left as rustc wrote it.

## Tests

The anchor's fixtures live under
[`tests/ui/hidden/unsatisfied-dependency/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/hidden/unsatisfied-dependency):
`cascade_after_use_site` (the worked example above), `generic_consumer_use_site` (the value-argument
case), `call_site_tuple_input` (the partial tuple recovery), `call_site_written_shapes` (every
written shape the anchor reads: each definite literal kind, a struct literal, a constant, a
non-generic call, and a `PhantomData` over a tuple, a reference, a slice, and generic paths),
`cgp_fn_use_site` (the `#[cgp_fn]` trait call recovered as a `[CGP-E003]` block),
`auto_dispatch_missing_variant_impl` (a receiver built by an enum-variant constructor, resolved to
the dispatch payload's missing impl), `foreign_context_error_route` (a call on a context from an
upstream crate), and the `cascade_later_stage*` shapes whose pipeline stages the walk then descends.
The decline boundary is pinned by `generic_consumer_unwritten_arg`, and the span gate by
`unrelated_error_before_call` (an unrelated `Send` error before the failing call keeps its own
diagnostic) and by `unrelated_error_in_call_argument` and `unrelated_error_in_awaited_argument` (the
same error inside the call's argument, awaited or not, keeps its own diagnostic too), and the
pass-through fixture `local_blanket_trait` (a plain error in a function that also calls a failing
blanket-trait method is left alone).

The data-call anchor's fixtures are the extensible-data family under
[`tests/ui/data/extensible-data/`](https://github.com/contextgeneric/cargo-cgp/tree/main/tests/ui/data/extensible-data):
`build_field_twice` (the worked example above), `build_from_overlapping_sources` (a builder typed
after one merge), `finalize_build_premature` (a "no method named" `E0599`), `extract_field_twice`
(an `E0308` on a remainder an `if let` binds), `finalize_extract_early` (a remainder a `match` arm
binds), `downcast_on_remainder` (a remainder used where its enum belongs), `from_variant_wrong_case`
and `build_with_default_without_default` (type-relative calls), and `upcast_missing_variant` (a
cast on a constructed value). The pass-through fixture `data_operation_name_not_in_scope` pins the
in-scope rule.

The provider-call anchor's fixtures are `provider_called_directly` (the worked example above) and
`provider_called_directly_without_error_type` (a `#[cgp_computer]` provider's fallible member,
called on a context without an error type, resolved to the missing wiring), under
`hidden/unsatisfied-dependency/`, and `matcher_missing_arm` under `data/extensible-data/` (a
matcher's `compute`, its input a fn parameter, resolved to the variant it never extracts).

The bound-call anchor's fixtures, under `hidden/unsatisfied-dependency/`, are
`raise_error_unwired_call` (the worked example above, the context from the turbofish),
`consumer_bound_call` (a consumer trait as a bound, the context from a reference argument, its
tree headed by the consumer), and `cgp_fn_where_bound` (a `#[cgp_fn]` blanket trait as a bound,
the context from a parameter binding of reference type, under `[CGP-E003]`). The consolidated
catalog lives in the parent document's [Tests](typed-root-cause-resolution.md#tests) section.

## Source

- [`crates/cargo-cgp-driver/src/resolve/call_site/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/call_site):
  one file per stage: `find_call.rs` (locating the call and the candidate consumers), `receiver.rs`
  (the context off the receiver), `seed.rs` (the signature unification, for each `CallForm`: a
  consumer method call, a data method call, and a type-relative path call), `written_ty.rs` (the types the
  call's arguments write), and `lower.rs` (the small syntactic type lowering, literal const
  arguments included); for the data-call anchor, `data_call.rs` (`resolve_data_call`, locating a
  method or type-relative call and its data operations in scope) and `chain.rs` (`data_expr_ty`,
  typing a value through the data operations and pattern bindings that produced it); for the
  provider-call anchor, `provider_call.rs` (`resolve_provider_call`, locating a type-relative call
  and the provider traits in scope that declare its function); for the bound-call anchor,
  `bound_call.rs` (`resolve_bound_call`, instantiating a called generic function's own bounds);
  and `receiver.rs`'s `declared_binding_ty`, a binding's declared type with its references.

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md): the pipeline overview.
- [Typed resolution: anchoring the starting obligation](typed-resolution-anchors.md): the six
  anchors tried before these four, and the by-blanket-trait anchor tried after them.
- [Typed resolution: walking to the root cause](typed-resolution-walk.md): how the seeded obligation
  (placeholders and all) is descended.
- [rustc diagnostic internals](rustc-diagnostic-internals.md): why `tcx.typeck` can never be forced
  from the emitter, the constraint this anchor's HIR-only reading exists to respect.
