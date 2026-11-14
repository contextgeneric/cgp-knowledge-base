# Website blog posts

One internal document per post on the [CGP blog](https://contextgeneric.dev/blog), and per substantial
draft. Each records what its post covers, which knowledge-base documents own that material, and how
its code and claims diverge from CGP v0.8.0. The rules that govern posts, including never rewriting a
published one, are in [../AGENTS.md](../AGENTS.md#do-not-rewrite-history).

## How stale the posts are

**The blog is the site's most-read writing and its least current.** Of the sixteen published posts,
eight write every provider inside-out with `#[cgp_provider]`/`#[cgp_new_provider]`, seven show
`#[cgp_context]` on a context definition, and four use the removed `Async` trait or one of its aliases.
The live site's [Introduction](https://contextgeneric.dev/docs/) still sends newcomers to the blog as
the most up-to-date resource; the `v0.8.0` branch's does not. The posts' ideas stay current where their
code does not, and several are the only prose on the design questions they work through. So each
record's "Where it diverges from CGP v0.8.0" section names what is stale, to read before quoting the
post, per [../AGENTS.md](../AGENTS.md#verify-code-against-current-cgp-and-never-against-a-blog-post).

## The catalog

Publication order, oldest first, which is roughly the order of increasing reliability. Status words
follow [../AGENTS.md](../AGENTS.md#status-vocabulary).

- [Announcing Context-Generic Programming](early-preview-announcement.md): 2024-12-19, *historical*.
  The launch post: what CGP is, how it grew out of the Hermes relayer, and a plan for 2025 since
  resolved in ways the post could not anticipate.
- [CGP v0.3.0 release](v0-3-0-release.md): 2025-01-09, *historical*. Abstract types via the removed
  `cgp_type!` function macro, the first getter macros, `CanWrapError`, and the `cgp-error-anyhow` and
  `cgp-runtime` crates.
- [CGP v0.4.0 release](v0-4-0-release.md): 2025-05-09, *historical*. The release that made CGP
  debuggable: `IsProviderFor`, `CanUseComponent`, `check_components!`, plus `#[cgp_context]`, the
  preset system, and the first datatype-generic support.
- [CGP v0.4.1 release](v0-4-1-release.md): 2025-06-14, *historical*. The `cgp-handler` crate
  introducing `Handler`, `Computer`, and `Producer`, and preset improvements built for Hypershell.
- [Hypershell: a type-level DSL for shell-scripting](hypershell-release.md): 2025-06-14,
  *historical*. The longest post on the site and the fullest account of building a DSL whose programs
  are types; also the site's best standalone introduction to CGP's wiring model.
- [Extensible data types, part 1: builders](extensible-datatypes-part-1.md): 2025-07-07,
  *historical*. Extensible records, safe enum upcasting and downcasting, and modular application
  construction from independent builder providers.
- [Extensible data types, part 2: interpreters](extensible-datatypes-part-2.md): 2025-07-09,
  *historical*. Extensible variants applied to the expression problem, building a modular arithmetic
  interpreter with two independent operations over one language.
- [Extensible data types, part 3: implementing records](extensible-datatypes-part-3.md): 2025-07-12,
  *historical*. The internals: partial records, the `MapType` markers, `BuildField`/`TakeField`, and
  the builder dispatchers built on them.
- [Extensible data types, part 4: implementing variants](extensible-datatypes-part-4.md): 2025-07-30,
  *historical*. The dual internals: partial variants, `Void`, `ExtractField`, the cast implementations,
  and the monadic visitor dispatchers.
- [CGP v0.5.0 release](v0-5-0-release.md): 2025-10-12, *historical*. `#[derive(CgpData)]`,
  `#[cgp_auto_dispatch]`, the optional builder, monadic computation, and the removal of the `Async`
  trait in favor of the `Send`-recovery proxy pattern.
- [CGP v0.6.0 release](v0-6-0-release.md): 2025-10-26, *historical*. `#[cgp_impl]`, direct
  delegation on the context type, and the removal of `HasCgpProvider`: the release that made CGP
  code start to look like ordinary Rust.
- [Announcing cgp-serde](cgp-serde-release.md): 2025-11-03, *historical*. Serde's traits rebuilt as
  CGP components, with two applications encoding the same data differently and an arena-allocating
  deserializer demonstrating context-and-capabilities.
- [CGP v0.6.1 release](v0-6-1-release.md): 2026-02-01, *historical*. Implicit context types in
  `#[cgp_impl]`, the `#[check_providers]` attribute, and associated types in getter traits.
- [A new website, and why we moved from Zola to Docusaurus](new-website.md): 2026-02-21, *current*.
  A meta post about the site itself and the project's use of LLM assistance; the only post whose
  subject is the website.
- [CGP v0.7.0 release](v0-7-0-release.md): 2026-02-28, *historical*. The largest ergonomics release:
  `#[cgp_fn]`, `#[implicit]`, `#[uses]`, `#[extend]`, `#[use_provider]`, `#[use_type]`, and the
  removal of `#[cgp_context]`.
- [RustLab 2025: how to stop fighting with coherence](rustlab-2025-coherence.md): 2026-03-07,
  *historical*. A slide-by-slide transcript of CGP's first conference talk, and the clearest narrative
  anywhere of why coherence exists and how provider traits work around it.
- [CGP v0.8.0: cargo-cgp, new documentation, and namespaces](v0-8-0-release.md): placeholder date
  2026-05-10, on the website's `v0.8.0` branch, **draft awaiting review and coordinated publication**.
  The social-media wiring progression, fixed defaults and their limits, verified cargo-cgp
  diagnostics, expanded documentation and optional agent support, other improvements, migration, and
  a practical closing.

## Drafts that live on branches

**A draft substantial enough to finish gets a record here as soon as it exists, with its branch
named**, so the catalog inventories all of CGP's writing; a draft on a feature branch is invisible to
anyone reading `main`.

- [Using an incoherent, dictionary-passing style Rust today](incoherent-rust-today.md): on the
  `incoherent-rust` branch, dated 2026-03-30, *draft*. About 12,800 words reading CGP against the
  dictionary-passing, incoherent-traits, and context-and-capabilities discussion, and arguing that CGP
  implements a fragment of it on stable Rust today. The only post aimed at the language-design
  reader, and the only one whose value decays with time.

The `rustlab-presentation` branch carries the RustLab transcript's slide assets rather than a post;
[site.md](../site.md#branches-and-what-is-not-on-main) records it.

## Reading the drift at a glance

Five breaking changes account for most of the staleness. Each is dated by the release that made it,
so a post published earlier shows the old form.

- **`#[cgp_impl]` replaced the inside-out provider form** (v0.6.0, October 2025). Earlier posts write
  `impl<Context> Greeter<Context> for GreetHello` with `#[cgp_new_provider]`; the current form is
  `#[cgp_impl(new GreetHello)] impl Greeter`, per
  [writing-providers](../../cgp/guides/writing-providers.md).
- **`#[cgp_context]` and `HasCgpProvider` are gone** (`HasCgpProvider` removed in v0.6.0;
  `#[cgp_context]` deprecated in v0.6.0 and removed in v0.7.0). Contexts carry their own wiring table,
  so every `#[cgp_context]` and `{Context}Components` struct in an older post is dead syntax.
- **The `Async` trait and `HasAsyncErrorType` were removed** (v0.5.0, October 2025), replaced by the
  `Send`-recovery proxy trait pattern in [send-bounds](../../cgp/concepts/send-bounds.md).
- **Presets were replaced by namespaces** (v0.8.0). `cgp_preset!`, `#[cgp::re_export_imports]`,
  `#[cgp_inherit]`, and `#[wrap_provider]` no longer exist; the mechanism is
  [namespaces](../../cgp/concepts/namespaces.md) via
  [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md).
- **Implicit arguments and attribute-based dependencies arrived late** (v0.7.0, February 2026). Earlier
  posts write `where Self: Trait` bounds and read fields through getter traits, where the idiom is
  [`#[uses]`](../../cgp/reference/attributes/uses.md) and
  [`#[implicit]`](../../cgp/reference/attributes/implicit.md).

What each *release* shipped, and how much survives, is in [releases/](../../releases/README.md), one
document per tag with the removal ledger; read a release document beside its post's record when the
post's claims need checking. [v0.1.0](../../releases/v0-1-0.md) and [v0.3.1](../../releases/v0-3-1.md)
have no post.

## Publication conventions

These hold for every post; [the release-announcement guide](../writing-guides/release-announcement.md)
adds a release post's own.

- **File:** `blog/<date>-<name>.md`, or a directory with an `index.md` when the post carries images.
- **Front matter:** `authors: [soares]` (defined in
  [blog/authors.yml](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/authors.yml));
  one or more tags from the fixed set in
  [blog/tags.yml](https://github.com/contextgeneric/contextgeneric.dev/blob/main/blog/tags.yml)
  (`release`, `deepdive`, `walkthrough`); an explicit `slug`; and a written `description`.
- **Excerpt:** a `{/* truncate */}` marker separates it from the body; Docusaurus warns on a post
  without one.

**Always set the `slug` on a new post, and never change a published one.** Without a slug, Docusaurus
publishes under a dated path: the [new-website post](new-website.md) is the one post in that state, at
`/blog/2026/02/21/new-website`. Leave it, because moving a live URL breaks every inbound link.

**Match a new release slug to its neighbours.** Posts through v0.6.1 use dashed versions
(`v0-6-1-release`); v0.7.0 and the v0.8.0 draft use dotted ones (`v0.7.0-release`). The announcement
bar in `docusaurus.config.ts` hardcodes one of these URLs.

**Every post carries a `description`, and adding one to a published post is not rewriting it**: it
changes no sentence, URL, or snippet, so the dated-artifact rule does not reach it. Add one
deliberately, because Docusaurus puts it in `rss.xml` and `atom.xml` in place of the excerpt, so a
subscriber's reader may show the new summary for a post it already holds; the rendered index still
shows the excerpt. Without one, Docusaurus derives a description from the opening paragraph, which a
search result cuts mid-clause and which loses the backticks around identifiers. The blog carries three
quarters of the site's search impressions, so the written description is worth most here.

- **Self-dating:** name the version or the moment, so a description of a removed construct reads as a
  record: *"CGP v0.4.0, the release that made CGP debuggable"*, not *"how to debug CGP"*.
- **No backticks:** the meta tag is plain text, and a stripped backtick runs identifiers together.
- **Length and the rest:** the reference guide's
  [conventions](../writing-guides/reference.md#conventions-the-port-must-follow).
