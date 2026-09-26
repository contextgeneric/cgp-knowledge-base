# CGP v0.8.0 — Grouping components with namespaces and paths

The **in-preparation announcement for the unreleased v0.8.0**, and the only forward-looking page on
the site. It builds a strong case for why flat wiring tables stop scaling and why the preset system
failed to fix it, then introduces namespaces and default implementations and stops without a
conclusion. Its first namespace snippet still shows an attribute name that was renamed during
development.

- **URL** — <https://contextgeneric.dev/blog/v0.8.0-release>
- **Source** — [blog/2026-05-10-v0.8.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/v0.8.0/blog/2026-05-10-v0.8.0-release.md),
  on the website's `v0.8.0` branch; the post is not on `main`
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

It is also unfinished. The text stops after a section on the caveats of default implementations,
with no conclusion and no migration guide, and an empty "Introducing cargo-cgp" heading sits at the
top of the body. It carries at least one uncorrected typo ("humen eyes"), and its opening sentence
claims the release has already happened.

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
aggregate provider, with the payoff that a two-entry wiring for `ProductionApp`, `TestApp`, and
`LocalApp` makes the differences between them readable at a glance. A section on default
implementations then defines a custom namespace, `DefaultAppComponents`, that inherits
`DefaultNamespace`, binds providers into it with `#[default_impl]` and with a `cgp_namespace!` block,
and wires a `ProductionApp` that names only its content filters. It closes with the caveats: a default
cannot be opted out of without leaving the namespace, and defaults suit a single-crate application.

The post's code follows the `web-app` crate of cgp-examples, which the post does not link. Where each
section's code lives in that crate is recorded in its
[project section](../../projects/cgp-examples/web-app/README.md#where-the-blog-posts-code-lives).

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

The draft's prefix attributes do not compile, and its prose disagrees with its own code in two
places. Its contexts, aggregate providers, and default-implementation code use current syntax, and
the namespace and default-implementation snippets match the `web-app` crate apart from the prefixes.

- **The prefix attribute is written without its namespace.** The first snippet shows
  `#[namespace(@app.core.user)]`, a name the attribute had during development, while the text
  beside it calls the attribute `#[prefix]`; the later snippets write `#[prefix(@app.core.user)]`.
  Neither compiles: a probe got ``cannot find attribute `namespace` in this scope`` for the first
  and ``unexpected end of input, expected `in` `` for the second. The current form names the target
  namespace, `#[prefix(@app.core.user in DefaultNamespace)]`; see
  [`#[prefix]`](../../cgp/reference/attributes/prefix.md).
- **The content-filter prefix is given two ways.** The text assigns `@app.core.content_filter` to
  `UsernameCensor` and `SpamMessageDetector`, but every wiring snippet routes them under
  `@app.extra.content_filter`, which is the path the crate uses.
- **The draft does not mention the `for` statement**, which merges several namespaces into one
  table and is part of the shipped namespace feature.
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
  writes `delegate_components! { ProductionApp { ... } }`, wiring the wrong context. Neither struct in
  that section derives `HasField`, which the providers' implicit `database` arguments need, though
  the earlier `ProductionApp` does.

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
