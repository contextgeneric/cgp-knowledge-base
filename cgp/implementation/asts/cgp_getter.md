# The `cgp_getter` and `cgp_auto_getter` AST stack

This stack covers the two getter macros together, because they share the getter-field parsing and the field-mode conversions and differ only in what they emit around a common getter-method body. `#[cgp_auto_getter]` parses a trait into `ItemCgpAutoGetter` and emits one blanket impl; `#[cgp_getter]` reuses the whole `#[cgp_component]` pipeline to produce an `EvaluatedCgpComponent`, wraps it in `ItemCgpGetter`, and appends three field-reading provider impls. Both feed on the shared `GetterField` parser and the `getter/` field-mode types. The two [entrypoint documents](../entrypoints/cgp_getter.md) cover what each stage produces; this document covers the types.

## Shared getter-field parsing: `GetterField` and `parse_getter_fields`

Both macros turn a getter trait's methods into `GetterField`s through the shared `parse_getter_fields` helper, which is the single source of truth for what a getter signature means. A `GetterField` records the field name (the method name), the field type to require, the return type, the receiver mutability, an optional `PhantomData` phantom-argument type, the field mode, and the receiver mode.

The parser enforces the getter-method contract. A getter must be a plain method (not `const`, `async`, `unsafe`, or generic) whose first argument is a reference: either `&self`/`&mut self` (`ReceiverMode::SelfReceiver`) or a typed receiver such as `foo: &Self::Foo` (`ReceiverMode::Type`), which reads the field out of that type instead of the context, with `Self` rewritten to the context.

The return type decides the field type and the *field mode*, the conversion the body applies, through the shared `parse_field_type`:

| Return type | Field type | `FieldMode` | Conversion |
|---|---|---|---|
| `&str` | `String` | `Str` | `.as_str()` |
| `Option<&T>` | `Option<T>` | `OptionRef` | `.as_ref()` |
| `Option<&str>` | `Option<String>` | `OptionStr` | `.as_deref()` |
| `&[T]` | any `AsRef<[T]>` | `Slice` | `.as_ref()` |
| `MRef<'_, T>` | `T` | `MRef` | `MRef::Ref(...)` |
| `&T` | `T` | `Reference` | none |
| any owned type | the type | `Copy` | `.clone()` |

`parse_field_type` also returns an `Option<Mut>` taken from a `&mut` in the type itself (the outer reference of `&mut T` or `&mut [T]`, or the inner one of `Option<&mut T>`), which selects the `HasFieldMut`/`get_field_mut` read and the mutable conversions (`.as_mut_str()`, `.as_mut()`, `.as_deref_mut()`, or an `AsMut<[T]>` bound). A mutable return requires a `&mut self` receiver. The `#[implicit]` extraction in the [`cgp_fn` stack](cgp_fn.md) keeps that type-derived mutability, but a getter discards it and keys the read off its receiver, which is the source of the `Option<&T>`-under-`&mut self` defect under Known issues.

`parse_getter_fields` also extracts an optional single associated return type and checks that, when present, the trait has exactly one method whose return type is that type.

The getter-method body itself is built by `derive_getter_method` from the `types/getter/` module, which emits `receiver.get_field(PhantomData::<Tag>) <conversion>` for the field's mode. The conversion suffix is chosen by `FieldMode::apply`, the single function that maps a field mode and mutability to the trailing `.as_str()`/`.as_ref()`/`MRef::Ref(...)`/etc.; the `#[implicit]` bindings in the [`cgp_fn` stack](cgp_fn.md) reach the same function through `GetFieldWithModeExpr`, which is why the two families convert fields identically.

## `ItemCgpAutoGetter`

`ItemCgpAutoGetter` is the whole AST for `#[cgp_auto_getter]`: a single struct holding the cleaned trait. Its `preprocess` associated function strips the CGP modifier attributes off the trait (discarding them, since the auto getter has no component to configure) and keeps the trait; there is no multi-stage pipeline because the macro emits no component.

Its `to_items` emits the trait unchanged plus one blanket impl, built by `to_blanket_impl`, which calls `derive_blanket_impl`. That impl fixes the context type to `__Context__`, adds each getter method reading its like-named field, and requires the corresponding `HasField` bound; a trait supertrait becomes a `__Context__: Supertrait` predicate, a trait generic parameter is preserved onto the impl, and a single associated return type is added as an extra parameter set to itself with its bounds carried over. The shape of the emitted impl is shown in the [entrypoint document](../entrypoints/cgp_auto_getter.md).

