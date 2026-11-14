# Writing the Projects section

The Projects section documents the libraries and demonstration programs built with CGP, one section
per project, and its job is to **teach CGP's design patterns through code that runs**. Each section is
ported from the project's section under [projects/](../../projects/README.md), as the reference is
ported from [cgp/reference/](../../cgp/reference/README.md), and its example pages are expanded into
short tutorials.

- **Where they live** — `docs/projects/<project>/`, under a `Projects` category with a hand-written
  index
- **Voice** — project voice, with the teaching "we" allowed on example pages, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from** — the project's section under [projects/](../../projects/README.md), which stays
  the source of truth
- **Plans and records** — [../projects/README.md](../projects/README.md) for the section, and one
  document per project beside it
- **Reading** — the shared set and [the Projects pages' row](README.md#projects-pages) of the
  reading map

## What the section is for

**The section serves two readers.** The pattern learner wants a CGP idea working in a program that
does something real, which neither the Concepts pages' small code nor the tutorials show; the example
pages are for that reader. The evaluator wants evidence that CGP holds up beyond a toy; for that
reader the section is social proof, per [evidence.md](../../communication-strategy/evidence.md), and
it is only as credible as the pages are candid about what each project is.

**The examples carry the section.** The reference, architecture, and guide pages exist so an example
page can link a construct's full account, and so a reader who adopts the project can look things up.
Write and publish a project's example pages first, with the most care.

## Ported, with one expansion

**Every page except an example page is a port**, with the four transformations of
[reference.md](reference.md#derived-from-the-internal-reference-and-kept-in-step-with-it):

- **Re-point every link**, per [Linking](#linking).
- **Drop the internal records**: the header fields recording the branch and checkout, everything in
  `issues.md` and `testing.md`, the probes, the "Public material derived from this" line, and every
  sentence addressed to an agent maintaining the project.
- **Orient a reader who does not know CGP**: gloss "context", "provider", and "wiring" on first use,
  and link the page that explains each.
- **Convert source links** to the project's repository on its default branch.

**An example page is an expansion.** It keeps the internal record's program and what running it
produced, leaves the defects in the record, and adds an introduction for a reader new to CGP, the
reason each part is written as it is, the pattern's name, and a route onward.

## The page kinds

A project section has seven kinds of page. File paths mirror the internal section, so a public page's
source is visible from its path, and within a project the sidebar runs examples, architecture, guides,
reference, and the limitations page last. Example pages are named in kebab case after the program,
reference pages in snake case after the construct.

| Page kind | Public path | Internal source |
|---|---|---|
| **Project index**: what the project is, library or demonstration, its status, how to add or run it, and the route into its examples | `index.md` | the project's or subproject's `README.md` |
| **Examples index**: the examples in teaching order | `examples/index.md` | `examples/README.md` |
| **Example page**: one runnable program or test, as a short tutorial | `examples/<program>.md` | `examples/<program>.md` |
| **Architecture pages**: the project's design, one idea per page, as explanation, with the one-page design as the index | `architecture/index.md`, `architecture/<idea>.md` | `architecture/README.md`, `architecture/<idea>.md` |
| **Guides**: one job per page | `guides/<job>.md` | `guides/<job>.md` |
| **Reference pages**: one page per public construct, for a library | `reference/<kind>/<construct>.md` | split from `reference/<family>.md` |
| **Limitations page**: the high-level limits of the design and status, for a library | `limitations.md` | the README and `architecture/`, never `issues.md` |
| **Comparison page**, for a project that rebuilds a well-known library or practice | named for what it compares against | the project's comparison document |

**An example page needs its internal record first.** Where the internal section has no per-example
document, one is written in this base before the page, because the record holds the run output and
probe results the page quotes. The error backends are the one variation: each crate has a single
walkthrough, which is that crate's `index.md`.

**`issues.md` and `testing.md` have no public page**, and their contents appear on none; a sentence
saying the project is lightly tested is as far as the test record reaches.

**A demonstration project omits the reference and the limitations page.** Nobody depends on
[cgp-examples](../../projects/cgp-examples/README.md)'s crates, so their items are explained where an
example page uses them, and each crate's status is a short section on its index.

The section's own index, `docs/projects/index.md`, is specified in the
[blueprint](../projects/README.md#the-section-index).

## The example page

An example page walks a reader through one program in the **applied register** of
[tutorial.md](tutorial.md#the-two-registers): the program is the subject, CGP is its material, and
the mechanism is linked rather than derived. A reader finishes it in about ten minutes, knowing what
the program does, how its wiring produces that behavior, and the pattern's name.

**It is a guided reading, not a build.** It keeps the tutorial obligations that fit a reading
(destination first, the problem before the solution, a result early, one path, the context's shape
stated) and drops those that assume the reader types every line (each construct introduced by its
need, explicit form before sugar). The *New to CGP?* admonition sends a reader who wants the
construction to the tutorials.

### It is a landing page, so it orients first

**Most readers arrive from a search or a link**, per
[information-architecture.md](../information-architecture.md#most-readers-do-not-arrive-at-the-homepage),
so the first screen does three things before any code:

- **Say what the program does**, in one or two sentences, as the destination.
- **Place it**: one sentence on what the project is, linking the project index, and one clause naming
  Context-Generic Programming in full and linking the Introduction; where the program's point is a
  choice of implementation, relate a short form of the tag line to it, per the
  [naming rule](../../communication-strategy/identity.md#the-name-and-the-tag-line-on-every-page).
- **Offer the prerequisites** in a `:::tip` admonition titled `### New to CGP?`, per the
  [admonition convention](reference.md#conventions-the-port-must-follow): the two or three pages to
  know first, usually Hello World and the Concepts page for the pattern, and that the page can be read
  without them.

### Then it states the problem

**A *The problem* section comes before any of the program's code**, so the walkthrough is not a tour
of machinery. In a few short paragraphs it answers:

- **What is the task?** The program's job in the reader's terms.
- **What makes it hard?** The requirement that turns an easy task into an interesting one.
- **What does it take without CGP?** How a reader would solve it otherwise, and what that costs. Quote
  the plain version where the project keeps one, as `expression` keeps `classic`; otherwise describe
  it in prose, since a sketch shown as code must compile. Omit this part only where no plain
  alternative is worth naming.

**The section is fair to the alternative.** Where plain Rust, a shell script, or Serde's derive is
the right choice for the task as stated, it says so, then names the requirement that tips the balance;
*The pattern* states what the CGP version costs. It never disparages another tool, per
[message.md](../../communication-strategy/message.md). A deliberately trivial program says the task is
trivial and the problem is the program's shape.

### Then it runs the program

**A *Run it* section shows the result before explaining it**: the command, what the machine needs,
and the output the program produced, quoted from a run. Where the record says the program was not
run, or needs network access or a paid key, the page says so instead of implying the output.

Two kinds of program need a different first step:

- **A program the repository has no runner for** gets the smallest test that runs it, as a file the
  reader saves, with the output a probe produced from that exact file. The page states that the
  repository has no test for it as a fact about running it, not as a gap.
- **A crate that only wires**, whose provider bodies are `todo!()`, says so on the first screen and
  opens with *Check it* instead: the check command, and what its passing means.

### Then it walks through the program, one idea per heading

**The body quotes the parts that carry the program's ideas, each under a heading that names the
idea**, not the file, per
[projects/writing-guide.md](../../projects/writing-guide.md#the-shape-of-a-project-section), so the headings in
order summarize how the program works. In each part:

- **Name each construct on first appearance, with a one-clause gloss and a link**: a CGP construct
  to its [reference page](reference.md), a project construct to the project's reference page or, in
  a demonstration crate, explained in place. Leave the grammar to the reference.
- **Say why the code is written this way**, not only what it does.
- **State the context's shape when the program introduces it.** A project context is almost always
  environmental, which a reader who learned from Hello World has not seen, so introduce it as "a type
  that stands for this application, which is where its choices live", per
  [vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target), and
  say whether a component is self-targeted or parameter-targeted where it matters.

### Then it names the pattern

**A *The pattern* section names the CGP design pattern the program shows, when to use it, and what it
costs**, in a paragraph or two, linking the Concepts page that explains it and stating the cost beside
the benefit, per [message.md](../../communication-strategy/message.md). Where the program uses a
pattern past what a smaller program would need, say so.

### A change to try, when one is verified

**Where a small edit shows the pattern working, give it as a *Try a change* section**: swap one wiring
entry and see the output change, or remove one and read the error `cargo cgp check` reports. It also
shows a wiring failure before the reader causes one, per
[tutorial.md](tutorial.md#errors-checking-and-the-tooling).

**Where two pages show neighbouring designs, make the same change on both** and quote both results,
each page linking the other's *Try a change*.

**Every change must have been made and run**, its result recorded in the internal record first and
quoted as produced; a change nobody has run is left out. A page quoting `cargo cgp check` carries the
canonical qualification from
[vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each)
unchanged.

### It closes with a route

**An example page lists no defects or missing features**, even where its record has a *Known issues*
section. A limit of the design the program shows belongs in *The pattern*, as its cost.

**A *Where to go next* section ends every example page** with the next example in teaching order, the
architecture page or guide that develops what the program touched, and the Concepts or tutorial page
for the CGP idea behind it; where a blog post presented the program, a fourth link goes to the post's
section for it, per [Voice, costs, and the source posts](#voice-costs-and-the-source-posts).

### What an example page does not do

- **It does not derive CGP from first principles**: no desugaring, no explanation of a provider
  trait, no coherence argument. This is the rule most easily broken, because the Hypershell and
  cgp-serde posts each carried a CGP primer.
- **It does not document every item the program touches**; it names and links each one.
- **It does not offer alternatives**: one path through one program, per
  [tutorial.md](tutorial.md#what-every-tutorial-owes-its-reader); *Where to go next* links a second
  program that shows another way.

## The project index

**The index makes the case for reading the section.** It states what the project is in two or three
sentences, shows its smallest program with its output, and says who the project is for. It is candid
about status on its first screen: a library to depend on, a proof of concept, or a set of
demonstrations, and the toolchain it needs. Hypershell and cgp-serde call themselves proofs of
concept, and their indexes say so there, not only on the limitations page.

**It then routes**: the example pages in teaching order with one sentence each naming the pattern,
then the architecture pages, guides, reference, and limitations page. It ends with how to add the
crates or clone and run the repository, pinned to the version the pages describe.

## Architecture pages

**An architecture page explains one idea in the project's design, in the explanation shape of
[explanation.md](explanation.md) at a smaller scale**: the question first, the project's code as
illustration, then what the design costs and where to go next. The architecture index states the
whole design on one page and is often the best page for an evaluator. A paragraph true of any CGP
program belongs to the Concepts tier, which the page links instead, per
[projects/writing-guide.md](../../projects/writing-guide.md#leave-cgp-itself-to-cgp).

**Its source is the most internal document in a section**, written for someone about to change the
project, so apply the transformations of
[explanation.md](explanation.md#turning-a-concept-document-into-an-explanation-page) in full:

- **Open with the question an outside reader would ask**, rather than with how the mechanism is built.
- **Introduce one new term at a time**, in plain words, starting from what the reader knows.
- **Leave the machinery out** unless the page is about it: registration paths, lookup internals,
  diagnostic codes, and item inventories belong to the reference and the knowledge base. A table earns
  its place when a user consults it.

**The cost section states trade-offs, not defects**: what the design costs a reader, in their terms,
and when it is worth paying. It never lists open issues or missing features.

## Guides

**A guide does one job, in order, and names the mistakes that job invites.** The internal guides are
already written this way, so the port is mostly re-pointing. A debugging guide keeps each failure's
program, error, and root cause, per the base's
[error-message rule](../../AGENTS.md#show-the-example-behind-an-error-message), with `cargo cgp check`
output quoted as produced.

## Reference pages

**A project reference page documents one construct, completely**, as
[reference.md](reference.md#granularity-one-page-per-named-construct) requires; the port splits each
internal family document, and the project's plan records which pages it feeds. A **construct** is
anything a reader writes, wires, implements, joins, or calls by name: a syntax type, a component (its
consumer trait, provider trait, and key as one), a provider, a namespace, a bundle, a context, a
macro, a public trait, or an adapter type.

**Three kinds of item fold onto another's page**, and each project's reference index routes them in a
*Looking for a name you don't see?* table:

- **Two items that only mean something together** share the page of the one a reader writes: a
  Hypershell syntax type and its interpreting provider, under the syntax type; a `Code` marker and the
  provider wired for it, under the provider.
- **A marker type consumed by one construct** is documented on that construct's page.
- **An error or detail type produced by one provider** is documented on that provider's page.

**Each page follows the component and trait variant of the site reference's
[layered descent](reference.md#the-layered-page)**, with the fields of the internal entry template in
[projects/writing-guide.md](../../projects/writing-guide.md#reference-entries) placed inside it:

1. **A one-sentence summary**, from the entry's opening sentence.
2. **Overview**: the problem the construct solves in the project, with the gloss a newcomer needs.
3. **Definition**: the declaration as the source writes it, bodies elided, each attribute and bound
   explained.
4. **Usage**: the construct in a program or wiring table, and where the project's namespace or bundle
   already wires it.
5. **Behavior**: what it does and how it fails.
6. **Context dependencies**: what a context must supply or wire.
7. **Pairing**: the construct for the other direction of an operation, or that there is none.
8. **When to use it**: the neighbouring construct a reader may have wanted, from the project's guides.
9. **Related constructs**, **The ideas behind it**, linking the CGP reference and Concepts pages, and
   **Source**.

There is no *Under the hood*, since the CGP reference explains a project construct's machinery. A
project's own macro, such as `hypershell!`, follows the macro variant instead: its rewriting rules are
its *Usage*, and the desugared type its *Under the hood*. The front matter follows the reference's
conventions: the construct name as the `h1`, a search-facing `title`, and a `description`.

**Where a defect shapes how a construct is used, state the behavior and route the reader.** A
behavior a reader will meet, including what the construct rejects, goes in *Behavior* as a plain fact,
and *When to use it* sends the reader to the construct that fits: a byte provider whose JSON output it
cannot read back sends JSON users to a text encoding. The page never calls it a bug, lists it as a
known issue, or predicts a fix.

**Enumerate against the source, not the internal tables**; an item a reader can name and cannot find
is a hole.

## The limitations page

**The limitations page states the high-level limits a reader learning the project should know, not
its defects**: that it is a proof of concept, what its design rules out, what it needs to build, what
its errors are like, and what extending it can and cannot do. Write it from the README and the
architecture, each limit in a short section named for what it means to the reader, such as "Programs
are fixed at compile time". Close with where a simpler tool is the better choice, from the comparison
document where there is one.

**Bugs and unimplemented features stay off every public page**, this one included: they stay in
`issues.md`, and a defect listed publicly is out of date the day it is fixed.

**The page shrinks only where a limit stops being true.** Its candor makes the section credible, and
it is the first thing a well-meaning trim removes.

## Front matter and the provenance note

Every Projects page carries a `description` written from its own summary and names Context-Generic
Programming once in its opening paragraph; a directory with a generated index, such as `guides/`,
carries the name in its `_category_.json` description. The `h1` depends on the page kind:

- **An example page** is titled for what the program does, such as *Checksum a web page with a native
  pipeline*, with the program's name, `http_checksum_native`, as its `sidebar_label`.
- **A reference page** is titled with the construct's name, with a search-facing `title`.
- **Every other page** is titled with the words a reader would search: *Hypershell*, *Limitations*.

Sidebar labels carry no backticks, and an apostrophe inside a single-quoted YAML value is doubled, per
[the reference's conventions](reference.md#conventions-the-port-must-follow).

**Every written page closes with the provenance note.** Projects pages are agent-written from this
base, the first level in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md), so they use
the reference's shared sentence. A scaffolded stub carries none, per
[ai-disclosure.md](../../communication-strategy/ai-disclosure.md#linking-to-it-from-a-page). Each project's plan records the level.

## Linking

**A Projects page never links into the knowledge base**, per the
[one-way rule](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#links). Each kind of internal link has a fixed
replacement:

| Internal link target | Public replacement |
|---|---|
| `cgp/reference/…` | the construct's page under `/docs/reference/` |
| `cgp/concepts/…` | the Concepts page of the same name under `/docs/concepts/` |
| `cgp/guides/…` | no page; fold the recommendation into the sentence that needed it |
| `cgp/errors/…` | the matching section of `/docs/reference/errors` |
| `examples/…` (a worked example) | the tutorial carrying the scenario, or the Projects example page that shows it |
| `related-work/…` | the comparison page under `/docs/comparisons/` |
| another document in the project's section | its page in the project section, or nothing if it has no public page |
| another project's section | that project's page in the Projects section |
| `website/blog/…` (a post's record) | the live post |
| `communication-strategy/…` | dropped |

**A page that is not written is neither linked nor scaffolded as a stub.** A written page describes
the idea in place, or names the page as still being written without linking it, and gains the link
when the page exists, so the sidebar shows only usable pages. This differs from the site reference,
whose completeness obligation made a stub for every construct.

Links out of the site go to the project's repository on its default branch, the crate on crates.io or
docs.rs, and the documentation of the external libraries it builds on. A mention of `cargo cgp check`
links `/docs/cargo-cgp/check`, not the tool's repository.

## Code on a Projects page

**A Projects page quotes the project's own code, at the revision its plan names, and never a blog
post's.** Verify each snippet against the source and by running the program, and quote output and
diagnostics as produced.

**Projects pages are not mirrored in the website's `example-code` crate**, because the project's
repository already compiles its code, and the projects need what the crate lacks, such as
Hypershell's nightly toolchain and network-bound backends; the rule is in
[AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#code).

**Quote `cargo-cgp` output from the tool built at its current source**, which is the release the site
documents, so a pre-release on crates.io is neither quoted nor compared against, per the base's
[rule on versions](../../AGENTS.md#document-official-versions-never-pre-releases). Re-check the quoted
output when the tool releases.

**The code uses current idioms.** Where the project's source uses a form the
[guides](../../cgp/guides/README.md) tell readers to replace, the change is made in the project first
and the plan records it as a prerequisite. Until then, a page can describe a construct whose
declaration carries such a form by showing the method signature a reader calls or implements, without
quoting the declaration.

**Install instructions name a published version** built against the `cgp` version the site
describes. Where none exists, the page gives the git dependency and says why, or waits; the plan
records which.

## Voice, costs, and the source posts

**The pages use the project voice.** Material from the author-voice posts converts by grounding a
judgement rather than attributing it, keeping its uncertainty; personal history, such as how a
project got its name, stays on the blog and is linked.

**Every project index states the costs a reader would look for**: the toolchain, the compile time
where it is known, what the diagnostics look like when the wiring is wrong, and that the project is a
proof of concept where it is one. Never state a benchmark, compile time, or adoption claim the
project has not measured.

**Each post that presents a project gets a notice at its top pointing to the section, and each example
page links the post back.** The notice is the one sanctioned edit to a published post, per
[AGENTS.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/AGENTS.md#blog-posts): it adds a link and changes no claim. The plan names
the posts. The link back sits in *Where to go next*, at the post's section for the program where there
is one, and says the post's code predates the current design where it does.

**The notice goes on each post that presents a project or a feature its pages document**, once that
section is written: the post the section grew out of, the series posts that explain the feature's
internals, and a talk that used the project as its demonstration. Place it directly under the front
matter, or under the post's title where it has one, so the blog's excerpt shows it. Write it in the
project voice, say where the code predates the current design, and link the project section and its
Concepts page.

## What must not be on a Projects page

- **No link into the knowledge base**, and no internal vocabulary without a gloss.
- **No CGP primer**: one sentence of orientation and a link.
- **No bugs, missing features, or housekeeping**: defects, unimplemented features, stale metadata,
  unused items, and missing rustdoc stay in `issues.md`.
- **No dated framing**: no "this release", "recently", or version number attached to a behavior.
- **No speculation**; future work is left out.
- **No invented numbers**, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md).

## Checking a draft

- **Open an example page cold.** Within the first screen, a reader who has never heard of CGP knows
  what the program does, what the project is, and where to find background.
- **Read every `New to CGP?` box on its own.** Each links at least one CGP page, not only earlier
  project pages.
- **Check each example page's closing links**: the next example, a project page that develops the
  idea, and a Concepts or tutorial page.
- **Find the problem**: a *The problem* section before the code, fair to the alternative.
- **Read only the headings of an example page**; they summarize how the program works.
- **Find the pattern and its cost**, with a link to the page that explains it.
- **Run what the page runs**: every command, output, and *Try a change* result matches a run against
  the revision the plan names.
- **Search for knowledge-base links and unglossed terms**, including "context" on first use.
- **Check the front matter and the foot**: a `description`, the right kind of `h1`, and the provenance
  note.
- **Check the reference against the source**, one page per construct, with every folded name in the
  lookup table.
