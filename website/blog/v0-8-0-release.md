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

The opening ties the release to the author's aim of making CGP easier to debug, learn, and follow as
an application grows. Short cargo-cgp and documentation sections come first; namespaces are the main
technical deep dive; other improvements, migration, and a practical closing follow.

**cargo-cgp.** The section restores the author's account of verbose diagnostics as a long-standing
adoption barrier: a newcomer could need advanced Rust and CGP implementation knowledge to diagnose a
simple mistake. It names the accompanying v0.1.0 release and shows the readable diagnostic before an
expandable raw-compiler comparison, both captured from the exact missing-height program. It
identifies the example as `src/lib.rs` in a package using CGP v0.8.0, runs the checker in that
project, then repairs the field and verifies the check. It uses the canonical recognition
qualification and distinguishes the optional tool's pinned nightly from ordinary stable-Rust builds.
The compiler-API explanation follows the demonstration and precedes installation:
`cargo install --locked cargo-cgp` and `cargo cgp setup`, with the minimum Rust version and
Linux-only testing beside them, and links to the installation and expansion documentation.

**Documentation.** The section explains the earlier reliance on blog posts, the missing reference
material, and the author's limited time for a side project, keeping the author's estimate that
comparable documentation by hand would likely take months of full-time work. It states that agents,
primarily Claude Code, wrote much of the new material under the author's direction, and routes to
Reference, Concepts, Comparisons, and Projects. The quality concern and the feedback invitation come
before the explanation of the iterative knowledge-base process and its review limits, so the
explanation answers a question the reader already has. It links the public methodology, disclosure,
and knowledge-base current-state pages, and no knowledge-base repository directly. The skill is
optional learning and debugging help, not a proficiency guarantee.

**Namespaces.** The section opens with the earlier wiring burden and the limits of provider bundles,
states the practical payoff, and links ahead for readers who want the syntax or migration. The
motivation keeps the earlier grouping attempts, before the solution: why a nested macro call cannot
supply an expanded key list to `delegate_components!`, and why preset inheritance and macro
composition fell short; migration links back to it rather than repeating it.

- **The example:** a social-media application wiring environmental contexts with self-targeted
  components. It progresses from coarse manager traits through isolated dependencies and a
  higher-order filtering provider to nine flat wiring entries. Successive stages replace earlier
  definitions, database operations are labeled illustrative fragments, and the section links the
  public web-app walkthrough and source. Grouping methods is presented as a design choice, not a
  restriction on what a component can contain.
- **The cost and the reveal:** aggregate providers group the implementations, but array keys still
  repeat every component name on the application. The reveal shows the short application table, with
  the namespace opt-in explained beside it, before the prefix registrations that enable it; a lookup
  trace through the path and aggregate provider follows the completed configuration.
- **Bundles and checks:** path-keyed intermediate bundles join the namespace themselves, while
  bare-key leaf bundles do not. A standalone check of the concrete context is shown, and that final
  nine-component check is distinguished from the components each intermediate stage needs. The
  analogous `FilterSpamMessage` wrapper is introduced before the wiring uses it.
- **Configurations:** production, test, and hypothetical local configurations select whole groups
  with visible one-entry differences. Namespace grouping removes repeated routing entries; it does not
  remove individual provider bindings or component checks.
- **Context shapes:** the diagnostic example uses a value context, `Rectangle`, and the walkthrough
  explains the shift to an application context.

**Defaults.** Gradual adoption in a small application comes before the syntax, contrasting fixed
namespace choices with interchangeable provider bundles. The section shows `#[default_impl]` and its
equivalent namespace-body entry as alternatives, then binds a composite creator in the body, where
the configuration selects the generic wrapper's inner provider. It states non-overridability and the
ownership limits beside the benefit: a prefixed path registration requires the namespace's crate,
whereas an unprefixed local marker has different ownership rules. Structural prefixes belong in a
base namespace and fixed choices in a configuration namespace, leaving varying paths unbound.

**Other improvements, migration, and the closing.** Other improvements introduce `open`, table
iteration, implementation-only generics, shape macros, and fieldless variants through concrete uses,
then the handler-macro fixes and the restrictions the release lifts: reserved variant names, another
derive's helper attributes, async default bodies, and a provider's own const. Migration names every
removed preset construct and works a user-group conversion with its filter dependency and component
checks, stating the required component registrations before the migrated context and updating the
earlier default-provider implementation explicitly. It covers the `use_type` separator, direct
macro-crate renames, changed validation, possible unused imports and macro-name ambiguity, and
error-backend behavior. The closing invites a small wiring refactor or the Quickstart and asks for
specific diagnostic and documentation feedback without promising a roadmap.

## How it relates to the knowledge base

