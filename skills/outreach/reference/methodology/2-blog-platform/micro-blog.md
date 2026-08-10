# Micro.blog

**Entry verified, yield unmeasured.** The platform's discover page is a JS template; what is actually fetchable is the JSON Feed behind it, no key, no login:

```
GET https://micro.blog/posts/discover
```

50 items per call; `items[].author` gives `name`, `url`, `_microblog.username`. 50 items contained 40 distinct authors.

**`author.url` is the person's own site** — no guessing at ownership; a rare deterministic binding in this tier. Some are custom domains, the rest sit on `*.micro.blog` subdomains; both go through the [second hop](../_shared/landing-page-two-hop.md).

The platform has no email field; all yield on this path comes from the second hop.

## Dedup key

`(_microblog.username, Micro.blog)`.

## To verify

- **Pagination and topics.** Only the first screen of 50 has been fetched once; whether it pages back, and whether it can be queried by tagmoji or topic, untried.
- The share of custom domains, and the email hit rate after completing the second hop.
- The seller/buyer ratio of this cohort — the tier-wide gap, see [index.md](index.md).
