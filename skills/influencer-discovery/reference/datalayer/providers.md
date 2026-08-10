# Third-party vendors

A directory. Records only **capabilities, URLs, pricing model, experiment records**.

**No price comparison, no ranking, no recommendations — not even unit conversion** — record the pricing model verbatim; which is cheaper is for the use case to compute.

All pay-as-you-go. Anything with a monthly fee is out; see [index.md](index.md).

## Directory

| Vendor | Coverage | Pricing | Experiments |
|---|---|---|---|
| ScrapeCreators | 20+ platforms | $47 / 25,000 credits; $497 / 500,000 credits. **Cache hits free** | ✅ Instagram, TikTok, Threads |
| SociaVault | 25+ platforms; credits never expire | $29 / 6,000 credits; $79 / 20,000 credits | ✅ TikTok, Threads |
| LamaTok | TikTok only, **no Threads** | $0.001 / request; tiered discounts at $50 / $100 / $300 | ⬜ account has no balance; top up or claim in the dashboard |
| Bright Data | general scraping | $0.0015 / record; 5,000 records free per month | ⬜ zone still to be created in the console |
| TikHub | 16 platforms, **incl. Xiaohongshu / Bilibili / Weibo / Zhihu / Kuaishou / WeChat** | $0.001–0.01 / request | ⬜ not registered |

## URLs and auth

Credential variable names in [index.md](index.md#credentials).

| Vendor | base | endpoint list | header |
|---|---|---|---|
| ScrapeCreators | `https://api.scrapecreators.com` | `openapi.json` (175 endpoints) | `x-api-key` |
| SociaVault | `https://api.sociavault.com/v1/scrape/` | `llms.txt` | `X-API-Key` |
| LamaTok | `https://api.lamatok.com` | `/openapi.json` (23 endpoints) | `x-access-key` |
| Bright Data | — | — | `Authorization: Bearer` |

Both endpoint lists live under their respective docs domains, free to fetch.

## Unique capabilities

- **SociaVault `/tiktok/demographics`** — audience country distribution. The only vendor offering audience demographics pay-as-you-go;
  everyone else keeps this data in monthly-fee products.
- **ScrapeCreators cache hits are free** — re-fetching the same batch of objects costs nothing more.
- **ScrapeCreators' Threads user search** — search accounts by username, ten at a time.
  SociaVault has no such endpoint (the same path 404s); its Threads offering is only content search, profile,
  user posts, and single post — four endpoints.

## Probing costs nothing

SociaVault's balance endpoint `/v1/credits` and malformed-parameter requests both deduct no credits; probe freely.

## Three cross-vendor facts

**Instagram's `business_email` is always null; switching vendors will not get it.**

In the response, `business_contact_method` and `business_address_json` carry real values, and `should_show_public_contacts`
is mostly true — the structure is what the platform serves; only the email and phone values are hollowed out. Anonymous scraping of the public web page has none either.
**The value sits behind the login wall; it is a platform boundary.**

**Threads search gives no follower count; switching vendors will not get it.**

In both vendors' Threads search responses, the author object has **only** identity fields like `username` / `full_name` / `is_verified` —
**no `follower_count`, no bio**. Both vendors return the same underlying data
(the same post id), meaning they relay the same upstream — **this is dictated by the platform's response structure, not a vendor-selection problem.**

The consequence: filtering can only happen after the profile-page step, and profile pages are billed per person.

**TikTok bios cost one extra call; switching vendors will not remove it.**

The bio itself is obtainable — the `profile` endpoint gives `signature` and `bioLink`. What cannot be removed is that call:
search returns only handles, and every person needs a separate lookup.

ScrapeCreators' and SociaVault's search responses are raw relays of TikTok's internal API, structurally identical,
`signature` uniformly empty. Any service wrapping that API yields the same result — **dictated by the platform's response structure,
not vendor selection.** Unless some vendor does not relay directly and does its own enrichment; none verified so far.

## The unverified ones are one capability check away

Whether LamaTok's profile endpoint **returns `signature` / `bioLink` is unknown.** First thing after topping up is to verify it —
if it does not, LamaTok is just a video API and its coverage cell must be rewritten.
