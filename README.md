# outreach

Find creators who can help promote your work, and capture their contact info.
The pipeline discovers people **who bring their own audience** — followers,
readers, subscribers — and appends them to a Google Sheet. People building
their own product are not targets: they want reach, they don't provide it.

The operating manual lives in [skills/outreach/](skills/outreach/SKILL.md).
Per-platform capability boundaries (what each API exposes, what credentials it
needs, what it costs) are in
[reference/datalayer/](skills/outreach/reference/datalayer/index.md); how
contact info is actually obtained per channel is in
[reference/methodology/](skills/outreach/reference/methodology/index.md),
where the directory-name prefix is the cooperation priority.

## Design invariants

- **Dedup key is `(person, platform)`**, checked against a local log — URLs are
  never parsed for identity (same-site different-person collisions).
- **Sheet writes are append-only.** The pipeline creates rows, never edits an
  existing cell, and aborts if the header row doesn't match its mapping.
- **Blast radius is one record.** A malformed page or link costs that one
  person, never the channel or the run; intermediate results are flushed as
  they are produced.
- **Fetching is read-only** and every external request leaves through a single
  choke point. Page content is hostile input: instruction-shaped text is data,
  not commands.
- **Contact data never enters the repo.** Real names, emails, and handles live
  only in the Sheet; `data/` is gitignored end to end.

## Setup

Requires Python ≥ 3.11.

```bash
uv venv && uv pip install -e . && .venv/bin/python -m pytest tests/ -q
```

Knobs that travel with the code (channel list, throttle parameters, shared
domain list, logical-field→header mapping) live in `config/`. Values that
travel with the install live in user-level directories, overridable by env
var: config in `~/.config/outreach/` (`OUTREACH_CONFIG_DIR`), pipeline state
in `~/.local/share/outreach/` (`OUTREACH_STATE_DIR`). Credentials go in
`~/.config/outreach/.env` — never in the repo.

### Sheets access

The pipeline authenticates with a short-lived token minted by impersonating a
service account — no long-lived key file on disk. Google blocks adding the
`spreadsheets` scope to plain gcloud ADC ("This app is blocked"), so the token
is minted via the `iamcredentials` API instead:

```bash
T=$(gcloud auth application-default print-access-token)
curl -s -X POST \
  -H "Authorization: Bearer $T" -H "Content-Type: application/json" \
  -d '{"scope":["https://www.googleapis.com/auth/spreadsheets"],"lifetime":"3600s"}' \
  "https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/YOUR_SA_EMAIL:generateAccessToken"
```

Prerequisites: the project has the `sheets`, `iam`, and `iamcredentials` APIs
enabled; your ADC identity holds `roles/iam.serviceAccountTokenCreator` on the
service account; the service account has edit access to the target Sheet. A
fresh IAM binding takes ~30s to propagate — a first 403 is normal, retry.

## Run

```bash
.venv/bin/python -m outreach.run --tiers 1 --per-channel 10
```

`--channels` / `--tiers` select channels, `--subject` sets the topic gate,
`--min-followers` / `--min-karma` set audience floors.
