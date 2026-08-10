# Newsletter

Second-largest channel in the target sheet. **Identify the host first — it decides which path to take; the difference is one request versus five.**

Identifying the host **cannot rely on root-page string matching**, which misclassifies; falsify with the host's own endpoint (hit Substack's `/api/v1/archive` once — anything but 200 means not Substack).

## Entries

**Substack itself keeps two free entries open, neither needing anything beyond a seed.**

### Category API — cold start, directory-type

```
substack.com/api/v1/categories                     all categories with ids
substack.com/api/v1/category/public/<id>/all?page=N  25 publications per page, with a more flag for paging
```

Each record carries the publication name, subdomain, custom domain, **author's real name and handle**, and bio directly. Targeted by category, no seed required.

**The email fields are dead weight** — the two email fields in the records are almost always empty; addresses come from the feed hop below.

### Recommendation graph — targeted expansion, search-type

```
<publication domain>/api/v1/recommendations/from/<publication_id>
```

Returns not links but **full objects of the recommended publications**. Measured: one hop expands 7x+, each carrying the author's real name and handle. Covers only Substack internally; the graph does not cross hosts.

### The sponsorship-marketplace entry is dead

Verified across twenty of them: **"has a public directory" and "gives contact info" never co-occur**. Passionfroot's directory requires an account; handles have historical links as their only source, and 60% of that batch already 404s.

## Getting contact info

### Substack: no email on the platform; custom domains are the only way

**`<webMaster>` is gone from the feeds.** (Re-verified 2026-08-06; ten publications, zero hits.) Its JSON endpoints give no email field either. **A direct email path does not exist on this platform.**

What those endpoints give is **identity**: the author's real name and handle can be taken directly, no page guessing. The dedup key `(person, platform)` is therefore at its most solid on this platform.

Only one email path remains: **the custom domain in the record goes through the [second hop](../_shared/landing-page-two-hop.md)**; publications without a custom domain end here.

### Ghost: the Content API settings endpoint

Ghost's Content API key sits in plaintext in the homepage source — **it is a public read-only key meant for the frontend**.

```
/ghost/api/content/settings/?key=<key>    the support / members / default addresses
/ghost/api/content/authors/?key=<key>     author name / bio / website, email always null
```

**A grade below Substack; must be filtered by value**: drop `noreply@` outright, treat `@ghost.io` as a platform forwarding address. The sample is still too small; treat as a supplementary path, not the main one.

### beehiiv and the rest

**beehiiv fills `<webMaster>` with its own support address** — non-empty but does not count; a field being non-empty is not grounds to trust it. Its API requires a key, the page carries none in plaintext, and there is no public mirror like Ghost's.

WordPress, Buttondown, and static-site generators fill none of the feed fields. These fall back to the site itself: unlike blogs, **newsletter emails live more often on subpages than the homepage**. `/advertise`-style sponsorship entries exist on only a scattering of sites, and anything found must still pass [seller-vs-buyer.md](../_shared/seller-vs-buyer.md).

Failing all that, fall back to the second hop; see [landing-page-two-hop.md](../_shared/landing-page-two-hop.md). **Prefer structured fields as second-hop launch pads**: the external-links array in Substack author profiles, Ghost authors' `website` — both cheaper than parsing pages.

**Every email's footer** also carries contact info, but that requires subscribing — **do not subscribe**: it is a write operation, and it exposes this project's identity to the target.

## Judgment: personal newsletter or media product

This distinction decides whether the captured address counts:

- **Personal newsletter** — the author's own address; counts.
- **Media-ized newsletter** (editorial staff, rate card) — what you get is a role-facing address. **Useful for sponsorship placement, does not count for personal outreach**; see "What does not count" in [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

## Stop semantics

**Two kinds, tracked separately per entry.** The category API is **directory-type** — paging until `more` is false means enumeration is complete, a factual boundary. The recommendation graph and site search are **search-type**, stopping on consecutive no-new-results. Mixing the two in one record hides which path is still worth investing in.

## Dedup key

`(newsletter name, Newsletter)`.

Note the same person may have both a newsletter and a YouTube channel — that lands as **two rows**, a cost the design accepts (direction-safe, human-visible), not a bug.

## Boundaries

- Big-name newsletters often gate the rate card behind a form; **do not fill forms** — that is a write operation.
- No guessing personal emails — the existing contact notes in the target sheet say so themselves.
- **The public endpoints rate-limit at any real concurrency**; go serial with intervals. A rate-limited response does not look like a 404 — do not misread it as "absent".
- **Historical links cannot be reused directly.** The batch in the sheet pointing at sponsorship marketplaces has rotted at scale.

## To verify

- The Ghost path's actual hit rate — sample too small; must be topped up before promoting it to a main path.
- Whether beehiiv publication pages have a fixed author landing spot.
- The recommendation graph's second-hop new-yield rate and saturation point — the "consecutive no-new" threshold currently has no measured basis.
- The category API's paging ceiling and per-category totals.
