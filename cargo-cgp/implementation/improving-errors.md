# Improving error messages against real-world CGP code

This document is the procedure that [cargo-cgp/AGENTS.md](https://github.com/contextgeneric/cargo-cgp/blob/main/AGENTS.md#improving-error-messages-against-real-world-cgp-code)
summarizes as rules. The work is driven from outside the repository: you are given a CGP project whose
code does not compile, and every change lands as a test fixture before any code.

## Two rules that admit no exceptions

- **Never hard-code logic for an example's code.** Reason only about core CGP constructs, anchored by
  `DefId` to the `cgp` crates. A fix that matches on a name, type, or module from the example project is
  a defect even when today's message is perfect.
- **Keep every explanation generalized.** A knowledge-base document, an inline comment, and a UI fixture
  are framed around the core CGP concept, not around the project that exhibited it. Name the project at
  most as a passing aside the explanation does not depend on.

## Read first

- **Using the tool:** [Usage](../reference/usage.md), [Troubleshooting](../reference/troubleshooting.md),
  and the [error-code catalog](../error-code.md).
- **How the output is produced:** [Typed root-cause resolution](typed-resolution/overview.md),
  [The driver](driver/program.md), [Diagnostic reshapes](driver/diagnostic-reshapes.md),
  [Error processing](error-processing.md), [Architecture](architecture.md), and
  [Testing](testing.md).
- **The problem domain:** the [CGP error catalog](https://github.com/contextgeneric/cgp-knowledge-base/blob/main/cgp/errors/README.md)
  and the `/cgp` skill.

## The loop

1. **Reproduce the failure in the target project.** Run the check through the local Nix build from the
   project's directory, and capture the exact message.
2. **Learn the root cause from the project's own diff.** The project carries uncommitted changes that
   comment out the trigger. Read the diff, and treat the project as read-only; re-check its `git status`
   before finishing.
3. **Judge the gap.** Compare the output with the known root cause and decide what the message buries,
   misnames, or omits.
4. **Reproduce it as a simplified UI fixture before changing the tool.** Add a `<name>.rs` fixture under
   `tests/ui/` in its error class, with the `//@quality:` header matching the current output, bless it,
   and confirm the `.cgp.stderr` shows the shortcoming.
5. **Change the tool and verify the fixture first.** Make the improvement, usually in the resolver or
   the rustc-free wording, then re-run the UI suite and confirm the fixture improved and no other
   snapshot regressed.
6. **Re-check the target project.** Re-run the Nix check only after the fixture is green, and confirm
   the real-world message improved the same way. If it did not, return to step 4 with a fixture that
   captures the real cause.
7. **Confirm the fix the message names actually works.** Test it in a `git worktree` placed beside the
   project, never in the project itself. Apply the failing state, apply the named change, and run the
   check.
8. **Graduate the fixture if it earned it.** Change its `//@quality:` header to `acceptable` when the
   output now leads with the root cause, and keep it in its class directory.

## The fixture and the catalog

- Every post-codegen failure is pinned by a `cargo-cgp` UI fixture and cataloged in the
  [error catalog](https://github.com/contextgeneric/cgp-knowledge-base/blob/main/cgp/errors/README.md).
- The fixture records both the raw compiler baseline and the tool's output.
- The class document describes the anatomy and links the fixture; the macro's implementation document
  records a rejection case and a defect, not the observable error class.
- Update the class document and the fixture in the same change when both repositories are present.
