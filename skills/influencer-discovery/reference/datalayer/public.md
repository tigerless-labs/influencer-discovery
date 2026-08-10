# No auth

Obtainable with plain HTTP or official free APIs — no login state needed, no credits burned.

Covers YouTube, Newsletter (Substack / Ghost), Blog, Website, Podcast, DEV.to, WordPress.com,
Micro.blog, Gravatar, Hashnode, freeCodeCamp News, HackerNoon, Paragraph, GitHub, Medium,
Passionfroot, Paved, Hacker News, Product Hunt, and arbitrary off-platform pages.

**Whether the caller runs a platform is irrelevant to its listing here.** The boundary is a property of the platform; a platform ruled out
on the caller's side still keeps its boundary here.

## Confirmed

**YouTube** — a channel's `/about` page has the description body and the links section **both in the initial HTML**;
no JS execution, no key. The contact-info button on the About page is guarded by login and reCAPTCHA;
the anonymous response contains only its placeholder marker, no address; the official Data API's channel resource has no corresponding field either.
Links-section addresses are in on-site redirect form; the real address is in the query parameter.

**Podcast** — Apple's public search API returns shows by keyword, **each result carrying its feed address**,
no key, no cookie. Feeds are standard RSS; an email in `<itunes:owner>` is required by Apple's submission spec.

**GitHub** — use the official API; no cookies, no page scraping. The user resource has an `email` field,
populated only when the person sets it public. With a token vs. without, rates differ by about two orders of magnitude (core API 5000/h vs 60/h,
search 30/min vs 10/min).

**The published quota is not the only wall.** Endpoints like repo listing have a **secondary rate limit**: you get rejected
with most of the core quota remaining, while **the quota endpoint reports everything normal**. Once triggered, the same batch of endpoints is rejected together; recovery waits for the core quota reset.
Concurrency is the trigger.

**DEV.to** — public API, no key, no login. The article-list endpoint **inlines the author object**:
one request gets the author handle, `website_url`, and engagement counts, no per-person profile lookups.
Fetch by tag, 100 articles per page max. **The sort parameter decides sample quality**: the default is the latest-first stream;
only the time-windowed top sort surfaces authors with engagement.

**Substack** — public read-only endpoints exist under both publication domains and the main site, unauthenticated:
the category endpoint returns all categories with ids; a category's publication list is **fixed-size pages with a pagination flag**,
records carrying publication name, subdomain, custom domain, author real name, and handle.
There is also an endpoint fetching recommended publications by publication id, returning **full objects** for each.
**These JSON endpoints have not a single email field**, **and its RSS has no `<webMaster>` either** — the platform gives no emails at all.
**Rate-limits as soon as concurrency rises**; failures do not look like 404s.

**WordPress.com** — the `public-api.wordpress.com` reader API, no key, no login.
Fetch posts by tag; **each post inlines the author object** (name, stable username, self-reported website, Gravatar profile address)
plus post-level site address and site name. **The author object's `email` field is always `false`.**
Default order is reverse-chronological; **no parameter found for engagement or time-window sorting**.

**Gravatar** — username plus a `.json` suffix is the public profile, no key. Gives display name, bio, location,
a social-account list (twitter / linkedin / youtube and the like), **and `emails` when the person has set them public**
(`[{primary, value}]`). **No dependable `urls` field**; unknown usernames return 404.

**Micro.blog** — the discover page is a JS template, but `posts/discover` under the same path is a standard JSON Feed,
no key. 50 items per fetch; each item's `author` gives display name, **their own site address**, and platform username.
**No email field.** Pagination parameter unprobed.

**Bear Blog** — the discovery page returns a challenge page (403) to crawlers that declare themselves; no browser-free route.

**Tumblr** — the official tag API requires an API key; anonymous gets 401. The no-auth surface: tag-page HTML gives 7 blogs at a time,
**the time-cursor parameter has no effect** — responses are byte-identical; each blog's legacy JSON endpoint is still key-free,
with only seven fields, of which custom domain and feed were **empty across all 10 samples**; per-blog RSS has no author or email tag whatsoever.
The page embeds an anonymous bearer token that enables pagination — **that is bypassing the key gate, not a no-auth surface.**