## `EvaluatedCgpComponent` (reused) and `ItemCgpGetter`

`#[cgp_getter]` produces no getter-specific parse stage of its own; it drives the `#[cgp_component]` pipeline to an `EvaluatedCgpComponent` (documented in the [`cgp_component` AST stack](cgp_component.md)) and then wraps that in `ItemCgpGetter`. The `TryFrom<EvaluatedCgpComponent>` conversion is where the getter fields are parsed: it runs `parse_getter_fields` over the consumer trait and stores the resulting `GetterField`s and optional associated type alongside the evaluated component.

`ItemCgpGetter`'s `to_items` emits the component's own items first (the five core items plus the standard `UseContext`/`RedirectLookup` provider impls) and then appends the three getter-specific provider impls, each carrying its own `IsProviderFor` impl:

- `to_use_fields_impl` builds the `UseFields` impl, keyed by method name: for each field it emits the getter-method body reading `Symbol!("field_name")` and requires the matching `HasField` bound on the receiver type. Always emitted.
- `to_use_field_impl` builds the `UseField<__Tag__>` impl, where `__Tag__` is a *free* generic parameter added to the impl generics, so the getter reads whatever field the wiring supplies. Emitted only for a single-getter trait.
- `to_with_provider_impl` builds the `WithProvider<__Provider__>` impl, which delegates field access to an inner `FieldGetter`/`MutFieldGetter` provider (a slice field uses an `AsRef<[T]>`-valued bound, or `AsMut<[T]>` for a mutable slice). Emitted only for a single-getter trait.

Each of these threads the optional associated type through as an extra generic parameter, exactly as the auto-getter blanket impl does, keeping the three impls consistent with the consumer trait.

## Known issues

`GetterField` in `types/getter/method.rs` chooses the option conversion from the receiver's mutability rather than from the return type's, so a `&mut self` getter returning a shared `Option<&T>` or `Option<&str>` emits `.as_mut()` or `.as_deref_mut()` and fails with `E0308`. Both getter macros share the defect; it is described with its fix in [entrypoints/cgp_auto_getter.md](../entrypoints/cgp_auto_getter.md#known-issues).

`ItemCgpAutoGetter::preprocess` discards the collected attributes, so `#[prefix]` and `#[derive_delegate]` on a `#[cgp_auto_getter]` trait are dropped without an error, as the same document records.

## Tests

- The stage transforms are exercised end to end by the expansion snapshots indexed in the two entrypoint documents: the [`#[cgp_getter]` snapshots](../entrypoints/cgp_getter.md#snapshots) and the [`#[cgp_auto_getter]` snapshots](../entrypoints/cgp_auto_getter.md#snapshots).
- [parser_rejections/getters.rs](https://github.com/contextgeneric/cgp/blob/main/crates/tests/cgp-macro-tests/tests/parser_rejections/getters.rs) pins the getter-method contract checks in `parse_getter_fields`, driven through the shared `cgp_auto_getter` entrypoint: it rejects const, async, unsafe, and generic getter methods, a by-value `self` receiver, a `&mut` return under a `&self` receiver, more than one associated type, an associated type alongside a second method, and a non-getter trait item, plus `#[cgp_auto_getter]`'s rejection of any attribute argument.

## Source

- The auto-getter stack lives in [cgp-macro-core/src/types/cgp_auto_getter/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_auto_getter/) (`item.rs`, `blanket.rs`), driven by [cgp-macro-lib/src/cgp_auto_getter.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_auto_getter.rs) and documented in [entrypoints/cgp_auto_getter.md](../entrypoints/cgp_auto_getter.md).
- The full-getter stack lives in [cgp-macro-core/src/types/cgp_getter/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/cgp_getter/) (`item.rs`, `getter_field.rs`, `to_use_fields_impl.rs`, `use_field.rs`, `with_provider.rs`), driven by [cgp-macro-lib/src/cgp_getter.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-lib/src/cgp_getter.rs) and documented in [entrypoints/cgp_getter.md](../entrypoints/cgp_getter.md); it reuses the [`cgp_component` stack](cgp_component.md).
- The shared getter-field parser is in [cgp-macro-core/src/functions/getter/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/getter/parse.rs), the field-mode conversion in [cgp-macro-core/src/functions/field/parse.rs](https://github.com/contextgeneric/cgp/blob/main/crates/macros/cgp-macro-core/src/functions/field/parse.rs), and the field-mode and getter-method emit types in [cgp-macro-core/src/types/getter/](https://github.com/contextgeneric/cgp/tree/main/crates/macros/cgp-macro-core/src/types/getter/).
