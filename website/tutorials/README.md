# Website tutorials

This directory holds one internal document per tutorial series on the website, recording the
**teaching contract** the series is under, so a reviser finds it before changing the series. A
revision that keeps the prose current but breaks the contract has damaged the tutorial.

**Read [../writing-guides/tutorial.md](../writing-guides/tutorial.md) first.** The guide says what a
tutorial should be; the documents below record what each published series is and must not lose. Where
the two disagree, the guide is the intent and the gap belongs in the series' document.

## What a teaching contract fixes

**A tutorial is judged by its pedagogy more than its correctness**: progressive disclosure, per
[readers.md](../../communication-strategy/readers.md#the-comprehension-barriers), is what a
well-meaning edit such as "add namespaces to the tutorial" destroys first. Each document fixes what a
revision preserves unless the user says otherwise:

- **Objective**: what a reader can do at the end.
- **Prerequisites**: what the series assumes, and what it deliberately does not.
- **Concept sequence**: the order ideas arrive, with the reason where it is not obvious.
- **Level of explanation**: whether the series shows a mechanism's desugaring, gestures at it, or stays
  silent.
- **Register, shape, and payoff**: first-principles or applied, which of CGP's three shapes its running
  example wires, and the step where the reader sees why it was worth doing, one per part of a series.

**Adding to a tutorial means finding the right rung, not appending to the end.** A concept that does
not fit the ramp belongs in a new part or a new series, and the document says which.

## The catalog

The two published series overlap deliberately: both teach `#[cgp_fn]` and `#[implicit]` to a reader
new to CGP, one as a five-minute first contact and one as a multi-part progression. Read both
documents before changing either.

- [Hello World](hello-world.md): the single-page first contact, a `greet` function with one implicit
  argument run on two context structs, plus an optional plain-Rust appendix; it gets a reader to a
  working program before any CGP vocabulary.
- [Area calculation](area-calculation.md): the series from plain Rust functions to configurable static
  dispatch with higher-order providers, an index and two tutorials on the live site, and on to catching
  a mis-wiring in a third tutorial on the website's `v0.8.0` branch; where a reader goes after Hello
  World.

**The section has no applied-register tutorial yet**, so no tutorial reader meets an environmental
context, and the reader who evaluates by seeing a realistic system has nowhere to go. One is planned,
second in the section, per
[the guide](../writing-guides/tutorial.md#say-which-shape-the-tutorials-example-is-in).

## The document shape

Open with a level-one heading naming the series and a one-sentence statement of what a reader can do at
the end, then the identifying facts (URL, source path, page list, status) as a framed list. Then cover
**what it teaches**, walking the sequence; **the teaching contract**; **how it relates to the knowledge
base**, linking the reference, concept, example, and communication-strategy documents behind it;
**where it diverges from current CGP**; and **maintaining it**, naming what a revision must not break.
Register the document in the catalog above and in [../../summary.md](../../summary.md) in the same
change.
