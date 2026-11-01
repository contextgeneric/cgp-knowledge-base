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

The headline codes come in seven family blocks of ten; a family that outgrows its block takes the
next free one:

| Block | Family | Codes |
| --- | --- | --- |
| `CGP-E001` to `CGP-E009` | a trait the context cannot use, and the two type mismatches | `E001` to `E005` |
| `CGP-E010` to `CGP-E019` | conflicting wiring, and structural mistakes | `E010` to `E019` |
| `CGP-E020` to `CGP-E029` | wiring that never resolves, and the orphan rule | `E020` to `E022` |
| `CGP-E030` to `CGP-E039` | mistakes in what a macro was given | `E030` to `E039` |
| `CGP-E040` to `CGP-E049` | wiring keys and values that do not resolve | `E040` to `E044` |
| `CGP-E050` to `CGP-E059` | extensible data | `E050` |
| `CGP-E060` to `CGP-E069` | structural mistakes, continued | `E060`, `E061` |

The families differ in how the tool recovers them. The **trait-failure** codes `CGP-E001` to
`CGP-E005` come from the typed resolver; each carries the root cause in the accompanying `note`,
opening `root cause: …` over its dependency chain (see
[Typed root-cause resolution](implementation/typed-resolution/overview.md)), except the two
mismatch codes `CGP-E004` and `CGP-E005`, whose main messages already state their cause in full and
so carry the chain alone. (`CGP-E003` is the trait-failure code for a hand-written wrapper trait or
a blanket trait rather than a CGP consumer, and `CGP-E005` the abstract-type counterpart of
`CGP-E004`.) The **conflicting-wiring** codes `CGP-E010` to `CGP-E014` are different in kind: they
come from the duplicate-key conflict classifier, carry no root-cause note, and instead keep rustc's
two carets, which already point at the two colliding entries. They are five separate codes because
each rewrites the `E0119` into a distinct message form with its own fix. The **structural** codes
`CGP-E015` to `CGP-E019`, in the same block, name a mistake in the shape of what a macro was given
(a check table listing an entry twice, two check tables sharing a check-trait name, a `for` loop
whose key skips its variable, a `#[default_impl]` on a generic impl, a wiring entry whose key skips
its generic parameters), each recovered off the compiler from the generated items the `E0119`,
`E0428`, or `E0207` lands on, with its fix in a `help`. The family outgrew its block and continues
in the next free one: `CGP-E060`, a check entry that names no parameters for a component that takes
some, recovered from the check impl the `E0277` lands on, and `CGP-E061`, two `#[cgp_auto_dispatch]`
traits in one module that share a method name, recovered from the pair of `E0428`s on the items the
macro generates for the method. The **never-resolving and orphan** codes `CGP-E020` to `CGP-E022`
each rewrite a whole-program error into a CGP-framed one carrying its fix in a `help`. `CGP-E020`
and `CGP-E021` rewrite the `E0275` overflow of a wiring lookup that never ends, which has no
terminal leaf to descend to, split by how the tool's walk of the lookup is cut: an obligation met
again is a cycle (`CGP-E020`), and the depth limit reached without a repeat is a lookup that grows
(`CGP-E021`). `CGP-E022` rewrites an orphan-rule namespace registration's `E0210`/`E0117` (recovered
from the offending impl off the compiler, like the `E0119` family). The **macro-mistake** codes
`CGP-E030` to `CGP-E039` are each recovered off the compiler from the generated item the failing
token sits in and reworded with the fix in a `help`; the block is full, so a new macro-mistake code
takes the next free block. Four concern an
[undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md): `CGP-E030` a trait used in
a `#[cgp_fn]`/`#[cgp_impl]` body but not declared via `#[uses(…)]`, `CGP-E031` an inner provider a
higher-order provider calls but never imported via `#[use_provider]`, `CGP-E035` an abstract type
used but not imported via `#[use_type]`, and `CGP-E036` a requirement of a component that a provider
does not declare. Four concern the
[wrong component half](../cgp/errors/lowering/wrong-component-half.md): `CGP-E032` a `#[cgp_impl]`
header naming the component's consumer trait, `CGP-E033` a `#[cgp_impl]` on a trait that is not a
CGP component at all, `CGP-E034` an inner-provider bound (typically `#[use_provider]`) naming the
consumer trait, and `CGP-E037` a provider trait named in `#[uses]`. `CGP-E038`, a
`#[cgp_impl(Provider)]` that never declares its provider, is cataloged with the names that do not
resolve, and `CGP-E039` is a provider-trait impl written without `#[cgp_provider]` (the
[provider impl without the macro](../cgp/errors/lowering/provider-impl-without-macro.md) class).
The **wiring-name** codes `CGP-E040` to `CGP-E044` cover a name in a `delegate_components!` entry that
is wrong, all in the
[unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md) class: `CGP-E040` a
consumer trait as a key, `CGP-E041` a component not in scope, `CGP-E042` a key that names no
component, `CGP-E043` a provider never declared, and `CGP-E044` a type in an `@`-path never
declared. Except `CGP-E040`, they come from name
resolution, before the compiler builds the HIR, so the tool holds those errors and reshapes them
once resolution is over. The **extensible-data** code `CGP-E050` heads a failed call to one of CGP's
data operations (a builder, an extractor, a cast), resolved by the typed resolver like the
trait-failure codes, its headline the field or variant at fault. Each entry below gives the rewritten message, the mistake behind it, the
fix, and the [CGP error catalog](../cgp/errors/README.md) class it recognizes.

### `CGP-E001`: consumer trait not implemented

- **Message:** `` [CGP-E001] <cause> ``, the root cause in the sentence its tree code words
  (`` [CGP-E001] missing field `height` on `Rectangle` ``). Several causes of one kind on one owner
  are stated together (`` missing fields `first_name` and `last_name` on `Person` ``), naming the
  first three and counting the rest when there are more than four
  (`` missing fields `alpha`, `beta`, `gamma`, and 3 more on `App` ``); mixed causes take the class
  sentence with their count,
  `` [CGP-E001] the consumer trait `<Consumer>` is not implemented for context `<Context>`: 2 root causes ``
  (pluralized when a use-site failure spans several components).
- **Means:** the context cannot use a component it is expected to use: the wiring is missing, or a
  transitive dependency of the wired provider is unmet, so the blanket impl that would give the
  context its consumer trait does not apply.
- **Triggered by:** an unsatisfied `Context: CanUseComponent<Marker, Params>` bound, a
  `check_components!` / `delegate_and_check_components!` entry failing, a consumer-method call
  (`E0599`) on a context that cannot use a component it wires or on a type parameter that does not
  have the consumer trait as a bound, a call to a generic function whose consumer-trait bound the
  context fails (`E0277`), a consumer-trait bound on a context in an impl's own `where` clause, or a
  `Key -> Table` wiring entry whose table lacks the key. The Rust code stays whatever rustc
  assigned (`E0277` at a check or a bound, `E0599` at a method call).
- **Fix:** follow the `root cause:` note(s): add the missing field or derive, wire the missing
  component, or satisfy the ordinary bound the chain bottoms out on. A `help` names each fix the
  tool can confirm.
- **Upstream class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md).

### `CGP-E002`: provider trait not implemented

- **Message:** `` [CGP-E002] <cause> ``, by the rules of `CGP-E001`; the class sentence, used for
  mixed causes, is
  `` the provider trait `<Provider trait>` with context `<Context>` is not implemented for provider `<Provider>` ``.
- **Means:** a provider a `#[check_providers(...)]` entry lists, or a provider whose own method is
  called directly, fails to implement its provider trait for the context: its impl-side
  `where`-clause dependencies do not hold.
- **Triggered by:** a failing `#[check_providers(...)]` entry, recognized by the generated check
  impl whose supertrait is `IsProviderFor` and whose `Self` is the listed provider, or a failing
  call to a provider trait's method through the provider's own path
  (`PipeHandlers::<…>::compute(&(), …)`, `Add::try_compute(&App, …)`). The tree starts at that
  provider, whatever the context wires. Any other failure the resolver traces is classed by
  the trait its anchor recovered, even when rustc's own headline stops on a provider's
  `IsProviderFor` bound (a dispatch combinator, a `RedirectLookup`, or a provider deep in the
  chain): such a block is `CGP-E001` or `CGP-E003`. A failure the resolver declines has no anchor,
  so the text rewrite restates an `IsProviderFor` headline in the provider form under this code, and
  keeps rustc's notes in place of a root-cause tree.
