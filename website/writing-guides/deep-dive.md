# Writing a deep dive

A deep dive is a **multi-page living document** that develops one substantial CGP project or technique
end to end. It is the site's most ambitious page type: the material is the largest the project
publishes, and unlike a blog post it is expected to be kept current as CGP changes rather than left to
age as a dated record.

- **Where they live** — `docs/deep-dives/<name>/`, one directory per deep dive, with an `index.md` and
  numbered pages
- **Voice** — project voice, unlike the blog posts they grow out of; see
  [The voice change is the hardest part](#the-voice-change-is-the-hardest-part)
- **Records** — [../deep-dives/README.md](../deep-dives/README.md), one internal document per deep dive

## Why this page type exists

CGP's three richest pieces of writing are blog posts: the
[Hypershell announcement](../blog/hypershell-release.md) at roughly 16,500 words, the
[four-part extensible-datatypes series](../blog/extensible-datatypes-part-1.md), and the
[cgp-serde announcement](../blog/cgp-serde-release.md). Between them they are the only prose anywhere
on several of CGP's most important design questions, and they are also the site's most-discussed
material.

They have two problems a blog post cannot solve. They are **dated artifacts** the site's rules forbid
rewriting, so as CGP moves they drift — every one of them predates namespaces, `#[cgp_impl]`,
`#[implicit]`, and the `open` statement, and their wiring code is now uniformly stale. And they are
**single pages of extraordinary length**, which suits a reader who sits down for two hours and fails
everyone else.

A deep dive fixes both by being a different artifact rather than an edit. It is a **new document under
`docs/`**, which means [document-the-present](../AGENTS.md#do-not-rewrite-history) applies in full and
it is corrected in place forever. And it is **split into pages small enough to read in one sitting**,
so a reader can take one idea, stop, and come back. The blog post stays exactly where it is, as the
record of what was said in its moment.

## The relationship to the original post

A deep dive **supersedes a blog post's usefulness without replacing the post**. Three rules keep that
relationship honest.

**The post is not edited.** It remains a dated artifact; its internal document already records what has
gone stale in it. The one legitimate change is adding a short dated note pointing readers at the deep
dive, and that decision belongs to the user rather than to an agent.

**The deep dive is not a copy with the syntax patched.** The blog posts are structured as arguments
delivered once, with a beginning that assumes nothing and an end that trails into future work. A deep
dive is structured for a reader arriving at page four from a search result. Reuse the *material* — the
worked examples, the explanations, the honest trade-offs — and rebuild the *structure*.

**Material that has found a better home moves out.** The Hypershell post carries a self-contained CGP
primer because nothing else on the site could carry one at the time. The
[explanation tier](explanation.md) now can, so the deep dive links to *Why CGP exists* and *How CGP
works* rather than re-teaching them. This is the single biggest reduction available: a deep dive should
teach its own subject and nothing else.

## The voice change is the hardest part

A blog post is written in the **author's voice** — first person, personal, candid about uncertainty and
about the author's own reasons. A deep dive lives under `docs/` and is written in the **project
voice**. That conversion is where a careless rewrite does the most damage, because the passages most
worth keeping are often the most personal.

Three moves handle almost every case. **Judgement is grounded rather than attributed**: "the learning
curve is steep, and it falls on DSL implementors rather than DSL users" keeps the claim and drops the
"I think". **Uncertainty is stated as uncertainty**, not deleted: "the cause is not fully understood;
the measurements available are rough" is project voice and is honest, where quietly dropping the
admission is neither. And **genuinely personal material stays on the blog** — the story of naming
Hypershell after a 2012 project is the author talking, and the deep dive should link to the post rather
than paraphrase it in the third person.

What must not happen is the concession disappearing in the conversion. The
[Hypershell post's Disadvantages section](../blog/hypershell-release.md) — the learning curve, the error
messages, the inability to load programs at runtime, the slow compilation — is the most credible thing
in it, and a deep dive without an equivalent has lost more than it gained.

## Splitting into pages

The split is the point of the format, and it obeys one rule: **a page is one idea a reader can finish**.
Aim for something a motivated reader gets through in ten to fifteen minutes, and let the number of pages
fall out of the material rather than fixing it in advance.

Four structural obligations follow from readers arriving in the middle.

**Every page opens by orienting.** One or two sentences saying what this page covers and where it sits
in the sequence, because a search result lands on page four as readily as page one.

**Every page ends by routing** — the next page, and the reference or explanation page for anything it
touched but did not develop.

**The `index.md` is a real page, not a table of contents.** It states what the whole deep dive is about,
who it is for, what the reader will understand at the end, and how long the whole thing is — the
declared-length habit from the author's own long-form writing, which is what makes length acceptable
rather than ambushing. It then lists the pages with a sentence each.

**One running example carries the whole deep dive.** This is what the source blog posts already do well
and what makes a multi-page document cohere; switching domains between pages resets the reader.

## Keeping the code current

A deep dive's code is bound by the [synchronization rule](../../AGENTS.md#the-synchronization-rule) like
any docs page, and this is the obligation that makes the format expensive. Three things follow.

**Draw code from the live repository, not from the blog post.** Each deep dive's internal document names
the code base it tracks, and every one of the three planned deep dives has a repository that is already
partly modernized ahead of its post. Take the snippets from there.

**Use the modern idioms** the [guides](../../cgp/guides/README.md) teach, even where the tracked
repository does not yet. Where the guide and the repository disagree, that disagreement is a code change
worth recording in the deep dive's internal document rather than a licence to publish the older form.

**Verify against the source, and prefer [examples/](../../examples/README.md)** where an example already
carries the same scenario in verified form — the three planned deep dives correspond closely to the
[shell-scripting DSL](../../examples/shell-scripting-dsl.md),
[application builder](../../examples/application-builder.md),
[expression interpreter](../../examples/expression-interpreter.md), and
[modular serialization](../../examples/modular-serialization.md) examples.

## What must not be in a deep dive

**No re-teaching of CGP fundamentals.** One paragraph of orientation and a link to the
[explanation pages](explanation.md). This is the rule most often broken, because the source posts all
break it by necessity.

**No dated framing.** "In this release", "we have just shipped", "as of today" belong to the blog post
this grew out of. A deep dive describes how things are.

**No first-person narration**, per the voice rule above.

**No construct reference.** Name the constructs, show them in use, and link to
[docs.rs](https://docs.rs/cgp) or the reference for the full grammar.

**No unmarked speculation.** The source posts contain substantial future-work sections. Ideas that have
since shipped are now simply features; ideas that have not should be clearly marked as unbuilt, or left
out.

## Checking a draft

**Open each page cold and ask whether it orients you** — a reader arriving from a search result must
know within two sentences what the page is and what it belongs to.

**Check that the fundamentals are linked, not taught.** If a page explains what a provider trait is, that
explanation belongs to the explanation tier.

**Find the trade-offs.** A deep dive that has lost its source post's honesty about costs has lost the
thing that made the post credible.

**Check the voice** is the project's throughout, and that no concession was deleted in the conversion
from the author's.

**Diff the code against the tracked repository** and verify every snippet against the source and the
`/cgp` skill.
