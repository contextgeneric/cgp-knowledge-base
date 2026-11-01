# Typed resolution: the transformed diagnostic

A resolved failure's diagnostic is rebuilt from three parts: a coded headline, one `root cause:`
note, and the fix `help`s. The wording is decided in the rustc-free crate from the `Resolved` model
and only applied by the emitter. [The anchors](typed-resolution-anchors.md) and
[the walk](typed-resolution-walk.md) produce the causes worded here, and
[error-code.md](../error-code.md) catalogs every code with its example.

## The coded headline

**The class comes from the anchor, never from the bound rustc's headline stopped on,** because that
bound may be dispatch plumbing or a provider deep in the chain, which the programmer never asserted
on. The Rust error code (`E0277`, `E0599`, `E0271`) is always kept. Each class has a class sentence,
naming the trait off its `DefId`, so it stays exact when two components share a name:

| Code | Class | Class sentence |
| --- | --- | --- |
| `[CGP-E001]` | A context that cannot implement a consumer trait | `` the consumer trait `C` is not implemented for context `X` `` |
| `[CGP-E002]` | A `#[check_providers]` entry, or a provider's method called directly | `` the provider trait `P` with context `X` is not implemented for provider `Q` `` |
| `[CGP-E003]` | A trait that is no consumer: a hand-written wrapper or a blanket trait | `` the trait `W` is not implemented for … `` |
| `[CGP-E004]` | An `E0271` traced to a `HasField` projection | none: the cause is the headline |
| `[CGP-E005]` | An `E0271` traced to any other associated type | none: the cause is the headline |
| `[CGP-E050]` | A call to an extensible-data operation | as `[CGP-E003]` |

`[CGP-E003]` and `[CGP-E050]` name a foreign subject, or one that carries no wiring, plainly rather than
calling it a context. A data cause reached through a check or a consumer keeps that anchor's class.

**The displayed headline states the causes the note lists, by three rules:**

- **One cause** reads as itself, in the same sentence the `root cause:` line and the tree's last
  entry use.
- **Several causes of one kind on one owner** are stated together: fields missing from a struct
  (`` missing fields `first_name` and `last_name` on `Person` ``), wiring missing from a context,
  entries missing from a table, or data traits a type lacks. A list longer than four names its first
  three and counts the rest, while the note lists every cause
  ([`many_missing_fields`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/many_missing_fields.rs)).
- **Mixed causes** keep the class sentence with their count:
  `` [CGP-E001] the consumer trait `CanCalculateVolume` is not implemented for context `Shape`: 2 root causes ``.

