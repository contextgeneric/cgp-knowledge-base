# Writing the related-work comparisons

This guide holds the rules for writing and revising a related-work comparison. The knowledge base's
[AGENTS.md](../AGENTS.md) holds the rules every document follows.

## Compile the foreign snippets, and record the toolchain

- Compile or type-check every foreign snippet that can be compiled, and note the toolchain and version.
- Adapt a documentation example that does not compile as written rather than reproducing its defect.
- Use Nix to compile a snippet where it is cheap; skip a package that builds a whole compiler toolchain
  and check the documented signatures instead.
- Say when a snippet cannot be run, and quote the proposal's own form.
- Record the toolchain and version each family of snippets was compiled with in Sources.
- Note a syntax that changed between versions where the snippet appears, with the older form named.

## What every comparison covers

- Explain the related concept faithfully enough that its own community would recognize it, and
  honestly enough that a skeptic who prefers it would accept the comparison.
- Represent the concept as its proponents would recognize it before critiquing it.
- Explain the concept in real depth: its sub-concepts, vocabulary, and mechanism.
- Show each important sub-concept in the related work's own language and idiom, beside the CGP
  counterpart where one exists.
- State what users like and dislike about the related work, drawing on real sentiment rather than
  invented objections.
- Explain where CGP takes the same approach, where it diverges, and why, including where the related
  work is the better fit.
- Close with concrete guidance for presenting CGP to a reader who knows the concept.

## Sources

- Ground every factual claim in a real source: official documentation, primary papers, or reputable
  community writing, with opinion attributed as opinion; invent no quotation, statistic, or
  version-specific behavior.
- For a concept from programming-language research, read the foundational paper and the current
  research that generalizes or corrects it, not only the documentation.
- Note the version or edition when behavior is version-specific.
- Record the sources in a **Sources** section, with a note on what each supports.
- Verify an uncertain detail against the source rather than trusting memory.

## The CGP side and the document shape

- Verify every CGP snippet against the source, use the modern idioms, and draw from
  [../examples/](../examples/README.md).
- Use the knowledge base's vocabulary on the CGP side, and introduce the related work's own term once.
- Follow the document shape: Purpose, the concept in depth, how CGP expresses it, what users like and
  dislike, how CGP compares, presenting CGP, and Sources.
- Register a new document in [README.md](README.md), and cross-link the concepts, the reference, and
  sibling comparisons.
