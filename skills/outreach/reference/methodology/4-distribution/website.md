# Website

**Sites that do distribution** — tool-recommendation sites, directories, list sites, link hubs. One criterion only: **its output is pushing other people's work to its readers**.

**Company sites and product sites do not belong here and do not enter the sheet.** They want traffic and will not distribute for us; see [seller-vs-buyer.md](../_shared/seller-vs-buyer.md). This tier narrows from "sites with an address" to "sites with distribution capability" — the narrowing is in admission, not in scraping method.

In the target sheet this tier is mostly `Contact Method = Contact Form`, not `Email` — that is not a scraping failure; these sites simply only offer forms.

## Entry

**Search-type.** Enter through queries like "best X tools", "X alternatives", "awesome X"; landing pages that self-describe as lists, directories, or hubs become candidates.

Historically most rows in this tier were landing points carried over from other channels. **After the narrowing, that route no longer produces rows for this channel** — a second hop landing on a company or product site records only an address entry in the log, never a row.

## Want the submission entry, not a person

**This tier's output is not a specific person** but **how to submit work**: an inclusion form, `submit@`, a "suggest a tool" page.

**Role-facing addresses count here.** `info@` / `submit@` / `contact@` do not count as a general rule (see [landing-page-two-hop.md](../_shared/landing-page-two-hop.md)); **this channel is the sole exception** — the target is the site itself, and that is its public-facing entry.

**Contact forms** — record the form URL as the contact method, **do not fill it**. Filling a form is a write operation, out of scope.

**awesome lists do not belong here** — their submission entry is a PR, not an email.

## Stop semantics

Search-type — **consecutive rounds with no new results**.

## Dedup key

`(site name, Website)`.

**One site, one row.** Rows in this tier are not people; there is one submission entry and no "different people at the same site" — precisely the boundary with [self-hosted.md](../3-personal-site/self-hosted.md): a blog's key is the author, here the key is the site.

## Boundaries

- Forms are not filled.
- Obfuscated emails (images, JS assembly) are not broken.
- **Paid inclusion must be flagged.** "Can be submitted to" and "can be submitted to for free" are two different things — do not blend them into one cell.
- **Guard against roster-page contamination**: a page listing addresses from five or more distinct registered domains is not the site's own; see [landing-page-two-hop.md](../_shared/landing-page-two-hop.md).

## To verify

- How many genuine distribution sites one round of queries yields from scratch, and what share is paid inclusion.
- How many of the sheet's existing 62 Website rows fit the narrowed definition. Historical rows are not cleaned, but the ratio should be known.
