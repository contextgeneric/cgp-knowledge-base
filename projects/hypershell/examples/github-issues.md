# `github_issues`

A request to the GitHub API whose URL is joined from fields and literals, with URL encoding, a
header, and the JSON response decoded into a Rust type.

- **Source** — [crates/hypershell-examples/examples/github_issues.rs](https://github.com/contextgeneric/hypershell/blob/v0.8.0/crates/hypershell-examples/examples/github_issues.rs)
- **Run** — `cargo run --example github_issues`
- **Needs** — network, unauthenticated access to `api.github.com`, which is rate-limited
- **Result** — prints the open issues of `rust-lang/rust` as `Issue` values

## The program

```rust
pub type Program = hypershell! {
    SimpleHttpRequest<
        GetMethod,
        JoinArgs [
            FieldArg<"base_url">,
            StaticArg<"/repos/">,
            UrlEncodeArg<FieldArg<"github_org">>,
            StaticArg<"/">,
            UrlEncodeArg<FieldArg<"github_repo">>,
            StaticArg<"/issues">,
        ],
        WithHeaders [
            Header<
                StaticArg<"User-Agent">,
                StaticArg<"hypershells">,
            >
        ],
    >
    | DecodeJson<Vec<Issue>>
};

#[derive(HasField)]
pub struct MyApp {
    pub http_client: Client,
    pub base_url: String,
    pub github_org: String,
    pub github_repo: String,
}

#[derive(Debug, Deserialize)]
pub struct Issue {
    pub id: u64,
    pub state: String,
    pub title: String,
}
```

The context joins `HypershellNamespace`. `main` prints the program's output, which is the
`Vec<Issue>` that `DecodeJson` names.

## Context and wiring

The URL is a `JoinArgs`, which concatenates its parts because the URL extractor routes it through
the string extractor, and each `UrlEncodeArg` encodes a field's value. The `User-Agent` header is
required by the GitHub API. The program's output type is fixed by the last stage, so the result of
`handle` is a `Vec<Issue>` with no conversion in `main`.

## What it demonstrates

- `JoinArgs` as concatenation and `UrlEncodeArg`: see [arguments](../reference/arguments.md#joinargs-joinstringargs-and-joinextractargs).
- Headers: see [HTTP](../reference/http.md#withheaders-header-and-the-request-builder-updater).
- Decoding into a Rust type named in the program: see [JSON](../reference/json.md).

## Known issues

The header comment (lines 20–23) says the context uses `#[cgp_inherit]` and `HypershellPreset`,
both removed; the code uses `namespace HypershellNamespace;`. See
[issues.md](../issues.md#housekeeping).

## Public material derived from this

None yet.
