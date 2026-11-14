# Overview

The Overview is the feature tour: each headline feature with a compiled example, its limit, and the
page that explains it, then the breadth features in a linked list and the problems the features
answer.

- **URL:** <https://contextgeneric.dev/docs/overview>
- **Source:** [docs/overview.md](https://github.com/contextgeneric/contextgeneric.dev/blob/main/docs/overview.md)
- **Status:** Current
- **How it was made:** written by an agent from this base, level one of the four in
  [ai-disclosure.md](../../communication-strategy/ai-disclosure.md), replacing an earlier agent
  revision; its examples are compiled and its quoted diagnostic captured; flagged for the author's
  read before publication

## What it covers

The page follows
[the homepage guide's specification](../writing-guides/homepage.md#the-overview-the-feature-tour). It
opens with the problem it answers, the name and the tag line whole, a pointer for newcomers, and the
note that the examples are fragments of compiled programs.

*Key features* walks the five features under identity.md's titles through the profile-picture
scenario: `App`, `GCloudApp`, and `TestApp` wiring `FetchS3Object`, `FetchGCloudObject`, and
`FetchLocalObject` for one storage component; the forwarding implementation that `App`'s wiring
amounts to; `App` without `bucket_id` rejected by `check_components!`, with the `cargo cgp check`
output quoted; the error type made abstract with `#[use_type]` and a provider's `#[uses]`
dependency; and `get_user` as a `#[cgp_fn]` with an implicit `database`. Each section keeps its
condition: wiring checks nothing until a component is used or checked, portability depends on the
selected providers, and the raw errors stay long without `cargo-cgp`.

*Beyond choosing implementations* lists abstract types, extensible records and variants, composable
handlers, namespaces, and higher-order providers, one or two sentences each with its Concepts page
and no code, so a first-time reader meets only the constructs the five features need. A table maps
each problem in [message.md](../../communication-strategy/message.md#the-problems-cgp-removes) to the
Concepts page that answers it, and the page ends with when a plain trait is enough and where to go
next.

## How it relates to the knowledge base

[Identity](../../communication-strategy/identity.md#the-headline-feature-set) fixes the features and
their titles, [the message](../../communication-strategy/message.md) the problems and their limits,
and [seo.md](../seo.md#the-tag-line-orients-the-reader-the-features-carry-the-searchable-words) the
page each feature links. The scenario comes from the
[profile-picture example](../../examples/profile-picture.md), under the names the `cgp` README uses.

The code is compiled in the [`example-code` crate](../site.md#the-example-code-crate) as the
standalone binary `tests/overview.rs`, with stand-ins for the storage clients and the pool; the
rejected program is a fixture under `tests/compile_fail/overview/`, and the quoted
`cargo cgp check` block is bound to it for recapture.

## Maintaining it

- Read the specification before any change and run its draft checks after one.
- Keep the feature titles verbatim and each snippet equal to `tests/overview.rs`.
- Recapture the quoted diagnostic after a `cgp` or `cargo-cgp` change.
- Link each subject's owning page rather than explaining it here.
