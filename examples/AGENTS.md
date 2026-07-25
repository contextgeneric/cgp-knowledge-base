# AGENTS.md — the worked examples

This directory holds the knowledge base's self-contained worked examples — one document per use case,
each developing a realistic scenario from its contexts and components through to the wiring that
connects them. Read [README.md](README.md) for the catalog and what an example is for, and the
base-wide [../AGENTS.md](../AGENTS.md) for the rules every section shares — the synchronization rule,
the dual-reader prose style, document-the-present, and how a document registers itself. The rules
below add what is specific to examples.

The examples sit at the base's top level rather than inside a member section because they serve the
whole ecosystem. They exist for two reasons: they are the canonical source of code snippets the rest
of the base reuses — the [construct reference](../cgp/reference/README.md), the
[concepts](../cgp/concepts/README.md), the [guides](../cgp/guides/README.md), and the
[related-work](../related-work/README.md) comparisons all draw on them — and they are the raw material
an agent works from when writing expanded documentation such as a tutorial or an article. An example
is judged by whether it is quotable and correct, not by whether it covers every detail.

## An example is not a second copy of the reference

A [reference document](../cgp/reference/README.md) explains one construct completely — its syntax,
exact expansion, and corner cases — while an example shows several constructs cooperating to solve a
problem and deliberately leaves the mechanics to the reference. Keep the prose in an example light:
enough to make the code legible, a short note on which CGP concept each step demonstrates, and a link
to the reference document that owns that concept. Do not re-explain a construct an example uses; link
to it instead. Examples are still subject to the synchronization rule — code that no longer reflects
current CGP is a bug — so verify every snippet against the source the same way you would a reference
document's Expansion section, and invoke the `/cgp` skill before writing any CGP code here.

## Adding an example from an outside source

To add a new example from a source — example code, an article, a tutorial, or any external write-up —
treat the source as a *reference for the scenario and the patterns*, then write a fresh,
self-contained example document that stands on its own. Do not cite, name, link, or otherwise point
back to the original source; the example must read as native knowledge-base material with no
dependency on where the idea came from. This is the one place the base deliberately parts from the
[related-work](../related-work/AGENTS.md) rule that everything external is cited: a related-work
document's credibility rests on being traceable, while an example's rests on being self-contained.
Re-derive the code in current CGP vocabulary and verify it against the implementation rather than
copying the source's code verbatim, since the source may use older syntax or a different dialect. Give
the example its own coherent narrative arc — usually a progression from the simplest form of the use
case to the fully wired and composed version — rather than mirroring the source's structure.

## Document structure

Follow the shape of the existing examples. Open with a level-one heading naming the use case and a
one-sentence summary of what it demonstrates and why it is a useful template. Follow that with a short
framed list of the concepts the example demonstrates, each linking to its reference document, and a
note of any shared assumption such as `use cgp::prelude::*;`. Then develop the use case in titled
sections, each introducing one step of the progression with a sentence of context, the code, and a
brief concept note pointing into the reference. Register the new document in the catalog in
[README.md](README.md), and in [../summary.md](../summary.md), in the same change.

## When an example needs a concept the base does not cover

Document the concept where it belongs rather than explaining it inside the example. Add the missing
detail to the relevant [reference document](../cgp/reference/README.md), or — when the concept is a
cross-cutting idea that ties several constructs together — add a new page under
[cgp/concepts/](../cgp/concepts/) and register it in the [concepts index](../cgp/concepts/README.md).
The example then links to that documentation like any other, keeping itself focused on the use case
rather than on teaching a new construct.
