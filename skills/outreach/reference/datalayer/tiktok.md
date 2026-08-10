# TikTok

Third-party API: ScrapeCreators or SociaVault; the two vendors' endpoints are equivalent (see [providers.md](providers.md)).
**The bio is in the profile, not in search results** — every person needs a separate extra lookup; switching vendors will not remove it.
**The profile contains no structured contact field**; the only outward leads are the `signature` text and `bioLink`.

## Discovery: two endpoints, an order of magnitude apart

**`/v1/tiktok/search/users`** — parameters are only `query` / `cursor` / `trim`.
1 credit → 30 handles:

```
signature (bio)    always empty
search_user_desc   just the nickname, not the bio
follower_count     populated
```

**It matches usernames/nicknames, not profile content** — the search term only hits accounts with those words in their names.
The only usable field at this tier is `follower_count`.

**`/v1/tiktok/search/keyword`** — likewise 1 credit → 30 videos, **matched on content**,
working back to authors from videos. Carries play/like/comment counts; the same author can appear repeatedly.

The author's `signature` here is empty as well.

## Enrichment: `/v1/tiktok/profile`

**1 credit per person**; gives `signature` (the bio, 80-character cap) and
`bioLink` (`{link, risk}`; risk is TikTok's own risk score).

**None of Instagram's set of business fields** — the only outward lead in the profile is `bioLink`.

## Per-call cost

Search and profile are 1 credit each. **Search carries no bio, so every candidate costs one extra profile call** —
the sole source of the cost difference vs. Instagram. Unit prices in [providers.md](providers.md).
