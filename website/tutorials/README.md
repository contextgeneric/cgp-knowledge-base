# Website tutorials

This directory holds one internal document per tutorial series published on the website. Where a
[blog document](../blog/README.md) records what a post said and how far it has drifted, a tutorial
document records the **teaching contract** the tutorial is under: what it sets out to achieve, who it
is written for, what it assumes they already know, which concepts it introduces and in what order, and
how much explanation it pitches at each. A revision that keeps the prose current but breaks that
contract has damaged the tutorial, and these documents exist so the contract is written down where a
reviser will find it.

## Why tutorials need a different document

A tutorial is not a reference and is not judged as one. Its correctness matters, but its *pedagogy*
matters more: a tutorial that is technically flawless and introduces the consumer/provider split on
page one has failed, while one that defers a mechanism until the reader has a reason to want it has
succeeded even if it says less. The judgment involved is what
[technical-barriers.md](../../communication-strategy/technical-barriers.md) calls progressive
disclosure, and it is the easiest thing for a well-meaning revision to destroy — an agent asked to
"add namespaces to the tutorial" can wreck a carefully built ramp in one edit.

So each document below fixes four things that a revision must preserve unless the user says otherwise.
The **objective** is what a reader can do at the end. The **prerequisites** are what the tutorial
assumes and, just as importantly, what it deliberately does not assume. The **concept sequence** is
the order in which ideas are introduced, with the reason for that order where it is not obvious. And
the **level of explanation** is how deep the tutorial goes when a mechanism must be mentioned —
whether it shows the desugaring, gestures at it, or stays silent.

Adding to a tutorial therefore means finding the right rung, not appending to the end. A concept that
does not fit the ramp belongs in a new part of the series or a new series, and the document says which.

## The catalog

Two tutorial series are published, and they overlap deliberately: both teach `#[cgp_fn]` and
`#[implicit]` to a reader new to CGP, one as a five-minute first contact and the other as a
multi-part progression. Read both documents before changing either, since a change to the shared
ground affects the other's assumptions.

- [Hello World](hello-world.md) — the single-page first contact. A `greet` function with one implicit
  argument, run on two different context structs, plus an optional "behind the scenes" section showing
  the plain-Rust equivalent. Its whole job is to get a reader to a working program before they meet
  any CGP vocabulary.
- [Area calculation](area-calculation.md) — the three-part series that carries a reader from plain
  Rust functions to configurable static dispatch with higher-order providers. It is the site's only
  sustained teaching material and the place a reader is sent after Hello World.

## Where tutorials sit among the site's material

The site offers four routes into CGP and they are not interchangeable, so a tutorial revision should
know which gap it fills. The [Introduction page](../site-structure.md) is orientation and routing, not
teaching. The [blog](../blog/README.md) carries depth but is largely out of date and organized by
release rather than by concept. The [CGP Patterns book](https://patterns.contextgeneric.dev/) teaches
from first principles but has not been updated for some time. **The tutorials are the only
maintained, sequenced teaching material on the site**, which makes them the highest-value pages to
keep current and the ones a newcomer should be routed to first.

Their raw material is [examples/](../../examples/README.md), which exists partly to be quoted: an
example is a verified end-to-end progression, and a tutorial is that progression with the teaching
prose around it. Draw code from there rather than writing new snippets that then need their own
verification.

## The document shape

Follow the shape of the two existing documents. Open with a level-one heading naming the series and a
one-sentence statement of what a reader can do at the end. Give the identifying facts — URL, source
path, page list, status — as a short framed list. Then cover, in prose: **what it teaches**, walking
the sequence; **the teaching contract**, stating objective, prerequisites, concept order, and
explanation level; **how it relates to the knowledge base**, linking the reference, concept, example,
and communication-strategy documents behind it; **where it diverges from current CGP**, if anywhere;
and **maintaining it**, naming what a revision must not break. Register the document in the catalog
above and in [../../summary.md](../../summary.md) in the same change.
