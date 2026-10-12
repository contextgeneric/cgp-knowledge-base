# CGP Error Codes

`cargo-cgp` assigns a stable error code to every main message it rewrites into a CGP-specific one
and to every entry of the dependency tree it renders, and this document is the catalog of those
codes. A code names one recognized class of CGP mistake or one dependency-chain step (what it means,
what triggers it, and how to fix it) so that a reader who sees a code in the tool's output can look
it up here, and so that the tool's own tests and future JSON output can refer to a class by a short,
stable identifier rather than by its prose.

The hundreds digit says *what* a code classifies. The **`CGP-E0xx`** codes name **main messages**,
the diagnostic's headline, and come in family blocks of ten, so a reader can tell the family of a
mistake from its number. The **`CGP-E1xx`** codes name **dependency-tree entries**, one code per
rendering template: `CGP-E101` to `CGP-E109` for the steps of the chain, and `CGP-E110` onward for
the root causes it ends at. Keeping the two apart lets a reader tell at a glance whether a code tags
the error's headline or one entry of the chain beneath it.

## The scheme, and why it looks unlike a Rust code

A CGP error code is the letters `CGP-E` followed by three digits (`CGP-E001`, `CGP-E002`, and so on)
shown in square brackets at the start of the rewritten main message:

```text
error[E0277]: [CGP-E001] missing field `height` on `Rectangle`
```

The `CGP-E` prefix is deliberately unlike Rust's own `E0277` shape, so a reader never mistakes one
namespace for the other: `E0277` is a Rust code you explain with `rustc --explain`, while
`[CGP-E001]` is a CGP code you look up here. The two coexist on the same line by design: **the
diagnostic's own Rust code is always kept**. A rewritten message restates the same error more
readably; it does not reclassify the error away from rustc, so `error[E0277]:` (or `error[E0599]:`
at a consumer-call use site, or `error[E0271]:` at a field-type mismatch) stays in the header, the
trailing `rustc --explain` line stays meaningful, and the CGP code rides inside the message text
where it reads as a tag on the cause it states. This also keeps the code greppable: a reader
confirming a class need only search the output for `CGP-E001`.

## When a code is assigned

A code is assigned only when two things are both true: `cargo-cgp` **rewrote the main message**, and
that main message was **identified as a class of CGP error**. The rewrite preserves the semantics of
the original message (an unsatisfied `CanUseComponent<AreaCalculatorComponent>` bound *is* the
consumer trait `CanCalculateArea` failing to be implemented) and the code is the handle for the
class it was recognized as.

Everything else is uncoded by design. A diagnostic whose main message is not a CGP class keeps
rustc's own message and plain `error[E0277]:` header even when its *sub-messages* were rewritten;
the root-cause notes, renamed obligation chains, and resugared type names are supporting detail of
one error, not classifications of their own. The [uncoded rewrites](#uncoded-rewrites) section below
records each such rewrite, so the absence of a code on them is documented rather than merely
implied.

## Codes

The headline codes come in six family blocks of ten; a family that outgrows its block takes the next
free one. Four blocks hold codes today, and two are reserved for classes the tool does not reshape
yet:

| Block | Family | Codes |
| --- | --- | --- |
| `CGP-E001` to `CGP-E009` | a trait the context cannot use, and the two type mismatches | `E001` to `E005` |
| `CGP-E010` to `CGP-E019` | conflicting wiring | `E010` to `E014` |
| `CGP-E020` to `CGP-E029` | wiring that never resolves, and the orphan rule | `E020`, `E022` |
| `CGP-E030` to `CGP-E039` | mistakes in what a macro was given | `E030` to `E034` |
| `CGP-E040` to `CGP-E049` | wiring keys and values that do not resolve | none yet |
| `CGP-E050` to `CGP-E059` | extensible data | none yet |

The families differ in how the tool recovers them. The **trait-failure** codes `CGP-E001` to
`CGP-E005` come from the typed resolver; each carries the root cause in the accompanying `note`,
opening `root cause: …` over its dependency chain (see
[Typed root-cause resolution](implementation/typed-root-cause-resolution.md)), except the two
mismatch codes `CGP-E004` and `CGP-E005`, whose main messages already state their cause in full and
so carry the chain alone. (`CGP-E003` is the trait-failure code for a hand-written wrapper trait or
a blanket trait rather than a CGP consumer, and `CGP-E005` the abstract-type counterpart of
`CGP-E004`.) The **conflicting-wiring** codes `CGP-E010` to `CGP-E014` are different in kind: they
come from the duplicate-key conflict classifier, carry no root-cause note, and instead keep rustc's
two carets, which already point at the two colliding entries. They are five separate codes because
each rewrites the `E0119` into a distinct message form with its own fix. The **never-resolving and
orphan** codes `CGP-E020` and `CGP-E022` each rewrite a whole-program coherence error into a
CGP-framed one carrying its fix in a `help`: `CGP-E020` a wiring cycle's `E0275` (a cycle has no
terminal leaf to descend to), and `CGP-E022` an orphan-rule namespace registration's
`E0210`/`E0117` (recovered from the offending impl off the compiler, like the `E0119` family). The
**macro-mistake** codes `CGP-E030` to `CGP-E034` are each recovered off the compiler from the
generated impl the failing token sits in and reworded with the fix in a `help`. Two concern a
used-but-undeclared dependency: `CGP-E030` a trait used in a `#[cgp_fn]`/`#[cgp_impl]` body but not
declared via `#[uses(…)]`, and `CGP-E031` an inner provider a higher-order provider calls but never
imported via `#[use_provider]`. Three concern a trait named where a provider trait belongs:
`CGP-E032` a `#[cgp_impl]` header naming the component's consumer trait, `CGP-E033` a `#[cgp_impl]`
on a trait that is not a CGP component at all, and `CGP-E034` an inner-provider bound (typically
`#[use_provider]`) naming the consumer trait. Each entry below gives the rewritten message, the
mistake behind it, the fix, and the [CGP error catalog](../cgp/errors/README.md) class it
recognizes.