Causes are listed in the order the walk reached them, which is
[the order the program wrote them](typed-resolution-walk.md#walking-the-dependency-graph-downward).
The class sentence also stays as the block's internal headline for the de-duplication ledger, since
a re-report the resolver declined carries that wording from the text rewrite.

**A mismatch's headline is unusually specific.** Here `HasField<Symbol!("height")>` holds, since
`Rectangle` derives it, but with `Value = i32`, so only the projection fails. The resolver reads the expected
type from the projection and the actual type off the struct:

```rust
#[cgp_impl(new RectangleArea)]
impl AreaCalculator {
    fn area(&self, #[implicit] width: f64, #[implicit] height: f64) -> f64 {
        width * height
    }
}

#[derive(HasField)]
pub struct Rectangle {
    pub width: f64,
    pub height: i32, // `RectangleArea` needs `f64`
}
```

```text
error[E0271]: [CGP-E004] field `height` on `Rectangle` has type `i32`, but `f64` is required
  --> src/main.rs:47:9
   |
47 |         AreaCalculatorComponent,
   |         ^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: this is required through the dependency chain:
             [CGP-E101] consumer trait impl `CanCalculateArea` for context `Rectangle`
             └─ [CGP-E102] provider trait impl `AreaCalculator` with context `Rectangle` for provider `RectangleArea`
               └─ [CGP-E112] field `height` on `Rectangle` has type `i32`, but `f64` is required
```

An `E0271` traced to anything else is a consequence rather than a mismatch: a `Send`-recovery
wrapper's opaque future, say, whose `type mismatch resolving …` is unreadable. It takes the anchor's
class
([`foreign_wrapper_chain`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/duplication/foreign_wrapper_chain.rs)).

**rustc's headline survives in two cases:**

- **It states a recovered leaf,** such as an ordinary bound like `f64: Eq` the solver descended to,
  so it already names the cause. The one change is an empty list, which rustc prints as `Nil` or
  `Void` and the leaf writes `Product![]` or `Sum![]`, so the headline takes the leaf's wording,
  uncoded
  ([`constrained_delegate_key`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/constrained-key/constrained_delegate_key.rs),
  [`constrained_delegate_key_empty_sum`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/constrained-key/constrained_delegate_key_empty_sum.rs)).
- **It is no trait bound and names no class,** such as an unrelated `E0308`.

A headline that states a mid-chain symptom, an ordinary bound that is no recovered leaf, is
replaced: naming the trait the context fails to implement is truer than leaking the symptom.

## The root-cause notes

**rustc's sub-messages are always replaced, and a failure gets one note however many causes it
has.** Every cause's paths fold into one [dependency graph](dependency-graph-rendering.md), which
merges the nodes they share and branches where they diverge. This collapses the long prefix a
program-sized context type would otherwise repeat. The heading is a singular `root cause:` when all
paths end on one leaf, or a `root causes:` list when they differ.

The chain repeats the root cause as its own last entry, so it always ends at the cause. A branch
[elided against an earlier block](dependency-graph-rendering.md#eliding-across-blocks) keeps that
end too, and a note with no chain names the cause in its lead. Paths render as a bare
`@app.GreeterComponent`, and module qualifiers are stripped except where they tell two types apart,
as [Resugaring](resugaring.md#the-path-strips-that-run-first) describes.

A lead is worded by why its leaf is unmet.
[The leaf shapes](typed-resolution-leaves.md#the-leaf-shapes) decide which leaf a bound is, and
these are the readings a reader meets:

| Leaf | Code | Reads as |
| --- | --- | --- |
| Absent field | `CGP-E110` | `` missing field `height` on `Rectangle` `` |
| Field without the derive | `CGP-E111` | `` `HasField` not derived for field `name` of `Person` `` |
| Field of the wrong type | `CGP-E112` | `` field `height` on `Rectangle` has type `i32`, but `f64` is required `` |
| Missing wiring, by marker or path | `CGP-E113` | `` missing wiring for `BarProviderComponent` on `App` `` |
| Missing dispatch entry | `CGP-E114` | `` missing entry for `Tagged<Bytes>` in provider `SinkHandlers` `` |
| Not a provider | `CGP-E115` | `` `NotAGreeter` is not a provider of `Greeter` `` |
| Abstract-type mismatch | `CGP-E116` | `` abstract type `Error` of `HasErrorType` on `App` is `String`, but `AppError` is required `` |
| Ordinary bound | `CGP-E117` | `` the trait bound `f64: Eq` is not satisfied `` |
| Provider for other arguments | `CGP-E127` | `` `GreetPerson` implements `Greeter` only for `Person`, not `Robot` `` |
| Wiring without `IsProviderFor` | `CGP-E128` | `` the wiring of `GreeterComponent` on `App` has no `IsProviderFor` impl `` |
| Unbounded type parameter | `CGP-E129` | `` the type parameter `Context` of `run` is not bounded by `CanGreet` `` |

The extensible-data leaves, `CGP-E118` to `CGP-E126`, name the struct or enum rather than the
generated type: `` field `port` of `Config` is not set ``.

These corners of the wording are easy to break:

- **Several underived fields on one struct are one mistake,** since the derive emits an impl per
  field, so they coalesce into one cause over a tree that still ends at each field
  ([`base_area_2`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/base_area_2.rs)).
  An underived field beside a missing one, or on another struct, stays apart
  ([`underived_and_missing_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/underived_and_missing_field.rs)).
- **An intermediate consumer reads `consumer trait impl`** (`CGP-E101`), since the walk descends the
  real trait a provider `#[uses]`, rather than the `trait impl` (`CGP-E104`) a getter gets.
- **A missing redirect reads the same whether it came from a namespace or from `open`,** with the
  whole path as the key rather than its flattened item name, and each `RedirectLookup` hop names its
  own table
  ([`multi_redirect_missing`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/multi_redirect_missing.rs),
  [`open_aggregate_missing_entry`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/missing-wiring/open_aggregate_missing_entry.rs)).
- **The step above a not-a-provider leaf reads as a requirement,**
  ``provider trait `Greeter` required of provider `NotAGreeter` with context `App` ``, rather than as the impl
  the provider lacks.
- **A provider for other arguments names no fix,** since only the reader knows whether the wiring or
  the provider should change. Several impls join with "or", and an impl's own generic parameters
  print as `_`.
- **An associated type outside CGP reads `associated type` and carries no `help`,** since no wiring
  entry fixes it
  ([`plain_assoc_type_mismatch`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/types/plain_assoc_type_mismatch.rs)).

**A lead is dropped only where the headline was worded from that very leaf:** a mismatch class, a
variant payload of the wrong type, or a kept rustc headline restating the ordinary bound. Every
other block keeps its `root cause:` line, even though its headline states the same cause, so the
tree sits under a line naming where it ends. The test is what the header was worded from, not the
kind of leaf.

## The fix `help`s

**A `help` appears only when its premise holds, because a fix that does not compile is worse than
none.** A resolved block ends with a `help` for each fix, after the note, and the fixes of one kind
on one owner merge into one `help` with no cap. `fix_help_messages` builds them, for the per-block
plan and for the emitter's coalesced block alike, so a merged block carries the same fixes. These
premises guard them:

- **A missing field** gets a `help` only when its struct has named fields and derives `HasField` for
  another field. A tuple struct cannot gain a named field, and a struct with no `HasField` impl may
  lack the derive as well, since a fieldless struct's derive generates nothing
  ([`tuple_struct_named_field`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/fields/tuple_struct_named_field.rs),
  [`check_providers_unwired_provider`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/providers/check_providers_unwired_provider.rs)).
  The type comes from the `Value = T` constraint beside the requirement, and is named only when
  every route to the field agrees.
- **A key holding a reference or a lifetime** gets no `help`, since the compiler erased the lifetime
  and the entry cannot be pasted as written
  ([`higher_ranked_descent`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/check-trait-failure/resolution/higher_ranked_descent.rs)).
- **A missing data trait's derive** is offered only for a struct or enum the crate defines, of a
  kind each derive accepts.
- **A method for a builder or extractor in the wrong place, and an adapter or another component for
  a non-provider,** are each confirmed by the solver against the same value and context. A `help`
  that needs an import names the `use`, because the data traits are outside the prelude and the
  compiler's own suggestion names a crate path that does not compile.
- **A near miss** comes first, and its candidates are only the struct's own fields, the enum's own
  variants, or the context's own wiring, so a slip another context wires is never named
  ([`near_miss_in_another_context`](https://github.com/contextgeneric/cargo-cgp/blob/main/tests/ui/checks/unregistered-namespace-path/near_miss_in_another_context.rs)).
  A name is similar when it matches ignoring case or lies within two edits. A key is similar when
  one symbol segment is, or when it has one prefix segment more or fewer. Two type segments that
  differ name two types, so they never count.

A field-type mismatch, an ordinary bound, and the extensible-data state causes carry no `help`: the
headlines already state both types, a state cause names what to handle, and the others have no
single entry to name. A field a builder names that its struct lacks gets none either, since a merge
can still leave another field unset.

## Emitting the transformed diagnostic

The emitter maps the rustc code to a rustc-free `DiagKind` (`E0271` a projection mismatch, `E0599` a
use-site method, anything else a plain check) and calls `plan_resolved`, which returns the displayed
header (or `None` to keep rustc's), the class header, the `help`s, and an unrendered note. A
resolution anchored at the call plans as a use-site failure whatever its code, except an `E0271`, so
its class is the trait the call needs.

`transform_resolved` then edits rustc's `DiagInner`. With a header it replaces the main message and
collapses the span to the primary caret, since the original labels restate the replaced message. In
every case it replaces the children with the `help`s and discards rustc's structured suggestions,
and it never touches the Rust code. The note waits for the flush, because its graph depends on what
earlier notes drew, and then goes ahead of the `help`s, so each fix follows the cause it repairs.
The JSON emitter regenerates every field from the `DiagInner`.

When rustc's headline is an `IsProviderFor` bound, the plan also keeps the provider form the text
rewrite gives it, because a declined re-report of the same failure carries that wording and the
de-duplication ledger records both. This is the one place the text rewrite's name map serves a
resolved diagnostic. A final de-duplication suppresses a block that re-reports a failure already
shown, and the flush coalesces the blocks that share a root cause, as
[Diagnostic reshapes](diagnostic-reshapes.md) and [The driver](driver.md) describe.

## Further reading

- [Typed root-cause resolution](typed-root-cause-resolution.md): the pipeline overview and the
  consolidated tests and source catalogs.
- [Error processing](error-processing.md): the rustc-free crate the wording lives in.
- [The driver](driver.md): the emitter, its de-duplication ledger, and the fallback text rewrite.

## Tests

- [`tests/error_processing/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/tests/error_processing/diagnosis):
  the class headers, the displayed headlines (`headline.rs`), the notes, and the `help`s
  (`helps.rs`), over hand-built inputs with no compiler.
- [`tests/error_processing/coalesce.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/coalesce.rs):
  the underived-field coalescing and its boundaries.
- [`tests/error_processing/graph.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/graph.rs)
  and
  [`tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/tests/error_processing/tree.rs):
  the graph and the renderer.
- [The parent document's catalog](typed-root-cause-resolution.md#tests): the fixture groups end to
  end.

## Source

- [`cargo-cgp-error-processing/src/diagnosis/`](https://github.com/contextgeneric/cargo-cgp/tree/main/crates/cargo-cgp-error-processing/src/diagnosis):
  the model (`leaf/`, `resolved.rs`), the nodes and graph (`node.rs`, `graph.rs`), the wording
  (`wording/`), the coalescing (`coalesce.rs`), and the plan (`plan/`).
- [`cargo-cgp-error-processing/src/tree.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-error-processing/src/tree.rs):
  the renderer the graph expands into.
- [`emitter/stage/resolver.rs`](https://github.com/contextgeneric/cargo-cgp/blob/main/crates/cargo-cgp-driver/src/emitter/stage/resolver.rs):
  `transform_resolved`, which applies the plan.
