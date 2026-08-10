# TikTok

Data access: [datalayer/tiktok.md](../../datalayer/tiktok.md); whether to take this path:
[cost-ranking.md](../_shared/cost-ranking.md).

The search endpoint does not return bios, and contact info lives in the bio — two steps are
mandatory: get handles first, then fetch profiles one by one.

## Full chain

```
① content search           1 credit         → 30 videos, deduped to ~29 authors (no bio)
② client-side filter       0 credit         → top N by cumulative play count, descending
③ per-person profile       1 credit/person  → signature + bioLink
④ extract email from bio   0 credit
⑤ no email → second hop    0 credit
```

**Filtering must happen before ③** — search results carry follower and play counts, which is
enough to filter on.

### ① content search

```
GET /v1/scrape/tiktok/search/keyword?query=<keyword>&sort_by=most-liked
```

Endpoint contract (parameter names, headers): [datalayer/tiktok.md](../../datalayer/tiktok.md).

From `data.search_item_list` take three fields:

```
aweme_info.author.unique_id        handle
aweme_info.author.follower_count   follower count
aweme_info.statistics.play_count   play count
```

Dedup by `unique_id` and accumulate play counts. **The same author recurring is a signal of niche
relevance.**

`author.signature` is empty here.

Don't use `search/users`: it matches usernames/nicknames rather than content, and mostly returns
hollow accounts.

### ② client-side filter

Descending by cumulative play count. **Play count reflects current activity better than follower
count** — an account with a few thousand followers can have over a hundred thousand plays.

### ③ per-person profile

```
GET /v1/scrape/tiktok/profile?handle=<unique_id>
```

```
data.user.signature        bio, 80-character cap
data.user.bioLink.link     external link; bioLink is a {link, risk} object, not a string
```

### ④⑤ email extraction and second hop

Regex over `signature`. If nothing, follow `bioLink.link` into
[landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

Contact info in a bio is not necessarily an email — a WhatsApp number or an Instagram handle
**both count as reachable**.

## Expected hits

```
bio non-empty     ~100%
email in bio      ~53%      ← more than double Instagram's
has bioLink       ~93%
reachable         ~93%
```

## Parsing pitfalls

- **`search_item_list` and `user_list` are dicts, not lists**, keyed `"0"`…`"29"`.
  Indexing `[0]` directly raises KeyError; call `.values()` first.
- **`bioLink` is an object**; take `.link`.
- **An empty bio is genuinely empty.** Even a million-follower account can have an empty
  `signature` and a `None` `bioLink`; the person didn't fill it in — the endpoint isn't broken.
