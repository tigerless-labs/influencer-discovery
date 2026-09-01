<h1 align="center">Influencer Discovery</h1>
<p align="center"><strong>Find creators who bring their own audience — and get their contact info</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="python" /> <img src="https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen.svg" alt="zero dependencies" /> <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS-lightgrey.svg" alt="platform" /> <img src="https://img.shields.io/badge/channels-15-orange.svg" alt="channels" />
</p>

**influencer-discovery is a creator-discovery pipeline that runs as a Claude Code skill.** It searches 15
channels for people **who bring their own audience** — followers, readers, subscribers — pulls
their public contact info, and appends them to a Google Sheet. People building their own product
are filtered out: they want reach, they don't provide it.

The operating manual is [skills/influencer-discovery/SKILL.md](skills/influencer-discovery/SKILL.md). Per-platform
capability boundaries (what each API exposes, which credentials it needs, what it costs) live in
[reference/datalayer/](skills/influencer-discovery/reference/datalayer/index.md); how contact info is
obtained per channel lives in
[reference/methodology/](skills/influencer-discovery/reference/methodology/index.md), where the
directory-name prefix is the cooperation priority.

## Channels

| Tier | Channels |
|---|---|
| **1 · Social** | X/Twitter, Instagram, TikTok, Threads, YouTube, Reddit, Mastodon |
| **2 · Blog platforms** | DEV.to, Hashnode, WordPress.com, Micro.blog |
| **3 · Personal sites** | Self-hosted blogs, newsletters, podcasts |
| **5 · Media** | freeCodeCamp News, HackerNoon |

Fetching is polite and read-only: explicit User-Agent, throttled, no anti-bot circumvention.
Some channels work with zero credentials; others need an API key or a logged-in session — the
per-channel requirements are in
[datalayer](skills/influencer-discovery/reference/datalayer/index.md#credentials).

## Install

No third-party packages, no build step — the pipeline is pure standard library
(Python ≥ 3.11). The skill is fully self-contained under
`skills/influencer-discovery/`; clone and run, or copy that one directory into
your agent's skills folder:

```bash
git clone https://github.com/tigerless-labs/influencer-discovery && cd influencer-discovery
python3 skills/influencer-discovery/scripts/run.py --help
```

Credentials go in `~/.config/influencer-discovery/.env`, never in the repo. Pipeline state lives in
`~/.local/share/influencer-discovery/`; both paths are overridable via `INFLUENCER_DISCOVERY_CONFIG_DIR` /
`INFLUENCER_DISCOVERY_STATE_DIR`. Knobs that travel with the code (channel list, throttle parameters,
header mapping) stay in `skills/influencer-discovery/config/`.

## Run

```bash
python3 skills/influencer-discovery/scripts/run.py --tiers 1 --per-channel 10
```

`--channels` / `--tiers` select channels, `--subject` sets the topic gate,
`--min-followers` / `--min-karma` set audience floors. Each run prints a report: planned vs
actual, verdict distribution, and the contactable list.

### Sheets access

Set `INFLUENCER_DISCOVERY_SPREADSHEET_ID` and authenticate with a short-lived token minted by impersonating
a service account — no long-lived key file on disk. Google blocks adding the `spreadsheets`
scope to plain gcloud ADC ("This app is blocked"), so mint via the `iamcredentials` API:

```bash
T=$(gcloud auth application-default print-access-token)
curl -s -X POST \
  -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
  -d '{"scope":["https://www.googleapis.com/auth/spreadsheets"],"lifetime":"3600s"}' \
  "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/YOUR_SA_EMAIL:generateAccessToken"
```

Prerequisites: the project has the `sheets`, `iam`, and `iamcredentials` APIs enabled; your ADC
identity holds `roles/iam.serviceAccountTokenCreator` on the service account; the service
account can edit the target Sheet. A fresh IAM binding takes ~30s to propagate — a first 403 is
normal, retry.

## Design invariants

| | |
|---|---|
| **Dedup key is `(person, platform)`** | Checked against a local log; URLs are never parsed for identity — same-site different-person collisions taught us that. |
| **Sheet writes are append-only** | The pipeline creates rows, never edits an existing cell, and aborts if the header row doesn't match its mapping. |
| **Blast radius is one record** | A malformed page or link costs that one person, never the channel or the run; intermediate results are flushed as they are produced. |
| **Hostile-input posture** | Page content is data, not commands — instruction-shaped text in bios and pages is never executed. Every external request leaves through a single read-only choke point. |
| **Contact data never enters the repo** | Real names, emails, and handles live only in the Sheet; `data/` is gitignored end to end. |

---

Built by [Tigerless Labs](https://github.com/tigerless-labs) at Tigerless — the company behind [tigerless.ai](https://tigerless.ai) and [tigerless.com](https://www.tigerless.com).