**Paragraph** — the public REST API's **read endpoints are all unauthenticated**, with an OpenAPI spec available.
Publication search (hard cap 20 items, no pagination parameter), a cursor-paginated site-wide stream (60 per page max),
fetch by tag / slug / domain / wallet address, and **subscriber counts by publication id**.
The sitemap index has ten shards, 25,000 publication addresses per shard.
**The entire spec contains no email, social, or personal-website field**; socials live only in the profile page HTML's JSON-LD `sameAs`;
profile pages are server-rendered, no hydration shell. The RSS path `/@<slug>/rss` is universal;
`<author>` is a platform-synthesized relay address, not the person. User objects carry wallet addresses and Farcaster usernames.
**The two hosts rate-limit worlds apart**: the API host took about twenty requests at 3-second intervals unthrottled;
the web host 429s after six at 3-second intervals, with the penalty lasting several minutes.

**Mirror** — merged into Paragraph. On `mirror.xyz`, apart from a `robots.txt` 301, every path returns a challenge page to an honest UA.

**write.as** — the read site's feed is key-free, 88 posts / 49 blogs at a time; `author` is always the blog title, not a person.
Pagination lives under the read site's own paths; **the whole public surface is a rolling window of about 150 posts**; tag pages are nearly empty; no public directory.
Each blog has key-free JSON (including lifetime view count) and an ActivityPub actor (**no attachment, hence no contact fields**).
**Rate limiting is tight**: 429 after three requests at 2-second intervals.

**Hashnode** — **the GraphQL endpoint has been withdrawn**: any request 301s to an announcement page,
**with or without a token**; the old `api.hashnode.com` host 404s. The platform states both reads and writes require the publication to have Pro.
The remaining no-auth surface is HTML: tag pages are server-rendered, about 20 author handles per page;
profile pages are also server-rendered, giving social links and own domains, **no personal email**.

**freeCodeCamp News** — the site runs on Ghost but **does not expose the Content API's read-only key**.
The no-auth surface is the standard sitemap: the author sub-sitemap **returns every author page address at once, no pagination** (currently 559).
Author pages are server-rendered, giving own domains and social links, **no email field**.
RSS carries only 10 items and `dc:creator` is empty.

**HackerNoon** — RSS is key-free, 20 items at a time; `dc:creator` carries the author name; article links contain the author handle.
**Profile pages and any `/api/` path return a challenge page (403) to crawlers that declare themselves**; the sitemap is readable.

**Ghost** — the Content API is publicly readable; **the read-only key sits in plaintext as `data-key` in the site homepage source**.
The `settings` endpoint gives the site's few outward addresses; the `authors` endpoint gives author names, bios, and websites,
**with the email field in it always empty**.

**Domain registration data (RDAP)** — key-free standard JSON queries. **Covers only `.com/.net/.org`**;
`.io` `.me` `.co` and country suffixes all come up empty. **Must be serial**; concurrency gets rate-limited.
Responses mix registrar privacy-forwarding addresses with real registrant addresses.

**Medium** — profile pages, about pages, and tag pages all 403 for browserless clients;
`medium.com/feed/@<user>` is open — an article RSS without the profile's bio and external links.

**Passionfroot** — creator pages `passionfroot.me/<handle>` are public and server-rendered;
the discovery entry `/discover` requires an account; the sitemap has no creator pages. **No public directory.**

**Paved** — publication pages give crawlers a flat 429; readable in a browser but the key numbers are masked and there is no contact info;
the directory page requires login.

**Link-in-bio pages** — linktr.ee's external links are in the initial HTML, no browser needed; beacons.ai refuses crawlers.

**Off-platform pages are zero-cost** — no auth, no credits, just plain HTTP.
About one site in twenty refuses crawlers that declare themselves (403/429).

## To explore

- Whether the **YouTube official Data API's free quota** can carry the "known channel → description and links" enrichment,
  so pages are scraped only in the discovery stage.
- Whether **directories beyond podcast feeds** (Podcast Index and the like) can resolve feed addresses directly.
- Whether **sites of the same kind beyond the sponsorship marketplaces** have publicly browsable directories.
- The public API shapes of **Hacker News and Product Hunt**, unprobed.
- **Whether WordPress.com has any non-chronological sort**, and **Micro.blog's pagination and topic access**.
- **The Substack category endpoint's pagination cap** and per-category totals.
- **The Ghost route's site coverage** — verified on only a handful of sites.
