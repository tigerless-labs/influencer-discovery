# Self-hosted blog

**Own domain, their own site, hanging under no platform.** This tier has no platform entry to use — discovery runs only through directory sites and tech communities; contact info lives on their own pages.

**Personal sites publish emails less than company blogs do** — the batch already in the target sheet (skewed toward company blogs) has emails 60% of the time; genuinely personal sites discovered from scratch only 40%. Do not estimate the latter from the former's numbers.

## Entries

**Four key-free sources, none of which blocks an honest crawler. Use them crosswise, because their biases complement each other:**

- **Personal-site directories** (personalsit.es, blogroll.org, indieblog.page) — select for "personal", but **not for technical**. One round can produce a thousand-plus domains.
- **Tech communities** (Hacker News' Algolia endpoint, Lobsters' JSON feed) — select for "technical", but **not for personal**. Filter by **per-domain submission frequency**: one or two submissions is usually a personal blog, high frequency is media. The two communities barely overlap; neither is a subset of the other.

Lobsters' story JSON has a field that directly marks "submitter is the author" — **the only deterministic site→person binding in the whole chain**; no guessing.

Walking outward from blogrolls takes restraint — that is graph traversal, and the design docs have ruled out unbounded expansion.

### Confirmed reachable, not yet run

Key-free, open to honest crawlers; **only fetchability verified, yield not**:

- **Kagi's Small Web feed** — a machine-readable source dedicated to small personal sites, returning a hundred-plus domains per call. Same bias as personal-site directories, and the largest of that class.
- **ooh.directory** — categorized directory; the homepage shows only the day's updates, so browse by category; predominantly non-tech blogs.
- **Vertical list sites** (the "Top 100 blogs in X" kind) — one page gives a hundred-plus domains, but they are **roster pages**: run them as standalone roster sources, never treat one as a second-hop landing point — reason in [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

## Getting contact info

After discovery you land on their own site; **the path is the shared ladder**, not restated here: [landing-page-two-hop.md](../_shared/landing-page-two-hop.md). The hit rates for tiers ①–⑥ were measured precisely on this tier's sites.

## RSS gives names, not emails

**The email slots are dead** — `managingEditor` and `webMaster`, verified once each on two entirely disjoint batches of personal sites, are still zero.

**But the name slot is the best in the chain.** `<author>` / `<dc:creator>` carries the author's name 70% of the time — coverage far above `<meta name="author">` and JSON-LD `Person` nodes. That is exactly the missing half of the dedup key.

Likewise, JSON-LD is worthless as an **email** source (every hit duplicated the homepage) and valuable as an **identity** source.

## Stop semantics

Search-type — **consecutive rounds with no new results**.

## Dedup key

`(author display name, Blog)`.

**Rank display-name sources by coverage: RSS `<author>` / `<dc:creator>` first**, then `<meta name="author">`, then JSON-LD `Person`, with the GitHub account's real name as last resort. Scrape it from the page; never guess it from the domain.

**One domain may house multiple authors** (team blogs, company engineering blogs); deduping by domain collapses them into one — exactly the URL-dedup false merge the design docs describe. **Multi-author sites do not belong here**: media goes to [5-media/](../5-media/index.md); company engineering blogs are product sites and stay out of the sheet.

## Boundaries

- Mostly static sites without CDNs; polite intervals must be generous; domain-registration lookups must be serial.
- Third-party subscribe/contact/booking widgets **do not leak the owner's email** — the recipient address lives server-side; do not parse them.
- Some blogs have only socials and no email; then the social handle is the recorded contact form.
- Personal-blog domains change and historical links die — dead links go in the run report, not the log.

## To verify

- Domains produced by the discovery entries have passed neither the seller-vs-buyer test nor an overlap check against existing sheet rows.
- Lobsters' profile endpoint rate-limits tightly; the required polite interval is unmeasured.
