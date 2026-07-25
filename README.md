# The CGP Knowledge Base

Context-Generic Programming (CGP) is a language extension for Rust, with pluggable trait
implementations at compile-time. In ordinary Rust a trait has one implementation per type; CGP lets
one trait have many interchangeable implementations and lets each context choose which one it uses,
through a small wiring table the compiler resolves statically — so the flexibility costs nothing at
runtime. It is an ordinary library on stable Rust that desugars to plain traits and impls, adopted
one component at a time, and it reaches beyond swappable implementations to abstract types each
context picks for itself, extensible records and variants, and a family of composable handlers.

This repository is the **consolidated knowledge base for every project in the CGP ecosystem**,
written by and for AI coding agents. Its purpose is to be the one place an agent goes to learn and to
record what is known about CGP — the full semantics of every construct, the internals of the
toolchain that reads CGP errors, the worked examples, the comparisons with related paradigms, and the
strategy for writing about CGP publicly. Each member project keeps its code; the documentation for
all of them lives here.

## Why this exists

CGP's behavior is recorded as much in prose as in code, and the code is a poor place to learn it
from. CGP is implemented almost entirely as procedural macros, so an agent reading the macro source
sees token-stream manipulation and AST transforms rather than the meaning those transforms produce —
"`#[cgp_component]` generates a consumer trait, a provider trait, and two blanket impls that connect
them" has to be reconstructed by mentally running the macro. The same holds for the toolchain:
reading `cargo-cgp`'s two binaries tells you what each function does, not why the split exists or
what the compiler hides from a diagnostic. This knowledge base captures those reconstructions once,
in prose, so the next agent reads the conclusion instead of re-deriving it.

Gathering them into one repository answers a second problem. The documentation used to live inside
each project, which meant an agent had to discover it repository by repository, every cross-project
reference was a fragile URL into someone else's tree, and the same conventions were restated in
several places and drifted apart. One base gives one place to look, one set of authoring rules, and
one home for the relationships *between* projects — the error classes `cgp` produces and `cargo-cgp`
reshapes, for instance, are now two directories apart rather than two repositories apart.

The knowledge base is also a contract. When an agent changes how a macro expands or how the tool
presents an error, the matching document is where the intended new behavior is stated in plain
language, so a reviewer can compare the prose against the code. Documentation that drifts out of
sync with the code is worse than none, which is why keeping it accurate is part of the change that
made it stale rather than a follow-up — see [AGENTS.md](AGENTS.md) for that rule and the rest of the
authoring conventions.

## How it is organized

The base holds two kinds of top-level directory: one per **member project**, documenting that
project's own subject, and one per **cross-cutting section**, holding material that belongs to the
ecosystem rather than to any single project. A member directory is the home of everything specific to
its project and is verified against that project's source; a cross-cutting directory draws on all of
them. Each directory carries a `README.md` that catalogs its contents and, where it needs rules of
its own, an `AGENTS.md`.

### `cgp/` — the CGP library

[cgp/](cgp/README.md) documents the CGP language extension itself: what each construct means, what
code it expands to, and how the macros that produce it are built. It is the largest section, and it
divides into five parts — [reference/](cgp/reference/README.md), one self-contained document per
construct and the ground truth to read before writing CGP; [concepts/](cgp/concepts/README.md), the
cross-cutting overviews that span several constructs; [guides/](cgp/guides/README.md), which is
prescriptive where the other two are descriptive and directs the choice between constructs;
[errors/](cgp/errors/README.md), the catalog of the compiler errors CGP produces *after* codegen,
organized by kind and built around whether the compiler surfaces or hides each cause; and
[implementation/](cgp/implementation/README.md), the macro internals plus every pointer into the test
suite.

### `cargo-cgp/` — the CGP toolchain

[cargo-cgp/](cargo-cgp/README.md) documents the cargo subcommand that makes CGP's compiler errors
readable and shows the Rust that CGP macros generate. [reference/](cargo-cgp/reference/README.md) is
the usage side — installing the tool, running its commands, diagnosing one that will not run;
[implementation/](cargo-cgp/implementation/README.md) is the internals, from the two-executable split
and the `rustc_driver` wrapping to the typed resolver that turns a wiring failure into a dependency
tree; [issues/](cargo-cgp/issues/README.md) tracks the gaps the tool has not yet closed, each backed
by a fixture that reproduces it; and [error-code.md](cargo-cgp/error-code.md) catalogs the
`[CGP-Exxx]` codes it stamps on the messages it rewrites.

