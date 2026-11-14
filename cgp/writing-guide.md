# Writing the `cgp` documents

This guide holds the rules for writing and revising the reference, concept, and guide documents
under `cgp/`. The knowledge base's [AGENTS.md](../AGENTS.md) holds the rules every document follows;
the [error catalog](errors/writing-guide.md) and the
[implementation documents](implementation/writing-guide.md) have guides of their own.

## Keeping a document in step with its construct

A construct's reference document changes with the construct and leads with its current form:

- Add a construct's reference document and register it in the index; remove or supersede both when
  the construct is removed; revise the Expansion section when the expansion changes.
- Lead with the current form and keep a legacy form only as a clearly labeled note for reading
  existing code.
- State what needs updating in the skill when its checkout is absent.

## Authoring conventions

Documents here draw their code from the examples and verify it against the source:

- Show code freely, and let the prose around it carry the meaning.
- Prefer snippets that match the worked examples in [../examples/](../examples/README.md); replace an
  ad-hoc snippet with the example-aligned one during a review.
- Verify against the source before writing; the Expansion section must reflect the real default
  identifiers, not idealized ones.
- Let a concept page use simplified code when the reduction explains the concept better; the code is
  an illustration, not a reproduction, and still uses current idioms and compiles.

## Reference documents

A reference document records every form its construct accepts, in a fixed shape:

- Follow the document shape: Purpose, Syntax, Syntax Grammar when the macro has custom syntax,
  Expansion, Examples, Related constructs, Known issues when needed, Source, and Public pages when the
  public reference splits the document.
- Place a document by what the construct is: `macros/`, `derives/`, `attributes/`, `components/`,
  `providers/`, `traits/`, or `types/`.
- Register a new reference document in [reference/README.md](reference/README.md) in the same
  change.
- A component belongs in `components/`, not `traits/`.
- Be exhaustive: document every form the parser accepts, including the rare, advanced, and legacy
  forms.
- Enumerate against the parser, not against the previous draft.
- Name the independent grammar axes and say when they combine.
- Link every mentioned construct; record an undocumented one as a gap in the index.
- Write the Source section as a bullet list, one pointer per bullet, and never point at a test.
- Where the public reference splits the document, list its pages by their live URLs.

## Syntax Grammar conventions

A Syntax Grammar section states exactly what the macro parses, in the Rust Reference's notation:

- Give a Syntax Grammar section to a macro whose invocation accepts a bespoke grammar.
- Omit it for a macro whose invocation is a plain Rust item without arguments.
- Describe only the tokens the macro itself parses, not the surrounding delimiters or the item.
- Write one production per line in a fenced ` ```ebnf ` block, in the Rust Reference's notation.
- Use CamelCase for a nonterminal, `ALL_CAPS` for a lexer token, and backticked characters for a
  terminal.
- Treat a CamelCase name the grammar does not define as a Rust grammar production, not a new one.
- Use `x?` for optional, `x*` for zero or more, `x+` for one or more, `A | B` for alternation,
  `( … )` for grouping, and juxtaposition for an ordered sequence.
- Use character ranges, exclusions, negative lookahead, and comments only when the construct needs
  them, following the Rust Reference.
- Define a shared sub-grammar once in the macro that owns it and reference it by name.
- Open the section with a sentence naming what the grammar covers, the block, and a short paragraph
  explaining a nonterminal or constraint a reader could not infer.
- Verify the grammar against the argument and body parsers, not against the prose.

## Concept and guide documents

A concept document explains one idea across constructs, and a guide recommends a choice between them:

- Give a concept document one idea that spans several constructs, with only the mechanism needed to
  make it legible.
- Give a concept its own page when a single construct does not own it and a reader would otherwise
  assemble it from three reference documents.
- Give a guide a recommendation, its trade-offs, and a concrete before/after refactoring.
- Move a guide's long explanation of a construct to the reference or a concept and link it.
- Link a guide's exact syntax to the reference, its mechanism to the concepts, and its worked scenario
  to the examples.
- Register a new concept in [concepts/README.md](concepts/README.md) and a new guide in
  [guides/README.md](guides/README.md).
- Keep a guide's snippets compiling against current CGP; a recommendation that names removed syntax is
  a bug.

## Say which shape an example wires

Every example names the shape it wires, so a reader can tell which arrangement the code shows:

- Say which context shape and which target an example uses, with the qualifiers
  [vocabulary.md](../communication-strategy/vocabulary.md#qualifying-a-context-and-a-target)
  defines.
- Say so in a sentence when a document introduces a second shape; the labels need not appear.

## Reviewing and updating a document

A review checks every claim against the source before it improves the prose:

- Review in two passes: confirm every claim against the source, then improve how the document reads.
- Follow the implementation when the document, the skill, and the implementation disagree.
- Verify specific behavior against the tests and snapshots, and state it in your own words without
  citing the test.
- Record surprising behavior, sharp edges, and bugs under Known issues; remove the note when fixed.
- Rewrite a drifting document rather than adding another patch, and collapse a repeated explanation
  into the document that owns it.
- Re-check the document's place in the section; move or split it when it keeps explaining another
  construct.
- Update the index, [../summary.md](../summary.md), and the cross-links when a document moves or splits.
