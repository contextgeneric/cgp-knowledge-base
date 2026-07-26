# AGENTS.md — the worked examples

This directory holds the knowledge base's self-contained worked examples — one document per use case,
each developing a realistic scenario from its contexts and components through to the wiring that
connects them. Read [README.md](README.md) for the catalog and what an example is for, and the
base-wide [../AGENTS.md](../AGENTS.md) for the rules every section shares — the synchronization rule,
the dual-reader prose style, document-the-present, and how a document registers itself. The rules
below add what is specific to examples.

The examples sit at the base's top level rather than inside a member section because they serve the
whole ecosystem: the [construct reference](../cgp/reference/README.md), the
[concepts](../cgp/concepts/README.md), the [guides](../cgp/guides/README.md), and the
[related-work](../related-work/README.md) comparisons all quote them, and an agent writing a tutorial
or an article works from them. An example is judged by whether it is quotable and correct, not by
whether it covers every detail.

## Leave the mechanics to the reference

[README.md](README.md) explains why an example and a reference document are complementary; the rule
that follows is to keep the prose in an example light. Give enough to make the code legible, a short
note on which CGP concept each step demonstrates, and a link to the reference document that owns that
concept — and never re-explain a construct the example uses. Examples are bound by the
[synchronization rule](../AGENTS.md#the-synchronization-rule) like everything else, so verify every
snippet against the source the way you would a reference document's Expansion section, and invoke the
`/cgp` skill before writing any CGP code here.

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

## Name the shape the example wires

Say, in the opening summary or the first wiring section, **what kind of context the example wires and what
its components target**, because an example is the raw material an agent quotes into a tutorial or a page
and the shape has to travel with the code. A context is either a **value context**, where the wired type
*is* the data the capability operates on, or an **environmental context**, a type standing for an
application; a component is either **self-targeted** or **parameter-targeted**. Both pairs are defined in
the [modularity hierarchy](../cgp/concepts/modularity-hierarchy.md).

The catalog in [README.md](README.md) records the shape for every existing example, and the distribution is
worth knowing before writing a new one: eight of the nine wire an environmental context, and the ninth —
[area calculation](area-calculation.md) — is the one both website tutorials are built from. So a reader who
learns CGP from the teaching material meets the least common shape first, which is exactly why an example
must not leave its own shape implicit.

## When an example needs a concept the base does not cover

Document the concept where it belongs rather than explaining it inside the example. Add the missing
detail to the relevant [reference document](../cgp/reference/README.md), or — when the concept is a
cross-cutting idea that ties several constructs together — add a new page under
[cgp/concepts/](../cgp/concepts/) and register it in the [concepts index](../cgp/concepts/README.md).
The example then links to that documentation like any other, keeping itself focused on the use case
rather than on teaching a new construct.