### `examples/` — worked examples

[examples/](examples/README.md) holds self-contained worked examples, one realistic use case developed
end to end per document, from its contexts and components through to the wiring that connects them.
They sit at the top level because they serve the whole base rather than one member: they are the
canonical source of the code snippets the reference, concept, guide, and related-work documents reuse,
so the same running scenarios recur everywhere a reader looks.

### `related-work/` — CGP against the ideas it resembles

[related-work/](related-work/README.md) looks outward instead of inward. Each document takes an
external concept, framework, or language feature that resembles CGP — dependency injection, implicit
parameters, type classes, algebraic effects, row polymorphism, ML modules, reflection, dynamic
dispatch — explains it faithfully and with citations, weighs what its users like and dislike about it,
and positions CGP against it. They exist to serve future user-facing writing, giving an agent who must
explain CGP to readers of a particular background the honest comparison to build on.

### `communication-strategy/` — writing about CGP in public

[communication-strategy/](communication-strategy/README.md) turns that outward-facing material into
guidance for *presenting* CGP — landing pages, tutorials, articles, blog posts, threads. Where a
related-work document compares CGP to one external idea, a communication-strategy document generalizes
across those comparisons into audience-level strategy: which readers exist and what each already
believes, which hooks earn attention, which misunderstandings CGP reliably provokes, and what
vocabulary keeps everything written about CGP reading as one voice.

## Finding your way in

Four files at the top level orient an agent before it opens any section. Read them in this order and
you know what exists, what the rules are, and where the code lives.

- [summary.md](summary.md) — a one-line summary of **every** markdown file in the base, deeply
  nested ones included. Read it first: it is the fastest way to learn the whole contents at once and
  to pick the handful of documents a task actually needs.
- [AGENTS.md](AGENTS.md) — the authoring and maintenance rules every document here is bound by,
  consolidated from the member projects: the synchronization rule, the prose style, how a document
  registers itself, and how cross-project references are written.
- [sibling-projects.md](sibling-projects.md) — the member projects, their repositories, and the
  revision of each to read, plus the rule for finding a sibling locally versus linking to it.
- Each directory's own `README.md` — the catalog of that section, and the place a new document
  registers itself.

## The projects it documents

The knowledge base currently documents three member projects, and the list will grow as the
ecosystem does. [`cgp`](https://github.com/contextgeneric/cgp) is the library — the proc-macro suite
and the runtime crates its expansions target. [`cargo-cgp`](https://github.com/contextgeneric/cargo-cgp)
is the first-class toolchain that rewrites CGP compile errors and expands CGP macros.
[`cgp-skills`](https://github.com/contextgeneric/cgp-skills) holds the agent skills built *from* this
base — the `/cgp` skill an agent loads before reading or writing CGP code — which live in their own
repository because a skill is deployed on its own and may not link back to anything here.
[sibling-projects.md](sibling-projects.md) records where each one lives; adding a member means adding
it there, giving it a directory here if it needs one, and registering that directory in this README.

## How to use it

An agent working on CGP reads two things before it acts: the `/cgp` skill, for the mental model and
the vocabulary the whole base assumes, and the document that owns whatever it is about to touch. The
skill and the knowledge base are complementary rather than redundant — the skill teaches how to read
and write CGP, while the documents here carry the exhaustive per-construct semantics, the internals,
and the corner cases the skill deliberately omits. Read the two together: the skill for the shape of
the forest, a reference document for the individual tree.

Which document that is depends on the task, and [summary.md](summary.md) is the index that answers
it. Understanding or changing a construct means its reference document; changing the macro that
implements it means its implementation document too; debugging a compile error means the error
catalog and the guides; explaining CGP to someone means the related-work document for their
background and the communication-strategy guidance for the format. When a task spans projects — a
diagnostic change that touches both a `cgp` construct and a `cargo-cgp` fixture — read both members'
documents, because keeping them in step is part of the change.
