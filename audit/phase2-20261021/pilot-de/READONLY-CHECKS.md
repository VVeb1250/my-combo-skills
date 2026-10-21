# Pilots D and E: read-only code checks, 2026-10-22

Scope as approved: read source through `gh api` only. No install, no download to the repo, no
execution of external code, no model session. Fetched files were held in `/tmp` as text and
deleted afterwards. Tags: **[O]** read by me in the source at the pinned SHA, **[I]**
inference, **[U]** not checked.

## D. pbakaus/impeccable @ dad8dbb3aac21ad1fa236c110315ef4abece23e8 (Apache-2.0, LICENSE read)

Question: what is the telemetry default, and does it touch `impeccable detect`?

| Finding | Evidence |
| --- | --- |
| `cli.rs` in the detect crate contains no telemetry code. Telemetry lives in `crates/context/src/telemetry.rs` and serves the `concept-seed` and `serve-question` commands (the "roll API") | [O] `crates/detect/src/cli.rs` has 0 hits for "telemetry"; `telemetry.rs` module comment |
| **Default is on.** `opt_out_reason` returns `None` "when it is on"; off only via `DO_NOT_TRACK`, `IMPECCABLE_NO_TELEMETRY` (any value other than empty/`0`/`false`), `"telemetry": false` in `~/.impeccable/config.json`, or the project's `.impeccable/config.json` / `config.local.json`. `impeccable telemetry off` writes the user config | [O] `telemetry.rs` `opt_out_reason`, `env_opts_out`, `config_says_off` |
| With telemetry off the roll **still calls the API**; it adds a header so the server records nothing. API base is `https://impeccable.style/api` unless `IMPECCABLE_API_URL` is set, timeout 4 s | [O] `api_base`, `TELEMETRY_HEADER` comment ("the roll still happens ... the server records nothing") |
| The `detect` verb dispatches straight to `impeccable_detect::run_detect(rest, io, &engines())`. The `detect`, `core`, `html` and `foundation` crates have no HTTP dependency; only `context`, `live` and `skills` depend on `ureq` | [O] `crates/cli/src/main.rs` dispatch; every `Cargo.toml` in the tree |
| The browser engine launches a local headless Chrome (`--headless=new`, `--remote-debugging-port=0`, a temp `--user-data-dir`) and talks to it over loopback CDP; a URL target is then fetched by that Chrome | [O] `crates/browser/src/cdp.rs` |
| Other outbound paths in the same binary: `skills install/update/check` (a GitHub release zip is named in source), `context_cli` contacting `impeccable.style`, font rendering via `fonts.googleapis.com` | [O] URL grep over `cli`, `context`, `skills`, `live` sources; call sites other than `telemetry.rs` not read [U] |

Conclusion [I]: telemetry is **not a blocker for detect-only use**: the detect path reaches no
network code in the crates it depends on. Safe-use recipe if piloted: run only
`impeccable detect`, set `DO_NOT_TRACK=1` anyway, never run `concept-seed`, `serve-question`,
`skills`, `update`, `install`, `context`, or `live`.

Still unverified [U]: the body of `run_detect`; how the binary is obtained and launched
(`engine-probe` handshake and "unversioned user cache" comments suggest an npm launcher that
finds or fetches an engine, which was not read); per-rule fixture coverage (the earlier reader
found about 12 of 64 rule ids with no same-named fixture). Pilot D still needs approval for the
binary install and a local Chrome.

## E. trailofbits/skills @ a3131740a39291e42fd15b9eac07e0b393ad71b1, supply-chain-risk-auditor (CC BY-SA 4.0)

Question: redirect and token handling in `collect.py` / `sources.py`.

| Finding | Evidence |
| --- | --- |
| The HTTP client is `urllib.request.build_opener()` with the default redirect handler; the docstring calls following redirects "load-bearing" (`jrburke/r.js` 301s to `requirejs/r.js`) | [O] `sources.py:86,103` |
| **urllib forwards every request header on a redirect except content-length and content-type, including `Authorization`, whatever the new host** | [O] CPython 3.14.7 `HTTPRedirectHandler.redirect_request` source, run read-only with `inspect` |
| The Bearer token is attached in only two places, both to `https://api.github.com/repos/...` (the repo lookup and the five SECURITY.md probes); every other host gets no `Authorization` | [O] `sources.py:557-559, 590` |
| The repo host is gated: `github_repo` raises unless the normalized slug starts with `github.com/` and has exactly `owner/repo`, so a package manifest cannot point the token at another host directly | [O] `sources.py:546-556` |
| `gh auth token` is run on **every** invocation, including `--offline`, before the offline flag is consulted | [O] `collect.py:1431` (`token = sources.gh_token()`), `sources.py:517-531` |
| A token is read from the `gh` CLI only; if `gh` is missing, `gh_token` returns `None` and the run is anonymous with a note in the report | [O] `sources.py:517-531`, `collect.py:1435` |
| The cache key includes an `anon`/`gh` marker; the cache directory is created `0700` with an ownership check on POSIX; on Windows the check cannot run and the report states that caveat | [O] `sources.py:88-123` docstrings |

Assessment:
- Cross-host leak of the GitHub token needs `api.github.com` itself to answer a request with a
  redirect to another host. GitHub's repo rename redirects stay on `api.github.com` [I,
  unverified], so I rate the practical exposure **low**, but nothing in the collector enforces
  it and no test covers it [O: the earlier reader found only a "redirects are followed" test].
  A hardened copy would strip `Authorization` on a host change.
- Running the collector as shipped would call `gh auth token`, i.e. read the user's GitHub
  credential, even for a no-network run. This conflicts with the owner's standing preference
  against credential probing, so **if piloted it must run with `gh` absent from `PATH`**, which
  the code handles (anonymous run, 60 GitHub requests per hour, so most repo lookups would
  come back unavailable, which is exactly the tri-state behaviour under test).

Verdict [I]: pilot E is acceptable only as: fixture lockfile with 3 to 5 dependencies, `gh`
hidden from `PATH`, network to the seven registry/advisory hosts and anonymous
`api.github.com`, and the files downloaded to a fresh empty directory and run with
`py -I`, not from inside it. That needs owner approval for the download and the network use.

Not read [U]: `render.py`, `model.py` bodies, the optional `pip-audit` branch end to end, the
`uv` PEP 723 header (whether `py -I` can run it without `uv`).

## Net effect on the plan

- D: telemetry question answered; stays Pilot, now blocked only on binary install and local
  Chrome approval, not on privacy.
- E: token question answered; stays Pilot with the `gh`-absent condition above; do not run it
  as shipped.
- Neither changes the Adopt set. Neither check ran external code or a model.
