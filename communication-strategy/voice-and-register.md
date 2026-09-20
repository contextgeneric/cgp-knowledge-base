# Voice and register

Write CGP documentation in the project's voice and blog posts in the author's voice, using plain
language, specific claims, and visible tradeoffs.

[Author-personality.md](author-personality.md) records the author's preferences and observed habits.
This document turns them into guidance for a passage. Use [writing-styles.md](writing-styles.md)
for sentence revision and [vocabulary.md](vocabulary.md) for CGP terminology.

## The layered voice

Choose the voice according to the page. The website's documentation speaks as the project; the
blog speaks as the author.

**Project voice** addresses the reader as “you” and names the project as “CGP.” Use it on the
homepage, documentation, tutorials, and READMEs. Explain claims in terms another maintainer could
verify. Keep personal history and first-person narration out of these pages, except for the
explicit exceptions below. A tutorial may use “we” to mean the writer and reader working through
an example together.

**Author voice** is personal and first-person. Blog posts may explain how an idea arose, express
uncertainty, thank readers, or ask for direction. Preserve those choices when revising a human
draft. Consistency across the site does not require making a personal account sound institutional.

The [Contribute page's sponsorship section](https://contextgeneric.dev/docs/contribute) deliberately
uses the author's voice. Preserve its personal account of capacity and support. If another docs
passage requires a personal statement, make the change of voice explicit rather than attributing
the statement to an impersonal project.

Never use “we” to mean the author alone. Use “CGP” for a project claim or “I” in an appropriate
personal passage. Ground judgments in project prose: explain which use case CGP fits and why,
rather than calling it the best approach without a stated comparison.

## The register: plain, unhurried, and specific

Explain CGP as a knowledgeable colleague would: carefully, with familiar words and enough detail
to understand the claim. Keep the same clarity in both voices while preserving the blog's personal
character.

Prefer specific facts to praise. “The compiler resolves provider selection” tells the reader more
than “powerful, seamless modularity.” Remove an adjective or adverb when it adds neither meaning
nor a necessary qualification.

Give an explanation the length its subject needs. A long piece should state its scope near the
start so readers can decide where to focus. Simplify the entry without removing advanced material
that belongs on the page; the [website rules](../website/AGENTS.md#layer-the-depth-do-not-omit-the-advanced-material)
define that obligation by page type.

Name the construct, operation, or limitation behind an abstract claim. Show the wiring entry
behind “explicit,” the generated call behind “static dispatch,” or a verified diagnostic behind
“difficult errors.” The evidence makes the claim assessable.

## The moves that make CGP prose work

Introduce a construct as an answer to a problem the reader can recognize. Explain the ordinary
Rust approach fairly, show where it becomes insufficient for the example, and then show what CGP
changes. The [area tutorial](../website/tutorials/area-calculation.md) and
[RustLab account](../website/blog/rustlab-2025-coherence.md) provide models for that progression.

Show expansions where they explain or justify the abstraction. A first-principles explanation can
start with an explicit impl and then replace it with a macro. An applied introduction can start
with the recommended syntax and explain the generated code after the reader has a working model.
The [tutorial guide](../website/writing-guides/tutorial.md) supports both approaches; neither
requires opening every introduction with raw provider traits.

State a relevant cost beside the benefit it qualifies. “This adds a wiring table that callers
must trace” describes a cost. “The modest learning curve is outweighed by substantial benefits”
leaves both sides unspecified. Say when an ordinary trait or another tool is sufficient.

Use analogies to explain relationships, then state their limits. Wiring can be described as a
settings table, provided the passage says the compiler resolves it without a runtime table lookup.
An analogy should lead to the mechanism rather than replace it.

## Show it: canonical examples, diagrams, and diffs

Reuse established examples so readers can concentrate on the changing CGP idea. Choose among
these before introducing another domain:

- **Encoder pair:** `Display`-based and `AsRef<[u8]>`-based implementations motivate distinct
  providers and per-type wiring. The basic example uses a value context and a self-targeted
  component. If the value moves into a parameter, explain that change beside the code.
- **Greeter:** A method reads an implicit `name` from `Person`, then works on another matching
  context. Hello World uses `#[cgp_fn]`; component examples introduce `CanGreet` and a provider.
- **Email swap:** `App` selects `SendViaSmtp`, while `TestApp` selects `RecordEmails`. These are
  environmental contexts with a self-targeted component.
- **Area calculation:** `Rectangle`, `Circle`, area providers, and a scaling wrapper introduce
  provider reuse and higher-order composition.

Use the verified code in [examples/](../examples/README.md) and the website's `example-code`
crate. When a different example is necessary, record why in the page's internal document and add
it to this catalog. Identify the context and target whenever an example changes their roles.

Reuse a diagram when the same idea appears on several pages. Keep labels close to what they
identify, omit decoration, and ensure the prose remains understandable without the image.
The [website task plan](../website/tasks.md) tracks the shared diagrams for a wiring table, the
consumer/provider split, and providers selected independently by contexts. Store these as SVGs
among the site's static assets. The supporting reading research belongs in
[evidence.md](evidence.md#sources-for-the-craft-this-section-borrows).

Make before-and-after examples directly comparable. If the claim is that only annotations change,
show the unchanged bodies and highlight the changed lines using Docusaurus code comments.
Do not elide the part readers need to verify the comparison.

Public code examples must meet these requirements:

- **Declare their scope:** Make examples runnable or label them as fragments and identify omissions.
- **Use current idioms:** Follow the [CGP guides](../cgp/guides/README.md).
- **Explain what code alone cannot:** Comments should identify a relevant dependency, assumption,
  or witness to an overlap rather than repeat the code.
- **Verify diagnostics:** Quote actual compiler output from the relevant source and toolchain.

## Words and habits to avoid

Remove language that adds promotion without information. Common cases include:

- **Inflated adjectives:** “Genuinely,” “seamlessly,” or “powerful” without a concrete meaning.
- **Unmeasured performance praise:** “Blazingly fast” or unsupported comparisons.
- **Vague adjective lists:** “Clean, modern, and maintainable” without explaining what changed.
- **Stacked hedges:** “May potentially help” where “may help” preserves the claim.
- **An institutional voice for one person:** A corporate “we” or unsupported claims about “our users.”
- **Invented evidence:** Benchmarks, adoption figures, quotations, or claims that developers love a feature.
- **Dismissive comparisons:** Describing another tool unfairly to make CGP look better.

Preserve useful uncertainty and warmth. The author's pleasure in sharing work belongs in a blog
post; an intensifier attached to a technical claim needs evidence. [Vocabulary.md](vocabulary.md)
contains the accuracy rules for terms such as “capability,” “zero-cost,” and “AI-assisted.”

## Improving copy that is already published

Improve unclear or inflated prose within the requested scope. Existing wording is not a reason to
retain an unsupported claim, but a local revision is not permission to rewrite the whole site.

Docs pages describe current behavior and can be corrected in place. Published blog posts are dated
records and follow the separate restrictions in [website/AGENTS.md](../website/AGENTS.md#do-not-rewrite-history).
Record drift in their internal documents rather than silently updating historical code or claims.

Preserve passages that deliberately carry the author's personal voice. The sponsorship section and
personal statements about maturity or capacity are not generic copy to standardize. Follow the
page's provenance record and [AI disclosure policy](ai-disclosure.md) when distinguishing revision
from authorship.

## Checking a draft

Review the draft in this order:

1. **Specificity:** Does it sound like the project or author, with concrete claims instead of
   generic praise?
2. **Costs:** Are relevant limitations stated where the reader needs them?
3. **Restraint:** Can intensifiers be removed without losing meaning, evidence, or uncertainty?
4. **Voice:** Does the voice match the page, including its documented exceptions?

Then use [writing-styles.md](writing-styles.md) for sentence checks and
[reader-simulation.md](reader-simulation.md) to test whether the explanation follows from the
reader's knowledge. Fluency alone does not establish accuracy or clarity.
