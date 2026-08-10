# Hashnode

**The API is no longer free; this path now goes through HTML.** The GraphQL endpoint 301s every request to an announcement page — **with or without a token**. This is not an auth failure; the endpoint has been withdrawn entirely. The old `api.hashnode.com` 404s.

The platform's own position is that both reads and writes require the publication to be on Pro. **We do not pay that for discovery** — the key-free path below is sufficient.

## Discover people via tag pages; profile pages give socials

### ① Tag page

```
GET https://hashnode.com/n/<tag>   → 301 https://hashnode.com/tag/<tag>
```

Server-side rendered; handles sit directly in the HTML as `href="/@<handle>"`, no JS execution needed. **Cross-tag overlap is heavy** — scale by switching tags, with diminishing returns.

### ② Profile page: schema.org Person

```
GET https://hashnode.com/@<handle>
```

**What you need is not in the ordinary ld+json script tags.** The two blocks at the top of the page are the platform's own WebSite and Organization; **the person's `ProfilePage` block is buried in Next's escaped payload** — its `mainEntity` is the Person, giving the name and their self-declared external links (`sameAs`).

**Own domains have two sources; combine them**: `sameAs`, plus bare links in the `og:description` bio. Reading only the bio misses most of them — measured: bio-only left 2 out of 72 people.

**Do not wildcard-scrape external links from the page.** The sidebar carries the platform's own promo slots and **other people's** accounts; wildcard scraping attributes unrelated people to the profile owner.

**The only mailto on the page is the platform's own support inbox** — a role address, does not count (see [landing-page-two-hop.md](../_shared/landing-page-two-hop.md)).

## The sponsorship channel is a separate matter

The platform has an official creator-sponsorship channel. **It does not produce contact info** — it is a payment path on the sending side and outside this document's scope — but it overturns the impression that "sponsorship-marketplace things never have a public directory". Kept here as a reminder: what needs verifying is **whether it has a public creator directory**; not yet verified.

## Stop semantics

Search-type — **consecutive rounds with no new results**. Cross-tag overlap is heavy, so convergence comes faster than on DEV.to.

## Dedup key

`(handle, Hashnode)`.

## Measured

One round of five tags yielded about eighty handles; **28% have an own domain, and 26% of those completed the second hop to an email** — net, one round produces five contactable people. **Cross-tag overlap is heavy and a single round hits bottom**; scale requires switching tags.

## To verify

- Whether the sponsorship channel has a publicly browsable creator directory — if so it beats the tag pages, because **people listed there are sellers by definition**.
- Whether tag pages paginate, and the total volume per tag.