### `CGP-E001`: consumer trait not implemented

- **Message:** `` [CGP-E001] <cause> ``, the root cause in the sentence its tree code words
  (`` [CGP-E001] missing field `height` on `Rectangle` ``). Several causes of one kind on one owner
  are stated together (`` missing fields `first_name` and `last_name` on `Person` ``); mixed causes
  take the class sentence with their count,
  `` [CGP-E001] the consumer trait `<Consumer>` is not implemented for context `<Context>`: 2 root causes ``
  (pluralized when a use-site failure spans several components). The class sentence is also the
  internal headline a declined re-report is matched on.
- **Means:** the context cannot use a component it is expected to use: the wiring is missing, or a
  transitive dependency of the wired provider is unmet, so the blanket impl that would give the
  context its consumer trait does not apply.
- **Triggered by:** an unsatisfied `Context: CanUseComponent<Marker, Params>` bound, a
  `check_components!` / `delegate_and_check_components!` entry failing, or a consumer-method call
  (`E0599`) on a context that cannot use a component it wires. The Rust code stays whatever rustc
  assigned (`E0277` at a check, `E0599` at a call site).
- **Fix:** follow the `root cause:` note(s): add the missing field or derive, wire the missing
  component, or satisfy the ordinary bound the chain bottoms out on.
- **Upstream class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md).

### `CGP-E002`: provider trait not implemented

- **Message:** `` [CGP-E002] <cause> ``, by the rules of `CGP-E001`; the class sentence, used for
  mixed causes, is
  `` the provider trait `<Provider trait>` with context `<Context>` is not implemented for provider `<Provider>` ``.
- **Means:** a provider a `#[check_providers(...)]` entry lists fails to implement its provider
  trait for the context: its impl-side `where`-clause dependencies do not hold.
- **Triggered by:** a failing `#[check_providers(...)]` entry, recognized by the generated check
  impl whose supertrait is `IsProviderFor` and whose `Self` is the listed provider. The tree starts
  at that provider, whatever the context wires. Any other failure the resolver traces is classed by
  the trait its anchor recovered, even when rustc's own headline stops on a provider's
  `IsProviderFor` bound (a dispatch combinator, a `RedirectLookup`, or a provider deep in the
  chain): such a block is `CGP-E001` or `CGP-E003`. A failure the resolver declines has no anchor,
  so the text rewrite restates an `IsProviderFor` headline in the provider form under this code,
  and keeps rustc's notes in place of a root-cause tree
  ([`generic_check_without_params`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/generic_check_without_params.rs)).
- **Fix:** follow the `root cause:` note(s) to the dependency the provider is missing.
- **Upstream class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md) (its
  provider-side face).

### `CGP-E003`: wrapper trait not implemented

- **Message:** `` [CGP-E003] <cause> ``, by the rules of `CGP-E001`; the class sentence, used for
  mixed causes, is `` the trait `<Wrapper>` is not implemented for context `<Context>` ``, naming a
  foreign subject plainly (`` for `Router<Arc<App>>` ``).
- **Means:** a trait that is *not* a CGP consumer trait (so its class sentence reads "the trait",
  not "the consumer trait") cannot be implemented for the context, because a CGP component it
  depends on fails. Two shapes reach this code: a plain **wrapper trait** the programmer wrote (the
  transfer example's `CanHandleApiSend`, which adds a `Send` bound over a CGP consumer supertrait),
  and a `#[cgp_fn]` / `#[blanket_trait]` **blanket trait**
  (`impl<Context> Describe for Context where Self: …`), which is a first-class core-CGP trait
  consumed like a consumer trait but is not a CGP *component* (it has no provider trait or
  `DelegateComponent`). Either way it is the [`CGP-E001`](#cgp-e001-consumer-trait-not-implemented)
  case for a trait that is not itself a CGP component.
- **Triggered by:** a failure surfaced *inside* a `impl Wrapper for Context` block (its header, a
  method signature, or a forwarding call), often as a raw `E0271`/`E0277`/`E0599` that names no CGP
  construct, which the resolver anchors on the enclosing impl and traces through the wrapper's CGP
  consumer supertrait to the root cause; **or** a `#[cgp_fn]` / `#[blanket_trait]` blanket trait the
  context cannot satisfy, reached either by a direct method call (`app.describe()`, an `E0599` the
  [call-site anchor](implementation/typed-resolution-call-site.md) recovers from the call
  expression) or through a `where` bound (`fn f<C: Describe>(…)`, an `E0277` the by-blanket-trait
  use-site anchor recovers). Whether the failing trait is a CGP consumer or one of these
  non-component traits is decided by its **fingerprint**: a CGP consumer carries a blanket impl
  routing to a provider trait, while a wrapper has only its concrete impl and a `#[cgp_fn]` trait
  has a blanket impl over the bare context with no provider.
- **Fix:** follow the `root cause:` note to the CGP dependency the trait needs. The dependency tree
  leads with the trait itself, then the traits it composes, down to the cause.
- **Upstream class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md) (reached
  through a hand-written wrapper or a `#[cgp_fn]` blanket trait).

### `CGP-E004`: field has the wrong type

- **Message:**
  `` [CGP-E004] field `<field>` on `<Context>` has type `<actual>`, but `<expected>` is required ``,
  with `` `<expected>` (`<normalized>`) `` in place of `` `<expected>` `` when the required type
  projects through the context's own wiring (below).
- **Means:** a context field the wiring reads is present and derives `HasField`, but its type is not
  the type a provider needs. The `HasField<Symbol!("<field>")>` trait bound holds; only the
  associated-type projection `<Context as HasField<Symbol!("<field>")>>::Value == <expected>` fails.
  The expected type is read from the failing projection, and the actual type is queried from the
  struct itself (by `DefId`, so a same-named struct in another module is never read).
- **The required type is shown in both forms when they differ.** A provider reading a field whose
  type is expressed through an [abstract type](../cgp/concepts/abstract-types.md) it imports
  (`#[implicit] database: &Pool<Db>` under `#[use_type(HasDbType.Db)]`) requires
  `Pool<<Context as HasDbType>::Db>`, a projection through the context's own wiring rather than a
  constant. The message keeps that un-normalized form, because it names *where* the requirement
  comes from and points the reader at the wiring entry, and appends what it reduces to in
  parentheses, because that is what the reader compares against the field:
  `` field `database` on `App` has type `Pool<Sqlite>`, but `Pool<<App as HasDbType>::Db>` (`Pool<Postgres>`) is required ``.
  Neither form alone is enough: the projection does not say what it resolves to, and the reduction
  does not say where it came from, so both are carried. A required type that is already concrete
  normalizes to itself and gets no parenthetical.
- **Triggered by:** a
  `` type mismatch resolving `<Context as HasField<Symbol!("<field>")>>::Value == <expected>` ``
  (`E0271`) that the typed resolver traced through CGP wiring to a `HasField` projection, a
  `check_components!` entry whose provider reads the field with the wrong type. The Rust code stays
  `E0271`.
- **Fix:** change the field's type on the struct to the expected type (or change the provider to
  accept the actual type). The accompanying `note` shows the dependency chain the field is read
  through.
