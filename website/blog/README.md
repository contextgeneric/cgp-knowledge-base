# Website blog posts

This directory holds one internal document per post published on the
[CGP blog](https://contextgeneric.dev/blog). Each document records what its post covers, which
knowledge-base material owns that content, and — crucially — exactly how the post's code and claims
diverge from CGP as it stands at v0.8.0. Read [../README.md](../README.md) for why this section exists
and [../AGENTS.md](../AGENTS.md) for the rules that govern it, including the prohibition on rewriting
a published post into agreement with the current library.

## Why the drift matters more here than anywhere else

The blog is the site's largest and most-read body of writing, and it is also the least current. The
[Introduction page](https://contextgeneric.dev/docs/) still directs newcomers to the blog as the most
up-to-date resource, so a reader following that advice lands on posts teaching syntax the compiler no
longer accepts. Of the seventeen posts, eight write every provider inside-out with
`#[cgp_provider]`/`#[cgp_new_provider]`, seven show `#[cgp_context]` on a context definition, and four
use the removed `Async` trait or one of its aliases. The posts remain valuable — their *ideas* are
current even where their *code* is not, and several are the only prose anywhere on the design
questions they work through — but they can only be mined safely by an agent who knows which parts are
dead.

Each document below therefore carries a "Where it diverges from CGP v0.8.0" section listing the
concrete constructs, names, and claims that no longer hold, with what replaced each. Read that section
before quoting a post's code anywhere, and never take current syntax from a post.

## The catalog

The posts are listed in publication order, oldest first, which is also roughly the order of increasing
reliability. Each entry gives the post's slug, its date, and a one-line summary; the status word is
the section's fixed vocabulary from [../AGENTS.md](../AGENTS.md).

- [Announcing Context-Generic Programming](early-preview-announcement.md) — 2024-12-19, *historical*.
  The launch post: what CGP is, how it grew out of the Hermes relayer, and a plan for 2025 whose items
  have since been resolved in ways the post could not anticipate.
- [CGP v0.3.0 release](v0-3-0-release.md) — 2025-01-09, *historical*. Abstract types via the
  now-removed `cgp_type!` function macro, the first getter macros, `CanWrapError`, and the
  `cgp-error-anyhow` and `cgp-runtime` crates.
- [CGP v0.4.0 release](v0-4-0-release.md) — 2025-05-09, *historical*. The release that made CGP
  debuggable: `IsProviderFor`, `CanUseComponent`, `check_components!`, plus `#[cgp_context]`, the
  preset system, and the first datatype-generic support.
- [CGP v0.4.1 release](v0-4-1-release.md) — 2025-06-14, *historical*. The `cgp-handler` crate
  introducing `Handler`, `Computer`, and `Producer`, and preset improvements built for Hypershell.
- [Hypershell: a type-level DSL for shell-scripting](hypershell-release.md) — 2025-06-14,
  *historical*. The longest post on the site and still the fullest account of building a DSL whose
  programs are types; also the site's best standalone introduction to CGP's wiring model.
- [Extensible data types, part 1: builders](extensible-datatypes-part-1.md) — 2025-07-07,
  *historical*. Extensible records, safe enum upcasting and downcasting, and modular application
  construction from independent builder providers.
- [Extensible data types, part 2: interpreters](extensible-datatypes-part-2.md) — 2025-07-09,
  *historical*. Extensible variants applied to the expression problem, building a modular arithmetic
  interpreter with two independent operations over one language.
- [Extensible data types, part 3: implementing records](extensible-datatypes-part-3.md) — 2025-07-12,
  *historical*. The internals: partial records, the `MapType` markers, `BuildField`/`TakeField`, and
  the builder dispatchers built on them.
- [Extensible data types, part 4: implementing variants](extensible-datatypes-part-4.md) — 2025-07-30,
  *historical*. The dual internals: partial variants, `Void`, `ExtractField`, the cast implementations,
  and the monadic visitor dispatchers.
- [CGP v0.5.0 release](v0-5-0-release.md) — 2025-10-12, *historical*. `#[derive(CgpData)]`,
  `#[cgp_auto_dispatch]`, the optional builder, monadic computation, and the removal of the `Async`
  trait in favor of the `Send`-recovery proxy pattern.
- [CGP v0.6.0 release](v0-6-0-release.md) — 2025-10-26, *historical*. `#[cgp_impl]`, direct
  delegation on the context type, and the removal of `HasCgpProvider` — the release that made CGP
  code start to look like ordinary Rust.
- [Announcing cgp-serde](cgp-serde-release.md) — 2025-11-03, *historical*. Serde's traits rebuilt as
  CGP components, with two applications encoding the same data differently and an arena-allocating
  deserializer demonstrating context-and-capabilities.
- [CGP v0.6.1 release](v0-6-1-release.md) — 2026-02-01, *historical*. Implicit context types in
  `#[cgp_impl]`, the `#[check_providers]` attribute, and associated types in getter traits.
- [A new website, and why we moved from Zola to Docusaurus](new-website.md) — 2026-02-21, *current*.
  A meta post about the site itself and the project's use of LLM assistance; the only post whose
  subject is the website.
- [CGP v0.7.0 release](v0-7-0-release.md) — 2026-02-28, *historical*. The largest ergonomics release:
  `#[cgp_fn]`, `#[implicit]`, `#[uses]`, `#[extend]`, `#[use_provider]`, `#[use_type]`, and the
  removal of `#[cgp_context]`.
- [RustLab 2025: how to stop fighting with coherence](rustlab-2025-coherence.md) — 2026-03-07,
  *historical*. A full slide-by-slide transcript of CGP's first conference talk, and the clearest
  narrative anywhere of why coherence exists and how provider traits work around it.
- [CGP v0.8.0: grouping components with namespaces](v0-8-0-release.md) — placeholder date
  2026-05-10, **draft for an unreleased version**. The namespace feature, unfinished: it stops
  mid-argument, covers one feature of several, and teaches an attribute name that changed twice
  during development. Begun as the v0.7.1 announcement before the release was renumbered.

## Reading the drift at a glance

Five breaking changes account for most of the staleness across the catalog, and knowing which post
sits on which side of each is usually enough to judge a snippet without opening the divergence
section. The dates below are the release that made the change, so any post published earlier shows the
old form.

- **`#[cgp_impl]` replaced the inside-out provider form** (v0.6.0, October 2025). Everything before
  it writes `impl<Context> Greeter<Context> for GreetHello` with `#[cgp_new_provider]`; the current
  form is `#[cgp_impl(new GreetHello)] impl Greeter`, per
  [writing-providers](../../cgp/guides/writing-providers.md).
- **`#[cgp_context]` and `HasCgpProvider` are gone** (deprecated v0.6.0, removed v0.7.0). Contexts now
  carry their own wiring table directly; every `#[cgp_context]` and every `{Context}Components` struct
  in an older post is dead syntax.
- **The `Async` trait and `HasAsyncErrorType` were removed** (v0.5.0, October 2025), replaced by the
  `Send`-recovery proxy trait pattern in [send-bounds](../../cgp/concepts/send-bounds.md).
- **Presets were replaced by namespaces** (v0.8.0, unreleased). `cgp_preset!`,
  `#[cgp::re_export_imports]`, `#[cgp_inherit]`, and `#[wrap_provider]` no longer exist; the current
  mechanism is [namespaces](../../cgp/concepts/namespaces.md) via
  [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md).
- **Implicit arguments and attribute-based dependencies arrived late** (v0.7.0, February 2026).
  Any post before it declares dependencies with hand-written `where Self: Trait` bounds and reads
  fields through getter traits, where the current idiom is
  [`#[uses]`](../../cgp/reference/attributes/uses.md) and
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md).

## Publication conventions

Posts live at `blog/<date>-<name>.md`, or in a directory with an `index.md` when they carry images.
Front matter sets the author (always `soares`, defined in
[blog/authors.yml](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/authors.yml)),
one or more tags from the fixed set in
[blog/tags.yml](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/tags.yml) —
`release`, `deepdive`, `walkthrough` — and an explicit `slug`. A `{/* truncate */}` marker separates
the excerpt shown on the index from the body, and Docusaurus warns on any post that omits it.

**Always set the `slug`.** Without one, Docusaurus does not derive a flat URL from the filename — it
publishes the post under a *dated* path instead, so `2026-02-21-new-website.md` becomes
`/blog/2026/02/21/new-website` rather than `/blog/new-website`. Exactly one post is currently in that
state, the [new-website post](new-website.md), and its URL is inconsistent with every other post on
the site as a result. The fix is a one-line front-matter addition, though it changes that post's URL
and so is the user's call.

One further inconsistency is worth knowing before adding a post: the release-note slugs are not
uniform. Posts through v0.6.1 use dash-separated versions (`v0-6-1-release`), while v0.7.0 and the
v0.8.0 draft use dotted ones (`v0.7.0-release`). Match whichever neighbours a new post rather than
assuming a single rule, and check the announcement bar in `docusaurus.config.ts`, which hardcodes one
of these URLs.

## Where the release history lives

These documents record what each *post* said. What each *release* actually shipped — and how much of
it survives — is tracked separately in [releases/](../../releases/README.md), one document per tag,
with a removal ledger dating every construct that has been renamed or deleted. Each release document
links to its announcement post and to the document here that covers it; read the pair together when a
post's claims need checking against what the release really contained. Two of the release documents
have no post at all ([v0.1.0](../../releases/v0-1-0.md) and [v0.3.1](../../releases/v0-3-1.md)), and
one post — the [v0.8.0 draft](v0-8-0-release.md) — covers a release that has not happened yet.