- **Fix:** follow the `root cause:` note(s) to the dependency the provider is missing.
- **Upstream class:** [check-trait failure](../cgp/errors/checks/check-trait-failure.md) (its
  provider-side face), and [unsatisfied dependency](../cgp/errors/hidden/unsatisfied-dependency.md)
  for a provider's method called directly.

### `CGP-E003`: wrapper trait not implemented

- **Message:** `` [CGP-E003] <cause> ``, by the rules of `CGP-E001`; the class sentence, used for
  mixed causes, is `` the trait `<Wrapper>` is not implemented for context `<Context>` ``, naming a
  foreign subject or a type without wiring plainly (`` for `Router<Arc<App>>` ``,
  `` for `Shape` ``).
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
  [call-site anchor](implementation/typed-resolution/call-site.md) recovers from the call
  expression) or through a `where` bound (`fn f<C: Describe>(…)`, an `E0277` the bound-call anchor
  recovers from the called function's own bound). Whether the failing trait is a CGP consumer or one of these
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

- **`CGP-E010`: duplicate wiring.**
  `` [CGP-E010] conflicting wiring: `<Context>` wires <key> twice ``: the same key mapped twice.
  The key is a component marker, an `@`-path, or an ordinary type (a per-type default's `String`),
  each worded as what it is; the subject is the context, or the namespace lookup trait when the
  collision is inside a namespace
  (`` conflicting wiring: `DefaultImpls1<ShowImplComponent>` wires type `String` twice ``).
  **Fix:** remove one of the two entries the carets point at.
- **`CGP-E011`: overlapping wiring.**
  `` [CGP-E011] conflicting wiring: `<Context>` wires <key>, which <source> already covers ``: two
  distinct but overlapping keys, where one cannot claim what the other already covers (a generic
  entry over a specific one, an `@`-path over a namespace forwarding, or a path that covers another,
  as a prefix or through a generic segment). The source is the key that covers the other, whichever
  entry comes first; when neither covers the other, the key is the one the two share and the source
  is the first entry's. Two distinct keys take this code whatever the entries map them to, redirects
  included. A child namespace redefining a key it inherits takes this code too, with the namespace
  as the subject and the parent as the source. **Fix:** remove or narrow the overlapping entry. (A
  key the namespace resolves to a *redirect* is `CGP-E013` instead.)
- **`CGP-E012`: multiple namespaces.**
  `` [CGP-E012] conflicting wiring: `<Context>` joins both `<A>` and `<B>`, but a target type in `delegate_components!` can join only one namespace ``:
  two blanket forwardings that each cover every key, from joining two namespaces (or a namespace
  plus a bare-key `for` loop, which desugars the same way). **Fix:** join one namespace and inherit
  the others into it, or move a bare `for` key into a path.
- **`CGP-E013`: redirect collision.**
  `` [CGP-E013] conflicting wiring: `<Context>` wires <component> directly, but it is redirected to `<path>` ``:
  a direct wiring that collides with a redirect of the same key: an `open` header, an explicit `=>`
  redirect, a `namespace` join that maps the key to a redirected path, or, with a namespace as the
  subject, a namespace binding a key its *inherited parent* redirects, the shape a bare marker key
  produces for a component carrying a `#[prefix(...)]`. The last two are recovered by normalizing
  the forwarded namespace's `Delegate` for that key. The fix rides in a `help`:
  `` wire the provider `<Provider>` with the key `<path>` ``. A redirect looks a component up with
  its type parameters appended to the path, so for a generic component the key takes a generic
  segment per parameter, `` <path>.<<Param>> <Param> ``, which serves every value the direct entry
  served:
  `` wire the provider `UseDelegate<AreaTable>` with the key `@AreaCalculatorComponent.<Shape> Shape` ``.
  The `help` is omitted when the direct entry names no provider a reader wrote. **Fix:** wire the
  entry's provider under the redirected path rather than the bare key.
- **`CGP-E014`: duplicate redirect.**
  `` [CGP-E014] conflicting wiring: `<Context>` redirects <component> twice, to `<path>` and to `<path>` ``
  (`` twice, both times to `<path>` `` when the two targets agree): the same key redirected more
  than once: two `open`s or `=>` mappings on a context, an `open` of a component the joined
  namespace already redirects through its `#[prefix]`, or the same `@`-path registered twice inside
  one `cgp_namespace!` block (where the subject is the namespace trait rather than a context). Two
  `#[prefix]` attributes registering one component into one namespace take this code too; their two
  registrations carry the attribute's span, so both carets cover `#[cgp_component]`. **Fix:** keep a
  single redirect.

### `CGP-E015`–`CGP-E019`, `CGP-E060`, and `CGP-E061`: structural mistakes

These seven codes name a mistake in the shape of what `check_components!`,
`delegate_and_check_components!`, `delegate_components!`, `cgp_namespace!`, `#[default_impl]`, or
`#[cgp_auto_dispatch]` was given, which the compiler rejects through the items the macro generated.
The raw errors name those items (`__CheckApp`, an impl's type parameter) and carry suggestions that
do not fix the program, so each rewrite names the mistake in the terms the program wrote and puts
the fix in a `help`. The driver recognizes each from the generated items at the caret
(`detect::structural`), and the rustc-free `plan_structural_mistake` and `structural_mistake_help`
word them.

- **`CGP-E015`: a check entry listed twice.**
  `` [CGP-E015] `check_components!` checks `<entry>` twice for `<Context>` ``, the entry written as
  the table wrote it (`` `ShowerComponent: u32` `` for one with parameters), from the `E0119` between
  the two identical check impls. rustc's two carets stay. **Fix (in the `help`):**
  `` remove one of the two `<entry>` entries ``
  ([`check_duplicate_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/check_duplicate_entry.rs)).
- **`CGP-E016`: two check tables sharing a check-trait name.**
  `` [CGP-E016] two `check_components!` tables in one module check `<Context>` `` when both derive
  `__Check<Context>`, or `` … name their check trait `<Name>` `` when two `#[check_trait(...)]`
  attributes give one name, from the `E0428` on the second definition. The two carets are labelled
  as the first and the second table. The `E0428` comes from name resolution, before any query is
  safe, so the driver recognizes it by the span's expansion from `check_components!` alone, naming
  the macro by the last segment of the path the call was written with, so a call written as
  `cgp::prelude::check_components!` counts and a crate's own `table_check_components!` does not.
  **Fix (in the `help`):** merge the two tables, or name one table's check trait with
  `#[check_trait(...)]`
  ([`check_twice_same_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/check_twice_same_context.rs),
  [`check_twice_qualified_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/check_twice_qualified_call.rs)).
- **`CGP-E017`: a `for` loop whose key skips its variable.**
  `` [CGP-E017] the `for` loop in the wiring of `<Context>` binds `<T>`, but its key `<key>` does not use it ``,
  one block in place of rustc's three `E0207`s (the key variable and the value variable, in the
  entry and its `IsProviderFor` twin), with the caret on the variable and rustc's suggestions
  dropped. **Fix (in the `help`):** `` write `<T>` in the key where the type the loop covers goes ``
  ([`for_loop_key_without_var`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/for_loop_key_without_var.rs)).
- **`CGP-E018`: a `#[default_impl]` on a generic provider impl.**
  `` [CGP-E018] `#[default_impl]` cannot register `<Provider>` for `<key>`, because the provider's impl is generic over `<T>` ``,
  from the `E0207` the registration's copied parameter produces, for a provider generic over a type
  or written in the explicit-context form (`impl<Context> … for Context`). rustc's suggestion to
  remove the parameter is dropped. **Fix (in the `help`):**
  `` write `<Provider>`'s impl for `<key>` alone, in the concise `#[cgp_impl]` form without `<T>` ``
  ([`default_impl_generic_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_generic_provider.rs)).
  A provider struct that is itself generic over the parameter (`#[cgp_impl(ShowWith<T>)]`) takes the
  same code when the key is a type, and its help registers the provider at the key:
  `` write the impl for `<key>` alone, as `#[cgp_impl(<Provider at key>)]` with `<key>` in place of `<T>` ``
  ([`default_impl_generic_provider_struct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/default_impl_generic_provider_struct.rs)).
- **`CGP-E019`: a wiring entry whose key skips its generic parameters.**
  `` [CGP-E019] the entry for `<key>` in the wiring of `<Context>` binds `<T>`, but its key does not use it ``,
  or `` … in the namespace `<Namespace>` … `` for a `cgp_namespace!` entry, naming every parameter
  the key leaves out (`` binds `T` and `U`, but its key does not use them ``). It replaces the
  `E0207` rustc reports for each such parameter in every impl the entry lowers to (its
  `IsProviderFor` twin, and a check impl under `delegate_and_check_components!`), with the caret on
  the parameter rustc reports first and rustc's suggestions, to add the parameter to the context or
  to remove it, dropped, since neither compiles. **Fix (in the `help`):**
  `` write a concrete type in place of `<T>` in `<Provider>`, and remove `<T>` from the entry's generic parameters ``,
  naming where the entry uses the parameter when that is not a plain provider (the table a `->`
  entry forwards to), and only removing it when nothing uses it
  ([`unconstrained_generic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/unconstrained_generic.rs),
  [`entry_generic_shapes`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unconstrained-generic/entry_generic_shapes.rs)).

- **`CGP-E060`: a check entry that names no parameters for a component that takes some.**
  `` [CGP-E060] the check of `<entry>` on `<Context>` names no parameters, so it checks the component at the unit parameters `()` ``,
  from the `E0277` on the check impl of a `check_components!` or `delegate_and_check_components!`
  entry whose parameters are `()` while the component's consumer trait takes parameters, either its
  own (`CanCalculateArea<Shape>`) or one its key's marker carries (`<I> FooKeyComponent<I>`). rustc
  reports it as a provider that does not implement `IsProviderFor`, with a `where` suggestion
  spliced into the entry for a generic key; both are dropped and the caret stays on the entry.
  **Fix (in the `help`):**
  `` check it at the parameters its provider implements: `#[check_params(<P>)]` `` for
  `delegate_and_check_components!`, or `` `<entry>: <P>` `` (`` `<entry>: [<P1>, <P2>]` `` for
  several) for `check_components!`. The parameters are those of the component's provider impls for
  the context, each kept only when the context passes the check at it; without one, the error is not
  reworded this way
  ([`generic_component_unit_params`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/generic_component_unit_params.rs),
  [`generic_check_without_params`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/generic_check_without_params.rs),
  [`check_trait_named_as_wrapper`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/checks/check_trait_named_as_wrapper.rs)).
- **`CGP-E061`: two `#[cgp_auto_dispatch]` traits in one module that share a method name.**
  `` [CGP-E061] two `#[cgp_auto_dispatch]` traits in one module declare the method `<method>` ``, in
  place of the two `E0428`s on the items the macro names after the method alone, the helper
  `__compute_<method>__` and the computer `Compute<Method>`. The computer's `E0428` carries the
  report, its carets on the two method names labelled as the first and the second declaration, with
  a note naming the two generated items; the helper's is dropped. The pair is recognized from the
  two diagnostics alone, since an `E0428` comes from name resolution: the helper's caret comes from
  a `#[cgp_auto_dispatch]` expansion, and the computer's name is the one the same method gives.
  **Fix (in the `help`):**
  `` rename `<method>` in one of the two traits, or declare the traits in different modules ``
  ([`auto_dispatch_shared_method_name`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/auto_dispatch_shared_method_name.rs),
  [`auto_dispatch_shared_method_names`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/conflicting-wiring/auto_dispatch_shared_method_names.rs)).

The structural codes report a mistake once, however many errors rustc gives for it. The upstream
classes are [conflicting wiring](../cgp/errors/wiring/conflicting-wiring.md) for `CGP-E015`,
`CGP-E016`, and `CGP-E061`, [unconstrained generic](../cgp/errors/wiring/unconstrained-generic.md)
for `CGP-E017` to `CGP-E019`, and
[check-trait failure](../cgp/errors/checks/check-trait-failure.md#when-a-check-names-no-parameters)
for `CGP-E060`.

### `CGP-E020`: wiring that leads back to itself

- **Message:**
  `` [CGP-E020] the wiring for the consumer trait `<Consumer>` on context `<Context>` never resolves, because the lookup leads back to itself ``,
  with a `help` naming the provider that closes the loop.
- **Means:** resolving the component's wiring meets a requirement it is already resolving, so the
  lookup never ends. A component wired to `UseContext` with no other implementation of its consumer
  trait is the plain case: `UseContext` provides the provider trait by requiring the consumer trait,
  which the wiring routes back to `UseContext`. An `open` error route that raises its own `String`
  through `DebugError`, and a recursive data type serialized through providers that re-enter the
  context, close the same kind of loop through other providers.
- **Triggered by:** an `E0275` overflow whose requirement is a `Context: CanUseComponent<Marker, …>`
  bound, at a `check_components!` entry, or the consumer trait itself, at a consumer-method call
  (`Person: CanGreet` at `Person.greet()`), whose consumer obligation the tool walks until an
  obligation repeats among its own ancestors. The call's obligation is recovered as the
  [call-site anchor](implementation/typed-resolution/call-site.md) recovers a failing call's, and
  only for the consumer trait the overflow names. The Rust code stays `E0275`. The note pointing at
  the generated `__Check…` trait is dropped, since the kept caret already covers the check entry,
  and so is rustc's advice to raise the recursion limit, which cannot end the loop
  ([`use_context_cycle`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle.rs),
  [`use_context_cycle_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/use_context_cycle_call.rs)). A lookup can also overflow
  through a type the compiler could not resolve (an earlier `E0425` or `E0412`), with no loop in the
  wiring; its walk ends without a cut, so the overflow keeps rustc's wording, and the earlier error
  is the one to fix. Any overflow whose walk is not cut keeps rustc's wording and notes
  ([`cross_context_cycle_reuse_distinct`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/cross_context_cycle_reuse_distinct.rs)).
- **Fix (in the `help`):**
  `` wire a provider in place of `<Provider>`, which provides `<Provider trait>` for `<Context>` by requiring `<Requirement>` on `<Type>` again ``,
  naming the provider whose requirement closes the loop (`UseContext`, or `DebugError` for the
  `String` route), the consumer trait it requires with its arguments, and the type it requires it
  of, which is the context when the loop stays on one context. The provider is named only when a
  wiring entry chose it, directly or through a redirect. A loop that closes inside a higher-order
  provider, such as the inner `UseContext` a dispatcher routes each variant through, gets
  `` wire the component to a provider that does not require the consumer trait it provides ``
  instead.
- **Upstream class:** [wiring cycle](../cgp/errors/wiring/wiring-cycle.md).

### `CGP-E021`: wiring that grows without end

- **Message:**
  `` [CGP-E021] the wiring for the consumer trait `<Consumer>` on context `<Context>` never resolves, because each step requires it for a larger type (`<Larger>`, …) ``,
  naming the first larger requirement (`` `CanShow<Vec<u32>>` `` for `CanShow<u32>`), or the first
  larger type when the lookup grows in the type the consumer trait is required of
  (`` `Vec<u32>` `` for `u32`), with a `help` naming the provider whose requirement grows.
- **Means:** each step of the lookup requires the consumer trait again for a larger type, so no
  requirement repeats, and the compiler gives up at its recursion limit. A provider of
  `CanShow<T>` that requires `CanShow<Vec<T>>` is the plain case.
- **Triggered by:** the same `E0275` overflow at a check entry or a consumer-method call, when the
  walk reaches its depth limit without meeting a repeated obligation
  ([`divergent_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring.rs),
  [`divergent_wiring_call`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_wiring_call.rs),
  [`divergent_self_wiring`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/wiring-cycle/divergent_self_wiring.rs)). The Rust code stays `E0275`, and the `__Check…` note
  and rustc's advice to raise the recursion limit are dropped, since no limit ends a lookup that
  grows.
- **Fix (in the `help`):**
  `` wire a provider in place of `<Provider>`, which provides `<Provider trait>` for `<Context>` by requiring `<Requirement>` on `<Type>`, a larger type at every step ``,
  where `<Requirement>` is the consumer trait with its arguments and `<Type>` is the context, or the
  larger type when the lookup grows in it,
  or `` wire the component to a provider whose requirements do not grow with each step `` when no
  wiring entry chose that provider.
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
  `help` naming the fix: `` declare it as a dependency with `#[uses(<Trait><Args>)]` ``. For a
  generic trait the help writes the arguments the call uses, as in `#[uses(CanFormatPair<(u32, u64)>)]`;
  an argument the tool cannot read stays as the trait's own parameter, and the help adds
  `` , with the type the call uses in place of `<Param>` ``.
- **Means:** a `#[cgp_fn]`/`#[cgp_impl]` body calls a CGP trait (a consumer trait, or a
  `#[cgp_fn]`/`#[blanket_trait]` blanket trait) on the context, as a method on `self` or as an
  associated function on `Self` (`Self::raise_error(…)`), but the enclosing definition never
  declared it. `#[cgp_fn]` lowers the body into a blanket impl over a generated generic context,
  `impl<__Context__> Describe for __Context__ where __Context__: GetName`, and `#[cgp_impl]` into a
  provider impl over the same context, `impl<__Context__> Greeter<__Context__> for GreetHello`, with
  `self` renamed to `__context__: &__Context__` and `Self` to `__Context__`. Either way a trait the
  body uses must be a `where` bound on `__Context__`, added with `#[uses(…)]`. Omitted, the call
  cannot resolve on `__Context__`.
- **Triggered by:** an `E0599`, either "the method `…` exists for reference `&__Context__`, but its
  trait bounds were not satisfied", whose note points at a transitive `HasField` bound, or "no
  associated function or constant named `…` found for type parameter `__Context__`", whose
  suggestions are spliced into the macro attribute. The resolver confirms it structurally: the
  failing call sits in a generated impl over a bare type-parameter context (the impl's `Self` in a
  `#[cgp_fn]` blanket impl, the provider trait's first argument in a `#[cgp_impl]` provider impl)
  and is made on that context (a receiver that is a parameter must be declared as the context, read
  from the method's signature and followed through the `let` an `async fn` adds; a receiver no
  signature types is accepted only in a `#[cgp_fn]` impl; an associated function's qualifying type
  must name the context), the called function belongs to a CGP trait, and that trait is not among
  the impl's `where` bounds. The help's arguments come from unifying the call's arguments (their
  written types, or a parameter's declared type) with the function's declared inputs; a trait with a
  lifetime or const parameter gets no help. A call on another generic parameter (`value: &Value`)
  is deliberately left as rustc wrote it, since its fix is a bound on `Value`, which `#[uses]` cannot
  give. Fixtures:
  [`undeclared_uses_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait.rs)
  for a `#[cgp_fn]` body,
  [`undeclared_uses_trait_in_cgp_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait_in_cgp_impl.rs)
  and
  [`undeclared_uses_trait_in_async_cgp_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_uses_trait_in_async_cgp_impl.rs)
  for provider bodies,
  [`undeclared_generic_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_generic_trait.rs)
  and
  [`undeclared_generic_trait_parameter`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_generic_trait_parameter.rs)
  for a generic trait's arguments,
  [`raise_error_in_cgp_fn`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/raise_error_in_cgp_fn.rs),
  [`raise_error_written_source`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/raise_error_written_source.rs),
  and
  [`raise_generic_missing_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/raise_generic_missing_bound.rs)
  for `Self::raise_error(…)`, and
  [`undeclared_trait_on_non_context_parameter`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/undeclared_trait_on_non_context_parameter.rs)
  for the call left alone. The Rust code stays `E0599`. Any `[T]: Sized` cascade the unresolved
  return type trails (in an `async` body especially) is left as rustc wrote it: those errors can
  land off the failing expression (on the binding pattern, or a later statement the unresolved type
  flows into) where suppressing them reliably would need type information the emitter cannot obtain
  without risking the suppression of an unrelated error.
- **Fix (in the `help`):** add the trait to the definition's `#[uses(…)]` list, with the arguments
  the call uses (or a hand-written `where Self: <Trait>` bound), so it becomes a bound on the
  generated context.
- **Upstream class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md).

### `CGP-E031`: inner provider used but not imported

- **Message:** `` [CGP-E031] the inner provider `<Inner>` is used but not imported ``, with a
  `help`: `` import it with `#[use_provider(<Inner>: <ProviderTrait><Args>)]` ``. For a generic
  component the help writes the component's parameters after the context, as in
  `#[use_provider(Inner: AreaCalculator<Shape>)]`; a parameter the call does not fix stays named,
  and the help adds `` , with the type the call uses in place of `<Param>` ``. A provider trait with
  a lifetime or const parameter gets the header without a help, since the help writes only type
  arguments
  ([`missing_use_provider_lifetime_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_lifetime_component.rs)).
- **Means:** a higher-order provider's body calls an inner provider as an associated function
  (`<Inner>::method(self)`) that it never imported, so the inner parameter carries no provider-trait
  bound and the call cannot resolve. It is the higher-order-provider counterpart of
  [`CGP-E030`](#cgp-e030-trait-used-but-not-declared): an undeclared dependency, here an
  inner provider imported with `#[use_provider]` rather than a `#[uses]` trait.
- **Triggered by:** an `E0599` "no associated function … found for type parameter `<Inner>`" whose
  help names the "type parameter is bounded by the trait" shape. The resolver confirms it
  structurally: the failing call is `Param::method(…)` on a generic parameter of an enclosing
  provider-trait impl, the method belongs to a CGP provider trait, and the parameter is not bounded
  by it. The impl's own context parameter never qualifies: `Self::method(…)` in a `#[cgp_impl]` body
  names the generated `__Context__`, whose missing bound is a `#[uses]` dependency, not an inner
  provider. rustc's own suggestion leaks the generated `__Context__` and offers the *consumer* trait
  as a bound (the wrong fix); the rewrite names the inner provider and the `#[use_provider]` fix
  instead. The component's parameters come from the call, as for `CGP-E030`: the method's signature
  is instantiated with its `Self` pinned to the inner provider and its context to the impl's, and
  each input is unified with the argument's readable type; the impl's own generic parameters may be
  written, since the attribute sits on the same impl
  ([`missing_use_provider_generic_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/missing_use_provider_generic_component.rs)).
  The Rust code stays `E0599`.
- **Fix (in the `help`):** import the inner provider with
  `#[use_provider(<Inner>: <ProviderTrait><Args>)]`, which supplies the leading context argument the
  provider trait needs.
- **Upstream class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md); see
  also [higher-order providers](../cgp/concepts/higher-order-providers.md) and
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
  code stays `E0107`. A requirement of the impl that fails on its own, such as a field the context
  lacks, is a separate mistake: the resolver reads the impl's requirements as written, so it is
  reported beside this error as the block the program gives once the header is fixed (`[CGP-E001]`
  for a missing field, `[CGP-E004]` for a field of the wrong type).
- **Fix (in the `help`):** change the impl header to name the provider trait the component pairs the
  consumer with.
- **Upstream class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md); the
  provider/consumer duality is described in
  [consumer and provider traits](../cgp/concepts/consumer-and-provider-traits.md).

### `CGP-E033`: `#[cgp_impl]` on a non-CGP trait

- **Message:**
  `` [CGP-E033] `#[cgp_impl]` can only implement a CGP component's provider trait, but `<Trait>` is not a CGP component ``,
  with a `help`:
  `` make `<Trait>` a component, as in `#[cgp_component(<Trait>Provider)]`, and implement its provider trait here (`impl <Trait>Provider`), or drop `#[cgp_impl]` and write a plain `impl` if it is an ordinary trait ``.
- **Means:** `#[cgp_impl]` is applied to a trait that is not a CGP component at all (neither a
  consumer nor a provider trait) so there is no provider trait to implement. Distinct from
  [`CGP-E032`](#cgp-e032-consumer-trait-used-in-a-provider-impl), where the trait *is* a component
  and only the wrong half was named: here the fix is to make the trait a component or to abandon
  `#[cgp_impl]`, not to name a different trait.
- **Triggered by:** the same `E0107` shape and structural gate as `CGP-E032` (the `__Context__`
  generic, a concrete `Self`, a user-written header trait), but the header trait's fingerprint is
  *neither* a consumer nor a provider trait. The Rust code stays `E0107`.
- **Fix (in the `help`):** make the trait a component with `#[cgp_component(…)]` and name the
  provider trait it generates in the impl header (making it a component alone leaves its consumer
  trait in the header, which is `CGP-E032`), or use an ordinary `impl` if it was never meant to be
  one.
- **Upstream class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md); see
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
- **Upstream class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md); see
  also [higher-order providers](../cgp/concepts/higher-order-providers.md).

### `CGP-E035`: abstract type used but not imported

- **Message:** `` [CGP-E035] the abstract type `<Type>` is used but not imported ``, with a `help`:
  `` import it with `#[use_type(<Trait>.<Type>)]` ``.
- **Means:** a `#[cgp_fn]`, `#[cgp_impl]`, or `#[cgp_component]` definition names an abstract type
  of the context, as `Self::Error` or a bare `Error`, without importing it with
  [`#[use_type]`](../cgp/reference/attributes/use_type.md). The context then carries no bound of
  the abstract-type trait that declares the type, so `Self::Error` names an associated type nothing
  declares, and a bare `Error`, which only the import rewrites, names no type at all.
- **Triggered by:** an `E0220` "associated type `Error` not found for `__Context__`" (or "for
  `Self`" in a `#[cgp_fn]`), read from the diagnostic's arguments (the type, its kind, and the
  type it was sought on). The resolver confirms that the caret sits in a method of an item a CGP
  macro generated (an impl over the reserved `__Context__`, a consumer or provider trait, or a
  `#[cgp_fn]` trait) and finds the one CGP abstract-type component (a trait with the
  `#[cgp_type]` fingerprint and no parameter of its own) that declares an associated type of that
  name. It is reported once per definition. A bare `Error` arrives earlier, as an `E0425`
  "cannot find type `Error` in this scope" from name resolution, when nothing can yet say which
  trait declares it; it becomes `CGP-E035` when a requirement of the component names that trait
  (see [`CGP-E036`](#cgp-e036-requirement-not-declared)), and the requirement's `E0277`s are then
  dropped, since the import satisfies them too. Fixtures:
  [`self_error_without_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_without_bound.rs),
  [`self_error_in_cgp_fn`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_in_cgp_fn.rs),
  [`self_error_in_component`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_in_component.rs),
  and
  [`self_error_used_twice`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_used_twice.rs)
  for `Self::Error`, and
  [`error_alias_without_use_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_without_use_type.rs)
  and
  [`use_type_component_self_error`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/use_type_component_self_error.rs)
  for a provider of a component that imports the type. The Rust code stays `E0220` (or `E0425`).
  Two cases are left as rustc wrote them: a second abstract-type trait declaring the same name makes
  the import ambiguous
  ([`self_error_two_traits`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/self_error_two_traits.rs)),
  and a bare `Error` that no requirement explains keeps its `E0425` with rustc's suggestion to
  import `std::error::Error`
  ([`error_alias_in_cgp_fn`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/error_alias_in_cgp_fn.rs)).
- **Fix (in the `help`):** import the type with `#[use_type(HasErrorType.Error)]` and write it bare.
- **Upstream class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md).

### `CGP-E036`: requirement not declared

- **Message:**
  `` [CGP-E036] the provider trait `<ProviderTrait>` requires `<Trait>` of the context, but the provider `<Provider>` does not declare it ``
  (`them` for several), with a `help` for each kind of declaration:
  `` declare it as a dependency with `#[uses(<Trait>)]` `` for a trait, and
  `` import it with `#[use_type(<Trait>.<Type>)]` `` for an abstract-type component.
- **Means:** a component requires a trait of every context, through
  [`#[extend(…)]`](../cgp/reference/attributes/extend.md) or `#[use_type(…)]` on its
  `#[cgp_component]`, which lowers to a `where` clause on the provider trait
  (`trait Greeter<__Context__> where __Context__: HasName`). A `#[cgp_impl]` provider must satisfy
  that clause from its own declarations, and this one does not declare the trait, even when its
  body never uses it.
- **Triggered by:** an `E0277` on `__Context__: <Trait>`, "required by a bound in" the provider
  trait, at the `#[cgp_impl]` attribute or a method signature. The resolver confirms it
  structurally: the caret sits in a provider impl over the reserved `__Context__`, outside its
  method bodies, the impl's trait is a CGP provider trait implemented for a provider type, and some
  `where` clause the provider trait places on the context does not hold under the impl's own
  declarations (checked with the trait solver in the impl's environment). Every such requirement is
  named, in the component's order, and an abstract-type component's requirement is worded as its
  `#[use_type]` import. It is reported once per provider, with the caret where rustc first reported
  it (usually the attribute) and without rustc's note that the error originates in the macro; an
  abstract type the provider also uses without importing it is reported as
  [`CGP-E035`](#cgp-e035-abstract-type-used-but-not-imported) instead. Fixtures:
  [`supertrait_missing_uses`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses.rs),
  [`supertrait_missing_uses_generic`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses_generic.rs)
  (a generic requirement, `TagFor<u32>`),
  [`supertrait_missing_uses_beside_body_error`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses_beside_body_error.rs)
  (an unrelated body error kept beside it), and
  [`use_default_getter_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/use_default_getter_context.rs)
  (a `#[cgp_impl(UseDefault)]` provider), and
  [`supertrait_missing_uses_self_argument`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/undeclared-dependency/supertrait_missing_uses_self_argument.rs)
  (a requirement naming the context, which the header and help write as `Self`). The Rust code
  stays `E0277`.
- **Fix (in the `help`):** declare the requirement on the provider, `#[uses(HasName)]` for a trait
  or `#[use_type(HasErrorType.Error)]` for an abstract-type component.
- **Upstream class:** [undeclared dependency](../cgp/errors/lowering/undeclared-dependency.md).

### `CGP-E037`: provider trait in `#[uses]`

- **Message:**
  `` [CGP-E037] `<Provider>` is a provider trait and cannot be a `#[uses]` dependency; a dependency names its consumer trait `<Consumer>` ``,
  with a `help`:
  `` name the consumer trait instead: `#[uses(<Consumer>)]` (not the provider trait `<Provider>`) ``.
- **Means:** `#[uses]` on a `#[cgp_fn]` or `#[cgp_impl]` names a component's *provider* trait.
  [`#[uses]`](../cgp/reference/attributes/uses.md) declares a trait of the context and writes it as
  `Self: <Trait>`, so a provider trait, whose first parameter is the context, is given one argument
  too few. It is the mirror of [`CGP-E034`](#cgp-e034-consumer-trait-in-an-inner-provider-bound):
  there a consumer trait stands where a provider trait belongs, here the reverse.
- **Triggered by:** an `E0107` "missing generics for trait `<Provider>`", whose rustc `help` adds the
  generated `<__Context__>`. The resolver confirms it from the HIR: the caret is the trait name of a
  `where` bound on the context (`Self`, or the reserved `__Context__`) of an impl a CGP macro
  generated, the trait is a CGP provider trait written without type arguments, and a consumer trait
  pairs with it; the search for that consumer skips the impl's own trait, whose blanket impl may be
  the one being lowered. Fixtures:
  [`uses_provider_trait`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/uses_provider_trait.rs)
  on a `#[cgp_fn]` and
  [`uses_provider_trait_in_impl`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/wrong-component-half/uses_provider_trait_in_impl.rs)
  on a `#[cgp_impl]` provider. The Rust code stays `E0107`.
- **Fix (in the `help`):** name the consumer trait in `#[uses]`.
- **Upstream class:** [wrong component half](../cgp/errors/lowering/wrong-component-half.md).

### `CGP-E038`: `#[cgp_impl]` provider not declared

- **Message:** `` [CGP-E038] the provider `<Provider>` is not declared ``, with a `help`:
  `` declare it with `#[cgp_impl(new <Provider>)]` ``.
- **Means:** `#[cgp_impl(GreetHello)]` without `new` implements the provider trait for a struct the
  author is expected to declare, and none is declared, so the impl names a type that does not exist.
  `new` makes the macro declare the struct.
- **Triggered by:** an `E0425` "cannot find type `<Provider>` in this scope" from name resolution
  whose caret is the `Self` type of an impl declaring the reserved `__Context__` parameter, read
  back from the HIR once resolution is over. The `E0425` of a wiring value naming the same provider
  is dropped as its consequence, and so is the `E0275` overflow a call of the component then reports
  under the next-generation solver
  ([`provider_not_declared`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/provider_not_declared.rs)).
  A provider some module of the crate or a public module of a dependency declares is not in scope
  rather than undeclared, so its `E0425` is left as rustc wrote it, with rustc's import suggestion
  when it gives one
  ([`names_not_imported`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/names_not_imported.rs)).
  The Rust code stays `E0425`.
- **Fix (in the `help`):** add `new` to the attribute, or declare the provider struct.
- **Upstream class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E039`: provider impl without the macro

- **Message:**
  `` [CGP-E039] the impl of `<Trait>` for `<Provider>` is written without `#[cgp_provider]` ``, with
  a `help`: `` add `#[cgp_provider]` to the impl of `<Trait>`, or write the provider with `#[cgp_impl]` ``.
- **Means:** a provider trait is implemented for a provider struct by a plain `impl`. The provider
  trait has `IsProviderFor` as a supertrait, and only `#[cgp_provider]` (or `#[cgp_impl]`) writes the
  provider's impl of it, so the plain impl fails its own supertrait.
- **Triggered by:** an `E0277` naming `IsProviderFor` whose caret is exactly the `Self` type of a
  local impl the user wrote of a CGP provider trait, when no `IsProviderFor` impl exists for that
  struct and the trait's component. rustc's implementor list is dropped, and a later `E0277` on the
  same provider's `IsProviderFor` bound, such as the failing check of a context that wires it, is
  dropped as its consequence
  ([`provider_impl_without_macro`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro.rs),
  [`provider_impl_without_macro_wired`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/lowering/provider-impl-without-macro/provider_impl_without_macro_wired.rs)).
  The Rust code stays `E0277`.
- **Fix (in the `help`):** add `#[cgp_provider]` to the impl, or write the provider with `#[cgp_impl]`.
- **Upstream class:** [provider impl without the macro](../cgp/errors/lowering/provider-impl-without-macro.md).

### `CGP-E040`: consumer trait as a wiring key

- **Message:**
  `` [CGP-E040] the wiring key `<Consumer>` is a consumer trait, but a key names a component ``,
  with a `help`: `` name its component instead: `<Component>` ``.
- **Means:** a `delegate_components!` key names a component's consumer trait, `CanGreet`, where its
  marker, `GreeterComponent`, belongs. The key becomes a type argument of `DelegateComponent`, so a
  trait there is a trait where a type belongs.
- **Triggered by:** an `E0782` "expected a type, found a trait" whose caret is exactly the key of a
  `DelegateComponent` impl (by `DefId`), read from the HIR, when the key resolves to a CGP consumer
  trait whose provider trait's delegation blanket names its marker
  ([`consumer_trait_as_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/consumer_trait_as_key.rs)).
  rustc's `dyn` suggestion is dropped. The Rust code stays `E0782`.
- **Fix (in the `help`):** write the component marker as the key.
- **Upstream class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E041`: component not in scope

- **Message:** `` [CGP-E041] the component `<Component>` is not in scope ``, with a `help`:
  `` import it with `use <path>;` ``.
- **Means:** a key names a component that exists, in a dependency or another module, but is not
  imported where the table is written, such as `ErrorTypeProviderComponent`, which the prelude does
  not export.
- **Triggered by:** an `E0425` "cannot find type" from name resolution whose caret is exactly a
  wiring key, or a whole segment of an `@`-path in a key or value, when exactly one component marker
  of that name exists among the traits the crate can see. The path is a `crate::` path for a local component, and for a dependency's the shortest
  public path from a direct dependency's root, found by walking its modules and following
  re-exports; the compiler's own path printing names a crate re-exported under another name by its
  crate name (`cgp::cgp_core::…`), which does not compile. A repeat at the same key prints once, and
  rustc's suggestions are dropped
  ([`error_key_not_imported`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/error_key_not_imported.rs),
  [`component_in_module_not_imported`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/component_in_module_not_imported.rs),
  [`path_segment_component_not_imported`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_component_not_imported.rs)).
  Two components of the same name decline. The Rust code stays `E0425`.
- **Fix (in the `help`):** import the component.
- **Upstream class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E042`: wiring key names no component

- **Message:** `` [CGP-E042] the wiring key `<Key>` names no component ``, with a `help`:
  `` name the component of `<Consumer>` instead: `<Component>` ``.
- **Means:** a key was guessed from a consumer trait's name with `Component` appended
  (`HasScalarTypeComponent`, `CanGreetComponent`), while the marker is named after the provider
  trait (`ScalarTypeProviderComponent`, `GreeterComponent`).
- **Triggered by:** an `E0425` "cannot find type" from name resolution whose caret is exactly a
  wiring key, when no component has that name and the name without its `Component` suffix names
  exactly one consumer trait with a component
  ([`scalar_type_guessed_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/scalar_type_guessed_key.rs),
  [`consumer_trait_name_as_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/consumer_trait_name_as_key.rs)).
  A repeat at the same key prints once. The Rust code stays `E0425`.
- **Fix (in the `help`):** write the consumer trait's component.
- **Upstream class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E043`: provider not declared

- **Message:**
  `` [CGP-E043] the provider `<Provider>` wired for `<Key>` is not declared ``, with a `help` only for
  a near miss: `` a provider of `<Key>` with a similar name exists: `<Provider>` ``.
- **Means:** a wiring value names a provider struct that nothing declares, often a misspelling.
- **Triggered by:** an `E0425` "cannot find type" from name resolution whose caret is exactly a
  wiring value. The near miss is looked for among the providers that implement the provider trait of
  the key's component, with the same closeness rule as the other near-miss helps. rustc's
  suggestion of a similarly named trait (often the provider trait) is dropped, and an `E0275`
  overflow on the requirement the entry leaves unprovable (the context implementing the consumer
  trait, as a call reports it, or `CanUseComponent` of the component, as a check reports it) is
  dropped as its consequence, whatever parameters the component takes
  ([`value_not_declared`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_not_declared.rs),
  [`value_not_declared_near_miss`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/value_not_declared_near_miss.rs),
  [`generic_component_value_not_declared`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/generic_component_value_not_declared.rs)).
  A provider some module of the crate or a public module of a dependency declares is not in scope
  rather than undeclared, so its `E0425` is left as rustc wrote it, with rustc's import suggestion
  when it gives one
  ([`names_not_imported`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/names_not_imported.rs)).
  The Rust code stays `E0425`.
- **Fix:** declare the provider, or name one that exists.
- **Upstream class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E044`: type in a wiring path not declared

- **Message:** `` [CGP-E044] the type `<Name>` in a wiring path is not declared ``, with a `help` for
  a whole segment:
  `` declare or import the type `<Name>`, or write the segment in lowercase to make it a symbol ``.
- **Means:** an `@`-path in a key, or in the value a `=>` redirects to, names a type that nothing
  declares. A path segment that is not a lowercase identifier stays the type it spells, and only a
  lowercase one becomes a symbol, so a misspelled or never declared name stays a type that does not
  resolve.
- **Triggered by:** an `E0425` "cannot find type" from name resolution whose caret is an unresolved
  type inside the path spine (`PathCons`) of a `DelegateComponent` impl's key or `Delegate` type,
  found by its span in the HIR. A segment that names one component marker is `CGP-E041` instead. The
  header replaces the compiler's, and the compiler's other suggestions stay (a similarly named
  struct is a correct near miss), except the "missing a type parameter" one, which no wiring entry
  can take. The `help` is added only when nothing else says how to fix the name, and only for a type
  that is a segment by itself, since one nested in a segment's generic arguments has no lowercase
  form. A later report of the same name prints once, and an `E0275` overflow on the requirement a
  value's entry leaves unprovable is dropped as its consequence
  ([`path_segment_not_declared`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_not_declared.rs),
  [`path_segment_near_miss`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_near_miss.rs),
  [`path_segment_nested_type`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/path_segment_nested_type.rs),
  [`generic_component_path_type_checked`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/generic_component_path_type_checked.rs)).
  A type some module of the crate or a public module of a dependency declares is not in scope
  rather than undeclared, so its `E0425` is left as rustc wrote it, with rustc's import suggestion
  when it gives one
  ([`names_not_imported`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/wiring/unresolved-wiring-name/names_not_imported.rs)).
  The Rust code stays `E0425`.
- **Fix (in the `help`):** declare or import the type, or write the segment in lowercase.
- **Upstream class:** [unresolved wiring name](../cgp/errors/wiring/unresolved-wiring-name.md).

### `CGP-E050`: extensible-data operation not implemented

- **Message:** `` [CGP-E050] <cause> ``, the root cause in the sentence its tree code words
  (`` [CGP-E050] missing variant `Bar` on `Big` ``), by the rules of `CGP-E001`; the class sentence,
  used for mixed causes, is `` the trait `<Trait>` is not implemented for `<Type>` ``, naming the
  data trait (`` `CanUpcast<Big>` ``) and its subject plainly.
- **Means:** one of CGP's extensible-data operations, a cast such as `upcast` or `downcast` or a
  builder or extractor operation, is called on a value whose field or variant is not in the state
  the operation needs, or on a type that lacks the data derive it needs. The operation's trait is
  implemented only for the states where it is valid, tracked by the presence markers of the partial
  types a data derive generates, so the cause is a field or variant, named by the tree's leaf
  (`CGP-E118` to `CGP-E126`, a missing field as `CGP-E110`, or the ordinary bound an operation
  needs, such as `Port: Default` for a defaulted finalize, as `CGP-E117`).
- **Triggered by:** a call to an operation of a trait the `cgp-field` or `cgp-field-extra` crate
  defines (other than the field-access traits such as `HasField`), in scope at the call, by method
  (`builder.build_field(…)`) or by type-relative path (`Shape::from_variant(…)`), on a value the
  [data-call anchor](implementation/typed-resolution/call-site.md#calls-to-extensible-data-operations)
  types: a constructed value, or a builder, extractor, or remainder typed through the chain of data
  operations and pattern bindings that produced it. Its obligation fails as an `E0277`, an `E0271`,
  an `E0599` ("no method named", or the method-bounds shape), or an `E0308` on a tag argument (a
  variant extracted twice). The same causes reached through a check or a consumer keep that
  anchor's class (`CGP-E001`), and a `#[cgp_auto_dispatch]` call keeps `CGP-E003`. The Rust code
  stays whatever rustc assigned.
- **Fix:** follow the cause: drop a second setting of a field or extraction of a variant, set an
  unset one, add a missing variant or align a payload type, add the derive a `help` names, or call
  the method a `help` names (with the `use` it gives).
- **Upstream class:** [extensible data](../cgp/errors/data/extensible-data.md).

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
  hop through the context's own consumer-trait impl (a `CanUseComponent` step). A type that
  carries no wiring of its own is not a context, so it is named plainly:
  `` consumer trait impl `HasScalarType` for `NoScalar` ``.
- **`CGP-E102`: provider trait impl.**
  `` provider trait impl `<Trait>` with context `<Ctx>` for provider `<Provider>` ``: a hop through
  a provider's provider-trait impl (an `IsProviderFor` step). Directly above a `CGP-E115` leaf for
  the same provider, which has no such impl, the hop reads as the requirement it is,
  `` provider trait `<Trait>` required of provider `<Provider>` with context `<Ctx>` ``, under the
  same code.
- **`CGP-E103`: redirect lookup.** `` redirect lookup to `@…` in `<Table>` ``: a hop through a
  namespace or `open` `RedirectLookup<Table, Path>`, naming the table the path is looked up in: the
  context for its own `open` or `namespace`, or an aggregate provider that `open`s a component in
  its own table. Two lookups along the same route for different dispatch keys render this same text
  but are distinct nodes in the dependency graph (the key is part of a node's identity), so each
  keeps its own branch and leaf.
- **`CGP-E104`: trait impl (general).** `` trait impl `<Trait>` for `<Type>` ``: a hop through any
  other trait, such as a user's blanket trait or an ordinary bound restated as an impl, named with
  all its arguments (`` trait impl `EncodeVariants<App>` for `Sum![u64, f64]` ``). It is coded even
  though the trait itself may not be a CGP construct.
- **`CGP-E110`: missing field (leaf).** `` missing field `<f>` on `<T>` ``: the chain bottoms out on
  a context field that is genuinely absent. When the struct derives `HasField` for its other fields,
  a `help` names the field to add with the type the requirement gives it,
  `` add the field `<f>: <type>` to `<T>` ``; when the struct carries a similar field, a `help`
  names it first, `` a similar field exists on `<T>`: `<g>` ``, and a tuple struct's position
  written as a string tag (`Symbol!("0")`) gets
  `` a field of the tuple struct `<T>` is keyed by `Index<0>`, not by `Symbol!("0")` ``. The same leaf states a field an
  extensible-data builder operation names that its struct does not declare (a `build_from` source's
  field the target lacks); it then gets the near miss but no add-the-field `help`, since adding it
  can leave another field the merge never sets.
- **`CGP-E111`: unimplemented accessor (leaf).**
  `` `HasField` not derived for field `<f>` of `<T>` ``: the struct carries the field but has not
  derived `HasField` for it (the fix rides in a separate `help`,
  `` add `#[derive(HasField)]` to `<T>` ``). Several such fields on *one* struct are one mistake:
  the derive emits an impl per field, so they coalesce into a single root cause under the same code,
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
  provider is `CGP-E114`. A `help` names the entry to write,
  `` wire `<key>` to a provider in the wiring of `<Ctx>` ``, after a near miss when the context
  wires a similar key, `` a similar key exists in the wiring of `<Ctx>`: `<key>` ``.
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
  under a `CGP-E103` hop that reads `` in `ByteSink` ``. A `help` names the entry to add,
  `` add an entry for `<key>` to `<T>` ``.
- **`CGP-E115`: not a provider (leaf).** `` `<X>` is not a provider of `<T>` ``: the chain bottoms
  out on a type wired where a *provider* was expected that does not implement the provider trait at
  all. The mistake is putting a non-provider (often a request or value type) into a provider slot,
  for example `UseBasicAuth<QueryBalanceRequest>` with the endpoint handler omitted, so the request
  type sits where an `ApiHandler` belongs. Distinct from `CGP-E114`: the owner is not a table missing one
  entry, so the fix is to use an actual provider (wrap it in the handler), not to add a wiring
  entry. When an adapter type wraps the wired type into a provider of the trait, a `help` names it
  in place of the wired type, ``wire `WithProvider<ReadDisplayName>` in place of `ReadDisplayName` ``,
  with the `use` it needs when the prelude does not export it. The adapter is any impl of the
  provider trait whose `Self` is a type over one type parameter that the impl bounds by a trait
  (`WithProvider<P>`, `Promote<P>`), applied to the wired type and confirmed to hold by the
  solver; no adapter is named by its name. For two CGP core providers used where they have no impl, a
  `help` names what serves the slot: `UseFields` for a `UseField` wired to a multi-method getter
  (when the solver confirms it implements the getter for the context), and an `open` statement for
  a `UseDelegate` wired to a component that does not declare `#[derive_delegate]`
  (``dispatch with `open AreaCalculatorComponent;` and one `@AreaCalculatorComponent.Shape: <provider>` entry per type``,
  when the component's provider trait has a `RedirectLookup` impl). When the wired type is a provider of other components for
  the same context (a `Farewell` provider wired under `GreeterComponent`), a `help` says so and gives
  both ways out, ``` `SayBye` provides `Farewell`: wire it under `FarewellComponent`, or wire a provider of `Greeter` here ```.
- **`CGP-E116`: associated type mismatch (leaf).**
  `` abstract type `<assoc>` of `<Trait>` on `<Owner>` is `<actual>`, but `<expected>` is required ``:
  the chain bottoms out on an associated type the owner supplies differently from what a provider
  requires (the leaf face of the `CGP-E005` main message). It reads `associated type` in place of
  `abstract type` when the trait is not a CGP abstract-type component, and renders its required type
  through the same helper as `CGP-E112`, so a requirement that projects through another abstract
  type reads `` but `Tx<<App as HasDbType>::Db>` (`Tx<Postgres>`) is required `` here too. The
  non-`HasField` sibling of `CGP-E112`.
- **`CGP-E117`: ordinary trait bound (leaf).** `` the trait bound `<S: Trait>` is not satisfied ``:
  the chain bottoms out on an ordinary (non-CGP) trait bound, such as `f64: Eq` required of the type
  a context wires for an abstract type. The entry keeps the compiler's own wording, with a CGP empty
  list written `Product![]` where the compiler prints `Nil`. When the compiler's headline already
  states the bound, the tool keeps that headline, in the same wording, and the note carries the tree
  alone, ending at this entry.
- **`CGP-E118`: field already set (leaf).** `` field `<f>` of `<T>` is already set ``: a builder
  operation needs the field unset (a second `build_field`, or a second merge source carrying it),
  and the builder's presence marker for it is `IsPresent`. The builder of `T` is the partial type a
  data derive generates, and the chain step above names it in words
  (`` trait impl `BuildField<Symbol!("host")>` for the builder of `Config` with `host` and `port` set ``).
- **`CGP-E119`: fields not set (leaf).** `` field `<f>` of `<T>` is not set ``, or
  `` fields `<f>` and `<g>` of `<T>` are not set ``: an operation needs the fields set (a finalize,
  a `take_field`) and the builder's markers for them are not `IsPresent`.
- **`CGP-E120`: missing variant (leaf).** `` missing variant `<V>` on `<T>` ``: an operation names a
  variant the enum does not declare, as a cast between enums whose variants do not match, or a
  construction by a tag the enum lacks. A `help` names a similar variant the enum declares,
  `` a similar variant exists on `<T>`: `<W>` ``.
- **`CGP-E121`: variants not extracted (leaf).** `` variant `<V>` of `<T>` is not extracted ``: an
  extractor is finalized while its markers say it may still yield the variants, as a matcher whose
  arms leave one out does.
- **`CGP-E122`: variant type mismatch (leaf).**
  `` variant `<V>` on `<T>` has type `<actual>`, but `<expected>` is required ``: a cast between two
  enums whose variants of one name carry different payloads. The variant counterpart of
  `CGP-E112`; an `E0271` block states it as its headline.
- **`CGP-E123`: data trait not implemented (leaf).** `` `<T>` does not implement `<Trait>` ``: a
  trait only a data derive implements (`HasFields`, `HasExtractor`, `HasBuilder`, `FromVariant`)
  is unmet on a type that is not a partial value. Several on one type merge into one cause sentence
  (`` `Shape` does not implement `HasFields` and `HasExtractor` ``), and a `help` names the derives
  in one attribute when the type is a struct or enum the crate defines, of a kind each derive
  accepts: `` add `#[derive(HasFields, ExtractField)]` to `<T>` ``.
- **`CGP-E124`: variant already extracted (leaf).** `` variant `<V>` of `<T>` is already extracted ``:
  an extractor whose marker for the variant is `IsVoid`, the remainder of an extraction that did not
  yield it, is asked for it again. rustc reports it as an `E0308` on the tag argument, since only the
  other variants' impls remain.
- **`CGP-E125`: field not optional (leaf).** `` field `<f>` of `<T>` is not optional ``: an
  optional builder's operation (`set`, `set_optional`) on a field the builder holds set or unset,
  as a record's core builder does. A `help` names the conversion with the import its trait needs,
  `` call `to_optional` on the builder first to hold each field as optional, with `use cgp::extra::field::impls::ToOptional;` in scope ``,
  when the builder takes it.
- **`CGP-E126`: builder or extractor in the wrong place (leaf).**
  `` an extractor of `<T>` does not implement `<Trait>` `` (`` a builder of `<T>` … ``): a partial
  value given to an operation that needs a trait only the struct or enum itself implements, as
  `downcast` called on the remainder of an earlier downcast. A `help` names the method the partial
  value takes instead when one holds,
  `` call `downcast_fields` in place of `downcast` on an extractor, with `use cgp::core::field::impls::CanDowncastFields;` in scope ``.
- **`CGP-E127`: provider for other arguments (leaf).**
  `` `<P>` implements `<Trait>` only for `<A>`, not `<B>` ``, or
  `` `<P>` implements `<Trait>` only with `<Param> = <A>`, not `<Param> = <B>` ``: the chain bottoms
  out on a provider that implements the provider trait, but not for the arguments the wiring gives
  it. Exactly one argument differs from every impl the provider has: the context, as for a
  provider written with `#[cgp_impl(new GreetPerson)] impl Greeter for Person` and wired on
  `Robot`, or a component parameter, named as the provider trait names it, as for a pipeline stage
  that takes `u64` after one that returns `String`. Several impls join with "or", and an impl's own
  generic parameters print as `_` (`` `Input = Result<_, _>` ``). Distinct from `CGP-E115`: the
  type is a provider, so the fix is a provider for these arguments, or other arguments for this
  provider, and the cause names no `help`.
- **`CGP-E128`: wiring without `IsProviderFor` (leaf).**
  `` the wiring of `<C>` on `<X>` has no `IsProviderFor` impl ``: the context wires the component
  through a hand-written `DelegateComponent` impl, and nothing implements `IsProviderFor` for it
  beside, as `delegate_components!` does with each entry. A check of the component passes, since it
  needs only the delegate's `IsProviderFor`, but a consumer call routes through the provider blanket,
  which also needs the context's, so every call fails. When the impl is one the program wrote, a
  `help` names the entry to write instead,
  `` replace the hand-written `DelegateComponent` impl with `delegate_components! { <X> { <C>: <P> } }` ``.
- **`CGP-E129`: unbounded type parameter (leaf).**
  `` the type parameter `<T>` of `<f>` is not bounded by `<Trait>` ``: a consumer-trait method called
  on a value whose type is a type parameter of the enclosing function or impl, which does not bound
  the parameter by the consumer trait (`context.greet()` in `fn run<Context>(context: &Context)`).
  The method exists only where the parameter has the bound, so the fix is the bound, and a `help`
  names it, `` add the bound `<T>: <Trait>` to `<f>` ``. Raw rustc frames the call as a method
  probe and suggests associated-function syntax, which the block drops.

## Uncoded rewrites

These rewrites improve a diagnostic's readability without classifying its main message, so they
carry no code. They are listed here so their codelessness is a recorded decision.

**Root-cause notes and dependency chains** replace a resolved diagnostic's sub-messages with one
`root cause: …` note over the dependency chains of every recovered cause, and a `help` for each fix
the causes call for.
They accompany a coded main message or a kept rustc one; the note itself is never coded.
[The transformed diagnostic](implementation/typed-resolution/output.md) owns them.

**Obligation-note renaming** rewrites the `required for … to implement …` chain notes of an
unresolved (fallback) diagnostic to name the consumer and provider traits instead of the wiring
traits. A generated parameter such as `__Context__` is never called a context: a provider note
leaves it out, and a consumer note names it plainly. The rename runs in the driver;
[`rewrite/message.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/rewrite/message.rs)
owns the string transform.

**Path stripping** removes the module paths rustc prints in front of type names, so
`cgp::prelude::Chars` becomes `Chars` and `cgp::prelude::TryComputer::try_compute` becomes
`TryComputer::try_compute` (a trait or type before an item is not a module, so it stays), but keeps
a qualifier that tells two types apart, so `std::io::Error` beside a crate's own `Error` stays
qualified. CGP's own paths and its encoding types (`Symbol`, `Chars`, `Cons`, and the rest) always
lose their qualifier, except in a `use` statement a `help` writes, whose path the reader types
whole. It applies to every message the tool rewrote, and to a message it left alone
only when one of the resugarings below fired there; otherwise the paths stay as rustc printed them.
It only shortens a name;
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
sub-message into `` missing field `name` on `Context` `` when the diagnostic shows the context
implementing `HasField` for another field, and leaves every other clause as rustc wrote it;
[`rewrite_missing_fields`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/postprocess/missing_field.rs)
owns it.

**Method-probe advice removal** drops rustc's "this is an associated function, not a method" framing
and "use associated function syntax instead" suggestion from a consumer-method `E0599` the resolver
declined, both artifacts of CGP's `self`-less provider methods, the second actively wrong, so the
unmet wiring bound the diagnostic also names leads. rustc's other suggestions stay. It only removes
noise, adding no classification;
[`is_method_probe_advice_text`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/signals.rs)
recognizes the phrasings and the driver's emitter applies the drop.

**A misspelled `#[use_type]` import's help** replaces the compiler's suggestion to respell the alias,
which leaves the import's misspelling in place and does not compile, with a `help` naming the rename
in the import, and in each use of the alias unless the import gives an `as` alias of its own. It
applies to an `E0576` whose caret is a bare alias in an item a CGP macro generated, and keeps the
compiler's header;
[`reshape_use_type_misspellings`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/use_type_misspelling.rs)
applies it, and the class is
[unresolved imported abstract type](../cgp/errors/lowering/unresolved-imported-type.md).

## Maintaining this catalog

This catalog is bound by the same synchronization rule as the rest of the knowledge base
([cargo-cgp/AGENTS.md](AGENTS.md)): the codes are defined in the code, so this document must track
them. The constants live in the
[`code`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/code.rs)
module of the error-processing crate, and are stamped by the main-message rewrites, all rustc-free,
in that same crate. The text forms are stamped by
[`rewrite_trait_bound`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/rewrite/message.rs) and [`rewrite_wiring_overflow`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/overflow.rs),
the second taking the overflow's reason, and its `help`, from
[`wiring_overflow_reason` and `wiring_overflow_help`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/overflow.rs)
over the `WiringOverflow` the driver's walk recovers, the typed check-failure form by
[`plan_resolved`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/plan/diagnosis_plan.rs)'s
`categorized_header` (fed from the resolved failure), and the `CGP-E010`–`CGP-E014` conflict forms
by
[`plan_wiring_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/wiring.rs)
(fed from the conflict the driver's `detect::conflict` classifier recovers, one code per
`WiringConflict` shape), the `CGP-E015`–`CGP-E019`, `CGP-E060`, and `CGP-E061` structural forms by
[`plan_structural_mistake`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/structural.rs)
(fed from the `StructuralMistake` the driver's `detect::structural` detectors recover), and the
`CGP-E022` orphan form by
[`plan_orphan_conflict`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/diagnosis/orphan.rs)
(fed from the `OrphanConflict` the driver's `detect::orphan` classifier recovers). The
`CGP-E030`–`CGP-E037` and `CGP-E039` macro-mistake forms come from the wording functions in the same
crate's
[`diagnosis`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis)
module (`plan_undeclared_trait`, `plan_missing_use_provider`, `plan_cgp_impl_misuse`,
`plan_unimported_abstract_type`, `plan_undeclared_requirement`, `plan_provider_trait_in_uses`, and
`plan_provider_impl_without_macro`),
fed from the matching detectors in the driver's `detect` module, and the `CGP-E038` and
`CGP-E040`–`CGP-E044` wiring-name forms come from `plan_unresolved_wiring_name` in the same module,
fed from the driver's `detect::wiring_name` detectors. The `CGP-E1xx` dependency-tree entry codes
are stamped when a node renders: the inner chain nodes by the structured
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
