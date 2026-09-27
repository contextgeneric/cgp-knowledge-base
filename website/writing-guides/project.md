# Writing the Projects section

The Projects section documents the libraries and demonstration programs built with CGP, one section
per project, and their main job is to **teach CGP's design patterns through code that runs**. Each
section is ported from the project's section under [projects/](../../projects/README.md), the way
the reference is ported from [cgp/reference/](../../cgp/reference/README.md), and its example pages
are expanded into short tutorials rather than ported line for line.

- **Where they live** — `docs/projects/<project>/`, one directory per project, under a `Projects`
  category with a hand-written index
- **Voice** — project voice, with the teaching "we" allowed on example pages, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md)
- **Derived from** — the project's section under [projects/](../../projects/README.md), which stays
  the source of truth
- **Plans and records** — [../projects/README.md](../projects/README.md) for the section, and one
  document per project beside it

## What the section is for

The section serves two readers at once, and the page kinds below exist to keep them apart. **The
pattern learner** wants to see a CGP idea working in a program that does something real: a namespace
assembling a language, a per-type table choosing a JSON encoding, a builder merging subsystems. The
Concepts pages explain those ideas with deliberately small code, and the tutorials build them up
from a rectangle. What neither shows is the idea inside a system someone would actually write, and
that is what the example pages are for. **The evaluator** wants evidence that CGP holds up beyond a
toy. For that reader the section is the project's social proof, per
[evidence.md](../../communication-strategy/evidence.md), and its value depends on the pages being
candid about what each project is.

So the examples carry the section. A project's reference, architecture, and guide pages exist so
that an example page can name a construct and link to its full account, and so that a reader who
adopts the project has somewhere to look things up. **Write and publish a project's example pages
first**, and give them the most care.

## Ported, with one expansion

