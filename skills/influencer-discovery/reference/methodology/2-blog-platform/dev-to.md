# DEV.to

Public API, no key, no login. **Discovery and author fields arrive in one call — no per-person profile lookups.**

## Full chain

```
① Content search        0 requests/person   → 100 articles per tag, author website_url and handle inlined
② Client-side filter    0 requests          → by reactions; fields already in the results
③ Own site → second hop  1 request/person
```

### ① Content search

```
GET https://dev.to/api/articles?tag=<tag>&per_page=100&top=365
```

**The `top` parameter makes or breaks this chain.** Without it you get the latest-first feed, where **70% of authors have zero reactions**; with `top=365`, zero-reaction drops to 7%, median reactions 18, 90th percentile 163. `state=rising` is as bad as the latest feed.

From the `user` object take:

```
username · name · website_url · github_username · twitter_username
```

From the article take `public_reactions_count` (audience signal) and `canonical_url` (**pointing off-site = they maintain their own site**, the hardest threshold signal in this tier).

Scale by switching tags, not by paging. **Dedup by `username` during accumulation** — about 20% of authors recur across tags, which is a vertical-relevance signal.

### ② Client-side filter

**First bucket by `canonical_url` pointing off-site, then look at `reactions`.**

On a zero-barrier platform most people are not bloggers. A `canonical` pointing off-site means **the original of this article lives on their own domain** and DEV.to is just a cross-post — they have already paid the self-hosted-site threshold. **This bucket goes first.**

`reactions` is the platform's only public audience metric; there is no follower-count field.

### ③ Own site → second hop

Follow `website_url` out; see [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

## Expected yield

One round of twelve tags, 558 deduplicated authors:

```
website_url               ~64%
canonical pointing off-site  ~18%      ← own blog
appears across tags       ~22%
```

## Two paths not taken

**Do not fetch profile pages to mine bios.** `GET /api/users/by_username?url=<username>` costs one extra request per person; bios are non-empty 98% of the time but **only 2% contain an email**. The entire cost of this path is wasted.

**Do not take the `github_username` hop.** It does yield emails, but using that field as a contact path means filtering for "this person distributes" by "this person writes code" — it selects for founders and self-builders, who fail the admission gate. See [seller-vs-buyer.md](../_shared/seller-vs-buyer.md) for the test.

## Stop semantics

Search-type — **consecutive rounds with no new results**. `top=365` is a time window, not a directory; exhausting it does not mean the well is dry — switching tags yields more people.

## Dedup key

`(username, DEV.to)`.

The handle is unique and stable. **Never key on display name** — `name` is mutable and non-unique.

## Boundaries

- Most people on this platform are developers writing about what they are building; **buyer density may be higher than on personal blogs** — the seller-vs-buyer test cannot be skipped.
- An author's home base is often elsewhere (own blog, newsletter), especially the batch whose `canonical_url` points off-site. **Discovering the same person from their home base is cheaper.**

## To verify

- **Seller/buyer ratio.** The most critical gap in this tier; never measured. The captured titles and tag distribution are enough to judge, but the pass hasn't been run.
- Final email hit rate over `website_url` alone, with the GitHub hop removed. The existing reachability numbers include GitHub and cannot be reused directly.
- Yield difference between `top` set to 30 / 90 vs 365.
