# Ecosystem projects

This directory documents the projects that **use** CGP without being part of it. Where
[cgp/](../cgp/README.md) and [cargo-cgp/](../cargo-cgp/README.md) document the language extension and
its toolchain, the projects here are libraries built *on top of* CGP: they demonstrate what the
paradigm makes possible, they exercise it at a scale the test suite cannot, and they are the closest
thing the ecosystem has to public evidence that CGP works on real problems.

## What belongs here

A project earns a directory here when it is a **library** developed under the
[contextgeneric](https://github.com/contextgeneric) organization, built with CGP rather than being
part of CGP, and public enough that the website or a blog post points at it. All three conditions
narrow the set, and two kinds of near-miss are worth naming so the boundary stays clear.

[Hermes SDK](https://github.com/informalsystems/hermes-sdk/) — CGP's first real-world adopter, and the
codebase the paradigm grew out of — is a library built with CGP but lives outside the organization and
is not developed alongside it, so it is an external reference recorded in
[sibling-projects.md](../sibling-projects.md) rather than a project here. The
[`cgp-examples`](https://github.com/contextgeneric/cgp-examples) and
[`cgp-example-profile-picture`](https://github.com/contextgeneric/cgp-example-profile-picture)
repositories are inside the organization and track the current release, but they are collections of
runnable demonstrations rather than libraries anyone depends on — their documented form is
[examples/](../examples/README.md), which re-derives their scenarios as self-contained worked examples,
so they too are recorded only in [sibling-projects.md](../sibling-projects.md).

The distinction from a **member project** is about what the project is, not how carefully it is
documented. A member builds CGP itself; a project here is built with it. Both are verified against
their own source, and a project section grows from a single orienting `README.md` into a fixed shape
(architecture, reference, guides, tests, and open issues) as it is documented. That shape, and the
rules for writing it, are in [AGENTS.md](AGENTS.md). A project document explains the project's own
design and links to [cgp/](../cgp/README.md) for the CGP constructs it uses rather than re-explaining
them.

## The catalog

Two projects are documented so far. Both track the CGP version in development, 0.8.0-alpha, and both
have a public announcement post whose code has since gone stale, which is a recurring pattern worth expecting: the
project moves with the library while the post that announced it does not.

- [hypershell/](hypershell/README.md) — a modular, type-level DSL for shell-script-like programs
  written as Rust types and interpreted at compile time. The project that drove the handler family
  into existence, and the reference implementation of the type-level DSL technique.
- [cgp-serde/](cgp-serde/README.md) — Serde's `Serialize` and `Deserialize` rebuilt as CGP
  components, so that how each value type is encoded becomes a per-context wiring choice. The clearest
  demonstration of CGP's coherence workaround on a library every Rust developer already knows.
  Documented in the full project shape, against its `v0.8.0` branch.

## How these relate to the rest of the base

Each project connects outward in three directions, and the documents make all three explicit. It has
a **worked example** in [examples/](../examples/README.md) that re-derives its scenario in verified
current syntax — [shell-scripting DSL](../examples/shell-scripting-dsl.md) for Hypershell,
[modular serialization](../examples/modular-serialization.md) for cgp-serde — and that example, not
the project's announcement post, is what other documents quote. It has an **announcement post** with
an internal document under [website/blog/](../website/blog/README.md) recording how far that post has
drifted. And it exercises a set of **CGP constructs and concepts**, linked per project so an agent
can find the semantics behind anything it meets in the source.

For the communication strategy these projects are the ecosystem's most concrete social proof, which
[evidence.md](../communication-strategy/evidence.md) argues is what
the evaluator profile actually wants — a real system built with CGP rather than another argument. That
value depends on them staying current, so a project that falls behind the library stops being evidence
and starts being a liability.

## Adding a project

Create a directory named for the project with a `README.md` following the front-door shape in
[AGENTS.md](AGENTS.md#the-shape-of-a-project-section): what it is, which revision is documented, how it
is organized, what CGP it uses, how it relates to the rest of the base, and its current status.
Register it in the catalog above and in [../summary.md](../summary.md) in the same change, add it to
[../sibling-projects.md](../sibling-projects.md) so its checkout and repository are findable, and check
whether the website's Resources page should list it. The section then grows into
the shape [AGENTS.md](AGENTS.md) fixes, with [cgp-serde/](cgp-serde/README.md) as the worked instance.