**Every page except an example page is a port.** The internal documents already carry the
information, verified against the project's source. They are wrong for a public reader in the same
ways the internal reference is, so the same four transformations apply as in
[reference.md](reference.md#derived-from-the-internal-reference-and-kept-in-step-with-it):

- **Re-point every link**, per [Linking](#linking) below. The internal documents link into `cgp/`,
  `examples/`, and each other, and a public page may link none of those.
- **Drop the internal records.** The header fields that record the documented branch and local
  checkout, everything in `issues.md` and `testing.md`, the probes, the "Public material derived
  from this" line, and every sentence addressed to an agent maintaining the project stay in the
  knowledge base.
- **Orient a reader who does not know CGP.** The internal documents assume the `/cgp` skill. A
  public page glosses "context", "provider", and "wiring" on first use, and links the page that
  explains each.
- **Convert source links** to the project's repository on its default branch, since that is where
  the published code lives.

**An example page is an expansion instead.** The internal example document is a record: it quotes
the parts of a program that carry its ideas, says what running it produced, and lists its defects.
The public page keeps the program and what running it produced, leaves the defects in the record,
and adds what a record leaves out: an introduction for a reader new to CGP, the reason each part is
written the way it is, the name of the pattern it shows, and a route onward. It is the one page kind
in the section that is written rather than transformed, which is why it is specified in the most
detail below.

## The page kinds

A project section is built from seven kinds of page. The file paths mirror the internal section
wherever it has a matching document, so the mapping from a public page to its source is visible from
the path.

- **The project index** (`index.md`) — what the project is, whether it is a library or a
  demonstration, its status, how to add or run it, and the route into its examples. Ported from the
  project's `README.md`.
- **Example pages** (`examples/*.md`) — one page per runnable program or test, each a short
  tutorial. Expanded from the project's `examples/` documents; where the internal section has no
  per-example document, one is written there first, per the
  [blueprint](../projects/README.md#how-a-page-maps-to-its-source). The error backends are the one
  variation: each crate has a single walkthrough, and it is that crate's `index.md`.
- **Architecture pages** (`architecture/*.md`) — the project's own design, one idea per page,
  written as explanation. Ported from `architecture/`.
- **Guides** (`guides/*.md`) — one job per page: writing a program, adding a provider, debugging the
  wiring. Ported from `guides/`.
- **Reference pages** (`reference/**/*.md`) — one page per public construct, for a library a reader
  depends on. Split from the family documents in `reference/`.
- **The limitations page** (`limitations.md`) — the high-level limits of the project's design and
  status, for a library. Written from the project README and the architecture, not from `issues.md`.
- **A comparison page**, named for what it compares against — for a project that rebuilds a
  well-known library or practice, such as cgp-serde against Serde. Ported from the project's
  comparison document.

Above the projects sits one more page, the **section index** at `docs/projects/index.md`, which
introduces the projects and routes a reader from a pattern to the example page that shows it. Its
contents are specified in the [blueprint](../projects/README.md#the-section-index) rather than here,
since there is only one.

`issues.md` and `testing.md` have no public page, and their contents do not appear on any. A
project's defects, missing features, and test gaps are records for the people working on it; a
public reader learning the project needs only the high-level limits, as [The limitations
page](#the-limitations-page) describes. A sentence saying the project is lightly tested is as far as
the test record reaches.

**A demonstration project omits the reference and the limitations page.** Nobody depends on the
crates in [cgp-examples](../../projects/cgp-examples/README.md), so a reference for their items
would document names no reader types, and the limits worth stating fit in a sentence on the index.
Their items are shown and explained where an example page uses them, and a crate's status goes in a
short section on its index.

## The example page

An example page takes one program from the project and walks a reader through it as a short tutorial
in the **applied register** of [tutorial.md](tutorial.md#the-two-registers): the subject is the
program, CGP is the material it is built from, and the mechanism is linked rather than derived. A
reader should finish it in about ten minutes, knowing what the program does, how its wiring produces
that behavior, and the name of the CGP pattern it shows.

**An example page is not a tutorial, and the difference decides its shape.** A tutorial builds a
program from nothing, one step at a time, so the reader types every line. An example page starts
from a program that already exists and runs, and guides the reader through it in the order its ideas
make sense. So it borrows the tutorial's obligations that fit a guided reading (destination first, a
result early, one path, the context's shape stated), and it drops the ones that assume the reader is
building (problem before construct, explicit form before sugar). A reader who wants the construction
goes to the tutorials; the *New to CGP?* admonition below is how the page sends them there.

### It is a landing page, so it orients first

**Most readers arrive at an example page from a search result or a link, not from the section
index**, per
[information-architecture.md](../information-architecture.md#most-readers-do-not-arrive-at-the-homepage).
The first screen therefore does three things before any code:

- **Say what the program does**, in one or two sentences, as the destination: "This program
  downloads a web page and prints its SHA-256 digest, with every stage of the pipeline written as a
  Rust type."
- **Place it**: one sentence on what the project is, linking the project index, and one clause on
  what CGP is, linking the Introduction.
- **Offer the prerequisites** in a `:::tip` admonition titled `### New to CGP?`, per the [admonition
  convention](../site-structure.md#conventions-the-port-must-follow). It names the two or three
  pages a reader should know before this one (usually Hello World and the Concepts page for the
  pattern the example shows) and says that the page can be read without them. That admonition is the
  "short introduction together with links" every example page owes, and it is what lets a reader who
  has never seen CGP know where to look next.

### Then it runs the program

**Show the result before explaining it.** A *Run it* section gives the command, what the machine
needs, and the output the program actually produced, quoted from a run rather than remembered. Where
the internal record says the program was not run, or needs network access or a paid key, the page
says so plainly instead of implying the output.

Two kinds of program need a different first step, and the `expression` and `web-app` pilots settled
both:

- **A program the repository has no runner for**, such as a context with no test, gets the smallest
  test that runs it, given as a file the reader saves, with the output a probe produced from that
  exact file. The page says the repository has no test for it, as a fact about how to run it, not as
  a gap.
- **A crate that only wires**, whose provider bodies are `todo!()`, has nothing to run, so its pages
  say so on the first screen and open with *Check it* instead: the check command, and what its
  passing means for the stage on the page.

### Then it walks through the program, one idea per heading

**The body quotes the program in the parts that carry its ideas, each under a heading that names the
idea** rather than the file: "Every stage is a type", "One table decides the encoding", "The context
joins the language in one line". This follows the internal convention in
[projects/AGENTS.md](../../projects/AGENTS.md#the-shape-of-a-project-section), and it is what makes
the page scannable: the headings in order summarize how the program works.

Three rules govern each part:

- **Name each construct the first time it appears, with a one-clause gloss and a link.** A CGP
  construct links its [reference page](reference.md); a project construct links the project's own
  reference page, or, for a demonstration crate, is explained where it first appears. Do not explain
  the construct's grammar; that is the reference's job.
- **Say why the code is written this way**, not only what it does. "The context has no fields,
  because every choice it makes is in its wiring" teaches the pattern; "`HypershellCli` is an empty
  struct" only describes the code.
- **State the context's shape when the program introduces it.** Almost every project program wires
  an **environmental context**, which is the shape a reader who learned from Hello World has not
  seen, so the first context on the page is introduced as "a type that stands for this application,
  which is where its choices live", per
  [vocabulary.md](../../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target). Say
  whether a component is self-targeted or parameter-targeted when the difference matters to the code
  on the page.

### Then it names the pattern

**A section titled *The pattern* says, in a paragraph or two, which CGP design pattern the program
demonstrates, when a reader would use it, and what it costs.** This section is what turns a
walkthrough into a tutorial: the reader leaves with a named technique they can apply elsewhere. Link
the Concepts page that explains the pattern, and state its cost beside its benefit, per
[message.md](../../communication-strategy/message.md). Where the program uses a pattern past the
point a smaller program would need it, as a demonstration often does, say so.

### A change to try, when one is verified

**Where a small edit shows the pattern working, give it as a *Try a change* section.** Swapping one
wiring entry and seeing the output change, or removing one and reading the error `cargo cgp check`
reports, is the fastest way for a reader to believe the pattern rather than take it on trust. It
also discharges the tutorial obligation to show a wiring failure before the reader causes one, per
[tutorial.md](tutorial.md#errors-checking-and-the-tooling).

**Where two pages show neighbouring designs, make the same change on both.** Removing one entry from
a coarse-grained context and from its fine-grained successor, and quoting both errors, shows what the
split buys more directly than any sentence can; each page links the other's *Try a change*.

Every such change must have been made and run, and its output quoted as it was produced. The
internal record is where that result is recorded first; a change nobody has run is left out rather
than described. When the page quotes `cargo cgp check`, it carries the canonical qualification from
[vocabulary.md](../../communication-strategy/vocabulary.md#terms-to-use-and-how-to-introduce-each)
unchanged.

### It closes with a route

**An example page does not list defects or missing features**, even where the internal record for
the program has a *Known issues* section. A limit of the design that the program shows, such as a
program being fixed at compile time, belongs in *The pattern*, as its cost.

**A *Where to go next* section** ends every example page with three kinds of link: the next example
in the project's teaching order, the architecture page or guide that develops what this program
touched, and the Concepts or tutorial page for the CGP idea behind it. A page that ends without
routing has dropped its reader, per
[information-architecture.md](../information-architecture.md#most-readers-do-not-arrive-at-the-homepage).

### What an example page does not do

**It does not derive CGP from first principles.** No desugaring section, no explanation of what a
provider trait is, and no coherence argument. Those belong to the tutorials and the Concepts pages,
and the `New to CGP?` admonition is where the page sends a reader who needs them. This is the rule
most easily broken, because the blog posts that first presented Hypershell and cgp-serde each
carried a CGP primer; a Projects page teaches its own program and nothing else.

**It does not document every item the program touches.** It names each construct and links it. A
reader who needs a provider's every bound follows the link.

**It does not offer alternatives.** One path through one program, per
[tutorial.md](tutorial.md#what-every-tutorial-owes-its-reader). Where the project has a second
program showing another way, the *Where to go next* section links it.

## The project index

**The index is a real page that makes the case for reading the section.** It states what the project
is in two or three sentences, shows its smallest program with the output it produces, and says who
the project is for. Then it is candid about status: whether the project is a library a reader can
depend on, a proof of concept, or a set of demonstrations, and which toolchain it needs. Hypershell
and cgp-serde describe themselves as proofs of concept, and the index must say so on its first
screen rather than on the limitations page alone.

It then routes. **List the example pages in teaching order with one sentence each, naming the
pattern each shows**, then the architecture pages, the guides, the reference, and the limitations
page. It ends with how to add the crates or clone and run the repository, pinned to the version the
pages describe.

## Architecture pages

**An architecture page explains one idea in the project's design, and follows the explanation shape
of [explanation.md](explanation.md) at a smaller scale.** Open by naming the question the page
answers, explain the idea with the project's code shown as illustration, and close with what the
design costs and where to go next. The architecture `README.md` in the internal section, which
states the whole design on one page, becomes the architecture index, and it is often the best single
page in the section for an evaluator.

A paragraph that would be true of any CGP program belongs to the Concepts tier, and the page links
there instead, per the rule the internal documents already follow in
[projects/AGENTS.md](../../projects/AGENTS.md#leave-cgp-itself-to-cgp).

**An architecture page is the easiest page to leave looking internal, because its source document is
the most internal of all.** An internal architecture document is written for someone about to change
the project: it opens with the mechanism, names every item, and records where the design is
incomplete. Ported as it stands, it reads as a maintainer's notes. Apply the three transformations
of [explanation.md](explanation.md#turning-a-concept-document-into-an-explanation-page) in full:

- **Open with the question an outside reader would ask**, such as "how does one line give a context
  the whole language?", and answer it, rather than opening with how the mechanism is built.
- **Introduce one new term at a time**, in plain words, before using it: a bundle, a namespace, an
  input dispatcher. Start from what the reader knows, such as a shell pipeline or a generic impl.
- **Leave the machinery out** unless the page is about it: registration paths, lookup internals,
  diagnostic codes, and item-by-item inventories belong to the reference and the knowledge base. A
  table earns its place when a user consults it, as the table of what each stage accepts does.

**The cost section states trade-offs, not defects.** Say what the design costs a reader, in their
terms, and when the cost is worth paying, the way the site's Concepts pages do: "the layers make the
language easy to reuse and harder to trace". A cost section never lists the project's open issues or
missing features; those stay in the knowledge base.

## Guides

**A guide does one job, in order, and names the mistakes that job invites.** The internal guides are
already written this way, so the port is mostly re-pointing. A debugging guide keeps each failure's
program, the error it produces, and the root cause, per the base's [error-message
rule](../../AGENTS.md#show-the-example-behind-an-error-message), and quotes `cargo cgp check` output
as it was produced.

## Reference pages

**A project reference page documents one construct, completely**, which is the rule the site
reference follows in [reference.md](reference.md#granularity-one-page-per-named-construct). The
internal reference groups each family into one document, so the port splits it: one internal family
document feeds several public pages, and the project's plan records which.

A **construct** here is anything a reader writes, wires, implements, joins, or calls by name: a
syntax type, a component (whose consumer trait, provider trait, and key are one construct), a
provider, a namespace, a bundle, a context, a macro, a public trait, or an adapter type. Three kinds
of item do not get a page of their own, and each project's reference index carries a *Looking for a
name you don't see?* table that routes them:

- **Two items that only mean something together** share the page of the one a reader writes. A
  Hypershell syntax type and the provider that interprets it are one page, under the syntax type's
  name, which is the adaptation the internal reference already makes. A `Code` marker and the
  provider wired for it are one page under the provider's name.
- **A marker type consumed by one construct**, such as Hypershell's HTTP method markers, is
  documented on that construct's page, as the site reference documents `IsPresent` with `MapType`.
- **An error or detail type produced by one provider** is documented on that provider's page.

**Each page follows the variant of the site reference's [layered
descent](reference.md#the-layered-page) that its component and trait pages use**, with the fields of
the internal entry template in [projects/AGENTS.md](../../projects/AGENTS.md#reference-entries)
placed inside it, so that a beginner can stop early and an agent porting a page knows where each
internal field lands:

1. **A one-sentence summary**, from the entry's opening sentence.
2. **Overview** — the problem the construct solves in the project, with the gloss a newcomer needs.
3. **Definition** — the declaration as the source writes it, bodies elided, with each attribute and
   bound explained. From the entry's Definition.
4. **Usage** — the construct in a program or a wiring table, with a short example, and where the
   project's namespace or bundle already wires it for the reader.
5. **Behavior** — what it does and how it fails, from the entry's Behavior.
6. **Context dependencies** — what a context must supply or wire for the construct to work.
7. **Pairing** — where the project has both directions of an operation, the construct for the other
   direction, or that there is none.
8. **When to use it** — which neighbouring construct a reader may have wanted instead, drawn from
   the project's guides, which have no other public home for that judgement.
9. **Related constructs**, **The ideas behind it**, linking the CGP reference and Concepts pages the
   construct rests on, and **Source**.

There is no *Under the hood*, since a project construct's machinery is the CGP construct it is built
from and the CGP reference already explains it. The one exception is a project's own macro, such as
`hypershell!`, whose page follows the macro variant instead: its rewriting rules are its *Usage*,
and the desugared type is its *Under the hood*. The front-matter conventions are the reference's:
the construct name as the `h1`, a search-facing `title`, and a `description`, per
[site-structure.md](../site-structure.md#conventions-the-port-must-follow).

**Where a defect shapes how a construct is used, state the behavior and route the reader.** A
reference page must describe what the construct does, including what it rejects, so a behavior a
reader will meet goes in *Behavior* as a plain fact, and *When to use it* sends the reader to the
construct that fits their case: a byte provider whose JSON output it cannot read back sends JSON
users to a text encoding. The page never calls the behavior a bug, lists it as a known issue, or
predicts a fix; the defect record stays in `issues.md`.

**Enumerate against the source, not against the internal tables.** The internal tables are complete
as far as the last documenting pass found, and a public reference carries the site reference's
completeness obligation: an item a reader can name and cannot find is a hole.

## The limitations page

**The limitations page states the high-level limits a reader learning the project should know, not
its defects.** Those are the limits that follow from what the project is and how it is designed:
that it is a proof of concept, what its design rules out, what it needs to build, what its errors
are like, and what extending it can and cannot do. Write it from the project README and the
architecture, each limit in a short section named for what it means to the reader, such as "Programs
are fixed at compile time".

**Bugs and unimplemented features stay out of every public page**, this one included. They are the
project's records, kept in `issues.md` for the people fixing them, and they change too often to
publish: a defect listed publicly is out of date the day it is fixed. A reader who meets one reports
it, and the page loses nothing by not predicting it.

Close with where a simpler tool is the better choice, drawn from the comparison document where there
is one, because that is the question an evaluator reading this page is asking.

**The page must not shrink as the project matures except where a limit stops being true.** The
candid account of costs is what makes the rest of the section credible, and it is the first thing a
well-meaning trim removes.

## Front matter and the provenance note

Every Projects page carries a `description` written from its own summary, as every site page does,
per [site-structure.md](../site-structure.md#conventions-the-port-must-follow). The `h1` depends on
the page kind:

- **An example page** is titled for what the program does, as a tutorial is titled for an outcome:
  *Checksum a web page with a native pipeline*. Its `sidebar_label` is the program's name,
  `http_checksum_native`, which is what a reader who has cloned the repository looks for.
- **A reference page** is titled with the construct's name, and carries a search-facing `title`.
- **Every other page** is titled with the words a reader would search: *Hypershell*, *Limitations*,
  *Choosing an error backend*.

Sidebar labels carry no backticks, and an apostrophe inside a single-quoted YAML value is doubled,
per the same conventions.

**Every written page closes with the provenance note.** Projects pages are agent-written from this
base, which is the first level in [ai-disclosure.md](../../communication-strategy/ai-disclosure.md),
so they use the reference's shared sentence and link the same section of the disclosure page. A
scaffolded stub carries none, per [AGENTS.md](../AGENTS.md#disclosing-ai-use-on-a-page). Each
project's plan records the level when its pages land.

## Linking

**A Projects page may never link into the knowledge base**, per the [one-way
rule](../AGENTS.md#the-one-way-link-rule), and the internal documents are made of such links. Each
kind of internal link has a fixed public replacement:

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

**A page that is not written yet is not linked, and is not scaffolded as a stub.** A reader arriving
at a placeholder from inside a tutorial has been sent nowhere, so a written page describes the idea
in place, or names the page as still being written without linking it, and gains the link when the
page exists. The section's sidebar then shows only pages a reader can use. This differs from the
site reference, whose completeness obligation made a stub for every construct worth having.

Links out of the site go to the project's repository on its default branch, to the crate on
crates.io or docs.rs, and to the documentation of external libraries the project builds on. A
mention of `cargo cgp check` links the site's page for it, `/docs/cargo-cgp/check`, rather than the
tool's repository.

## Code on a Projects page

**A Projects page quotes the project's own code, taken from its repository at the revision the page
describes, and never from a blog post.** The project's plan names that revision. Verify each snippet
by comparing it with the source and by running the program, and quote output and diagnostics as they
were produced.

**Projects pages are not mirrored in the website's `example-code` crate.** That crate verifies code
written for the site, and a project's code is already compiled by its own repository; a second copy
would be one more thing to keep in step. The projects also need what the crate does not carry, such
as Hypershell's nightly toolchain and its network-bound backends. The rule and its reason are
recorded in [AGENTS.md](../AGENTS.md#verify-code-against-current-cgp-and-never-against-a-blog-post).

**Quote `cargo-cgp` output from the tool built at its current source**, the same output the site's
compile errors page documents, and record in the example's internal document where the published
release prints something different. The published v0.1.0-alpha reports a missing dispatcher entry as
`[CGP-E107]` where the source reports `[CGP-E110]`, for instance, and a reader running the release
will see the first. Re-check the quoted output when the tool releases.

**The code must use current idioms.** Where the project's source still uses a form the
[guides](../../cgp/guides/README.md) tell readers to replace, the page does not publish it: the
change is made in the project first, and the plan records it as a prerequisite. Showing a legacy
form on a page that exists to teach patterns would teach the wrong one.

A page that needs to explain a construct whose declaration still carries such a form can describe
it without quoting the declaration, by showing the method signature a reader calls or implements,
until the project change lands and the construct's own page is written.

**Install instructions name a published version.** A page that tells a reader to add a project's
crates names a release built against the `cgp` version the site describes. Where no such release
exists, the page gives the git dependency and says why, or the page waits; the project's plan
records which.

## Voice, costs, and the source posts

The pages use the **project voice**. The blog posts that first presented each project are in the
author's voice, and material taken from them converts by grounding judgement rather than attributing
it: "the learning curve falls on the people extending the language rather than the people using it"
keeps a claim and drops the "I think". Uncertainty stays as uncertainty. Personal history, such as
how a project got its name, stays on the blog and is linked.

**Every project index states the costs a reader would look for**: the toolchain the project needs,
how long it takes to compile where that is known, what the diagnostics look like when the wiring is
wrong, and that the project is a proof of concept where it is one. Never state a benchmark, a
compile time, or an adoption claim the project has not measured.

**When a project section is published, a pointer to it goes at the top of the blog post it grew out
of.** That is the one sanctioned edit to a published post, settled in
[AGENTS.md](../AGENTS.md#do-not-rewrite-history): it adds a link and changes no claim. The project's
plan names the posts that get one.

## What must not be on a Projects page

- **No link into the knowledge base**, and no internal vocabulary without a gloss.
- **No CGP primer.** One sentence of orientation and a link; the explanation belongs to the
  tutorials and Concepts.
- **No bugs, missing features, or housekeeping.** Defects, unimplemented features, stale metadata,
  unused items, and missing rustdoc are records for the project's maintainers, kept in `issues.md`.
- **No dated framing**: no "this release", no "recently", no version number attached to a behavior.
  The pages describe the project as it is and are corrected in place.
- **No speculation.** Future work is left out.
- **No invented numbers**, per
  [voice-and-register.md](../../communication-strategy/voice-and-register.md).

## Checking a draft

- **Open an example page cold.** Within the first screen, does a reader who has never heard of CGP
  know what the program does, what the project is, and where to go if they need background?
- **Read every `New to CGP?` box on its own.** Each must link at least one CGP page, usually the
  Hello World tutorial and the Concepts page for the pattern, not only the earlier examples it
  builds on. A box that routes only to other project pages leaves the CGP newcomer where it found
  them.
- **Check each example page's closing links**: the next example, a page of the project's own that
  develops the idea, and a Concepts or tutorial page.
- **Read only the headings of an example page.** They should summarize how the program works.
- **Find the pattern and its cost.** Every example page names one pattern, links the page that
  explains it, and states what it costs.
- **Run what the page runs.** Every command, output, and *Try a change* result matches a run against
  the revision the plan names.
- **Search for knowledge-base links and unglossed terms**, including "context" on its first use.
- **Check the front matter and the foot**: a `description`, the right kind of `h1`, and the
  provenance note.
- **Check the reference against the source**, one page per construct, with every folded name in the
  lookup table.