- **Upstream class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md) (its
  projection-mismatch face).

### `CGP-E005`: abstract type has the wrong type

- **Message:**
  `` [CGP-E005] abstract type `<assoc>` of `<Trait>` on `<Owner>` is `<actual>`, but `<expected>` is required ``,
  reading `associated type` in place of `abstract type` when the trait is not a CGP abstract-type
  component.
- **Means:** the owner supplies one concrete type for an associated type while a provider the wiring
  reaches requires another. The archetype is a CGP
  [abstract type](../cgp/concepts/abstract-types.md): a context binds `HasErrorType::Error` by
  wiring `ErrorTypeProviderComponent` to `UseType<String>`, while a provider pins the same type with
  `#[use_type(HasErrorType.{Error = AppError})]`. As with
  [`CGP-E004`](#cgp-e004-field-has-the-wrong-type), the trait bound itself holds: the context *does*
  implement `HasErrorType`, and only the associated-type projection
  `<Ctx as HasErrorType>::Error == AppError` fails. The expected type is read from the failing
  projection, and the actual type by normalizing the projection, so a `UseType<T>` wiring and a
  hand-written `impl HasErrorType for Ctx` are read the same way.
- **Triggered by:** a `` type mismatch resolving `<Ctx as Trait>::Assoc == T` `` (`E0271`) that the
  typed resolver traced through CGP wiring to a projection other than `HasField`'s. The Rust code
  stays `E0271`.
- **The required type is shown in both forms when they differ,** on the same rule as
  [`CGP-E004`](#cgp-e004-field-has-the-wrong-type). A provider can pin an abstract type to a type
  that *projects through another one*
  (`#[use_type(HasDbType.Db, HasTransactionType.{Transaction = Tx<Db>})]` requires
  `Tx<<App as HasDbType>::Db>`) so the message keeps that form, which names the wiring the
  requirement flows from, and appends what it reduces to:
  `` to be `Tx<<App as HasDbType>::Db>` (`Tx<Postgres>`) ``. A pin to a concrete type normalizes to
  itself and gets no parenthetical.
- **Fix:** reconcile the two sides. For a `#[cgp_type]` component a `help` names both ways:
  `` wire `<Marker>` to `UseType<<expected>>` in the wiring for `<Owner>`, or change the provider to work with `<actual>` ``,
  with the component marker recovered from the trait, so the reader is pointed at the wiring entry
  rather than left to find it. **The `help` uses the *reduced* type where the header uses both**,
  because it prescribes an edit the reader types rather than describing the requirement:
  `` UseType<Tx<Postgres>> `` is a wiring entry, while `` UseType<Tx<<App as HasDbType>::Db>> ``
  would restate the requirement and leave them to reduce it. An ordinary trait's associated type has
  no such wiring entry, so it carries no `help`.
- **Upstream class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md) (its
  abstract-type projection-mismatch face).

### `CGP-E010`–`CGP-E014`: the duplicate-key wiring-conflict family

These five codes all rewrite the same underlying failure: an `E0119` conflicting-implementation
error on a wiring entry's impls, produced when a `delegate_components!` block wires one key (or
overlapping keys) more than once, or when two namespace entries claim one key (whose conflict lands
on the namespace's own lookup trait rather than `DelegateComponent`, and where an entry may come
from a `cgp_namespace!` body, a provider's `#[default_impl(… in …)]`, or the inheritance blanket a
`new Child: Parent` header emits). A generated pair's redundant `IsProviderFor` half is always
suppressed, and the Rust code stays `E0119`. What differs, and why each has its own code, is the
shape of the collision, and so the message and the fix. In every case an `@`-path key renders as
its entry wrote it, in bare `@a.b` notation (no `Path!(…)` wrapper), with a generic segment
named by its parameter (`@ComputerComponent.Code.u64`) and a type segment with its arguments
(`@DescriberComponent.Wrap<u64>`), and the upstream reference is
[conflicting wiring](../cgp/errors/wiring/conflicting-wiring.md) with its two namespace faces
[overlapping namespace forwarding](../cgp/errors/wiring/namespace-forwarding-conflict.md) and
[namespace override conflict](../cgp/errors/wiring/namespace-override-conflict.md).

