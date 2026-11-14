# Writing a project section

This guide holds the rules for writing and revising the documents of an ecosystem project's section.
The knowledge base's [AGENTS.md](../AGENTS.md) holds the rules every document follows, including
linking a project at the branch [../sibling-projects.md](../sibling-projects.md) records.

## A project section documents its project in depth

A project section is verified against the project's source, as `cgp/` is against `cgp`:

- Verify the section against the project's source, exactly as `cgp/` is verified against `cgp`.
- Treat a change to the project's bounds, wire format, context dependencies, or crate as a change to
  the matching document.
- Make both the project change and the document change when the checkout is present; when it is absent,
  state what needs updating.
- Do not modify the project's source while documenting it; record a defect, missing test, or stale
  metadata in the section's `issues.md`.
- Match a reproduced project's code to the branch [../sibling-projects.md](../sibling-projects.md)
  records.
- Record a project's older idiom as a change in its `issues.md`, not by modernizing an example alone.

## Verify behavior with a probe, not by reading alone

A claim about how the project behaves is checked by running it:

- Check a runtime claim by running it in a scratch crate that declares dependencies by version and
  overrides them with local paths.
- Check a compile-time claim by building the probe, and with `cargo cgp check` where a diagnostic is
  quoted.
- Keep the probe and its `CARGO_TARGET_DIR` outside the session scratchpad.
- State the result in your own words, and mark an unconfirmed claim as unconfirmed.
- Never link the probe from a document.

## Leave CGP itself to cgp/

A project section says what the project does with CGP, and links CGP itself:

- Link a CGP construct or idea to its document under [../cgp/](../cgp/README.md); say only what the
  project does with it.
- Test a paragraph by whether it would still be true of a different project; if it would, it belongs
  in `cgp/`.
- Link the worked example for the pattern; say only what the project's code does with it.
- Keep the project's facts here: layout, wiring, item behavior, design decisions, defects, test
  coverage, and run results.

## The shape of a project section

Every project section follows one shape:

- Follow the section shape in [README.md](README.md): a README, and the architecture, reference,
  guides, examples, comparison, testing, and issues documents the project needs.

## Reference entries

Each public item gets its own reference entry in a fixed shape:

- Give each public item its own level-two section: Definition, Behavior, Context dependencies, Pairing,
  and, when needed, Known issues.
- Open the family with a short introduction and close it with a **Source** bullet list.
- Put material that spans several items in its own section after the entries.

## Public material

Each document records the public material it feeds before a page uses it:

- End each document with the public material it feeds, or `None yet`.
- Treat each example document as the record its public page is written from.
- Give a program the site will show its own document, even where the project folds several programs
  into one; the page quotes only what the record verifies.
- Record a **Try a change** section, with the output or diagnostic it produced, before a page
  describes it.

## Registration

A new document registers in every index above it, in the same change:

- Register a new document in its directory's `README.md` and the project `README.md` as well as
  [../summary.md](../summary.md), in the same change.
- Register a new project section in [README.md](README.md) and
  [../sibling-projects.md](../sibling-projects.md).
