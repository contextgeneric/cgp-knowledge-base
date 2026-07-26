# CGP v0.8.0 — Grouping components with namespaces and paths

The **in-preparation announcement for the unreleased v0.8.0**, and the only forward-looking page on
the site. It builds a strong case for why flat wiring tables stop scaling and why the preset system
failed to fix it, then introduces namespaces and stops mid-argument — and the attribute syntax it
teaches was renamed twice during development.

- **URL** — <https://contextgeneric.dev/blog/v0.8.0-release>
- **Source** — [blog/2026-05-10-v0.8.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/2026-05-10-v0.8.0-release.md)
- **Dated** — 10 May 2026, tagged `release`; the date is a placeholder and must be set to the real
  release date before v0.8.0 ships
- **Documents** — [releases/v0-8-0.md](../../releases/v0-8-0.md)
- **Status** — **Draft**, for an unreleased version

## Why this one is different

Every other post on the site is a finished artifact whose only defect is age. This one is neither
finished nor about a shipped release.

It was **drafted as the v0.7.1 announcement**, when namespaces were expected to be a minor addition.
The work grew — namespaces required a new path system, the `open` statement, per-type defaults, and
ultimately the removal of the entire preset mechanism — so the release was renumbered to **v0.8.0**,
which is still in development at `0.8.0-alpha`. There is no v0.7.1 tag and there will not be one; the
last shipped release is [v0.7.0](../../releases/v0-7-0.md). Anything in the base that attributes
namespaces to "v0.7.1" is wrong.

