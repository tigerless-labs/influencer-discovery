# Data layer

**Each platform's capability boundary — independent of purpose.** What you can get, what you cannot, what credentials it takes, what it costs.
Hand it to someone doing product sourcing, sentiment monitoring, or recruiting instead, and this tier still works.

One file for the publicly accessible surface, one per platform for the rest; vendors are a separate axis, one file of their own.

- [public.md](public.md) — no auth: plain HTTP or official free APIs
- [providers.md](providers.md) — third-party vendor directory: capabilities, URLs, pricing model, experiment records
- [instagram.md](instagram.md) — third-party API, **verified working**
- [tiktok.md](tiktok.md) — third-party API, **verified working**
- [mastodon.md](mastodon.md) — **no auth**; discovery and fetching both key-free
- [threads.md](threads.md) — anonymous reaches the profile page; discovery needs the approval-gated official API or a third party
- [linkedin.md](linkedin.md) — cookie; the discovery step does not exist
- [twitter-x.md](twitter-x.md) — cookie; anonymous gets only the bio
- [reddit.md](reddit.md) — cookie, `rdt` CLI, verified

## Credentials

**All live in `~/.config/influencer-discovery/.env`, `chmod 600`.** Not in the repo, not in logs, not in reference.
Code reads by variable name only; paths appear only in config.

| Variable | Vendor | Status |
|---|---|---|
| `SCRAPECREATORS_API_KEY` | ScrapeCreators | verified working |
| `SOCIAVAULT_API_KEY` | SociaVault | verified working |
| `LAMATOK_API_KEY` | LamaTok | not verified; awaiting top-up |
| `BRIGHTDATA_API_TOKEN` | Bright Data | not verified; zone not yet created |

Runtime values that drift — balances, hit rates — are not recorded here; query a balance endpoint like `/v1/credits`,
or check the run report. Docs record only facts a single call cannot change.

**Do not borrow `~/.config/last30days/.env`.** That is another project's credentials file; sharing it means either side's
key rotation silently breaks the other.

## Three shared facts

**Cookies never touch disk** — read them from the browser cookie DB at use time; the value lives only in process memory.
Persisting means owning expiry, encryption, sync, and leak surface yourself. This machine's Chrome decrypts directly, no keyring blocking.

**The browser is available, but fetching does not rely on it.** This machine's Chrome extension is paired; it can open tabs and read page text.
Its tested use is **telling "the crawler cannot see it" apart from "it really is not there"** — for sites that refuse us,
what it buys back is access, not things that were never on the page. Authorization is per domain, so it can only run serially.

**Server-side filters generally do not exist** — no server-side filtering on follower count, region, or niche. But search results carry
`follower_count`, so **client-side filtering costs nothing extra**. The one exception is Instagram:
its query consumes the bio text itself, so filter conditions can be written into the query.

## One exclusion rule

**Anything with a monthly fee is out.** Modash, HypeAuditor, CreatorDB, Janney AI — all excluded.
Only pay-as-you-go, official free APIs, or self-built.

## Two kinds of credentials, different origins

**Purchased keys** live in the env file; a human fills them in once and replaces them on expiry.

**Login state never lands in env.** It is something the user's browser already has, fetched at use time: X's session token is read from the browser
and handed to the fetcher; Reddit's CLI fetches from the browser itself and stores it in its own credentials file.
**Neither is written into any file of this project, and neither is logged.**

**Login state is not a config item; it is the user's current state** — the browser either has it or it does not; it cannot be typed into env.

**Reading values out of Chrome's cookie store requires `browser-cookie3`** — the standard library cannot; the values are encrypted.
Platforms whose CLI handles login itself do not need it; it is used only on the routes without a CLI.
