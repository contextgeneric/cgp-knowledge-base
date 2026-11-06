# CGP v0.8.0 - cargo-cgp, new documentation, and namespaces

The release-branch announcement opens with cargo-cgp diagnostics and the expanded documentation
and optional agent support, then develops namespace wiring and migration from v0.7.0.

- **URL**: <https://contextgeneric.dev/blog/v0.8.0-release>
- **Source**:
  [blog/2026-05-10-v0.8.0-release.md](https://github.com/contextgeneric/contextgeneric.dev/blob/v0.8.0/blog/2026-05-10-v0.8.0-release.md),
  on the website's `v0.8.0` branch
- **Dated**: 10 May 2026 is the placeholder filename date; set the actual publication date at
  release
- **Tags**: `release`, `deepdive`
- **Status**: **Draft**, awaiting the author's review and coordinated publication
- **How it was made**: revision of a human-written draft by an agent; the footnote links the
  disclosure's blog-post section
- **Documents**: [releases/v0-8-0.md](../../releases/v0-8-0.md)

## What it covers

The opening connects the release to the author's aim of making CGP easier to debug, learn, and
follow as an application grows. The narrative uses personal motivation, concrete situations, and
observations about the code to introduce features. Paragraphs may develop toward their conclusions;
the author explicitly requested natural prose rather than mandatory point-first openings for this
post. The rest of the point-first-writing guidance still applies.

The cargo-cgp section restores the author's account of verbose diagnostics as a long-standing
adoption barrier: a newcomer could need advanced Rust and CGP implementation knowledge to diagnose
a simple mistake. It names the accompanying v0.1.0 release and shows the readable diagnostic
before an expandable raw-compiler comparison, both captured from the exact missing-height program.
It identifies the example as `src/lib.rs` in a package using CGP v0.8.0, specifies that the checker
runs in that project, then repairs the field and verifies the check. It uses the canonical recognition qualification
and distinguishes the optional tool's pinned nightly from ordinary stable-Rust builds.
The compiler-API explanation follows the diagnostic demonstration, before installation instructions.
The installation sequence includes `cargo install --locked cargo-cgp` and `cargo cgp setup`, with the
minimum Rust version and Linux-only testing stated beside it, and links to installation and expansion
documentation.

The documentation section explains the earlier reliance on blog posts, the missing reference
material, and the author's limited time for a side project. It preserves his estimate that writing
comparable documentation by hand would likely take months of full-time work, then explicitly states
that agents, primarily Claude Code, wrote much of the new material under the author's direction. It
routes to Reference, Concepts, Comparisons, and Projects before describing the iterative
knowledge-base process and review limits. It links the public methodology, disclosure, and
knowledge-base current-state pages. The skill is optional learning and debugging assistance rather
than a proficiency guarantee. The quality concern and feedback invitation precede the process
explanation, so the explanation answers a question the reader has already encountered. The post has
no direct knowledge-base repository links.

The short tooling and documentation sections come first so readers who skip the long namespace
walkthrough still see those improvements. Namespaces remain the main technical deep dive. The
namespace section opens with the earlier wiring burden and the limits of provider bundles, then
states its practical payoff and links for readers who want to skip to the syntax or migration. Its
social-media example progresses from coarse manager traits through isolated dependencies and a
higher-order filtering provider to nine flat wiring entries. Aggregate providers group the
implementations, but array keys still repeat every component name on the application. The namespace
reveal shows the short application table before explaining the prefix registrations that enable it.
The namespace opt-in is explained beside the short table, and the completed configuration is
followed by a lookup trace. Production, test, and hypothetical local configurations select whole
groups with visible one-entry differences.

The main example wires environmental contexts with self-targeted components. It explains that
successive stages replace earlier definitions, labels database operations as illustrative fragments,
and links the public web-app walkthrough and source. It explains that grouping methods is a design
choice rather than a restriction on what a component can contain.
The diagnostic example uses a value context, `Rectangle`; the namespace walkthrough explains the
subsequent shift to an application context.

The namespace section traces a component lookup through its path and aggregate provider. It explains
why path-keyed intermediate bundles join the namespace themselves, while bare-key leaf bundles do
not, and shows a standalone check of the concrete context. It distinguishes that final nine-component
check from the components needed by each intermediate stage, and introduces the analogous
`FilterSpamMessage` wrapper before using it in the wiring. Namespace grouping removes repeated
routing entries; it does not remove individual provider bindings or component checks.

The defaults section introduces gradual adoption in a small application before developing the
syntax, contrasting fixed namespace choices with interchangeable provider bundles. It shows
`#[default_impl]` and its equivalent namespace-body entry as alternatives, then binds a
composite creator in the body, where the configuration selects the generic wrapper's inner provider.
It states non-overridability and ownership limits beside the benefit:
a prefixed path registration requires the namespace's crate, whereas an unprefixed local marker has
different ownership rules. Structural prefixes belong in a base namespace and fixed choices in a
configuration namespace, leaving varying paths unbound.

The motivation also preserves the earlier grouping attempts. It explains why a nested macro call
cannot supply an expanded key list to `delegate_components!`, and why the preset inheritance and
macro-composition approaches were insufficient. This background sits before the namespace solution;
the migration section links back to it rather than repeating the history.

Other improvements introduce `open`, table iteration, implementation-only generics, shape macros,
and fieldless variants through concrete uses, then cover handler-macro fixes and the restrictions the
release lifts: reserved variant names, another derive's helper attributes, async default bodies, and a
provider's own const. Migration names all
removed preset constructs, works a user-group conversion with its filter dependency and component
checks, and covers the `use_type` separator, direct macro-crate renames, changed validation, possible
unused imports and macro-name
ambiguity, and error-backend behavior. Its required component registrations are stated before the
migrated context, and the default-provider example explicitly updates the earlier implementation.
The closing invites a small wiring refactor or the Quickstart
and asks for specific diagnostic and documentation feedback without promising a roadmap.

## How it relates to the knowledge base

The social-media progression comes from [the worked example](../../examples/social-media-app.md)
and the [web-app project record](../../projects/cgp-examples/web-app/README.md). Provider composition
and bundle behavior are owned by [higher-order providers](../../cgp/concepts/higher-order-providers.md)
and [aggregate providers](../../cgp/concepts/aggregate-providers.md).

The namespace semantics come from [namespaces](../../cgp/concepts/namespaces.md), the
[namespaces-and-prefixes guide](../../cgp/guides/namespaces-and-prefixes.md), and the references for
[`prefix`](../../cgp/reference/attributes/prefix.md),
[`default_impl`](../../cgp/reference/attributes/default_impl.md),
[`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md), and
[`delegate_components!`](../../cgp/reference/macros/delegate_components.md). The release inventory
and removals belong to [v0.8.0](../../releases/v0-8-0.md) and the
[removal ledger](../../releases/README.md#the-removal-ledger).

Tool scope and installation come from [the cargo-cgp usage reference](../../cargo-cgp/reference/usage.md)
and [installation](../../cargo-cgp/reference/installation.md). Public framing follows the
[release-announcement guide](../writing-guides/release-announcement.md),
[author voice](../../communication-strategy/voice-and-register.md), and
[AI disclosure policy](../../communication-strategy/ai-disclosure.md).

## Verification and deliberate simplifications

The website's [blog example
file](https://github.com/contextgeneric/contextgeneric.dev/blob/main/example-code/tests/blog/v0_8_0_release.rs)
compiles the initial database-only managers, the filter-dependent coarse and fine-grained
configurations, flat and hierarchical namespace routing, fixed defaults and their body-entry
alternative, and the migrated user group. It supplies page-elided domain types, methods, filter
providers, and database bodies, with explicit checks on concrete contexts. The local SQLite variant
is hypothetical; its omitted providers are supplied as stubs for compilation. These checks verify
wiring, not a database implementation or a complete web service.

The missing-height program is a [compile-fail
fixture](https://github.com/contextgeneric/contextgeneric.dev/blob/main/example-code/tests/compile_fail/blog/v0_8_0_missing_height.rs).
Both quoted diagnostic bodies were captured from that program in a temporary library target as
`src/lib.rs`, using cargo with stable Rust 1.99 and the local source-built cargo-cgp driver. The
repaired program passes cargo-cgp, and a runtime test asserts that a three-by-four rectangle has
area twelve. The historical preset and old attribute-separator listings are explicitly v0.7.0 input,
not current examples to compile against v0.8.0. The proposed `???` keys and nested helper-macro form
are labeled pseudocode in text fences, not presented as accepted Rust syntax.

The production site build passes without broken links or anchors, and the full example suite passes
against the sibling `cgp` checkout.

The narrative revision preserves all 36 fenced listings verbatim, including the diagnostics and
historical input, and preserves every heading and anchor. The namespace application table moves
ahead of its prefix-registration listings. A comparison of the listing multisets verifies that
the move neither drops nor duplicates a listing. The `blog_tests` target compiles the wiring stages and passes
both the repaired-rectangle runtime test and the missing-height compile-fail test.

## Original-draft preservation

The preservation audit compares the revision with the original draft at website commit
`080c125db58c`. It checks the explanations and all 29 original Rust listings, not just the section
headings. The original material remains represented as follows:

| Original material | Where the revision preserves it |
| --- | --- |
| Difficult diagnostics and the Rust/CGP knowledge needed to read them | The cargo-cgp motivation, exact missing-height example, diagnostic comparison, and compiler-API explanation |
| Documentation gaps, reliance on blog posts, limited personal time, and months of manual work | The documentation introduction, retaining the author's capacity argument |
| Claude Code, iterative planning and revision, reader skepticism, and a request for quality feedback | The documentation process and invitation to assess the actual explanations |
| Word/page-count placeholders | Measured documentation scale: about 330,000 prose words across more than 340 pages, plus an explicitly qualified printed-page equivalent |
| Further methodology writing | The author's interest in a dedicated follow-up, alongside the existing process page |
| All six documentation/agent resources and the skill's learning and diagnostic roles | The expanded resource list and skill subsection |
| Complete database-only managers, alternative SQLite managers, and initial two-entry wiring | The restored first stage, compiled separately in the blog example file |
| Content filters, cloud/AI production implementations, deterministic tests, and eight wiring entries | The dependency-growth example and its corrected production/test tables |
| Accumulating dependencies, ambiguous domain grouping, and limiting destructive operations in generic code | The fine-grained-trait motivation, including the profile-picture, user-post, and deletion examples |
| Fine-grained traits, filtering wrappers, SQL insert separation, and SQLite composition | The per-operation and higher-order-provider examples |
| Growth from four to nine entries and potentially much larger tables | The wiring-cost discussion and explicit user/post/filter bundles |
| Array keys, desired group keys, proposed helper macros, and their expansion/export difficulties | The bundle example, both restored pseudocode listings, and the earlier-approaches discussion |
| Preset history, single inheritance, macro-based composition, and old inheritance/local-table syntax | The motivation before namespaces and the explicitly historical migration example |
| Prefix registration, opt-in namespace selection, parent paths, and production/test/local differences | The namespace walkthrough, including different entry orders making flat tables harder to compare |
| Default-provider flexibility versus an intentionally fixed early implementation | The defaults introduction, including the logging-backed core variant |
| Namespace inheritance, default attributes and equivalent body entries, composite providers, and filter customization | The defaults examples, including the AI filter bundle the post wires directly |
| Ownership constraints, inability to opt out of one default, single-crate trade-offs, and gradual migration toward multiple crates | The defaults restrictions and gradual-adoption bridge |

The preserved content uses corrected `prefix` syntax and consistent paths, fixes the wrong `TestApp`
target and missing field derives, and quotes current diagnostics instead of stale codes and carets.
It qualifies claims that diagnostics are solved, broad macro impossibility claims, and the scope of
single-crate trade-offs. Those corrections preserve the argument without teaching invalid behavior.

The scale estimate counts regular Markdown/MDX files under the website's `docs/`, excluding symlinked
skill files, front matter, and fenced code. At the audit there were 343 files and approximately
330,600 whitespace-separated prose words. The printed equivalent assumes 300 words per page and is
explicitly a layout-dependent estimate rather than a measured PDF length.

## Maintaining it

Keep cargo-cgp and the documentation before the longer namespace explanation, as the author
requested for readers who may skip that walkthrough. Preserve the natural narrative style requested
for this post: paragraphs may begin with a situation, an observation, or a personal motivation and
develop toward the point. Do not impose point-first openings or a repeated problem-and-solution
template. Follow the remaining point-first-writing guidance on clear subjects, connected reasoning,
paragraph focus, accuracy, and plain language. Vary transitions around code listings and explain
their consequences without repeatedly announcing the next step or restating the syntax. Keep
independent migration changes in separate paragraphs so readers can scan by construct. Within the
namespace section, preserve the argument from useful provider separation to its wiring cost and then
to namespace organization. Preserve the author's background on the diagnostic, documentation, and
wiring challenges, including the time constraint and earlier grouping experiments. Preserve all
original substantive content and examples when reorganizing; use the audit above to check coverage.
Place that history where it motivates each improvement, rather than compressing it into a feature
summary. Keep migration focused on the upgrade, the defaults restrictions beside their examples, and
agent authorship separate from optional agent support. Keep the closing practical and personal, with
honest remaining costs and a bounded request for feedback.

The renamed headings retain explicit IDs for existing links from the web-app project pages:
`an-example-social-media-web-app`, `fine-grained-traits`,
`introducing-cgp-namespaces-and-paths`, and `default-implementations`. Preserve those IDs or update
all incoming links in the same change.

The publication work remains separate from revision. The author reads the post before publication;
the filename gets the actual release date, the fixed slug stays unchanged, and the site branch
publishes only with both official releases. Re-run the quoted diagnostics against the released tool,
verify the announcement bar and version pins, and add discussion links after submission. Release
wording already describes the official versions as shipped, as the branch rules require.
