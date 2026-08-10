# Instagram

Third-party API: ScrapeCreators. **The only platform where accounts can be searched by profile content.**

## Discovery: `/v1/instagram/search/profiles`

`query` consumes **bio or caption keywords**, not usernames. This is the only place among the 175 endpoints
where people can be found by creator attributes.

**1 credit → 4 to 7 creators**, results carrying:

```
biography · bio_links · external_url · category_name
is_business_account · is_professional_account · is_verified · is_private
username · full_name
```

**Carries `follower_count`, 4/4 hits** (re-verified 2026-08-07; the earlier "no follower count" note was wrong —
it tested `/v1/instagram/search`, a different endpoint that returns only username and full_name, not enough to judge a person).
**No separate profile purchase needed for follower counts**; a full round of nine hundred people fell back only four times.

**Search results already carry the bio and external links** — enough to judge a person; this is the structural difference from TikTok.

**Multi-word queries can 500.** `ai agent` works; `ai tools` errors reliably.

The query consumes the bio text itself, so filter conditions can be written into the search term — no after-the-fact filtering needed.

Underneath it wraps Google's index (the cursor is a Google results page). **Pagination returns are unstable** — the same query
paged three times returned 5 / 7 / 3 items, with the first result shifting. Volume comes from multiple query variants, not pagination.

## Enrichment: `/v1/instagram/profile`

1 credit; gives `follower_count`, `biography`, `external_url`, `bio_links`.

**`business_email` and `business_phone_number` are always null.** Zero hits across 74 samples, including
accounts with `is_business_account` true. In the same response `business_contact_method` has real values
(`CALL` / `UNKNOWN`), `business_address_json` has a city, and **43 accounts even have
`should_show_public_contacts` as `true`** — the structure is live; only these two values are hollowed out.
Anonymous scraping of the public web page yields not one email either. **The value sits behind the login wall; switching vendors will not get it.**

The same call also carries `edge_related_profiles` (32 similar accounts) and engagement data for the latest 12 posts.

## Per-call cost

Search and enrichment are 1 credit each. Unit prices in [providers.md](providers.md).
