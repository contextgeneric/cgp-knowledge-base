# AGENTS.md: the ecosystem projects

Read [README.md](README.md) for what qualifies as a project. The base-wide [../AGENTS.md](../AGENTS.md)
rules apply.

## A project section documents its project in depth

- Verify the section against the project's source, exactly as `cgp/` is verified against `cgp`.
- Treat a change to the project's bounds, wire format, context dependencies, or crate as a change to
  the matching document.
- Read the project at the branch [../sibling-projects.md](../sibling-projects.md) records, and link to
  it at that branch; this is the one departure from the root's `main` link rule.
- Make both the project change and the document change when the checkout is present; when it is absent,
  state what needs updating.
- Do not modify the project's source while documenting it; record a defect, missing test, or stale
  metadata in the section's `issues.md`.

## Verify behavior with a probe, not by reading alone

- Check a runtime claim by running it in a scratch crate that declares dependencies by version and
  overrides them with local paths.
- Check a compile-time claim by building the probe, and with `cargo cgp check` where a diagnostic is
  quoted.
- Keep the probe and its `CARGO_TARGET_DIR` outside the session scratchpad.
- State the result in your own words, and mark an unconfirmed claim as unconfirmed.
- Never link the probe from a document.

## Leave CGP itself to cgp/

- Link a CGP construct or idea to its document under [../cgp/](../cgp/README.md); say only what the
  project does with it.
- Test a paragraph by whether it would still be true of a different project; if it would, it belongs
  in `cgp/`.
- Link the worked example for the pattern; say only what the project's code does with it.
- Keep the project's facts here: layout, wiring, item behavior, design decisions, defects, test
  coverage, and run results.

## The shape of a project section

Follow the section shape in [README.md](README.md): a README, and the architecture, reference, guides,
examples, comparison, testing, and issues documents the project needs.

## Reference entries

- Give each public item its own level-two section: Definition, Behavior, Context dependencies, Pairing,
  and, when needed, Known issues.
- Open the family with a short introduction and close it with a **Source** bullet list.
- Put material that spans several items in its own section after the entries.

## Public material

- End each document with the public material it feeds, or `None yet`.
- Treat each example document as the record its public page is written from.
- Give a program the site will show its own document, even where the project folds several programs
  into one; the page quotes only what the record verifies.
- Record a **Try a change** section, with the output or diagnostic it produced, before a page
  describes it.

## Registration

- Register a new document in its directory's `README.md`, the project `README.md`, and
  [../summary.md](../summary.md) in the same change.
- Register a new project section in [README.md](README.md) and
  [../sibling-projects.md](../sibling-projects.md).