- **`CGP-E010`: duplicate wiring.** `` [CGP-E010] duplicate wiring for <key> on `<Context>` ``: the
  same key mapped twice. The key is a component marker, an `@`-path, or an ordinary type (a per-type
  default's `String`), each worded as what it is; the subject is the context, or the namespace
  lookup trait when the collision is inside a namespace
  (`` on `DefaultImpls1<ShowImplComponent>` ``). **Fix:** remove one of the two entries the carets
  point at.
- **`CGP-E011`: overlapping wiring.**
  `` [CGP-E011] `<Context>` cannot wire <key> that is already set through <source> ``: two distinct
  but overlapping keys, where one cannot claim what the other already covers (a generic entry over a
  specific one, an `@`-path over a namespace forwarding, or a path that covers another, as a prefix
  or through a generic segment). A child namespace redefining a key it inherits takes
  this code too, with the namespace as the subject and the parent as the source. **Fix:** remove or
  narrow the overlapping entry. (A key the namespace resolves to a *redirect* is `CGP-E013`
  instead.)
- **`CGP-E012`: multiple namespaces.**
  `` [CGP-E012] only one namespace can be used for each target type in `delegate_components!`, but `<Context>` uses both `<A>` and `<B>` ``:
  two blanket forwardings that each cover every key, from joining two namespaces (or a namespace
  plus a bare-key `for` loop, which desugars the same way). **Fix:** join one namespace and inherit
  the others into it, or move a bare `for` key into a path.
- **`CGP-E013`: redirect collision.**
  `` [CGP-E013] <component> on `<Context>` is redirected to `<path>` ``: a direct wiring that
  collides with a redirect of the same key: an `open` header, an explicit `=>` redirect, a
  `namespace` join that maps the key to a redirected path, or, with a namespace as the subject, a
  namespace binding a key its *inherited parent* redirects, the shape a bare marker key produces for
  a component carrying a `#[prefix(...)]`. The last two are recovered by normalizing the forwarded
  namespace's `Delegate` for that key. The fix rides in a `help`:
  `` wire the provider `<Provider>` with the key `<path>` ``. A redirect looks a component up with
  its type parameters appended to the path, so for a generic component the `help` names one key
  per parameter value instead:
  `` the redirect appends the parameter `<Param>` to `<path>`, so wire each provider with a `<path>.<<Param>>` key in place of `<Provider>` ``.
  The `help` is omitted when the direct entry names no provider a reader wrote. **Fix:** wire the
  entry's provider under the redirected path rather than the bare key.
- **`CGP-E014`: duplicate redirect.**
  `` [CGP-E014] duplicate redirect for <component> on `<Context>` … `` (naming one redirect target,
  or both when they differ): the same key redirected more than once: two `open`s or `=>` mappings on
  a context, an `open` of a component the joined namespace already redirects through its
  `#[prefix]`, or the same `@`-path registered twice inside one `cgp_namespace!` block (where the
  subject is the namespace trait rather than a context). **Fix:** keep a single redirect.

### `CGP-E020`: wiring never resolves

- **Message:**
  `` [CGP-E020] the wiring for the consumer trait `<Consumer>` on context `<Context>` never resolves — the lookup recurses without terminating ``,
  with a `help` naming the usual cause and the two fixes.
- **Means:** resolving the component's wiring recurses without bottoming out. This almost always
  means the wiring routes the component back to the context itself: a component delegated to
  `UseContext` whose only implementation of the consumer trait *is* that delegation.
- **Triggered by:** an `E0275` overflow whose requirement is a `Context: CanUseComponent<Marker, …>`
  bound. The Rust code stays `E0275`; the note pointing at the generated `__Check…` trait is
  dropped, since the kept caret already covers the check entry. An overflow at a check entry is
  rewritten only when walking the entry's consumer obligation meets a cycle or the depth cap. A
  lookup can also overflow through a type the compiler could not resolve (an earlier `E0425` or
  `E0412`), with no cycle in the wiring; that overflow keeps rustc's wording, and the earlier error
  is the one to fix.
- **Fix:** wire the component to a real provider, or implement the consumer trait directly on the
  context, so the lookup terminates.
- **Upstream class:** [wiring cycle](../cgp/errors/wiring/wiring-cycle.md).

### `CGP-E022`: orphan-rule namespace registration

- **Message:**
  `` [CGP-E022] cannot register the foreign <key> into the foreign namespace `<Namespace>` ``, where
  `<key>` is `` component `<Marker>` `` or `` path `@…` ``, with a `help` naming the ownership-based
  fix.
- **Means:** the crate is registering wiring into a namespace it does not own, keyed on a component
  (or `@`-path) it does not own either. A registration lowers to `impl Namespace<_> for Key`, and
  Rust's orphan rule rejects a foreign-trait impl with no local type covering it, so with *both* the
  namespace and the key foreign the impl is an orphan.
- **Triggered by:** an `E0210` (or its sibling `E0117`) whose generated impl is a foreign
  [namespace lookup trait](../cgp/reference/traits/default_namespace.md) implemented for a foreign
  key: a `#[default_impl(… in Namespace)]` or `#[prefix(… in Namespace)]` registration (naming
  `__Components__`), or a `cgp_namespace!` block re-opening a foreign namespace (naming
  `__Table__`). The Rust code stays `E0210`/`E0117`.
- **Fix (in the `help`):** own one end of the wiring. For a registration, key it on a component your
  crate defines, or register it from the crate that defines the namespace. For a `cgp_namespace!`
  re-open, define a new local namespace that *inherits* the foreign one
  (`cgp_namespace! { new MyNamespace: <Namespace> { … } }`) rather than extending it in place.
- **Upstream class:** [orphan-rule violation](../cgp/errors/wiring/orphan-rule.md).

### `CGP-E030`: trait used but not declared

- **Message:** `` [CGP-E030] the trait `<Trait>` is used but not declared as a dependency ``, with a
  `help` naming the fix: `` declare it as a dependency with `#[uses(<Trait>)]` ``.
- **Means:** a `#[cgp_fn]`/`#[cgp_impl]` body calls a CGP trait's method (a consumer trait, or a
  `#[cgp_fn]`/`#[blanket_trait]` blanket trait) on `self`, but the enclosing definition never
  declared it. `#[cgp_fn]` lowers the body into a blanket impl over a generated generic context,
  `impl<__Context__> Describe for __Context__ where __Context__: GetName`, and `#[cgp_impl]` into a
  provider impl over the same context, `impl<__Context__> Greeter<__Context__> for GreetHello`, with
  `self` renamed to `__context__: &__Context__`. Either way a trait the body uses must be a `where`
  bound on `__Context__`, added with `#[uses(…)]`. Omitted, the method cannot resolve on
  `__Context__`. This also covers a forgotten CGP *consumer* trait used the same way.