- **The example:** [the social-media worked example](../../examples/social-media-app.md) and the
  [web-app project record](../../projects/cgp-examples/web-app/README.md); provider composition and
  bundles are owned by [higher-order providers](../../cgp/concepts/higher-order-providers.md) and
  [aggregate providers](../../cgp/concepts/aggregate-providers.md).
- **Namespaces:** [namespaces](../../cgp/concepts/namespaces.md), the
  [namespaces-and-prefixes guide](../../cgp/guides/namespaces-and-prefixes.md), and the references for
  [`prefix`](../../cgp/reference/attributes/prefix.md),
  [`default_impl`](../../cgp/reference/attributes/default_impl.md),
  [`cgp_namespace!`](../../cgp/reference/macros/cgp_namespace.md), and
  [`delegate_components!`](../../cgp/reference/macros/delegate_components.md).
- **The release:** [v0.8.0](../../releases/v0-8-0.md) and the
  [removal ledger](../../releases/README.md#the-removal-ledger).
- **The tool:** [the cargo-cgp usage reference](../../cargo-cgp/reference/usage.md) and
  [installation](../../cargo-cgp/reference/installation.md).
- **Framing:** the [release-announcement guide](../writing-guides/release-announcement.md),
  [author voice](../../communication-strategy/voice-and-register.md), and the
  [AI disclosure policy](../../communication-strategy/ai-disclosure.md).

## Verification and deliberate simplifications

The website's [blog example
file](https://github.com/contextgeneric/contextgeneric.dev/blob/v0.8.0/example-code/tests/blog/v0_8_0_release.rs)
compiles the initial database-only managers, the filter-dependent coarse and fine-grained
configurations, flat and hierarchical namespace routing, fixed defaults and their body-entry
alternative, and the migrated user group. It supplies page-elided domain types, methods, filter
providers, and database bodies, with explicit checks on concrete contexts. The local SQLite variant
is hypothetical; its omitted providers are supplied as stubs for compilation. These checks verify
wiring, not a database implementation or a complete web service.

The missing-height program is a
[compile-fail fixture](https://github.com/contextgeneric/contextgeneric.dev/blob/v0.8.0/example-code/tests/compile_fail/blog/v0_8_0_missing_height.rs).
Both quoted diagnostic bodies were captured from that program in a temporary library target as
`src/lib.rs`, using cargo with stable Rust 1.99 and the local source-built cargo-cgp driver. The
`cargo check` body's `help:` line was later edited by hand to the `cgp::macro_prelude::Chars` path
that rustc prints once the prelude no longer carries `Chars`, matching the fixture's blessed output,
so both bodies are recaptured against the released tool. The repaired program passes cargo-cgp, and
a runtime test asserts that a three-by-four rectangle has area twelve. The historical preset and old
attribute-separator listings are explicitly v0.7.0 input, not current examples to compile against
v0.8.0. The proposed `???` keys and nested helper-macro form are labeled pseudocode in text fences,
not presented as accepted Rust syntax.

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

**Keep the order and the style the author asked for.** cargo-cgp and the documentation stay before the
longer namespace explanation, for readers who skip that walkthrough. The post is in natural style:
paragraphs may begin with a situation, an observation, or a personal motivation and develop toward
the point, so do not impose point-first openings or a repeated problem-and-solution template. Keep
the subjects clear, the reasoning connected, each paragraph on one point, and the language plain and
accurate. Vary transitions around code listings and explain their consequences without announcing the
next step or restating the syntax.

**Preserve the content and its placement:**

- **Substance:** every original substantive point and example when reorganizing; check coverage with
  the audit above.
- **Background:** the author's account of the diagnostic, documentation, and wiring challenges,
  including the time constraint and the earlier grouping experiments, placed where it motivates each
  improvement rather than compressed into a feature summary.
- **The namespace argument:** from useful provider separation, to its wiring cost, to namespace
  organization.
- **Separation:** independent migration changes in separate paragraphs, so readers can scan by
  construct; migration focused on the upgrade; the defaults restrictions beside their examples; agent
  authorship separate from optional agent support.
- **The closing:** practical and personal, with honest remaining costs and a bounded request for
  feedback.
- **Heading IDs:** the renamed headings keep explicit IDs that the web-app project pages link:
  `an-example-social-media-web-app`, `fine-grained-traits`,
  `introducing-cgp-namespaces-and-paths`, and `default-implementations`. Keep them, or update every
  incoming link in the same change.

**Publication is separate from revision.** The author reads the post before publication; the filename
gets the actual release date, the fixed slug stays, and the site branch publishes only with both
official releases. Re-run the quoted diagnostics against the released tool, verify the announcement
bar and version pins, and add discussion links after submission. Release wording already describes
the official versions as shipped, as the branch rules require.