It is also unfinished. The git history shows it built up over several commits ending at "Add
hierarchical delegation section," and the text stops after a paragraph comparing three contexts, with
no conclusion, no migration guide, and no coverage of the custom namespaces it promises earlier ("as
we will see in later sections"). It carries at least one uncorrected typo ("humen eyes"), and its
opening sentence claims the release has already happened.

The rule in [../AGENTS.md](../AGENTS.md) against rewriting published posts therefore does **not**
apply here. A draft for an unreleased version is live work, and editing it is the expected activity
rather than a violation — indeed finishing it is part of preparing the release.

## What it covers

The post is at its best in its motivation, which is the fullest published argument for CGP's
scalability problem. It builds a social-media backend with coarse `CanManageUser` and `CanManagePost`
traits, adds content-filtering dependencies, and then splits the coarse traits into fine-grained
per-operation ones — showing that fine-grained traits let a dependency like `CanCensorUsername` reach
only the one provider that needs it, and that higher-order providers can lift the filtering out into
`FilterCensoredUsername<CreateUserWithPostgres>` so the database provider does nothing but build SQL.
Then it counts the cost: nine wiring entries for a deliberately minimal application, and "dozens if
not hundreds" for a real one, which to an untrained reader is noise that obscures what the context
actually does.

It then explains why the obvious fixes fail. Array keys group entries but cannot *name* a group. Rust
cannot express "implement `DelegateComponent` for this list of types," and a macro expanding to a key
list will not work because macros expand lazily, so `delegate_components!` would see the unexpanded
call. And presets, the previous answer, support only single inheritance into a context because of
coherence, while their macro-based multiple inheritance is fragile precisely because macros cannot see
types.

The namespace introduction that follows shows components tagged with a hierarchical path prefix, a
context opting in with a `namespace` statement, and `@`-path keys bulk-delegating a whole group to an
aggregate provider — with the payoff that a three-line wiring for `ProductionApp`, `TestApp`, and
`LocalApp` makes the differences between them readable at a glance. Then it stops.

## How it relates to the knowledge base

The feature is [namespaces](../../cgp/concepts/namespaces.md), documented per construct as
[`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md),
[`RedirectLookup`](../../cgp/reference/providers/redirect_lookup.md),
[`Path!`](../../cgp/reference/macros/path.md), and
[`DefaultNamespace`](../../cgp/reference/traits/default_namespace.md), with the `namespace` and
`@`-path statements in
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md). The prescriptive
counterpart — how to actually refactor a growing table — is
[namespaces-and-prefixes](../../cgp/guides/namespaces-and-prefixes.md), which is the document to write
from. The release as a whole is tracked in [releases/v0-8-0.md](../../releases/v0-8-0.md), which lists
everything else v0.8.0 carries that this draft does not yet mention.

The running example is essentially the
[social media app example](../../examples/social-media-app.md), which follows the same arc from coarse
manager traits through fine-grained traits and higher-order providers to namespace-grouped wiring, in
current syntax. The intermediate steps map to
[impl-side dependencies](../../cgp/concepts/impl-side-dependencies.md),
[higher-order providers](../../cgp/concepts/higher-order-providers.md), and
[aggregate providers](../../cgp/concepts/aggregate-providers.md).

For the communication strategy, the motivation section is a strong asset. The "nine entries and
climbing" demonstration is a real, self-inflicted pain narrated honestly, which is what
[message.md](../../communication-strategy/message.md#the-problems-cgp-removes) asks for; and admitting that
presets were tried and did not work is exactly the candour
[message.md](../../communication-strategy/message.md#the-objections-readers-bring) argues buys credibility. It also speaks
directly to the "verbose / over-engineered" reflex recorded in
[evidence.md](../../communication-strategy/evidence.md) — a post that
concedes the verbosity and then fixes it is better positioned than one that denies it.

## Where it diverges from the feature as built

The syntax was renamed twice after this draft was written, so its namespace code does not compile.

- **`#[namespace(@app.core.user)]` is now `#[prefix(@app.core.user in SomeNamespace)]`.** The
  attribute went from `#[use_namespace]` to `#[namespace]` and finally to `#[prefix]` during
  development, and it now names the target namespace explicitly; see
  [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md).
- **`namespace default;` is now `namespace <Name>;`.** A context joins a *named* namespace defined
  with [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md); there is no `default`
  keyword. This is presumably what the unwritten later sections would have covered.
- **The draft does not mention `cgp_namespace!` at all**, nor namespace inheritance, per-type
  defaults via `#[default_impl(...)]`, or the lightweight `open` statement that handles per-type
  dispatch without a full namespace. All are part of the shipped feature.
- **It does not mention that presets are removed.** v0.8.0 deletes `cgp_preset!`,
  `#[cgp::re_export_imports]`, and `#[cgp_inherit]` outright, which is the release's largest breaking
  change and needs a migration guide the draft does not have.
- **It covers only one of the release's features.** [releases/v0-8-0.md](../../releases/v0-8-0.md)
  lists the rest — the `open` statement, `#[impl_generics]`, the `#[use_type]` separator change from
  `::` to `.`, the adoption of [`cargo-cgp`](../../cargo-cgp/README.md), and the move of all
  documentation into this knowledge base — none of which appear here.
- **The wiring examples omit checking.** A context wired this way should carry a
  [`check_components!`](../../cgp/reference/macros/check_components.md) assertion, and namespaces
  introduce their own failure modes — see
  [unregistered-namespace-path](../../cgp/errors/checks/unregistered-namespace-path.md),
  [namespace-override-conflict](../../cgp/errors/wiring/namespace-override-conflict.md), and
  [namespace-inheritance-cycle](../../cgp/errors/wiring/namespace-inheritance-cycle.md).
- **`delegate_and_check_components!` is used on `ProductionApp`**, which is correct for that simple
  case, but the later aggregate providers (`PostgresUserComponents`) are correctly wired with plain
  `delegate_components!` — a distinction the draft never explains and that
  [aggregate providers](../../cgp/concepts/aggregate-providers.md) covers.
- **One copy-paste error in the source:** the `TestApp` section defines the struct `TestApp` but then
  writes `delegate_components! { ProductionApp { ... } }`, wiring the wrong context.

## Maintaining it

This post has to be finished before v0.8.0 ships, and the material for it already exists. Write the
namespace sections from [namespaces](../../cgp/concepts/namespaces.md) and the
[namespaces-and-prefixes guide](../../cgp/guides/namespaces-and-prefixes.md); take the worked
progression from the [social media app example](../../examples/social-media-app.md); take the rest of
the release's contents and its breaking changes from
[releases/v0-8-0.md](../../releases/v0-8-0.md); and keep the motivation section as it stands, since it
is the best part of the draft and needs no change.

Four mechanical items go with it. The **placeholder date** in the filename must become the real
release date, which also sets the post's URL and its position in the blog index. The **announcement
bar** in `docusaurus.config.ts` still promotes v0.7.0 and must be repointed, per
[site-structure.md](../site-structure.md). The **opening sentence** claims the release has already
happened and must not go out before it has. And the [Introduction page](../site-structure.md), which
tells readers that posts from v0.7.0 onward are the most current material, should be re-checked once
this one exists.

The [launch-post playbook](../../communication-strategy/formats.md) governs the finished result, and
because this is a major release with breaking changes, its migration guide should follow the shape the
[v0.7.0 post](v0-7-0-release.md) used — each change stated with its before and after, and a plain
statement of what a reader must do.