- **Triggered by:** an `E0599` "the method `…` exists for reference `&__Context__`, but its trait
  bounds were not satisfied", whose note points at a transitive `HasField` bound. The resolver
  confirms it structurally: the failing call sits in a generated impl over a bare type-parameter
  context (the impl's `Self` in a `#[cgp_fn]` blanket impl, the provider trait's first argument in a
  `#[cgp_impl]` provider impl) and is made on that context (a receiver that is a parameter must be
  declared as the context, read from the method's signature and followed through the `let` an
  `async fn` adds; a receiver no signature types is accepted only in a `#[cgp_fn]` impl), the called
  method belongs to a CGP trait, and that trait is not among the impl's `where` bounds. A call on
  another generic parameter (`value: &Value`) is deliberately left as rustc wrote it, since its fix is
  a bound on `Value`, which `#[uses]` cannot give. Fixtures:
  [`undeclared_uses_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/used-but-undeclared/undeclared_uses_trait.rs)
  for a `#[cgp_fn]` body,
  [`undeclared_uses_trait_in_cgp_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/used-but-undeclared/undeclared_uses_trait_in_cgp_impl.rs)
  and
  [`undeclared_uses_trait_in_async_cgp_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/used-but-undeclared/undeclared_uses_trait_in_async_cgp_impl.rs)
  for provider bodies, and
  [`undeclared_trait_on_non_context_parameter`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/uncataloged/used-but-undeclared/undeclared_trait_on_non_context_parameter.rs)
  for the call left alone. The Rust code stays `E0599`. Any `[T]: Sized` cascade the unresolved return type
  trails (in an `async` body especially) is left as rustc wrote it: those errors can land off the
  failing expression (on the binding pattern, or a later statement the unresolved type flows into)
  where suppressing them reliably would need type information the emitter cannot obtain without
  risking the suppression of an unrelated error.
- **Fix (in the `help`):** add the trait to the definition's `#[uses(…)]` list (or a hand-written
  `where Self: <Trait>` bound), so it becomes a bound on the generated context.
- **Upstream class:** the post-codegen face of a missing impl-side dependency; closest to the
  [hidden unsatisfied-dependency](../cgp/errors/hidden/unsatisfied-dependency.md) class, but here
  the fix is declaring the dependency rather than satisfying it.

### `CGP-E031`: inner provider used but not imported

- **Message:** `` [CGP-E031] the inner provider `<Inner>` is used but not imported ``, with a
  `help`: `` import it with `#[use_provider(<Inner>: <ProviderTrait>)]` ``.
