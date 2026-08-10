# freeCodeCamp News

**The only directory-type, exhaustible platform in this tier.** One request returns every author — no tag-walking, no convergence estimating.

**There is editorial review, but that gate does not filter for "has their own site".** Measured over 501 authors, **only 28% have an own domain** — the same order as zero-barrier platforms; the earlier 12/12 was a twelve-person sample and does not survive scaling. The tier's first filter still applies here in full.

**Its value is exhaustibility, not purity:** five-hundred-plus authors listed in one shot, no guessing when to stop.

## The complete author list is in the sitemap

```
GET https://www.freecodecamp.org/news/sitemap-authors.xml
```

No key, no login, **one response with five-hundred-plus author-page URLs, no paging**. That is the full set; no reverse-engineering authors from articles. **The sitemap has no `lastmod`** — filtering by latest publish date does not exist at this entry.

The homepage and tag pages also surface authors (under 20 each) — **use them only when slicing by vertical**; for the full set go straight to the sitemap.

## Author pages give external links, not emails

```
GET https://www.freecodecamp.org/news/author/<slug>/
```

Server-side rendered. **Take external links from the `Person` block's `sameAs` in the ld+json** — do not wildcard-scrape links off the page: the page carries freeCodeCamp's own social accounts, app-store and CDN URLs, and wildcard scraping mistakes the platform for the person. Name and bio are in the same block.

**Addresses in `sameAs` are not guaranteed a protocol scheme** (bare `iriscode.co` observed); filter out anything non-http(s) before handing to the fetch layer.

**No email on the page** — not a single mailto. All emails come from the [second hop](../_shared/landing-page-two-hop.md), and the landing point here is an own domain, not a social profile — the best landing-point type of any channel.

The RSS (`/news/rss/`) **cannot be used for discovery**: 10 items per fetch, and `dc:creator` is empty.

## Stop semantics

Directory-type — **page to the end**. The sitemap is the end.

## Dedup key

`(author slug, freeCodeCamp News)`. The slug is unique and stable within the platform.

## Two measured ratios

501 authors (the sitemap's first five hundred, in slug lexicographic order):

- **28% have an own domain.**
- **34% of those complete the second hop to an email** — net, ten contactable people per hundred authors, **the highest absolute yield of any entry in this tier**.
- But **only three pass the scale gate** — the platform gives no audience numbers, leaving only sponsorship evidence on the own site.

## To verify

- **How many of the five-hundred-plus are still active** — the sitemap holds the historical full set; one article ever is enough to be listed. Slug-lexicographic sampling is effectively random, but not activity-weighted; whether ordering by latest publish would score higher is unmeasured.