- **Means:** a higher-order provider's body calls an inner provider as an associated function
  (`<Inner>::method(self)`) that it never imported, so the inner parameter carries no provider-trait
  bound and the call cannot resolve. It is the higher-order-provider counterpart of
  [`CGP-E030`](#cgp-e030-trait-used-but-not-declared): a used-but-undeclared dependency, here an
  inner provider imported with `#[use_provider]` rather than a `#[uses]` trait.
- **Triggered by:** an `E0599` "no associated function … found for type parameter `<Inner>`" whose
  help names the "type parameter is bounded by the trait" shape. The resolver confirms it
  structurally: the failing call is `Param::method(…)` on a generic parameter of an enclosing
  provider-trait impl, the method belongs to a CGP provider trait, and the parameter is not bounded
  by it. The impl's own context parameter never qualifies: `Self::method(…)` in a `#[cgp_impl]` body
  names the generated `__Context__`, whose missing bound is a `#[uses]` dependency, not an inner
  provider. rustc's own suggestion leaks the generated `__Context__` and offers the *consumer* trait
  as a bound (the wrong fix); the rewrite names the inner provider and the `#[use_provider]` fix
  instead. The Rust code stays `E0599`.
- **Fix (in the `help`):** import the inner provider with
  `#[use_provider(<Inner>: <ProviderTrait>)]`, which supplies the leading context argument the
  provider trait needs.
- **Upstream class:** a macro-lowering mistake with no upstream error-catalog class of its own; see
  [higher-order providers](../cgp/concepts/higher-order-providers.md) and
  [`#[use_provider]`](../cgp/reference/attributes/use_provider.md).

### `CGP-E032`: consumer trait used in a provider impl

- **Message:**
  `` [CGP-E032] `<Consumer>` is a consumer trait, but a `#[cgp_impl]` provider must implement its provider trait `<Provider>` ``,
  with a `help` naming the fix:
  `` change the impl header to target the provider trait: `impl <Provider>` (not `impl <Consumer>`) ``.
- **Means:** a `#[cgp_impl]` provider impl names the component's *consumer* trait in its header
  where the *provider* trait belongs. `#[cgp_impl(new P)] impl AreaCalculator { … }` is the
  idiomatic provider form; writing the consumer trait `CanCalculateArea` there makes the macro
  generate an inside-out impl of the wrong trait and reference a `CanCalculateAreaComponent` marker
  that does not exist, so one mistake yields a burst of cryptic errors
  (`E0425`/`E0107`/`E0186`/`E0207`) plus a downstream check failure, none naming the cause. It
  generalizes over the component's generic parameters: the macro always inserts the context as the
  leading generic, so the consumer trait is given one argument too many whatever its arity.
- **Triggered by:** the `E0107` "trait takes N generic arguments but N+1 supplied" on the impl
  header, confirmed structurally: an impl carrying the `#[cgp_impl]`-inserted `__Context__` generic,
  a concrete provider-struct `Self`, and a user-written header trait that is a CGP *consumer* trait
  (its consumer↔provider fingerprint yields the provider trait to suggest). The sibling
  macro-lowering errors and the downstream `NotAProvider` check re-report are suppressed. The Rust
  code stays `E0107`.
- **Fix (in the `help`):** change the impl header to name the provider trait the component pairs the
  consumer with.
- **Upstream class:** a macro-lowering mistake with no upstream error-catalog class of its own; the
  provider/consumer duality is described in
  [consumer and provider traits](../cgp/concepts/consumer-and-provider-traits.md).

### `CGP-E033`: `#[cgp_impl]` on a non-CGP trait

- **Message:**
  `` [CGP-E033] `#[cgp_impl]` can only implement a CGP component's provider trait, but `<Trait>` is not a CGP component ``,
  with a `help`:
  `` define `<Trait>` as a component with `#[cgp_component]`, or drop `#[cgp_impl]` and write a plain `impl` if it is an ordinary trait ``.
- **Means:** `#[cgp_impl]` is applied to a trait that is not a CGP component at all (neither a
  consumer nor a provider trait) so there is no provider trait to implement. Distinct from
  [`CGP-E032`](#cgp-e032-consumer-trait-used-in-a-provider-impl), where the trait *is* a component
  and only the wrong half was named: here the fix is to make the trait a component or to abandon
  `#[cgp_impl]`, not to name a different trait.
- **Triggered by:** the same `E0107` shape and structural gate as `CGP-E032` (the `__Context__`
  generic, a concrete `Self`, a user-written header trait), but the header trait's fingerprint is
  *neither* a consumer nor a provider trait. The Rust code stays `E0107`.
- **Fix (in the `help`):** annotate the trait with `#[cgp_component]` to make it a component, or use
  an ordinary `impl` if it was never meant to be one.
- **Upstream class:** a macro-lowering mistake with no upstream error-catalog class of its own; see
  [`#[cgp_impl]`](../cgp/reference/macros/cgp_impl.md) for what the macro requires of its target
  trait.

### `CGP-E034`: consumer trait in an inner-provider bound

- **Message:**
  `` [CGP-E034] `<Consumer>` is a consumer trait and cannot bound an inner provider; a higher-order provider imports its provider trait `<Provider>` ``,
  with a `help`:
  `` name the provider trait in the bound, idiomatically `#[use_provider(… : <Provider>)]` (not the consumer trait `<Consumer>`) ``.
- **Means:** a higher-order provider's inner-provider bound names the component's *consumer* trait
  where its *provider* trait belongs, most often through `#[use_provider]`.
  [`#[use_provider]`](../cgp/reference/attributes/use_provider.md) fills the leading context
  argument in, so `#[use_provider(Inner: CanCalculateArea)]` generates the bound
  `Inner: CanCalculateArea<Self>`, but the consumer trait takes no context parameter, so it is given
  one argument too many. It is the inner-bound sibling of
  [`CGP-E032`](#cgp-e032-consumer-trait-used-in-a-provider-impl) (the same consumer/provider
  confusion, in the impl header).
- **Triggered by:** the `E0107` on the consumer trait in the bound, confirmed structurally: an inner
  bound of a `#[cgp_impl]` provider impl whose trait is a CGP *consumer* trait (its
  consumer↔provider fingerprint yields the provider trait to suggest). The `E0308` body cascade the
  malformed bound trails (recognizable by its mention of the generated `__Context__`) is suppressed.
  The Rust code stays `E0107`.
- **Fix (in the `help`):** name the provider trait in the bound, idiomatically through
  `#[use_provider]`.
- **Upstream class:** a macro-lowering mistake with no upstream error-catalog class of its own; see
  [higher-order providers](../cgp/concepts/higher-order-providers.md).

## Dependency-tree entry codes (`CGP-E1xx`)

The `CGP-E1xx` range codes the entries of a `root cause:` note's dependency tree, one code per
distinct rendering template, so a reader can name a chain step (and a downstream tool can key on it)
just as with a main message. The code rides at the start of each tree entry:

```text
= note: root cause: [CGP-E110] missing field `name` on `App`
        this is required through the dependency chain:
          [CGP-E101] consumer trait impl `CanGreet` for context `App`
          └─ [CGP-E102] provider trait impl `Greeter` with context `App` for provider `GreetHello`
            └─ [CGP-E104] trait impl `HasName` for `App`
              └─ [CGP-E110] missing field `name` on `App`
```

Every entry carries a code, the root cause included: an ordinary trait bound keeps the compiler's
own wording, `` the trait bound `f64: Eq` is not satisfied ``, under the code `CGP-E117`. The
`root cause:` line above the tree reuses the code of the cause it names, so the line and the tree's
last entry carry the same code, as `CGP-E110` does in the example above.

The codes divide into the steps of the chain (`CGP-E101` to `CGP-E109`) and the root causes it ends
at (`CGP-E110` onward).

- **`CGP-E101`: consumer trait impl.** `` consumer trait impl `<Trait>` for context `<Ctx>` ``: a
  hop through the context's own consumer-trait impl (a `CanUseComponent` step).
- **`CGP-E102`: provider trait impl.**
  `` provider trait impl `<Trait>` with context `<Ctx>` for provider `<Provider>` ``: a hop through
  a provider's provider-trait impl (an `IsProviderFor` step).
- **`CGP-E103`: redirect lookup.** `` redirect lookup to `@…` in `<Table>` ``: a hop through a
  namespace or `open` `RedirectLookup<Table, Path>`, naming the table the path is looked up in: the
  context for its own `open` or `namespace`, or an aggregate provider that `open`s a component in
  its own table. Two lookups along the same route for different dispatch keys render this same text
  but are distinct nodes in the dependency graph (the key is part of a node's identity), so each
  keeps its own branch and leaf.
- **`CGP-E104`: trait impl (general).** `` trait impl `<Trait>` for `<Type>` ``: a hop through any
  other trait: a user's blanket trait, or an ordinary bound restated as an impl. It is coded even
  though the trait itself may not be a CGP construct.
- **`CGP-E110`: missing field (leaf).** `` missing field `<f>` on `<T>` ``: the chain bottoms out on
  a context field that is genuinely absent.
- **`CGP-E111`: unimplemented accessor (leaf).**
  `` `HasField` not derived for field `<f>` of `<T>` ``: the struct carries the field but has not
  derived `HasField` for it (the fix, a `#[derive(HasField)]`, rides in a separate `help`). Several
  such fields on *one* struct are one mistake: the derive emits an impl per field, so they coalesce
  into a single root cause under the same code,
  `` `HasField` not derived for fields `<f>` and `<g>` of `<T>` ``, over one merged tree whose
  branches still end at the per-field leaves.
- **`CGP-E112`: field type mismatch (leaf).**
  `` field `<f>` on `<T>` has type `<actual>`, but `<expected>` is required ``: the field is present
  and derived but has the wrong type (the leaf face of the `CGP-E004` main message). The required
  type is rendered by the same helper as that headline, so a wiring-derived requirement reads
  `` but `Pool<<App as HasDbType>::Db>` (`Pool<Postgres>`) is required `` here too and the two can
  never state one requirement two ways.
- **`CGP-E113`: missing delegate entry (leaf).** `` missing wiring for `<key>` on `<Ctx>` ``: the
  context wires no provider for a component, or terminates no namespace path (the `<key>` is a
  component marker or an `@`-path). The table is always the context; a key missing from an aggregate
  provider is `CGP-E114`.
- **`CGP-E114`: missing dispatch entry (leaf).** `` missing entry for `<key>` in provider `<T>` ``:
  the chain bottoms out on a *non-context* delegation table missing a key: an
  [aggregate provider](../cgp/concepts/aggregate-providers.md) missing a component wiring (including
  a table a context's `Key -> Table` entry forwards to), or a
  [`UseDelegate`/`UseInputDelegate`](../cgp/reference/providers/use_delegate.md) dispatch table
  missing a branch for the type it dispatches on (a `Code` fragment or an `Input` value's type). The
  sibling of `CGP-E113` for a provider table rather than the context: the fix is to add the entry to
  *that provider*, or to feed the stage a type the table already covers (the shape a handler
  pipeline hits when a stage's output type is not one a later stage's input dispatcher handles). The
  key may also be an `@`-path, when the aggregate `open`s a component in its own table or joins a
  namespace itself: `` missing entry for `@ComputerComponent.Sink.Digest` in provider `ByteSink` ``,
  under a `CGP-E103` hop that reads `` in `ByteSink` ``.
- **`CGP-E115`: not a provider (leaf).** `` `<X>` is not a provider of `<T>` ``: the chain bottoms
  out on a type wired where a *provider* was expected that does not implement the provider trait at
  all. The mistake is putting a non-provider (often a request or value type) into a provider slot
  (e.g. `UseBasicAuth<QueryBalanceRequest>` with the endpoint handler omitted, so the request type
  sits where an `ApiHandler` belongs. Distinct from `CGP-E114`: the owner is not a table missing one
  entry, so the fix is to use an actual provider (wrap it in the handler), not to add a wiring
  entry.
- **`CGP-E116`: associated type mismatch (leaf).**
  `` abstract type `<assoc>` of `<Trait>` on `<Owner>` is `<actual>`, but `<expected>` is required ``:
  the chain bottoms out on an associated type the owner supplies differently from what a provider
  requires (the leaf face of the `CGP-E005` main message). It reads `associated type` in place of
  `abstract type` when the trait is not a CGP abstract-type component, and renders its required type
  through the same helper as `CGP-E112`, so a requirement that projects through another abstract
  type reads `` but `Tx<<App as HasDbType>::Db>` (`Tx<Postgres>`) is required `` here too. The
  non-`HasField` sibling of `CGP-E112`.
- **`CGP-E117`: ordinary trait bound (leaf).**
  `` the trait bound `<S: Trait>` is not satisfied ``: the chain bottoms out on an ordinary (non-CGP)
  trait bound, such as `f64: Eq` required of the type a context wires for an abstract type. The
  entry keeps the compiler's own wording. When the compiler's headline already states the bound,
  the tool keeps that headline and the note carries the tree alone, ending at this entry.

## Uncoded rewrites

These rewrites improve a diagnostic's readability without classifying its main message, so they
carry no code. They are listed here so their codelessness is a recorded decision.

**Root-cause notes and dependency chains** replace a resolved diagnostic's sub-messages with one
`root cause: …` note per recovered cause (and a `#[derive(HasField)]` `help` where that is the fix).
They accompany a coded main message or a kept rustc one; the note itself is never coded.
[Typed root-cause resolution](implementation/typed-root-cause-resolution.md) owns them.

**Obligation-note renaming** rewrites the `required for … to implement …` chain notes of an
unresolved (fallback) diagnostic to name the consumer and provider traits instead of the wiring
traits. The rename runs in the driver;
[`rewrite/message.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/rewrite/message.rs)
owns the string transform.

**Path stripping** removes the module paths rustc prints in front of type names, so
`cgp::prelude::Chars` becomes `Chars`, but keeps a qualifier that tells two types apart, so
`std::io::Error` beside a crate's own `Error` stays qualified. CGP's own paths and its encoding
types (`Symbol`, `Chars`, `Cons`, and the rest) always lose their qualifier. It applies to every
message the tool rewrote, and to a message it left alone only when one of the resugarings below
fired there; otherwise the paths stay as rustc printed them. It only shortens a name;
[`strip_unambiguous_paths`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/strip_modules.rs)
owns it.

**`Symbol!` resugaring** reverses a `Symbol!` type expansion back to its surface form, so
`Symbol<2, Chars<'x', Chars<'y', Nil>>>` becomes `Symbol!("xy")`. It restores the syntax the
programmer wrote and nothing more;
[`resugar_symbol`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_symbol.rs)
owns it, and [Resugaring](implementation/resugaring.md) explains this and every other construct in
full.

**`Product!` / `Sum!` resugaring** reverses a type-level list expansion back to its surface form, so
`Cons<u64, Cons<String, Nil>>` becomes `Product![u64, String]` and an `Either`/`Void` list becomes
`Sum![…]`. A list whose elements are all `Field` cells folds one step further to CGP's `Struct!` or
`Enum!` shape when the shape has an exact spelling, because a record reads far better than a chain
of `Field` cells, and the shape can be copied back into code.
[`resugar_lists`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_list.rs)
owns the text form and the driver's `render_ty` the typed one.

**`Path!` resugaring** reverses a `Path!` type expansion back to its surface form, so
`PathCons<Symbol!("app"), PathCons<GreeterComponent, Nil>>` becomes `Path!(@app.GreeterComponent)`.
It restores the syntax the programmer wrote and nothing more. An open-ended path, whose list ends in
the generic tail `cgp`'s macros append to every `@`-path key (which rustc prints as `_`), has no
`Path!` spelling, so it stays a list with its segments resugared; a message the tool rewrites names
it as the key its entry wrote (`@foo.bar`).
[`resugar_path`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/resugar_path.rs)
owns it.

**Missing-field clause rewriting** turns an unmet `` `HasField<Symbol!("name")>` `` clause inside a
sub-message into `` missing field `name` on `Context` `` (or the `#[derive(HasField)]` form when the
context implements `HasField` for nothing);
[`rewrite_missing_fields`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/missing_field.rs)
owns it.

**Method-probe advice removal** drops rustc's "this is an associated function, not a method" framing
and "use associated function syntax instead" suggestion from a consumer-method `E0599` the resolver
declined, both artifacts of CGP's `self`-less provider methods, the second actively wrong, so the
unmet wiring bound the diagnostic also names leads. It only removes noise, adding no classification;
[`is_method_probe_advice_text`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs)
recognizes the phrasings and the driver's emitter applies the drop.

## Maintaining this catalog

This catalog is bound by the same synchronization rule as the rest of the knowledge base
([cargo-cgp/AGENTS.md](AGENTS.md)): the codes are defined in the code, so this document must track
them. The constants live in the
[`code`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/code.rs)
module of the error-processing crate, and are stamped by the main-message rewrites, all rustc-free,
in that same crate. The text forms are stamped by
[`rewrite_trait_bound` and `rewrite_wiring_overflow`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/rewrite/message.rs),
the typed check-failure form by
[`plan_resolved`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/plan.rs)'s
`categorized_header` (fed from the resolved failure), and the `CGP-E010`–`CGP-E014` conflict forms
by
[`plan_wiring_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/wiring.rs)
(fed from the conflict the driver's `resolve::conflict` classifier recovers, one code per
`WiringConflict` shape), and the `CGP-E022` orphan form by
[`plan_orphan_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/orphan.rs)
(fed from the `OrphanConflict` the driver's `resolve::orphan` classifier recovers). The `CGP-E1xx`
dependency-tree entry codes are stamped when a node renders: the inner chain nodes by the structured
[`DepNode`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/node.rs)
variants (the driver's
[`resolve::label`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-driver/src/resolve/label)
picks the variant from the trait kind), and the terminal leaf by the rustc-free
[`dependency_tree_leaf`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/wording/lead.rs)
(which prefixes the cause's `dependency_leaf_code`). The `root cause:` line above the tree takes the
same `dependency_leaf_code` in
[`cause_notes`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/wording/note.rs),
so the two cannot disagree. When a new main-message class is recognized, give it the next free
number in its family's block (a family that outgrows its block takes the next free one); a new tree
step takes the next number from `CGP-E101` to `CGP-E109`, and a new root cause the next from
`CGP-E110` onward. Add the constant and register the code here in the same change. When a rewrite
does not classify its main message (a kept rustc header), add it to
[uncoded rewrites](#uncoded-rewrites) instead: do not spend a code on it.
